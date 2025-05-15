import json
import logging
import asyncio
from app.lib.sqs import SQSClient
from app.api.services.number_printer_service import NumberPrinterService
from app.api.services.supabase_service import SupabaseService
from app.api.services.find_citer_service import FindCiterService

logger = logging.getLogger(__name__)

class WorkerService:
    def __init__(self, max_concurrent_jobs=10):
        self.sqs_client = SQSClient()
        self.number_printer_service = NumberPrinterService()
        self.supabase_service = SupabaseService()
        self.find_citer_service = FindCiterService()
        self.running = False
        self.max_concurrent_jobs = max_concurrent_jobs
        self.active_tasks = set()
    
    async def start(self):
        """
        Start the worker service with true concurrency
        """
        self.running = True
        logger.info(f"Worker service started with max_concurrent_jobs={self.max_concurrent_jobs}")
        
        while self.running:
            # Only poll for new messages if we have capacity
            if len(self.active_tasks) < self.max_concurrent_jobs:
                try:
                    await self.poll_messages()
                except Exception as e:
                    logger.error(f"Error polling messages: {str(e)}")
                    await asyncio.sleep(1)
            
            # Clean up completed tasks
            self.cleanup_tasks()
            
            # Short delay to prevent CPU spinning
            await asyncio.sleep(0.1)
    
    def cleanup_tasks(self):
        """Remove completed tasks from the active set"""
        done_tasks = {task for task in self.active_tasks if task.done()}
        self.active_tasks -= done_tasks
        
        # Check for exceptions in completed tasks
        for task in done_tasks:
            if task.exception():
                logger.error(f"Task failed with exception: {task.exception()}")
    
    async def stop(self):
        """
        Stop the worker service
        """
        self.running = False
        logger.info("Worker service stopping...")
        
        # Wait for all active tasks to complete (with timeout)
        if self.active_tasks:
            try:
                await asyncio.wait_for(asyncio.gather(*self.active_tasks, return_exceptions=True), timeout=10.0)
            except asyncio.TimeoutError:
                logger.warning("Timeout waiting for tasks to complete during shutdown")
        
        logger.info("Worker service stopped")
    
    async def poll_messages(self):
        """
        Poll for messages and start processing them without waiting
        """
        # Calculate how many messages we can process
        capacity = self.max_concurrent_jobs - len(self.active_tasks)
        if capacity <= 0:
            return
        
        # Limit batch size to our available capacity
        batch_size = min(capacity, 10)  # SQS max batch size is 10
        
        messages = await self.sqs_client.receive_messages(max_messages=batch_size, wait_time=1, visibility_timeout=300)
        
        if not messages:
            return
        
        logger.info(f"Received {len(messages)} messages, starting tasks immediately")
        
        # Start a new task for each message and add to active tasks
        for message in messages:
            # Create task that runs independently
            task = asyncio.create_task(self.process_message(message))
            self.active_tasks.add(task)
            
            # Add callback to clean up when done (alternative to periodic cleanup)
            task.add_done_callback(lambda t: self.active_tasks.discard(t) if t in self.active_tasks else None)
    
    async def process_message(self, message):
        """
        Process a single message completely independently
        """
        receipt_handle = message.get('ReceiptHandle')
        job_id = None
        
        try:
            # Get message body
            body_raw = message.get('Body', '{}')
            
            # Try to parse as JSON
            try:
                body = json.loads(body_raw)
            except json.JSONDecodeError:
                logger.warning(f"Received non-JSON message: {body_raw}")
                # Delete invalid message and skip processing
                await self.sqs_client.delete_message(receipt_handle)
                return
            
            # Extract job parameters
            job_id = body.get('job_id')
            if job_id:
                job_id = str(job_id).lower()
            else:
                logger.warning("Message missing job_id, skipping")
                await self.sqs_client.delete_message(receipt_handle)
                return
            
            logger.info(f"Starting job {job_id}")
            
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
                    # Process the job - this will be non-blocking since each job runs in its own task
                    result = await self.number_printer_service.print_numbers(end_number)
            elif job_type == 'find_citers':
                # Handle the citation processing job
                if not user_id:
                    result = {
                        "status": "failed", 
                        "error": "Missing required parameter: user_id"
                    }
                else:
                    # Process the citation job - this will be non-blocking since each job runs in its own task
                    result = await self.find_citer_service.process_citation_job(user_id)
            else:
                logger.warning(f"Unknown job type: {job_type}")
                result = {"status": "failed", "error": f"Unknown job type: {job_type}"}
            
            logger.info(f"Job {job_id} completed with result: {result}")
            
            # Update job status and save result
            status = result.get('status', 'unknown')
            await self.supabase_service.update_job_status(job_id, status, result)
            
            # Delete the message after successful processing
            await self.sqs_client.delete_message(receipt_handle)
            
        except Exception as e:
            logger.error(f"Error processing message for job {job_id}: {str(e)}")
            # Update job status to 'failed' if we have a job_id
            if job_id:
                await self.supabase_service.update_job_status(job_id, 'failed', {"error": str(e)})
            # Delete the message to avoid reprocessing
            await self.sqs_client.delete_message(receipt_handle)