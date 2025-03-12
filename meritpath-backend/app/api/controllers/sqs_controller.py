import logging
import uuid
from app.lib.sqs import SQSClient

logger = logging.getLogger(__name__)

class SQSController:
    def __init__(self):
        self.sqs_client = SQSClient()
    
    async def send_test_job(self, end_number=None):
        """
        Send a test job to the SQS queue
        """
        # Generate a unique job ID
        job_id = str(uuid.uuid4())
        
        job = {
            "job_id": job_id,
            "job_type": "print_numbers",
            "job_params": {
                "end_number": end_number
            }
        }
        
        message_id = await self.sqs_client.send_message(job)
        
        if message_id:
            return {
                "status": "success",
                "message": "Job sent to queue",
                "message_id": message_id,
                "job_id": job_id,
                "job": job
            }
        else:
            return {
                "status": "failed",
                "message": "Failed to send job to queue"
            } 