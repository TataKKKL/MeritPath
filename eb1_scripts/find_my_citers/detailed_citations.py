import argparse
from collections import defaultdict, Counter
import csv
import json
import matplotlib.pyplot as plt
from requests import Session
import s2
import time
from requests.exceptions import HTTPError, RequestException

s2_api_key: str | None = None
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


def get_author_details(author_id: str, target_author_id) -> dict:
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


def export_citation_data(sorted_citation_data, author_name):
    """Export detailed citation data to a CSV file named after the author."""
    filename = f"{author_name}_detailed_citation_data.csv"
    try:
        # Sort the data first by count (descending), then by paper_count (descending)
        sorted_citation_data.sort(key=lambda x: (-x[2], -x[4]))

        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                "Rank", "Citing Author", "Author ID", "Total Citations", "Author Paper Count",
                "Cited Papers and Citing Papers"
            ])
            for rank, (author, author_id, count, papers, paper_count) in enumerate(sorted_citation_data, start=1):
                papers_json = json.dumps(papers)
                writer.writerow([
                    rank, author, author_id, count, paper_count, papers_json,
                ])
        print(f"Detailed citation data exported to {filename}")
    except Exception as e:
        print(f"Error exporting citation data: {e}")
        filename = None
    return filename


def plot_citation_trends(citation_years, author_name):
    """Create and save a time-series plot of citation trends over time."""
    try:
        year_counts = Counter(citation_years)
        years = sorted(year_counts.keys())
        counts = [year_counts[year] for year in years]

        plt.figure(figsize=(10, 6))
        plt.plot(years, counts, marker="o")
        plt.title(f"Citation Trends Over Time for {author_name}")
        plt.xlabel("Year")
        plt.ylabel("Number of Citations")
        plt.tight_layout()
        plot_filename = f"{author_name}_citation_trends.png"
        plt.savefig(plot_filename)
        plt.close()
        print(f"Citation trend plot saved as {plot_filename}")
    except Exception as e:
        print(f"Error creating citation trend plot: {e}")
        plot_filename = None
    return plot_filename


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find authors who have cited your work the most using PyS2"
    )
    parser.add_argument(
        "--author_id",
        help=(
            "The author ID to search for. "
            "If not provided, the script will prompt for input."
        ),
        default=None,
    )
    parser.add_argument(
        "--s2_api_key",
        type=str,
        default=None,
        help="An API key for semantic scholar if you have one.",
    )

    args = parser.parse_args()
    s2_api_key = args.s2_api_key
    session = Session()
    if s2_api_key:
        session.headers.update({"x-api-key": s2_api_key})

    if args.author_id is None:
        author_id = input("Enter the author ID: ")
    else:
        author_id = args.author_id

    try:
        author_name = get_author_name(author_id)
        sorted_citation_data, citation_years = find_my_citers(author_id)
        csv_filename = export_citation_data(sorted_citation_data, author_name)
        plot_filename = plot_citation_trends(citation_years, author_name)

        print("Analysis completed successfully.")
        if csv_filename:
            print(f"CSV file: {csv_filename}")
        if plot_filename:
            print(f"Plot file: {plot_filename}")
    except Exception as e:
        print(f"An error occurred during the analysis: {e}")
        print("The program will now exit.")