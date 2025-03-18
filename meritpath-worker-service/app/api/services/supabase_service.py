import logging
import uuid
from app.lib.supabase import supabase

logger = logging.getLogger(__name__)

class SupabaseService:
    async def insert_job(self, job_id, user_id, job_type, params=None):
        """
        Insert a new job into the jobs table
        """
        try:
            # Use the provided job_id, don't generate a new one
            job_id = str(job_id).lower()  # Ensure lowercase UUID
            data = {
                "id": job_id,
                "user_id": user_id,
                "job_type": job_type,
                "status": "pending",
                "params": params or {}
            }
            
            response = supabase.table("jobs").insert(data).execute()
            
            if hasattr(response, 'error') and response.error:
                logger.error(f"Error creating job in Supabase: {response.error}")
                return None
                
            logger.info(f"Job created in Supabase with job_id: {job_id}")
            return job_id
        except Exception as e:
            logger.error(f"Exception creating job in Supabase: {str(e)}")
            return None
    
    async def get_job(self, job_id):
        """
        Get job details from the jobs table
        """
        try:
            # Ensure job_id is lowercase for consistency
            job_id = str(job_id).lower()
            
            response = supabase.table("jobs").select("*").eq("id", job_id).execute()
            
            if hasattr(response, 'error') and response.error:
                logger.error(f"Error getting job from Supabase: {response.error}")
                return None
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            
            return None
        except Exception as e:
            logger.error(f"Exception getting job from Supabase: {str(e)}")
            return None
    
    async def update_job_status(self, job_id, status, result=None):
        """
        Update job status in the jobs table.
        For 'processing' status, only updates if the job is in 'pending' or 'failed' state.
        """
        try:
            # Ensure job_id is lowercase for consistency
            job_id = str(job_id).lower()
            
            # Check current status if we're trying to update to 'processing'
            if status == 'processing':
                # Only update to processing if currently in pending or failed state
                response = supabase.table("jobs").update({
                    "status": status,
                    "updated_at": "now()"
                }).eq("id", job_id).in_("status", ["pending", "failed"]).execute()
            else:
                # For other statuses, just update
                response = supabase.table("jobs").update({
                    "status": status,
                    "updated_at": "now()"
                }).eq("id", job_id).execute()
            
            if hasattr(response, 'error') and response.error:
                logger.error(f"Error updating job status in Supabase: {response.error}")
                return False
            
            # Check if any rows were updated
            success = response.data and len(response.data) > 0
            
            if success:
                logger.info(f"Job status updated to {status} for job_id: {job_id}")
                
                # If result is provided and status is completed or failed, save the result
                if result and status in ["completed", "failed", "success"]:
                    await self.save_job_result(job_id, result)
            else:
                logger.info(f"No update performed for job {job_id} to status {status}")
                
            return success
        except Exception as e:
            logger.error(f"Exception updating job status in Supabase: {str(e)}")
            return False
    
    async def update_job_status_with_condition(self, job_id, new_status, expected_current_status, result=None):
        """
        Update job status only if current status matches expected_current_status.
        Returns True if update was successful, False otherwise.
        """
        try:
            # Ensure job_id is lowercase for consistency
            job_id = str(job_id).lower()
            
            # Update only if current status matches expected status
            data = {
                "status": new_status,
                "updated_at": "now()"
            }
            
            response = supabase.table("jobs").update(data) \
                .eq("id", job_id) \
                .eq("status", expected_current_status) \
                .execute()
            
            # Check if any rows were updated
            success = response.data and len(response.data) > 0
            
            if success:
                logger.info(f"Job status updated from {expected_current_status} to {new_status} for job_id: {job_id}")
                
                # If result is provided and status is completed or failed, save the result
                if result and new_status in ["completed", "failed", "success"]:
                    await self.save_job_result(job_id, result)
            else:
                logger.info(f"No update performed for job {job_id} - current status doesn't match expected {expected_current_status}")
                
            return success
        except Exception as e:
            logger.error(f"Exception updating job status in Supabase: {str(e)}")
            return False
    
    async def save_job_result(self, job_id, result):
        """
        Save job result to job_results table
        """
        try:
            # Ensure job_id is lowercase for consistency
            job_id = str(job_id).lower()
            
            data = {
                "job_id": job_id,
                "result": result
            }
            
            response = supabase.table("job_results").insert(data).execute()
            
            if hasattr(response, 'error') and response.error:
                logger.error(f"Error saving job result to Supabase: {response.error}")
                return False
                
            logger.info(f"Job result saved to Supabase for job_id: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Exception saving job result to Supabase: {str(e)}")
            return False