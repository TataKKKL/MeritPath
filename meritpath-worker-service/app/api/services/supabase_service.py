import logging
from app.lib.supabase import supabase

logger = logging.getLogger(__name__)

class SupabaseService:
    async def save_job_result(self, job_id, job_type, status, result):
        """
        Save job result to Supabase
        """
        try:
            data = {
                "job_id": job_id,
                "job_type": job_type,
                "status": status,
                "result": result
            }
            
            response = supabase.table("job_results").insert(data).execute()
            
            if hasattr(response, 'error') and response.error:
                logger.error(f"Error saving job result to Supabase: {response.error}")
                return False
                
            logger.info(f"Job result saved to Supabase with job_id: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Exception saving job result to Supabase: {str(e)}")
            return False 