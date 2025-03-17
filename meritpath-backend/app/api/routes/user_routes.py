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