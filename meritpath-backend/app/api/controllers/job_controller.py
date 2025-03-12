import logging
from app.lib.supabase import supabase

logger = logging.getLogger(__name__)

class JobController:
    async def get_job_result(self, job_id):
        """
        Get job result from Supabase
        """
        try:
            response = supabase.table("job_results").select("*").eq("job_id", job_id).execute()
            
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