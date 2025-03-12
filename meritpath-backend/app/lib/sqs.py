import os
import json
import logging
import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Get SQS configuration
SQS_TASK_QUEUE_URL = os.getenv("SQS_TASK_QUEUE_URL")
SQS_RESULTS_QUEUE_URL = os.getenv("SQS_RESULTS_QUEUE_URL")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

if not SQS_TASK_QUEUE_URL:
    logger.warning("Missing SQS_TASK_QUEUE_URL environment variable")

if not SQS_RESULTS_QUEUE_URL:
    logger.warning("Missing SQS_RESULTS_QUEUE_URL environment variable")

class SQSClient:
    def __init__(self):
        self.sqs = boto3.client('sqs', region_name=AWS_REGION)
        self.task_queue_url = SQS_TASK_QUEUE_URL
        self.results_queue_url = SQS_RESULTS_QUEUE_URL
    
    async def send_message(self, message_body, message_attributes=None):
        """
        Send a message to the task queue
        """
        try:
            if isinstance(message_body, dict):
                message_body = json.dumps(message_body)
                
            message_params = {
                'QueueUrl': self.task_queue_url,
                'MessageBody': message_body
            }
            
            if message_attributes:
                message_params['MessageAttributes'] = message_attributes
                
            response = self.sqs.send_message(**message_params)
            message_id = response.get('MessageId')
            
            if message_id:
                logger.info(f"Message sent to SQS task queue with ID: {message_id}")
                return message_id
            else:
                logger.error("Failed to send message to SQS task queue")
                return None
        except Exception as e:
            logger.error(f"Error sending message to SQS task queue: {str(e)}")
            return None 