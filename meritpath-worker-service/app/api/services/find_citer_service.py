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
    
    def _get_or_create_citer(self, citer_data):
        """
        Get a citer by Semantic Scholar ID or create it if it doesn't exist.
        Returns the citer ID.
        """
        semantic_scholar_id = citer_data.get("authorId")
        name = citer_data.get("name")
        paper_count = citer_data.get("paper_count", 0)
        
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
                # No total_citations field in the actual schema
            }).eq("id", citer_id).execute()
            
            return citer_id
        else:
            # Create new citer with only the columns that exist in the actual schema
            insert_data = {
                "semantic_scholar_id": semantic_scholar_id,
                "citer_name": name,
                "paper_count": paper_count
                # No total_citations field in the actual schema
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
    
    def find_my_citers(self, semantic_scholar_id, user_id):
        """
        Find authors who have cited the given author's papers.
        This updated version stores data in the normalized tables as it's processed.
        
        Args:
            semantic_scholar_id: The Semantic Scholar ID of the author
            user_id: The database user ID
            
        Returns:
            A list of authors who have cited the given author's papers, sorted by citation count
        """
        session = Session()
        your_papers = self.get_author_papers(semantic_scholar_id, session)
        
        # Still keep track of citation details for backward compatibility
        citation_details = {}
        citation_years = []
        total_papers = len(your_papers)
        processed_papers = 0
        
        logger.info(f"Processing {total_papers} papers for author {semantic_scholar_id}")
        
        # Process all author's papers and store them in the database
        for paper in your_papers:
            try:
                # Step 2.2: Store the paper in the database
                paper_id = self._get_or_create_paper(paper)
                
                if paper_id:
                    # Link the paper to the user
                    self._link_user_paper(user_id, paper_id)
                    
                    # Fetch citations for this paper
                    citations = self.get_citations(paper["paperId"], session)
                    logger.info(f"Processing paper: {paper['title']} - Found {len(citations)} citations")
                    
                    # Step 2.3: Process each citation
                    for citation in citations:
                        if "paperId" in citation:
                            # Store the citing paper
                            citing_paper_id = self._get_or_create_paper(citation)
                            
                            if citing_paper_id and paper_id:
                                # Create citation relationship
                                citation_id = self._create_citation(paper_id, citing_paper_id)
                                
                                # Get authors of the citing paper
                                authors = self.get_paper_authors(citation["paperId"], session)
                                
                                # Step 2.4: Process each author as a potential citer
                                for author in authors:
                                    author_name = author.get("name")
                                    author_id = author.get("authorId")
                                    
                                    if author_name and author_id:
                                        # Get author details including paper count
                                        author_details = self.get_author_details(author_id, semantic_scholar_id, session)
                                        author["paper_count"] = author_details["paper_count"]
                                        
                                        try:
                                            # Store or update citer
                                            citer_id = self._get_or_create_citer(author)
                                            
                                            if citer_id and citation_id:
                                                # Link citer to citation
                                                self._link_citer_citation(citer_id, citation_id)
                                        except Exception as e:
                                            logger.error(f"Error processing citer {author_name}: {e}")
                                            continue
                                        
                                        # For backward compatibility, also track the citation details
                                        if author_name not in citation_details:
                                            citation_details[author_name] = {
                                                "authorId": author_id,
                                                "papers": {},
                                                "paper_count": author_details["paper_count"]
                                            }
                                        
                                        if paper["title"] not in citation_details[author_name]["papers"]:
                                            citation_details[author_name]["papers"][paper["title"]] = []
                                        
                                        citation_details[author_name]["papers"][paper["title"]].append(citation["title"])
                            
                            if citation.get("year"):
                                citation_years.append(citation["year"])
                
                processed_papers += 1
                logger.info(f"Processed paper {processed_papers} of {total_papers}")
            except Exception as e:
                logger.error(f"Error processing paper {paper.get('title', 'unknown')}: {e}")
                continue
        
        # For backward compatibility, prepare the sorted citation data
        sorted_citation_data = []
        for author, data in citation_details.items():
            papers = data["papers"]
            total_citations = sum(len(citing_papers) for citing_papers in papers.values())
            
            sorted_citation_data.append({
                "author_name": author,
                "semantic_scholar_id": data["authorId"],
                "total_citations": total_citations,
                "papers": dict(papers),
                "paper_count": data["paper_count"],
            })
        
        sorted_citation_data.sort(key=lambda item: item["total_citations"], reverse=True)
        
        # Update the user's paper count. The error shows that 'updated_at' doesn't exist in users table
        try:
            self.supabase.table("users").update({
                "author_paper_count": total_papers
            }).eq("id", user_id).execute()
        except Exception as e:
            logger.error(f"Error updating user paper count: {e}")
        
        return sorted_citation_data, citation_years
    
    async def update_citation_tables(self, user_id, sorted_citation_data):
        """
        Update the user_citers table with the citation data for backward compatibility.
        The main citation data is already stored in the normalized tables during processing.
        
        Args:
            user_id: The user ID in the database
            sorted_citation_data: List of citation data for authors who cited the user
        """
        try:
            # Process in batches to reduce memory usage
            batch_size = 50
            total_citers = len(sorted_citation_data)
            
            for i in range(0, total_citers, batch_size):
                batch = sorted_citation_data[i:i+batch_size]
                
                # Process each citing author in the current batch
                for citer_data in batch:
                    citer_semantic_scholar_id = citer_data.get("semantic_scholar_id")
                    citer_name = citer_data.get("author_name")
                    total_citations = citer_data.get("total_citations")
                    paper_count = citer_data.get("paper_count")
                    papers = citer_data.get("papers", {})
                    
                    # Check if citer already exists in citers table
                    citer_response = self.supabase.table("citers").select("id").eq("semantic_scholar_id", citer_semantic_scholar_id).execute()
                    
                    citer_id = None
                    if citer_response.data and len(citer_response.data) > 0:
                        citer_id = citer_response.data[0].get("id")
                    
                    # If we have a valid citer_id, update the user_citers table for backward compatibility
                    if citer_id:
                        # Check if this user-citer relationship already exists
                        user_citer_response = self.supabase.table("user_citers").select("id").eq("user_id", user_id).eq("citer_id", citer_id).execute()
                        
                        # We now need to convert the papers structure to match what the existing database expects
                        # Based on the error logs, we need to modify this to match the actual schema
                        
                        # If relationship exists, update it
                        if user_citer_response.data and len(user_citer_response.data) > 0:
                            user_citer_id = user_citer_response.data[0].get("id")
                            
                            # Use the format expected by the existing schema
                            update_data = {
                                "total_cites": total_citations
                            }
                            
                            # Create a cited_papers_citing_papers structure if the schema expects it
                            if "cited_papers_citing_papers" in sorted_citation_data[0]:
                                update_data["cited_papers_citing_papers"] = papers
                            else:
                                # From the error logs and your SQL, it appears the schema might actually be paper_title/citing_paper_title
                                # Let's handle both cases by flattening the papers structure if needed
                                flattened_citations = []
                                for cited_paper, citing_papers in papers.items():
                                    for citing_paper in citing_papers:
                                        flattened_citations.append({
                                            "paper_title": cited_paper,
                                            "citing_paper_title": citing_paper
                                        })
                                
                                if flattened_citations:
                                    # If we need to update individual rows, do that instead
                                    for citation in flattened_citations:
                                        self.supabase.table("user_citers").upsert({
                                            "user_id": user_id,
                                            "citer_id": citer_id,
                                            "paper_title": citation["paper_title"],
                                            "citing_paper_title": citation["citing_paper_title"]
                                        }).execute()
                                else:
                                    # Just update the existing record
                                    self.supabase.table("user_citers").update(update_data).eq("id", user_citer_id).execute()
                        # If relationship doesn't exist, insert it based on the schema
                        else:
                            # Check if we need to insert flattened citation records
                            flattened_citations = []
                            for cited_paper, citing_papers in papers.items():
                                for citing_paper in citing_papers:
                                    flattened_citations.append({
                                        "user_id": user_id,
                                        "citer_id": citer_id,
                                        "paper_title": cited_paper,
                                        "citing_paper_title": citing_paper
                                    })
                            
                            if flattened_citations:
                                # Insert individual citation records
                                for citation in flattened_citations:
                                    self.supabase.table("user_citers").insert(citation).execute()
                            else:
                                # Insert a single record with the papers structure
                                self.supabase.table("user_citers").insert({
                                    "user_id": user_id,
                                    "citer_id": citer_id,
                                    "cited_papers_citing_papers": {
                                        "cited_papers": papers
                                    },
                                    "total_cites": total_citations
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
            
            # Find citers and store data in normalized tables
            sorted_citation_data, citation_years = self.find_my_citers(semantic_scholar_id, user_id)
            
            # Update user_citers table for backward compatibility
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
            
            return {
                "status": "failed",
                "error": str(e)
            }