from fastapi import APIRouter, Depends, HTTPException, Body
from app.middleware.auth import get_current_user
from app.lib.supabase import supabase
from pydantic import BaseModel
import logging
import argparse
from collections import defaultdict, Counter
import csv
import json
# import matplotlib.pyplot as plt
from requests import Session
import s2
import time
from requests.exceptions import HTTPError, RequestException


MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds


def api_call_with_retry(func, *args, **kwargs):
    """Wrapper function to retry API calls with exponential backoff."""
    for attempt in range(MAX_RETRIES):
        try:
            return func(*args, **kwargs)
        except (HTTPError, RequestException) as e:
            if attempt == MAX_RETRIES - 1:
                print(f"Error after {MAX_RETRIES} attempts: {e}")
                return None
            wait_time = RETRY_DELAY * (2 ** attempt)
            print(f"Error: {e}. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)

def get_author_details(author_id: str, session: Session) -> str:
    """Fetch the name of the author given the author ID."""
    author_details = api_call_with_retry(s2.api.get_author, authorId=author_id, session=session)
    return author_details

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

# not only update the semantic scholar id, but also update the user's profile
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
        
        # Update the user record
        session = Session()
        author_details = get_author_details(data.semantic_scholar_id, session)
        
        # Convert S2AuthorPaper objects to dictionaries
        papers_json = []
        for paper in author_details.papers:
            papers_json.append({
                "paperId": paper.paperId,
                "title": paper.title,
                "url": paper.url,
                "year": paper.year
            })
        
        response = supabase.table("users").update({
            "semantic_scholar_id": data.semantic_scholar_id,
            "name": author_details.name,
            "influential_citation_count": author_details.influentialCitationCount,
            "author_paper_count": len(author_details.papers),
            "papers": papers_json,  # Use the converted list of dictionaries
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



@router.get("/{user_id}/job_done")
async def check_job_done(
    user_id: str,
    current_user=Depends(get_current_user)
):
    """
    Check if a user is eligible to create new jobs
    
    A user is not eligible if they already have at least one successful find_citers job
    """
    try:
        # Optional: Add authorization check if needed
        # if current_user["id"] != user_id:
        #     raise HTTPException(status_code=403, detail="Not authorized to check this user's eligibility")
        
        # Query Supabase for successful find_citers jobs for this user
        response = supabase.table("jobs").select("*").eq("user_id", user_id).eq("job_type", "find_citers").eq("status", "success").execute()
        
        if hasattr(response, 'error') and response.error:
            logger.error(f"Error checking job eligibility: {response.error}")
            raise HTTPException(status_code=500, detail="Failed to check job eligibility")
        
        # If the user has at least one successful find_citers job, they are not eligible
        job_done = len(response.data) > 0
        
        return {
            "user_id": user_id,
            "job_done": job_done
        }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Exception checking job eligibility: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error checking job eligibility: {str(e)}")

@router.get("/{user_id}/citers")
async def get_user_citers(
    user_id: str,
    current_user=Depends(get_current_user)
):
    """
    Get all citers associated with a user (authenticated endpoint)
    
    Returns a list of citers with their details including citer_id, papers,
    total_citations, citer_name, and paper_count
    """
    try:
        # Query user_citers table for this user
        user_citers_response = supabase.table("user_citers").select("*").eq("user_id", user_id).execute()
        
        if hasattr(user_citers_response, 'error') and user_citers_response.error:
            logger.error(f"Error retrieving user citers: {user_citers_response.error}")
            raise HTTPException(status_code=500, detail="Failed to retrieve user citers")
        
        user_citers_data = user_citers_response.data
        
        if not user_citers_data:
            # Return empty list if no citers found
            return []
        
        # Get all citer_ids
        citer_ids = [item["citer_id"] for item in user_citers_data]
        
        # Create a dictionary for quick lookup of user_citer data
        user_citers_dict = {item["citer_id"]: item for item in user_citers_data}
        
        # Get citer details in batches to avoid exceeding query limits
        BATCH_SIZE = 50
        formatted_citers = []
        
        for i in range(0, len(citer_ids), BATCH_SIZE):
            batch_ids = citer_ids[i:i+BATCH_SIZE]
            
            # Get citer details from citers table for this batch
            citers_response = supabase.table("citers").select("*").in_("id", batch_ids).execute()
            
            if hasattr(citers_response, 'error') and citers_response.error:
                logger.error(f"Error retrieving citer details batch {i//BATCH_SIZE}: {citers_response.error}")
                continue  # Skip this batch but continue with others
            
            citers_data = citers_response.data
            
            # Process this batch of citers
            for citer in citers_data:
                citer_id = citer["id"]
                user_citer = user_citers_dict.get(citer_id)
                
                if user_citer:
                    try:
                        # Add sanitization and validation for each field
                        formatted_citer = {
                            "citer_id": str(citer_id),
                            "semantic_scholar_id": str(citer.get("semantic_scholar_id", "")),
                            "total_citations": int(user_citer.get("total_citations", 0)),
                            "citer_name": str(citer.get("citer_name", "")),
                            "paper_count": int(citer.get("paper_count", 0))
                        }
                        formatted_citers.append(formatted_citer)
                    except (ValueError, TypeError) as e:
                        # Log the problematic data but continue processing other citers
                        logger.warning(f"Skipping citer {citer_id} due to data conversion error: {str(e)}")
                        continue
        
        return formatted_citers
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Exception retrieving user citers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving user citers: {str(e)}")

@router.get("/{citer_id}/individual_citer")
async def get_current_user_citer(
    citer_id: str,
    current_user=Depends(get_current_user)
):
    """
    Get information about a specific citer for the current authenticated user
    
    Returns detailed information about the relationship between the current user and the specified citer
    """
    try:
        user_id = current_user["id"]
        
        # First check if this citer is associated with the current user
        user_citer_response = supabase.table("user_citers")\
            .select("*")\
            .eq("user_id", user_id)\
            .eq("citer_id", citer_id)\
            .execute()
        
        if hasattr(user_citer_response, 'error') and user_citer_response.error:
            logger.error(f"Error retrieving user citer relationship: {user_citer_response.error}")
            raise HTTPException(status_code=500, detail="Failed to retrieve user-citer relationship")
        
        user_citer_data = user_citer_response.data
        
        if not user_citer_data:
            raise HTTPException(status_code=404, detail="Citer not found for this user")
        
        user_citer = user_citer_data[0]
        
        # Get citer details from citers table
        citer_response = supabase.table("citers")\
            .select("*")\
            .eq("id", citer_id)\
            .execute()
        
        if hasattr(citer_response, 'error') and citer_response.error:
            logger.error(f"Error retrieving citer details: {citer_response.error}")
            raise HTTPException(status_code=500, detail="Failed to retrieve citer details")
        
        citer_data = citer_response.data
        
        if not citer_data:
            raise HTTPException(status_code=404, detail="Citer not found")
        
        citer = citer_data[0]
        
        # Combine the data from both tables
        result = {
            "citer_id": citer_id,
            "semantic_scholar_id": citer["semantic_scholar_id"],
            "papers": user_citer["papers"],
            "total_citations": user_citer["total_citations"],
            "citer_name": citer["citer_name"],
            "paper_count": citer["paper_count"]
        }
        
        return result
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Exception retrieving citer information: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving citer information: {str(e)}") 