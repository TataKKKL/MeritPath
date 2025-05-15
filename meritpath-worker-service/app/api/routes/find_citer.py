from fastapi import APIRouter
from app.api.controllers.find_citer_controller import FindCiterController

router = APIRouter(
    prefix="",
    tags=["find_citer"]
)
find_citer_controller = FindCiterController()

@router.post("/by-user-id")
async def find_citer_by_user_id(user_id: str):
    """
    Find authors who have cited the given user's papers by looking up their Semantic Scholar ID.
    """
    return await find_citer_controller.process_citation_job(user_id)
