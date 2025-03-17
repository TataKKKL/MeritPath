from fastapi import APIRouter, Query, Body, Path
from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.api.controllers.sqs_controller import SQSController

router = APIRouter(
    prefix="",
    tags=["sqs"]
)
sqs_controller = SQSController()

class JobRequest(BaseModel):
    job_type: str
    job_params: Optional[Dict[str, Any]] = None


@router.post("/jobs", include_in_schema=True)
async def send_job(job_request: JobRequest = Body(...)):
    """
    Send a job to the SQS queue with specified type and parameters
    
    Example:
    ```json
    {
        "job_type": "print_numbers",
        "job_params": {
            "user_id": "xxx",
            "end_number": 10
        }
    }
    ```
    
    Or:
    ```json
    {
        "job_type": "find_citers",
        "job_params": {
            "user_id": "xxx"
        }
    }
    ```
    """
    result = await sqs_controller.send_job(
        job_request.job_type, 
        job_request.job_params
    )
    return result 