from fastapi import APIRouter, Depends, HTTPException, Body, Query
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
from typing import Optional


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


@router.get("/{user_id}/papers")
async def get_user_papers(
    user_id: str,
    current_user=Depends(get_current_user)
):
    """
    Get all papers associated with a user (authenticated endpoint)
    
    Returns a list of papers with their details including title, year, and citation count
    """
    try:
        # Query user_papers table for papers of this user
        user_papers_response = supabase.table("user_papers").select("*").eq("user_id", user_id).execute()
        
        if hasattr(user_papers_response, 'error') and user_papers_response.error:
            logger.error(f"Error retrieving user papers: {user_papers_response.error}")
            raise HTTPException(status_code=500, detail="Failed to retrieve user papers")
        
        user_papers_data = user_papers_response.data
        
        if not user_papers_data:
            # Return empty list if no papers found
            return []
        
        # Get all paper_ids
        paper_ids = [item["paper_id"] for item in user_papers_data]
        
        # Get paper details in batches
        BATCH_SIZE = 50
        papers_dict = {}
        
        for i in range(0, len(paper_ids), BATCH_SIZE):
            batch_ids = paper_ids[i:i+BATCH_SIZE]
            
            # Get paper details from papers table for this batch
            papers_response = supabase.table("papers").select("*").in_("id", batch_ids).execute()
            
            if hasattr(papers_response, 'error') and papers_response.error:
                logger.error(f"Error retrieving paper details batch {i//BATCH_SIZE}: {papers_response.error}")
                continue  # Skip this batch but continue with others
            
            papers_data = papers_response.data
            
            # Add papers to dictionary
            for paper in papers_data:
                papers_dict[paper["id"]] = paper
        
        # Get citation counts for each paper
        paper_citation_counts = defaultdict(int)
        
        for i in range(0, len(paper_ids), BATCH_SIZE):
            batch_ids = paper_ids[i:i+BATCH_SIZE]
            
            # Get citations for this batch of papers
            citations_response = supabase.table("citations").select("cited_paper_id").in_("cited_paper_id", batch_ids).execute()
            
            if hasattr(citations_response, 'error') and citations_response.error:
                logger.error(f"Error retrieving citations for batch {i//BATCH_SIZE}: {citations_response.error}")
                continue  # Skip this batch but continue with others
            
            # Count citations for each paper
            for citation in citations_response.data:
                cited_paper_id = citation.get("cited_paper_id")
                if cited_paper_id:
                    paper_citation_counts[cited_paper_id] += 1
        
        # Format papers with citation counts
        formatted_papers = []
        for paper_id in paper_ids:
            paper = papers_dict.get(paper_id)
            
            if paper:
                try:
                    formatted_paper = {
                        "id": str(paper_id),
                        "semantic_scholar_id": str(paper.get("semantic_scholar_id", "")),
                        "title": str(paper.get("title", "")),
                        "year": int(paper.get("year", 0)),
                        "citation_count": paper_citation_counts.get(paper_id, 0)
                    }
                    formatted_papers.append(formatted_paper)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Skipping paper {paper_id} due to data conversion error: {str(e)}")
                    continue
        
        return formatted_papers
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Exception retrieving user papers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving user papers: {str(e)}")


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
                            "paper_count": int(citer.get("paper_count", 0)),
                            "location": str(citer.get("location", "")),
                            "affiliations": str(citer.get("affiliations", "")),
                            "selected": user_citer.get("selected", False),
                            "cited_papers_count": int(user_citer.get("cited_papers_count", 0)),
                            "citing_papers_count": int(user_citer.get("citing_papers_count", 0)),
                            "independent": user_citer.get("independent", True)
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
        print(user_citer)
        
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
        print(citer)
        # 'cited_papers_count': 4, 'citing_users_count': 8
        
        # Combine the data from both tables
        result = {
            "citer_id": citer_id,
            "semantic_scholar_id": citer["semantic_scholar_id"],
            "papers": user_citer["papers"],
            "total_citations": user_citer["total_citations"],
            "citer_name": citer["citer_name"],
            "location": citer["location"],
            "affiliations": citer["affiliations"],
            "paper_count": citer["paper_count"],
            "selected": user_citer["selected"],
            "cited_papers_count": user_citer["cited_papers_count"],
            "citing_papers_count": user_citer["citing_papers_count"],
            "independent": user_citer["independent"]
        }
        
        return result
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Exception retrieving citer information: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving citer information: {str(e)}")

@router.get("/{user_id}/citers/advanced")
async def get_user_citers_advanced(
    user_id: str,
    current_user=Depends(get_current_user),
    # Pagination parameters
    page: int = Query(1, ge=1, description="Current page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    offset: Optional[int] = Query(None, ge=0, description="Alternative to page"),
    
    # Search parameters
    search: Optional[str] = Query(None, max_length=100, description="Search term"),
    search_field: str = Query("citer_name", description="Field to search in"),
    
    # Sorting parameters
    sort_by: str = Query("total_citations", description="Field to sort by"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort direction"),
    
    # Filtering parameters
    independent: Optional[bool] = Query(None, description="Filter by independent status"),
    min_citations: Optional[int] = Query(None, ge=0, description="Minimum citations to your work"),
    max_citations: Optional[int] = Query(None, ge=0, description="Maximum citations to your work"),
    min_papers: Optional[int] = Query(None, ge=0, description="Minimum papers published"),
    max_papers: Optional[int] = Query(None, ge=0, description="Maximum papers published"),
    location: Optional[str] = Query(None, max_length=100, description="Filter by location")
):
    """
    Get all citers associated with a user with advanced filtering, sorting, and pagination
    
    Supports comprehensive search, filtering, and sorting capabilities for citers
    """
    try:
        # Validate sort field
        VALID_SORT_FIELDS = [
            'citer_name', 'paper_count', 'total_citations', 
            'cited_papers_count', 'citing_papers_count', 'independent'
        ]
        
        if sort_by not in VALID_SORT_FIELDS:
            raise HTTPException(status_code=400, detail=f"Invalid sort field. Must be one of: {VALID_SORT_FIELDS}")
        
        # Validate search field
        VALID_SEARCH_FIELDS = ['citer_name', 'location', 'affiliations']
        if search_field not in VALID_SEARCH_FIELDS:
            raise HTTPException(status_code=400, detail=f"Invalid search field. Must be one of: {VALID_SEARCH_FIELDS}")
        
        # Calculate pagination
        if offset is not None:
            start = offset
            current_page = (offset // limit) + 1
        else:
            start = (page - 1) * limit
            current_page = page
        
        # Step 1: Build query for user_citers table (filters that apply to user_citers)
        user_citers_query = supabase.table("user_citers").select("*").eq("user_id", user_id)
        
        # Apply filters to user_citers table
        if independent is not None:
            user_citers_query = user_citers_query.eq("independent", independent)
        
        if min_citations is not None:
            user_citers_query = user_citers_query.gte("total_citations", min_citations)
        
        if max_citations is not None:
            user_citers_query = user_citers_query.lte("total_citations", max_citations)
        
        # Get all user_citers that match the user_citers filters
        user_citers_response = user_citers_query.execute()
        
        if hasattr(user_citers_response, 'error') and user_citers_response.error:
            logger.error(f"Error retrieving user citers: {user_citers_response.error}")
            raise HTTPException(status_code=500, detail="Failed to retrieve user citers")
        
        user_citers_data = user_citers_response.data
        
        if not user_citers_data:
            return {
                "citers": [],
                "pagination": {
                    "currentPage": current_page,
                    "totalPages": 0,
                    "totalCount": 0,
                    "pageSize": limit,
                    "hasNext": False,
                    "hasPrev": False
                },
                "sorting": {
                    "sortBy": sort_by,
                    "sortOrder": sort_order
                }
            }
        
        # Get citer IDs from filtered user_citers
        citer_ids = [item["citer_id"] for item in user_citers_data]
        user_citers_dict = {item["citer_id"]: item for item in user_citers_data}
        
        logger.info(f"Processing {len(citer_ids)} citer IDs for user {user_id}")
        
        # Step 2: Process citers in batches to avoid URI length limits
        BATCH_SIZE = 50  # Reduced batch size to avoid URI length issues
        combined_citers = []
        
        for i in range(0, len(citer_ids), BATCH_SIZE):
            batch_ids = citer_ids[i:i+BATCH_SIZE]
            
            try:
                # Build query for this batch of citers
                citers_query = supabase.table("citers").select("*").in_("id", batch_ids)
                
                # Apply filters to citers table
                if min_papers is not None:
                    citers_query = citers_query.gte("paper_count", min_papers)
                
                if max_papers is not None:
                    citers_query = citers_query.lte("paper_count", max_papers)
                
                # Apply search filters to citers table
                if search and search_field in ['citer_name', 'location', 'affiliations']:
                    citers_query = citers_query.ilike(search_field, f"%{search}%")
                
                if location and search_field != 'location':  # Avoid duplicate location filter
                    citers_query = citers_query.ilike("location", f"%{location}%")
                
                # Apply sorting for citer table fields at database level
                if sort_by in ['citer_name', 'paper_count']:
                    ascending = sort_order == 'asc'
                    citers_query = citers_query.order(sort_by, desc=not ascending)
                
                # Get filtered citers for this batch
                citers_response = citers_query.execute()
                
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
                            formatted_citer = {
                                "citer_id": str(citer_id),
                                "semantic_scholar_id": str(citer.get("semantic_scholar_id", "")),
                                "total_citations": int(user_citer.get("total_citations", 0)),
                                "citer_name": str(citer.get("citer_name", "")),
                                "paper_count": int(citer.get("paper_count", 0)),
                                "location": str(citer.get("location", "")),
                                "affiliations": str(citer.get("affiliations", "")),
                                "selected": user_citer.get("selected", False),
                                "cited_papers_count": int(user_citer.get("cited_papers_count", 0)),
                                "citing_papers_count": int(user_citer.get("citing_papers_count", 0)),
                                "independent": user_citer.get("independent", True)
                            }
                            combined_citers.append(formatted_citer)
                        except (ValueError, TypeError) as e:
                            logger.warning(f"Skipping citer {citer_id} due to data conversion error: {str(e)}")
                            continue
                            
            except Exception as e:
                logger.error(f"Error processing batch {i//BATCH_SIZE}: {str(e)}")
                continue  # Skip this batch but continue with others
        
        # Step 3: Apply sorting for user_citers fields (in-memory sorting)
        if sort_by in ['total_citations', 'cited_papers_count', 'citing_papers_count', 'independent']:
            reverse = sort_order == 'desc'
            if sort_by == 'total_citations':
                combined_citers.sort(key=lambda x: x['total_citations'], reverse=reverse)
            elif sort_by == 'cited_papers_count':
                combined_citers.sort(key=lambda x: x['cited_papers_count'], reverse=reverse)
            elif sort_by == 'citing_papers_count':
                combined_citers.sort(key=lambda x: x['citing_papers_count'], reverse=reverse)
            elif sort_by == 'independent':
                combined_citers.sort(key=lambda x: x['independent'], reverse=reverse)
        
        # Step 4: Apply pagination to the final combined results
        total_count = len(combined_citers)
        end = start + limit
        paginated_citers = combined_citers[start:end]
        
        # Calculate pagination info
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0
        has_next = end < total_count
        has_prev = start > 0
        
        # Build filters object for response
        applied_filters = {}
        if search:
            applied_filters["search"] = search
            applied_filters["searchField"] = search_field
        if independent is not None:
            applied_filters["independent"] = independent
        if min_citations is not None:
            applied_filters["minCitations"] = min_citations
        if max_citations is not None:
            applied_filters["maxCitations"] = max_citations
        if min_papers is not None:
            applied_filters["minPapers"] = min_papers
        if max_papers is not None:
            applied_filters["maxPapers"] = max_papers
        if location:
            applied_filters["location"] = location
        
        response = {
            "citers": paginated_citers,
            "pagination": {
                "currentPage": current_page,
                "totalPages": total_pages,
                "totalCount": total_count,
                "pageSize": limit,
                "hasNext": has_next,
                "hasPrev": has_prev
            },
            "sorting": {
                "sortBy": sort_by,
                "sortOrder": sort_order
            }
        }
        
        if applied_filters:
            response["filters"] = applied_filters
        
        return response
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Exception retrieving user citers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving user citers: {str(e)}") 