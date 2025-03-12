from fastapi import APIRouter, Path
from app.api.controllers.job_controller import JobController

router = APIRouter(
    prefix="",
    tags=["jobs"]
)
job_controller = JobController()

@router.get("/{job_id}", include_in_schema=True)
async def get_job_result(job_id: str = Path(..., description="Job ID")):
    """
    Get job result by job ID
    """
    return await job_controller.get_job_result(job_id) 