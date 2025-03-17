from fastapi import APIRouter, Path, Depends
from app.api.controllers.job_controller import JobController
from app.middleware.auth import get_current_user

router = APIRouter(
    prefix="",
    tags=["jobs"]
)
job_controller = JobController()

@router.get("/{job_id}", include_in_schema=True)
async def get_job_result(
    job_id: str = Path(..., description="Job ID"),
    current_user=Depends(get_current_user)  # Add authentication dependency
):
    """
    Get job result by job ID
    """
    # You could add authorization logic here if needed
    # For example, check if the job belongs to the current user
    
    return await job_controller.get_job_result(job_id) 