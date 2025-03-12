from fastapi import APIRouter, Query
from app.api.controllers.sqs_controller import SQSController

router = APIRouter(
    prefix="",
    tags=["sqs"]
)
sqs_controller = SQSController()

@router.post("", include_in_schema=True)
async def send_test_job(end_number: int = Query(None, description="Optional end number")):
    """
    Send a test job to the SQS queue
    """
    return await sqs_controller.send_test_job(end_number) 