import logging
from requests import Session
import s2
from collections import defaultdict
import time
from requests.exceptions import HTTPError, RequestException
from app.lib.supabase import supabase
from app.api.routes.find_citer import update_citation_tables

logger = logging.getLogger(__name__)

# Constants
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

class FindCiterService:
    def __init__(self):
        self.supabase = supabase
        self.update_citation_tables = update_citation_tables
    
    def api_call_with_retry(self, func, *args, **kwargs):
        """Wrapper function to retry API calls with exponential backoff."""
        for attempt in range(MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except (HTTPError, RequestException) as e:
                if attempt == MAX_RETRIES - 1:
                    logger.error(f"Error after {MAX_RETRIES} attempts: {e}")
                    return None
                wait_time = RETRY_DELAY * (2 ** attempt)
                logger.info(f"API Error: {e}. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
    
    def get_author_details(self, author_id, target_author_id, session):
        """Fetch author details including paper count."""
        papers = self.get_author_papers(author_id, session)
        return {"paper_count": len(papers)}
    
    def get_author_papers(self, author_id, session):
        """Fetch papers for a given author ID from Semantic Scholar using PyS2."""
        author_papers = self.api_call_with_retry(s2.api.get_author, authorId=author_id, session=session)
        if author_papers:
            return [{"title": paper.title, "paperId": paper.paperId} for paper in author_papers.papers]
        return []
    
    def get_citations(self, paper_id, session):
        """Fetch citations for a given paper ID from Semantic Scholar using PyS2."""
        paper_details = self.api_call_with_retry(s2.api.get_paper, paperId=paper_id, session=session)
        if paper_details:
            return [
                {"title": citation.title, "paperId": citation.paperId, "year": citation.year}
                for citation in paper_details.citations
            ]
        return []
    
    def get_paper_authors(self, paper_id, session):
        """Fetch authors for a given paper ID from Semantic Scholar using PyS2."""
        paper_details = self.api_call_with_retry(s2.api.get_paper, paperId=paper_id, session=session)
        if paper_details:
            return [
                {"name": author.name, "authorId": author.authorId}
                for author in paper_details.authors
            ]
        return []
    
    def find_my_citers(self, semantic_scholar_id):
        """
        Find authors who have cited the given author's papers.
        
        Args:
            semantic_scholar_id: The Semantic Scholar ID of the author
            
        Returns:
            A list of authors who have cited the given author's papers, sorted by citation count
        """
        session = Session()
        your_papers = self.get_author_papers(semantic_scholar_id, session)
        citation_details = defaultdict(lambda: {"authorId": "", "papers": defaultdict(list)})
        citation_years = []
        coauthors = set()
        total_papers = len(your_papers)
        processed_papers = 0

        logger.info(f"Processing {total_papers} papers for author {semantic_scholar_id}")

        for paper in your_papers:
            try:
                citations = self.get_citations(paper["paperId"], session)
                logger.info(f"Processing paper: {paper['title']} - Found {len(citations)} citations")
                paper_authors = self.get_paper_authors(paper["paperId"], session)
                coauthors.update(author["name"] for author in paper_authors if author["authorId"] != semantic_scholar_id)

                for citation in citations:
                    logger.info(f"Processing citation {citation['title']}")
                    if "paperId" in citation:
                        authors = self.get_paper_authors(citation["paperId"], session)
                        for author in authors:
                            author_name = author.get("name")
                            author_id = author.get("authorId")
                            if author_name and author_id:
                                citation_details[author_name]["authorId"] = author_id
                                citation_details[author_name]["papers"][paper["title"]].append(citation["title"])
                        if citation.get("year"):
                            citation_years.append(citation["year"])

                processed_papers += 1
                logger.info(f"Processed paper {processed_papers} of {total_papers}")
            except Exception as e:
                logger.error(f"Error processing paper {paper['title']}: {e}")
                continue

        sorted_citation_data = []
        total_authors = len(citation_details)

        for index, (author, data) in enumerate(citation_details.items(), 1):
            try:
                logger.info(f"Processing author {author} ({index}/{total_authors})")
                citing_author_id = data["authorId"]
                papers = data["papers"]
                total_citations = sum(len(citing_papers) for citing_papers in papers.values())
                author_details = self.get_author_details(citing_author_id, semantic_scholar_id, session)
                sorted_citation_data.append({
                    "author_name": author,
                    "semantic_scholar_id": citing_author_id,
                    "total_citations": total_citations,
                    "papers": dict(papers),
                    "paper_count": author_details["paper_count"],
                })
            except Exception as e:
                logger.error(f"Error processing author {author}: {e}")
                continue

        sorted_citation_data.sort(key=lambda item: item["total_citations"], reverse=True)
        return sorted_citation_data, citation_years
    
    async def update_citation_tables(self, user_id, sorted_citation_data):
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
                citer_response = self.supabase.table("citers").select("id").eq("semantic_scholar_id", citer_semantic_scholar_id).execute()
                
                citer_id = None
                # If citer exists, update the record
                if citer_response.data and len(citer_response.data) > 0:
                    citer_id = citer_response.data[0].get("id")
                    self.supabase.table("citers").update({
                        "citer_name": citer_name,
                        "paper_count": paper_count,
                        "updated_at": "now()"
                    }).eq("id", citer_id).execute()
                # If citer doesn't exist, insert a new record
                else:
                    citer_insert_response = self.supabase.table("citers").insert({
                        "semantic_scholar_id": citer_semantic_scholar_id,
                        "citer_name": citer_name,
                        "paper_count": paper_count
                    }).execute()
                    if citer_insert_response.data and len(citer_insert_response.data) > 0:
                        citer_id = citer_insert_response.data[0].get("id")
                
                # If we have a valid citer_id, update the user_citers table
                if citer_id:
                    # Check if this user-citer relationship already exists
                    user_citer_response = self.supabase.table("user_citers").select("id").eq("user_id", user_id).eq("citer_id", citer_id).execute()
                    
                    # If relationship exists, update it
                    if user_citer_response.data and len(user_citer_response.data) > 0:
                        user_citer_id = user_citer_response.data[0].get("id")
                        self.supabase.table("user_citers").update({
                            "papers": papers,
                            "total_citations": total_citations,
                            "updated_at": "now()"
                        }).eq("id", user_citer_id).execute()
                    # If relationship doesn't exist, insert it
                    else:
                        self.supabase.table("user_citers").insert({
                            "user_id": user_id,
                            "citer_id": citer_id,
                            "papers": papers,
                            "total_citations": total_citations
                        }).execute()
            
            return True
        except Exception as e:
            logger.error(f"Error updating citation tables: {e}")
            return False
    
    async def process_citation_job(self, user_id):
        """
        Process a citation job for a user.
        
        Args:
            user_id: The user ID in the database
            
        Returns:
            A dictionary with the job result
        """
        try:
            # Get the semantic_scholar_id from the database
            response = self.supabase.table("users").select("semantic_scholar_id").eq("id", user_id).execute()
            
            if not response.data or len(response.data) == 0:
                return {
                    "status": "failed",
                    "error": f"User with ID {user_id} not found"
                }
            
            semantic_scholar_id = response.data[0].get("semantic_scholar_id")
            
            if not semantic_scholar_id:
                return {
                    "status": "failed",
                    "error": f"User with ID {user_id} does not have a Semantic Scholar ID"
                }
            
            # Find citers
            sorted_citation_data, citation_years = self.find_my_citers(semantic_scholar_id)
            
            # Update citation tables
            update_success = await self.update_citation_tables(user_id, sorted_citation_data)
            
            return {
                "status": "success",
                "user_id": user_id,
                "semantic_scholar_id": semantic_scholar_id,
                "database_updated": update_success,
                "citation_count": len(sorted_citation_data)
            }
        except Exception as e:
            logger.error(f"Error processing citation job: {e}")
            
            # No longer updating user status directly
            
            return {
                "status": "failed",
                "error": str(e)
            } 