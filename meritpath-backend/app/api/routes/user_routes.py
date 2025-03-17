from fastapi import APIRouter, Depends, HTTPException, Body
from app.middleware.auth import get_current_user
from app.lib.supabase import supabase
from pydantic import BaseModel
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Define request model
class SemanticScholarIdUpdate(BaseModel):
    semantic_scholar_id: str

# Create router
router = APIRouter(prefix="", tags=["users"])

@router.get("/{user_id}")
async def get_user_by_id(
    user_id: str, 
    current_user=Depends(get_current_user)
):
    """
    Get a user's information by ID (authenticated endpoint)
    """
    try:
        # Optional: Add authorization check if needed
        # if current_user["id"] != user_id:
        #     raise HTTPException(status_code=403, detail="Not authorized to access this user's information")
        
        # Query Supabase for the user
        response = supabase.table("users").select("*").eq("id", user_id).execute()
        
        if hasattr(response, 'error') and response.error:
            logger.error(f"Error retrieving user: {response.error}")
            raise HTTPException(status_code=500, detail="Failed to retrieve user information")
        
        data = response.data
        
        if not data:
            raise HTTPException(status_code=404, detail="User not found")
        
        return data[0]
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Exception retrieving user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving user: {str(e)}")

@router.put("/{user_id}/semantic-scholar-id")
async def update_semantic_scholar_id(
    user_id: str,
    data: SemanticScholarIdUpdate = Body(...),
    current_user=Depends(get_current_user)
):
    """
    Update a user's Semantic Scholar ID (authenticated endpoint)
    """
    try:
        # Check if user is updating their own ID or is an admin
        if current_user["id"] != user_id:
            # In a real app, check if user is admin
            # if not is_admin(current_user):
            raise HTTPException(status_code=403, detail="Not authorized to update this user's information")
        
        # Basic validation
        if not data.semantic_scholar_id or not data.semantic_scholar_id.strip():
            raise HTTPException(status_code=400, detail="Semantic Scholar ID cannot be empty")
        
        # Update the user record - REMOVED updated_at field
        response = supabase.table("users").update({
            "semantic_scholar_id": data.semantic_scholar_id
            # Removed the updated_at field since it doesn't exist
        }).eq("id", user_id).execute()
        
        if hasattr(response, 'error') and response.error:
            logger.error(f"Error updating semantic scholar ID: {response.error}")
            raise HTTPException(status_code=500, detail="Failed to update Semantic Scholar ID")
        
        data = response.data
        
        if not data:
            raise HTTPException(status_code=404, detail="User not found or no update performed")
        
        return data[0]
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Exception updating semantic scholar ID: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating Semantic Scholar ID: {str(e)}") 