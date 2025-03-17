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

def get_author_details_basic(author_id: str) -> str:
    """Fetch the name of the author given the author ID."""
    author_details = api_call_with_retry(s2.api.get_author, authorId=author_id, session=session)
    return author_details

def get_author_name(author_id: str) -> str:
    """Fetch the name of the author given the author ID."""
    author_details = api_call_with_retry(s2.api.get_author, authorId=author_id, session=session)
    return author_details.name.replace(" ", "_") if author_details else "Unknown_Author"


def get_author_papers(author_id: str) -> list[dict]:
    """Fetch papers for a given author ID from Semantic Scholar using PyS2."""
    author_papers = api_call_with_retry(s2.api.get_author, authorId=author_id, session=session)
    if author_papers:
        return [{"title": paper.title, "paperId": paper.paperId} for paper in author_papers.papers]
    return []


def get_citations(paper_id: str) -> list[dict]:
    """Fetch citations for a given paper ID from Semantic Scholar using PyS2."""
    paper_details = api_call_with_retry(s2.api.get_paper, paperId=paper_id, session=session)
    if paper_details:
        return [
            {"title": citation.title, "paperId": citation.paperId, "year": citation.year}
            for citation in paper_details.citations
        ]
    return []


def get_paper_authors(paper_id: str) -> list[dict]:
    """Fetch authors for a given paper ID from Semantic Scholar using PyS2."""
    paper_details = api_call_with_retry(s2.api.get_paper, paperId=paper_id, session=session)
    if paper_details:
        return [
            {"name": author.name, "authorId": author.authorId}
            for author in paper_details.authors
        ]
    return []


def is_coauthor(target_author_id: str, papers: list[dict]) -> bool:
    for paper in papers:
        paper_authors = get_paper_authors(paper["paperId"])
        if any(author['authorId'] == target_author_id for author in paper_authors):
            return True
    return False


def get_author_details(author_id: str, target_author_id: str = None) -> dict:
    """Fetch author details including paper count and citation count."""
    papers = get_author_papers(author_id)
    return {"paper_count": len(papers)}


def find_my_citers(author_id: str) -> tuple[list[tuple[str, str, int, dict, int]], list[int]]:
    your_papers = get_author_papers(author_id)
    citation_details = defaultdict(lambda: {"authorId": "", "papers": defaultdict(list)})
    citation_years = []
    coauthors = set()
    total_papers = len(your_papers)
    processed_papers = 0

    for paper in your_papers:
        try:
            citations = get_citations(paper["paperId"])
            print(f"Processing paper {paper['title']}")
            paper_authors = get_paper_authors(paper["paperId"])
            coauthors.update(author["name"] for author in paper_authors if author["authorId"] != author_id)

            for citation in citations:
                print(f"Processing citation {citation['title']}")
                if "paperId" in citation:
                    authors = get_paper_authors(citation["paperId"])
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
            author_details = get_author_details(citing_author_id, author_id)
            sorted_citation_data.append((
                author,
                citing_author_id,
                total_citations,
                dict(papers),
                author_details["paper_count"],
            ))
        except Exception as e:
            print(f"Error processing author {author}: {e}")
            continue

    sorted_citation_data.sort(key=lambda item: item[2], reverse=True)
    return sorted_citation_data, citation_years


if __name__ == "__main__":
    session = Session()
    author_id = "2280283715"
    author_details = get_author_details_basic(author_id)
    # Print all attribute values of the author_details object
    print(f"Author Name: {author_details.name}")
    print(f"Author ID: {author_details.authorId}")
    print(f"Influential Citation Count: {author_details.influentialCitationCount}")
    print(f"Aliases: {author_details.aliases}")
    print(f"URL: {author_details.url}")

    # Print information about papers
    print(f"\nTotal Papers: {len(author_details.papers)}")
    print("\nPapers:")
    for i, paper in enumerate(author_details.papers, 1):
        print(f"\n{i}. Title: {paper.title}")
        print(f"   Year: {paper.year}")
        print(f"   Paper ID: {paper.paperId}")
        print(f"   URL: {paper.url}")
    
    sorted_citation_data, citation_years = find_my_citers(author_id)
    print(f"Sorted Citation Data: {sorted_citation_data}")
    print(f"Citation Years: {citation_years}")

