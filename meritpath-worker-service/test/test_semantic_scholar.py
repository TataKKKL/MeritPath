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

def get_author_details(author_id: str) -> str:
    """Fetch the name of the author given the author ID."""
    author_details = api_call_with_retry(s2.api.get_author, authorId=author_id, session=session)
    return author_details



if __name__ == "__main__":
    session = Session()
    author_id = "2280283715"
    author_details = get_author_details(author_id)
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
    

