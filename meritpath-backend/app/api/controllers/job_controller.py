import logging
from app.lib.supabase import supabase

logger = logging.getLogger(__name__)

class JobController:
    async def get_job_result(self, job_id, user_id=None):
        """
        Get job result from Supabase
        """
        try:
            query = supabase.table("job_results").select("*").eq("job_id", job_id)
            
            # If user_id is provided, filter by user_id as well
            if user_id:
                query = query.eq("user_id", user_id)
                
            response = query.execute()
            
            if hasattr(response, 'error') and response.error:
                logger.error(f"Error retrieving job result: {response.error}")
                return {"status": "error", "message": "Failed to retrieve job result"}
            
            data = response.data
            
            if not data:
                return {"status": "not_found", "message": "Job result not found"}
            
            # Return the most recent result if there are multiple entries
            return {"status": "success", "result": data[0]}
        except Exception as e:
            logger.error(f"Exception retrieving job result: {str(e)}")
            return {"status": "error", "message": f"Error retrieving job result: {str(e)}"} 