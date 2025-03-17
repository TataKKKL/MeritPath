from fastapi import APIRouter, Query, Body, Path, Depends
from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.api.controllers.sqs_controller import SQSController
from app.middleware.auth import get_current_user

router = APIRouter(
    prefix="",
    tags=["sqs"]
)
sqs_controller = SQSController()

class JobRequest(BaseModel):
    job_type: str
    job_params: Optional[Dict[str, Any]] = None


@router.post("/jobs", include_in_schema=True)
async def send_job(
    job_request: JobRequest = Body(...),
    current_user=Depends(get_current_user)
):
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
    if job_request.job_params is None:
        job_request.job_params = {}
    
    job_request.job_params["authenticated_user_id"] = current_user["id"]
    
    result = await sqs_controller.send_job(
        job_request.job_type, 
        job_request.job_params
    )
    return result 