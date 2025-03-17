from fastapi import APIRouter, HTTPException
from requests import Session
import s2
from collections import defaultdict
import time
from requests.exceptions import HTTPError, RequestException
from app.lib.supabase import supabase

router = APIRouter()

# Constants
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# Helper functions
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

def get_author_details_basic(author_id: str, session: Session) -> str:
    """Fetch the name of the author given the author ID."""
    author_details = api_call_with_retry(s2.api.get_author, authorId=author_id, session=session)
    return author_details

def get_author_papers(author_id: str, session: Session) -> list[dict]:
    """Fetch papers for a given author ID from Semantic Scholar using PyS2."""
    author_papers = api_call_with_retry(s2.api.get_author, authorId=author_id, session=session)
    if author_papers:
        return [{"title": paper.title, "paperId": paper.paperId} for paper in author_papers.papers]
    return []

def get_citations(paper_id: str, session: Session) -> list[dict]:
    """Fetch citations for a given paper ID from Semantic Scholar using PyS2."""
    paper_details = api_call_with_retry(s2.api.get_paper, paperId=paper_id, session=session)
    if paper_details:
        return [
            {"title": citation.title, "paperId": citation.paperId, "year": citation.year}
            for citation in paper_details.citations
        ]
    return []

def get_paper_authors(paper_id: str, session: Session) -> list[dict]:
    """Fetch authors for a given paper ID from Semantic Scholar using PyS2."""
    paper_details = api_call_with_retry(s2.api.get_paper, paperId=paper_id, session=session)
    if paper_details:
        return [
            {"name": author.name, "authorId": author.authorId}
            for author in paper_details.authors
        ]
    return []

def get_author_details(author_id: str, target_author_id: str = None, session: Session = None) -> dict:
    """Fetch author details including paper count and citation count."""
    papers = get_author_papers(author_id, session)
    return {"paper_count": len(papers)}

def find_my_citers(semantic_scholar_id: str, session: Session) -> list[dict]:
    your_papers = get_author_papers(semantic_scholar_id, session)
    citation_details = defaultdict(lambda: {"authorId": "", "papers": defaultdict(list)})
    citation_years = []
    coauthors = set()
    total_papers = len(your_papers)
    processed_papers = 0

    for paper in your_papers:
        try:
            citations = get_citations(paper["paperId"], session)
            print(f"Processing paper {paper['title']}")
            paper_authors = get_paper_authors(paper["paperId"], session)
            coauthors.update(author["name"] for author in paper_authors if author["authorId"] != semantic_scholar_id)

            for citation in citations:
                print(f"Processing citation {citation['title']}")
                if "paperId" in citation:
                    authors = get_paper_authors(citation["paperId"], session)
                    for author in authors:
                        author_name = author.get("name")
                        author_id = author.get("authorId")
                        if author_name and author_id:
                            citation_details[author_name]["authorId"] = author_id
                            citation_details[author_name]["papers"][paper["title"]].append(citation["title"])
                    if citation.get("year"):
                        citation_years.append(citation["year"])

            processed_papers += 1
            print(f"Processed paper {processed_papers} of {total_papers}")
        except Exception as e:
            print(f"Error processing paper {paper['title']}: {e}")
            continue

    sorted_citation_data = []
    total_authors = len(citation_details)

    for index, (author, data) in enumerate(citation_details.items(), 1):
        try:
            print(f"Processing author {author} ({index}/{total_authors})")
            citing_author_id = data["authorId"]
            papers = data["papers"]
            total_citations = sum(len(citing_papers) for citing_papers in papers.values())
            author_details = get_author_details(citing_author_id, semantic_scholar_id, session)
            sorted_citation_data.append({
                "author_name": author,
                "semantic_scholar_id": citing_author_id,
                "total_citations": total_citations,
                "papers": dict(papers),
                "paper_count": author_details["paper_count"],
            })
        except Exception as e:
            print(f"Error processing author {author}: {e}")
            continue

    sorted_citation_data.sort(key=lambda item: item["total_citations"], reverse=True)
    return sorted_citation_data

# @router.post("/by-semantic-scholar-id")
# async def find_citer_by_semantic_scholar_id(semantic_scholar_id: str):
#     """
#     Find authors who have cited the given Semantic Scholar author's papers.
    
#     Args:
#         semantic_scholar_id: The Semantic Scholar ID of the author
        
#     Returns:
#         A list of authors who have cited the given author's papers, sorted by citation count
#     """
#     try:
#         session = Session()
#         sorted_citation_data = find_my_citers(semantic_scholar_id, session)
#         return {"citers": sorted_citation_data}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error finding citers: {str(e)}")

async def update_citation_tables(user_id: str, sorted_citation_data: list):
    """
    Update the citers and user_citers tables with the citation data.
    
    Args:
        user_id: The user ID in the database
        sorted_citation_data: List of citation data for authors who cited the user
    """
    try:
        # Process each citing author
        for citer_data in sorted_citation_data:
            citer_semantic_scholar_id = citer_data.get("semantic_scholar_id")
            citer_name = citer_data.get("author_name")
            total_citations = citer_data.get("total_citations")
            paper_count = citer_data.get("paper_count")
            papers = citer_data.get("papers", {})
            
            # Check if citer already exists in citers table
            citer_response = supabase.table("citers").select("id").eq("semantic_scholar_id", citer_semantic_scholar_id).execute()
            
            citer_id = None
            # If citer exists, update the record
            if citer_response.data and len(citer_response.data) > 0:
                citer_id = citer_response.data[0].get("id")
                supabase.table("citers").update({
                    "citer_name": citer_name,
                    "paper_count": paper_count,
                    "updated_at": "now()"
                }).eq("id", citer_id).execute()
            # If citer doesn't exist, insert a new record
            else:
                citer_insert_response = supabase.table("citers").insert({
                    "semantic_scholar_id": citer_semantic_scholar_id,
                    "citer_name": citer_name,
                    "paper_count": paper_count
                }).execute()
                if citer_insert_response.data and len(citer_insert_response.data) > 0:
                    citer_id = citer_insert_response.data[0].get("id")
            
            # If we have a valid citer_id, update the user_citers table
            if citer_id:
                # Check if this user-citer relationship already exists
                user_citer_response = supabase.table("user_citers").select("id").eq("user_id", user_id).eq("citer_id", citer_id).execute()
                
                # If relationship exists, update it
                if user_citer_response.data and len(user_citer_response.data) > 0:
                    user_citer_id = user_citer_response.data[0].get("id")
                    supabase.table("user_citers").update({
                        "papers": papers,
                        "total_citations": total_citations,
                        "updated_at": "now()"
                    }).eq("id", user_citer_id).execute()
                # If relationship doesn't exist, insert it
                else:
                    supabase.table("user_citers").insert({
                        "user_id": user_id,
                        "citer_id": citer_id,
                        "papers": papers,
                        "total_citations": total_citations
                    }).execute()
        
        return True
    except Exception as e:
        print(f"Error updating citation tables: {e}")
        return False

@router.post("/by-user-id")
async def find_citer_by_user_id(user_id: str):
    """
    Find authors who have cited the given user's papers by looking up their Semantic Scholar ID.
    Also updates the citers and user_citers tables with the citation data.
    
    Args:
        user_id: The user ID in the database
        
    Returns:
        A list of authors who have cited the given user's papers, sorted by citation count
    """
    try:
        # Query Supabase to get the semantic_scholar_id for the user
        response = supabase.table("users").select("semantic_scholar_id").eq("id", user_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
        
        semantic_scholar_id = response.data[0].get("semantic_scholar_id")
        
        if not semantic_scholar_id:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} does not have a Semantic Scholar ID")
        
        # Use the existing function to find citers
        session = Session()
        sorted_citation_data = find_my_citers(semantic_scholar_id, session)
        
        # Update the citers and user_citers tables
        update_success = await update_citation_tables(user_id, sorted_citation_data)
        
        return {
            "user_id": user_id, 
            "semantic_scholar_id": semantic_scholar_id,
            "database_updated": update_success
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding citers: {str(e)}")
