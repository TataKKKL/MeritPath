import logging
import uuid
from app.lib.sqs import SQSClient

logger = logging.getLogger(__name__)

class SQSController:
    def __init__(self):
        self.sqs_client = SQSClient()
    
    async def send_job(self, job_type, job_params=None):
        """
        Send a job to the SQS queue with specified type and parameters
        
        Args:
            job_type (str): Type of job to execute (e.g., "print_numbers", "find_citers")
            job_params (dict): Parameters for the job
        """
        # Generate a unique job ID
        job_id = str(uuid.uuid4())
        
        job = {
            "job_id": job_id,
            "job_type": job_type,
            "job_params": job_params or {}
        }
        
        message_id = await self.sqs_client.send_message(job)
        
        if message_id:
            return {
                "status": "success",
                "message": f"Job of type '{job_type}' sent to queue",
                "message_id": message_id,
                "job_id": job_id,
                "job": job
            }
        else:
            return {
                "status": "failed",
                "message": f"Failed to send job of type '{job_type}' to queue"
            }
