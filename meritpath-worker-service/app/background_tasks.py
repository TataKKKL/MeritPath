
import asyncio
import logging
from app.api.services.worker_service import WorkerService

logger = logging.getLogger(__name__)

worker_service = None
worker_task = None

async def start_worker_service():
    """
    Start the worker service in the background
    """
    global worker_service, worker_task
    
    if worker_service is None:
        # Create a worker with higher concurrency 
        worker_service = WorkerService(max_concurrent_jobs=20)
    
    if worker_task is None or worker_task.done():
        # Create a new background task that doesn't block startup
        worker_task = asyncio.create_task(run_worker())
        logger.info("Worker service task created")

async def run_worker():
    """
    Run the worker service in a separate task
    """
    global worker_service
    
    try:
        logger.info("Starting worker service...")
        await worker_service.start()
    except Exception as e:
        logger.error(f"Error in worker service: {str(e)}")

async def stop_worker_service():
    """
    Stop the worker service
    """
    global worker_service, worker_task
    
    if worker_service:
        logger.info("Worker service stopping...")
        await worker_service.stop()
    
    if worker_task and not worker_task.done():
        # Give it a moment to clean up
        try:
            await asyncio.wait_for(worker_task, timeout=5.0)
        except asyncio.TimeoutError:
            # If it doesn't stop gracefully, cancel the task
            worker_task.cancel()
            logger.info("Worker service task cancelled")
    
    logger.info("Worker service stopped")