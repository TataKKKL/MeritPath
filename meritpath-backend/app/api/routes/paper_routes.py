from fastapi import APIRouter, Depends, HTTPException
from app.middleware.auth import get_current_user
from app.lib.supabase import supabase
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

@router.get("/{paper_id}/citations")
async def get_paper_citations(
    paper_id: str,
    current_user=Depends(get_current_user)
):
    """
    Get all citations for a specific paper (authenticated endpoint)
    
    Returns a list of papers that cite the specified paper, with their details
    """
    try:
        # Check if the paper exists
        paper_response = supabase.table("papers").select("*").eq("id", paper_id).execute()
        
        if hasattr(paper_response, 'error') and paper_response.error:
            logger.error(f"Error retrieving paper: {paper_response.error}")
            raise HTTPException(status_code=500, detail="Failed to retrieve paper information")
        
        if not paper_response.data:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        # Query citations table for all citations where this paper is cited
        citations_response = supabase.table("citations").select("citing_paper_id").eq("cited_paper_id", paper_id).execute()
        
        if hasattr(citations_response, 'error') and citations_response.error:
            logger.error(f"Error retrieving citations: {citations_response.error}")
            raise HTTPException(status_code=500, detail="Failed to retrieve citation information")
        
        citations_data = citations_response.data
        
        if not citations_data:
            # Return empty list if no citations found
            return []
        
        # Get all citing paper IDs
        citing_paper_ids = [citation["citing_paper_id"] for citation in citations_data]
        
        # Get citing paper details in batches
        BATCH_SIZE = 50
        citing_papers = []
        
        for i in range(0, len(citing_paper_ids), BATCH_SIZE):
            batch_ids = citing_paper_ids[i:i+BATCH_SIZE]
            
            # Get paper details from papers table for this batch
            papers_response = supabase.table("papers").select("*").in_("id", batch_ids).execute()
            
            if hasattr(papers_response, 'error') and papers_response.error:
                logger.error(f"Error retrieving citing paper details batch {i//BATCH_SIZE}: {papers_response.error}")
                continue  # Skip this batch but continue with others
            
            papers_data = papers_response.data
            
            # Process this batch of papers
            for paper in papers_data:
                try:
                    formatted_paper = {
                        "id": str(paper.get("id", "")),
                        "semantic_scholar_id": str(paper.get("semantic_scholar_id", "")),
                        "title": str(paper.get("title", "")),
                        "year": int(paper.get("year", 0)),
                        "created_at": paper.get("created_at")
                    }
                    citing_papers.append(formatted_paper)
                except (ValueError, TypeError) as e:
                    # Log the problematic data but continue processing other papers
                    logger.warning(f"Skipping paper due to data conversion error: {str(e)}")
                    continue
        
        return citing_papers
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Exception retrieving paper citations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving paper citations: {str(e)}")

@router.get("/{paper_id}/details")
async def get_paper_details(
    paper_id: str,
    current_user=Depends(get_current_user)
):
    """
    Get detailed information about a specific paper (authenticated endpoint)
    
    Returns comprehensive details about the paper including title, semantic_scholar_id,
    year, and timestamps
    """
    try:
        # Get paper details from papers table
        paper_response = supabase.table("papers").select("*").eq("id", paper_id).execute()
        
        if hasattr(paper_response, 'error') and paper_response.error:
            logger.error(f"Error retrieving paper details: {paper_response.error}")
            raise HTTPException(status_code=500, detail="Failed to retrieve paper details")
        
        paper_data = paper_response.data
        
        if not paper_data:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        paper = paper_data[0]
        
        # Get citation count for this paper
        citations_response = supabase.table("citations").select("id", count="exact").eq("cited_paper_id", paper_id).execute()
        
        if hasattr(citations_response, 'error') and citations_response.error:
            logger.error(f"Error retrieving citation count: {citations_response.error}")
            citation_count = 0
        else:
            citation_count = citations_response.count
        
        # Format the paper with all available details based on the actual schema
        try:
            formatted_paper = {
                "id": str(paper.get("id", "")),
                "semantic_scholar_id": str(paper.get("semantic_scholar_id", "")),
                "title": str(paper.get("title", "")),
                "year": int(paper.get("year", 0)),
                "citation_count": citation_count,
                "created_at": paper.get("created_at"),
                "updated_at": paper.get("updated_at")
            }
            
            return formatted_paper
            
        except (ValueError, TypeError) as e:
            logger.error(f"Error formatting paper data: {str(e)}")
            raise HTTPException(status_code=500, detail="Error formatting paper data")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Exception retrieving paper details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving paper details: {str(e)}")