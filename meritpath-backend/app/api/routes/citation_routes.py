from fastapi import APIRouter, Depends, HTTPException
from app.middleware.auth import get_current_user
from app.lib.supabase import supabase
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

@router.get("/{paper_id}/citers")
async def get_citation_users(
    paper_id: str,
    current_user=Depends(get_current_user)
):
    """
    Get all users who have cited a specific paper
    """
    try:
        # Find all citations where this paper is cited
        citation_results = supabase.table("citations").select("id").eq("citing_paper_id", paper_id).execute()
        print(citation_results)
        
        if not citation_results.data:
            return {"citers": []}
        
        # Extract the citation IDs
        citation_ids = [item["id"] for item in citation_results.data]
        
        # Find all citers who have cited this paper using the citation_ids
        # TODO: citers appear multiple times in the citer_citations table?
        citer_citations = supabase.table("citer_citations").select("citer_id").in_("citation_id", citation_ids).execute()
        
        if not citer_citations.data:
            return {"citers": []}
        
        # Extract citer_ids
        citer_ids = [item["citer_id"] for item in citer_citations.data]
        
        # Lookup details for each citer in the citers table
        citers = supabase.table("citers").select("*").in_("id", citer_ids).execute()
        
        return {"citers": citers.data}
        
    except Exception as e:
        logger.error(f"Error getting citation users: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve citation users: {str(e)}")

@router.get("/{paper_id}/details")
async def get_citation_details(
    paper_id: str,
    current_user=Depends(get_current_user)
):
    """
    Get details of a specific paper with citation count
    """
    try:
        # Get paper details
        paper_response = supabase.table("papers").select("*").eq("id", paper_id).execute()
        
        if not paper_response.data:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        paper = paper_response.data[0]
        
        # Format the paper details with citation count
        formatted_paper = {
            "id": str(paper.get("id", "")),
            "semantic_scholar_id": str(paper.get("semantic_scholar_id", "")),
            "title": str(paper.get("title", "")),
            "year": int(paper.get("year", 0)),
            "created_at": paper.get("created_at"),
            "updated_at": paper.get("updated_at")
        }
        
        return formatted_paper
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting paper details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve paper details: {str(e)}")