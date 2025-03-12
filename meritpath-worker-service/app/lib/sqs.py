import os
import json
import logging
import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Get SQS configuration
SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

if not SQS_QUEUE_URL:
    logger.warning("Missing SQS_QUEUE_URL environment variable")

class SQSClient:
    def __init__(self):
        self.sqs = boto3.client('sqs', region_name=AWS_REGION)
        self.queue_url = SQS_QUEUE_URL
    
    async def receive_messages(self, max_messages=1, wait_time=1, visibility_timeout=30):
        """
        Receive messages from SQS queue
        """
        try:
            response = self.sqs.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=wait_time,
                VisibilityTimeout=visibility_timeout,
                AttributeNames=['All'],
                MessageAttributeNames=['All']
            )
            
            return response.get('Messages', [])
        except Exception as e:
            logger.error(f"Error receiving messages from SQS: {str(e)}")
            return []
    
    async def delete_message(self, receipt_handle):
        """
        Delete a message from the queue
        """
        try:
            self.sqs.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting message from SQS: {str(e)}")
            return False
    
    async def send_message(self, message_body, message_attributes=None):
        """
        Send a message to the queue
        """
        try:
            if isinstance(message_body, dict):
                message_body = json.dumps(message_body)
                
            message_params = {
                'QueueUrl': self.queue_url,
                'MessageBody': message_body
            }
            
            if message_attributes:
                message_params['MessageAttributes'] = message_attributes
                
            response = self.sqs.send_message(**message_params)
            return response.get('MessageId')
        except Exception as e:
            logger.error(f"Error sending message to SQS: {str(e)}")
            return None 