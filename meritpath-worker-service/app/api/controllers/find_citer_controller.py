from fastapi import HTTPException
from app.api.services.find_citer_service import FindCiterService

class FindCiterController:
    def __init__(self):
        self.find_citer_service = FindCiterService()
        
    async def process_citation_job(self, user_id: str):
        """
        Execute the find citer service and return the result.
        """
        result = self.find_citer_service.process_citation_job(user_id)
        return result 