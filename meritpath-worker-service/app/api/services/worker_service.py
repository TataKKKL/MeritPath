import json
import logging
import asyncio
import uuid
from app.lib.sqs import SQSClient
from app.api.services.number_printer_service import NumberPrinterService
from app.api.services.supabase_service import SupabaseService
from app.api.services.find_citer_service import FindCiterService

logger = logging.getLogger(__name__)

class WorkerService:
    def __init__(self):
        self.sqs_client = SQSClient()
        self.number_printer_service = NumberPrinterService()
        self.supabase_service = SupabaseService()
        self.find_citer_service = FindCiterService()
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
            messages = await self.sqs_client.receive_messages(max_messages=5, wait_time=20, visibility_timeout=300)
            
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
        job_id = None
        
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
            if job_id:
                job_id = str(job_id).lower()  # Ensure lowercase UUID
            else:
                logger.warning("Message missing job_id, skipping")
                await self.sqs_client.delete_message(receipt_handle)
                return
            
            job_type = body.get('job_type')
            job_params = body.get('job_params', {})
            user_id = job_params.get('user_id')
            
            # Check if job already exists in database
            existing_job = await self.supabase_service.get_job(job_id)
            
            update_success = False
            
            if existing_job:
                # If job exists and is already being processed or completed, skip it
                if existing_job.get('status') in ['processing', 'completed', 'success']:
                    logger.info(f"Job {job_id} is already in state {existing_job.get('status')}, skipping")
                    await self.sqs_client.delete_message(receipt_handle)
                    return
                
                # If job exists but is in a retryable state (pending, failed), use optimistic locking to update
                current_status = existing_job.get('status')
                logger.info(f"Found existing job {job_id} in state {current_status}")
                update_success = await self.supabase_service.update_job_status_with_condition(
                    job_id, 'processing', current_status)
            else:
                # Job doesn't exist, create it with status 'pending'
                job_id = await self.supabase_service.insert_job(job_id, user_id, job_type, job_params)
                if not job_id:
                    logger.error("Failed to create job record")
                    await self.sqs_client.delete_message(receipt_handle)
                    return
                
                # Now try to update from pending to processing
                update_success = await self.supabase_service.update_job_status_with_condition(
                    job_id, 'processing', 'pending')
            
            if not update_success:
                logger.info(f"Failed to update job {job_id} to processing state, another worker might be handling it")
                await self.sqs_client.delete_message(receipt_handle)
                return
            
            # Process based on job type
            result = None
            if job_type == 'print_numbers':
                end_number = job_params.get('end_number')
                if not user_id:
                    result = {
                        "status": "failed", 
                        "error": "Missing required parameter: user_id"
                    }
                else:
                    # Process the job
                    result = await self.number_printer_service.print_numbers(end_number)
            elif job_type == 'find_citers':
                # Handle the citation processing job
                if not user_id:
                    result = {
                        "status": "failed", 
                        "error": "Missing required parameter: user_id"
                    }
                else:
                    # Process the citation job
                    result = self.find_citer_service.process_citation_job(user_id)
            else:
                logger.warning(f"Unknown job type: {job_type}")
                result = {"status": "failed", "error": f"Unknown job type: {job_type}"}
            
            logger.info(f"Job result: {result}")
            
            # Update job status and save result
            status = result.get('status', 'unknown')
            await self.supabase_service.update_job_status(job_id, status, result)
            
            # Delete the message after successful processing
            await self.sqs_client.delete_message(receipt_handle)
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            # Update job status to 'failed' if we have a job_id
            if job_id:
                await self.supabase_service.update_job_status(job_id, 'failed', {"error": str(e)})
            # Delete the message to avoid reprocessing
            await self.sqs_client.delete_message(receipt_handle)