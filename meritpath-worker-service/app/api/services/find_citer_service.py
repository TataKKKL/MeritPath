import logging
from requests import Session
import s2
import time
from requests.exceptions import HTTPError, RequestException
from app.lib.supabase import supabase
from fastapi import APIRouter, HTTPException
import asyncio

logger = logging.getLogger(__name__)

# Constants
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# Create a router for API endpoints
router = APIRouter()

class FindCiterService:
    def __init__(self):
        self.supabase = supabase
    
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
    
    def get_author_papers(self, author_id, session):
        """Fetch papers for a given author ID from Semantic Scholar using PyS2."""
        author_papers = self.api_call_with_retry(s2.api.get_author, authorId=author_id, session=session)
        if author_papers:
            return [{"title": paper.title, "paperId": paper.paperId, "year": paper.year} for paper in author_papers.papers]
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
    
    def _get_or_create_paper(self, paper_data):
        """
        Get a paper by Semantic Scholar ID or create it if it doesn't exist.
        Returns the paper ID.
        """
        paper_id = paper_data.get("paperId")
        title = paper_data.get("title")
        year = paper_data.get("year")
        
        if not paper_id or not title:
            return None
            
        # Check if paper already exists
        paper_response = self.supabase.table("papers").select("id").eq("semantic_scholar_id", paper_id).execute()
        
        if paper_response.data and len(paper_response.data) > 0:
            # Paper exists, return its ID
            return paper_response.data[0].get("id")
        else:
            # Create new paper record
            insert_response = self.supabase.table("papers").insert({
                "semantic_scholar_id": paper_id,
                "title": title,
                "year": year
            }).execute()
            
            if insert_response.data and len(insert_response.data) > 0:
                return insert_response.data[0].get("id")
            
        return None
    
    def _create_citation(self, cited_paper_id, citing_paper_id):
        """
        Create a citation relationship between two papers.
        Returns the citation ID.
        """
        if not cited_paper_id or not citing_paper_id:
            return None
            
        # Check if citation already exists
        citation_response = self.supabase.table("citations").select("id").eq("cited_paper_id", cited_paper_id).eq("citing_paper_id", citing_paper_id).execute()
        
        if citation_response.data and len(citation_response.data) > 0:
            # Citation exists, return its ID
            return citation_response.data[0].get("id")
        else:
            # Create new citation
            insert_response = self.supabase.table("citations").insert({
                "cited_paper_id": cited_paper_id,
                "citing_paper_id": citing_paper_id
            }).execute()
            
            if insert_response.data and len(insert_response.data) > 0:
                return insert_response.data[0].get("id")
                
        return None
    
    def _get_or_create_citer(self, author_data, paper_count=0):
        """
        Get a citer by Semantic Scholar ID or create it if it doesn't exist.
        Returns the citer ID.
        """
        semantic_scholar_id = author_data.get("authorId")
        name = author_data.get("name")
        
        if not semantic_scholar_id or not name:
            return None
            
        # Check if citer already exists
        citer_response = self.supabase.table("citers").select("id").eq("semantic_scholar_id", semantic_scholar_id).execute()
        
        if citer_response.data and len(citer_response.data) > 0:
            # Citer exists, update and return ID
            citer_id = citer_response.data[0].get("id")
            
            # Update with only the columns that exist in the actual schema
            self.supabase.table("citers").update({
                "citer_name": name,
                "paper_count": paper_count
            }).eq("id", citer_id).execute()
            
            return citer_id
        else:
            # Create new citer with only the columns that exist in the actual schema
            insert_data = {
                "semantic_scholar_id": semantic_scholar_id,
                "citer_name": name,
                "paper_count": paper_count
            }
            
            insert_response = self.supabase.table("citers").insert(insert_data).execute()
            
            if insert_response.data and len(insert_response.data) > 0:
                return insert_response.data[0].get("id")
                    
        return None
    
    def _link_user_paper(self, user_id, paper_id):
        """Create a link between a user and a paper they authored."""
        if not user_id or not paper_id:
            return False
            
        # Check if link already exists
        link_response = self.supabase.table("user_papers").select("id").eq("user_id", user_id).eq("paper_id", paper_id).execute()
        
        if not link_response.data or len(link_response.data) == 0:
            # Create new link
            self.supabase.table("user_papers").insert({
                "user_id": user_id,
                "paper_id": paper_id
            }).execute()
            
        return True
    
    def _link_citer_citation(self, citer_id, citation_id):
        """Create a link between a citer and a citation they made."""
        if not citer_id or not citation_id:
            return False
            
        # Check if link already exists
        link_response = self.supabase.table("citer_citations").select("id").eq("citer_id", citer_id).eq("citation_id", citation_id).execute()
        
        if not link_response.data or len(link_response.data) == 0:
            # Create new link
            self.supabase.table("citer_citations").insert({
                "citer_id": citer_id,
                "citation_id": citation_id
            }).execute()
            
        return True
    
    def _update_user_citer_papers(self, user_id, citer_id, cited_paper_title, citing_paper_title):
        """
        Update the user_citers table with a new citation.
        Does not store citation data in memory.
        """
        try:
            # Check if relationship exists
            user_citer_response = self.supabase.table("user_citers").select("id, papers, total_citations").eq("user_id", user_id).eq("citer_id", citer_id).execute()
            
            if user_citer_response.data and len(user_citer_response.data) > 0:
                # Update existing relationship
                user_citer_id = user_citer_response.data[0].get("id")
                existing_papers = user_citer_response.data[0].get("papers", {})
                total_citations = user_citer_response.data[0].get("total_citations", 0)
                
                # Convert to dict if it's not already
                if not isinstance(existing_papers, dict):
                    existing_papers = {}
                
                # Update papers dict
                if cited_paper_title not in existing_papers:
                    existing_papers[cited_paper_title] = []
                
                # Add citing paper if not already present
                citation_added = False
                if citing_paper_title not in existing_papers[cited_paper_title]:
                    existing_papers[cited_paper_title].append(citing_paper_title)
                    total_citations += 1
                    citation_added = True
                
                # Only update if a new citation was added
                if citation_added:
                    # Calculate cited_papers_count and citing_papers_count
                    cited_papers_count = len(existing_papers.keys())
                    
                    # Count unique citing papers
                    unique_citing_papers = set()
                    for citing_papers_list in existing_papers.values():
                        for paper in citing_papers_list:
                            unique_citing_papers.add(paper)
                    
                    citing_papers_count = len(unique_citing_papers)
                    
                    self.supabase.table("user_citers").update({
                        "papers": existing_papers,
                        "total_citations": total_citations,
                        "cited_papers_count": cited_papers_count,
                        "citing_papers_count": citing_papers_count,
                        "updated_at": "now()"
                    }).eq("id", user_citer_id).execute()
            else:
                # Create new relationship
                papers = {cited_paper_title: [citing_paper_title]}
                self.supabase.table("user_citers").insert({
                    "user_id": user_id,
                    "citer_id": citer_id,
                    "papers": papers,
                    "total_citations": 1,
                    "cited_papers_count": 1,
                    "citing_papers_count": 1,
                    "location": None,
                    "affiliations": None
                }).execute()
            
            return True
        except Exception as e:
            logger.error(f"Error updating user_citer relationship: {e}")
            return False
    
    def update_citation_counts(self, user_id):
        """
        Update the cited_papers_count and citing_papers_count columns for all user_citers entries.
        Using individual updates instead of a custom SQL function.
        """
        try:
            # Get all user_citers entries for this user
            user_citers_response = self.supabase.table("user_citers").select("id, papers").eq("user_id", user_id).execute()
            
            if not user_citers_response.data:
                return True
                
            # Update each entry individually
            for entry in user_citers_response.data:
                citer_id = entry.get("id")
                papers = entry.get("papers", {})
                
                if not papers:
                    continue
                    
                # Count cited papers (keys in the papers object)
                cited_papers_count = len(papers.keys())
                
                # Count unique citing papers (values in the papers object)
                unique_citing_papers = set()
                for citing_papers_list in papers.values():
                    for paper in citing_papers_list:
                        unique_citing_papers.add(paper)
                
                citing_papers_count = len(unique_citing_papers)
                
                # Update the record
                self.supabase.table("user_citers").update({
                    "cited_papers_count": cited_papers_count,
                    "citing_papers_count": citing_papers_count
                }).eq("id", citer_id).execute()
            
            return True
        except Exception as e:
            logger.error(f"Error updating citation counts: {e}")
            return False
    
    def process_user_papers(self, semantic_scholar_id, user_id):
        """
        Memory-efficient version that directly updates the database without storing large data structures.
        
        Args:
            semantic_scholar_id: The Semantic Scholar ID of the author
            user_id: The database user ID
            
        Returns:
            Success flag
        """
        session = Session()
        
        # Get all the user's papers
        your_papers = self.get_author_papers(semantic_scholar_id, session)
        total_papers = len(your_papers)
        processed_papers = 0
        
        logger.info(f"Processing {total_papers} papers for author {semantic_scholar_id}")
        
        # Process each paper
        for paper in your_papers:
            try:
                # Store the paper in the database
                paper_id = self._get_or_create_paper(paper)
                paper_title = paper.get("title", "Unknown")
                
                if paper_id:
                    # Link the paper to the user
                    self._link_user_paper(user_id, paper_id)
                    
                    # Fetch citations for this paper
                    citations = self.get_citations(paper.get("paperId"), session)
                    logger.info(f"Processing paper: {paper_title} - Found {len(citations)} citations")
                    
                    # Process each citation
                    for citation in citations:
                        if "paperId" in citation:
                            citation_title = citation.get("title", "Unknown")
                            
                            # Store the citing paper
                            citing_paper_id = self._get_or_create_paper(citation)
                            
                            if citing_paper_id and paper_id:
                                # Create citation relationship
                                citation_id = self._create_citation(paper_id, citing_paper_id)
                                
                                # Get authors of the citing paper
                                authors = self.get_paper_authors(citation.get("paperId"), session)
                                
                                # Process each author as a potential citer
                                for author in authors:
                                    author_name = author.get("name")
                                    author_id = author.get("authorId")
                                    
                                    if author_name and author_id:
                                        # Skip if this is the user themselves
                                        if author_id == semantic_scholar_id:
                                            continue
                                            
                                        try:
                                            # Get an estimate of the author's paper count
                                            paper_count_estimate = len(self.get_author_papers(author_id, session))
                                            
                                            # Store or update citer
                                            citer_id = self._get_or_create_citer(author, paper_count_estimate)
                                            
                                            if citer_id and citation_id:
                                                # Link citer to citation
                                                self._link_citer_citation(citer_id, citation_id)
                                                
                                                # Update user_citer relationship directly in the database
                                                self._update_user_citer_papers(user_id, citer_id, paper_title, citation_title)
                                        except Exception as e:
                                            logger.error(f"Error processing citer {author_name}: {e}")
                                            continue
                
                processed_papers += 1
                logger.info(f"Processed paper {processed_papers} of {total_papers}")
            except Exception as e:
                logger.error(f"Error processing paper {paper.get('title', 'unknown')}: {e}")
                continue
        
        # Update the user's paper count
        try:
            self.supabase.table("users").update({
                "author_paper_count": total_papers
            }).eq("id", user_id).execute()
        except Exception as e:
            logger.error(f"Error updating user paper count: {e}")
        
        # Update the citation counts in user_citers table
        self.update_citation_counts(user_id)
        
        return True
    
    async def process_citation_job(self, user_id):
        """
        Process a citation job for a user.
        Memory-efficient version that updates the database directly.
        
        Args:
            user_id: The user ID in the database
            
        Returns:
            A dictionary with the job result
        """
        try:
            # Run the synchronous processing in a thread pool executor to avoid blocking
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                None,  # Use the default executor
                self._process_citation_job_sync,  # Pass the method
                user_id  # Pass the argument
            )
            return result
        except Exception as e:
            logger.error(f"Error in async wrapper for process_citation_job: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

    def _process_citation_job_sync(self, user_id):
        """Internal synchronous implementation of the citation job processing"""
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
            
            # Process papers and update database directly
            processing_success = self.process_user_papers(semantic_scholar_id, user_id)
            
            # Get citation count for reporting
            citation_count_response = self.supabase.table("user_citers").select("total_citations").eq("user_id", user_id).execute()
                
            citation_count = 0
            if citation_count_response.data:
                for row in citation_count_response.data:
                    citation_count += row.get("total_citations", 0)
            
            return {
                "status": "success",
                "user_id": user_id,
                "semantic_scholar_id": semantic_scholar_id,
                "database_updated": processing_success,
                "citation_count": citation_count
            }
        except Exception as e:
            logger.error(f"Error processing citation job: {e}")
            
            return {
                "status": "failed",
                "error": str(e)
            }

