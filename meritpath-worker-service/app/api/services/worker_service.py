import json
import logging
import asyncio
import uuid
from app.lib.sqs import SQSClient
from app.api.services.number_printer_service import NumberPrinterService
from app.api.services.supabase_service import SupabaseService

logger = logging.getLogger(__name__)

class WorkerService:
    def __init__(self):
        self.sqs_client = SQSClient()
        self.number_printer_service = NumberPrinterService()
        self.supabase_service = SupabaseService()
        self.running = False
    
    async def start(self):
        """
        Start the worker service
        """
        self.running = True
        logger.info("Worker service started")
        
        while self.running:
            await self.process_messages()
    
    async def stop(self):
        """
        Stop the worker service
        """
        self.running = False
        logger.info("Worker service stopped")
    
    async def process_messages(self):
        """
        Process messages from the queue
        """
        try:
            messages = await self.sqs_client.receive_messages(max_messages=5, wait_time=1)
            
            if not messages:
                logger.debug("No messages received")
                # Add a small delay when no messages are found to prevent CPU spinning
                await asyncio.sleep(0.5)
                return
            
            logger.info(f"Received {len(messages)} messages")
            
            for message in messages:
                await self.process_message(message)
        except Exception as e:
            logger.error(f"Error in process_messages: {str(e)}")
            # Add delay on error to prevent CPU spinning
            await asyncio.sleep(1)
    
    async def process_message(self, message):
        """
        Process a single message
        """
        receipt_handle = message.get('ReceiptHandle')
        
        try:
            # Get message body
            body_raw = message.get('Body', '{}')
            logger.info(f"Received raw message: {body_raw}")
            
            # Try to parse as JSON
            try:
                body = json.loads(body_raw)
            except json.JSONDecodeError:
                logger.warning(f"Received non-JSON message: {body_raw}")
                # Delete invalid message and skip processing
                await self.sqs_client.delete_message(receipt_handle)
                return
            
            logger.info(f"Processing message: {body}")
            
            # Extract job parameters
            job_id = body.get('job_id')
            job_type = body.get('job_type')
            job_params = body.get('job_params', {})
            
            if not job_id:
                logger.warning("Message missing job_id, generating a fallback ID")
                job_id = str(uuid.uuid4())
            
            # Process based on job type
            result = None
            if job_type == 'print_numbers':
                end_number = job_params.get('end_number')
                result = await self.number_printer_service.print_numbers(end_number)
            else:
                logger.warning(f"Unknown job type: {job_type}")
                result = {"status": "failed", "error": f"Unknown job type: {job_type}"}
            
            logger.info(f"Job result: {result}")
            
            # Save result to Supabase
            status = result.get('status', 'unknown')
            await self.supabase_service.save_job_result(job_id, job_type, status, result)
            
            # Delete the message after successful processing
            await self.sqs_client.delete_message(receipt_handle)
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            # In a production system, you might want to move this to a dead-letter queue
            # For now, we'll just delete it to avoid reprocessing
            await self.sqs_client.delete_message(receipt_handle) 