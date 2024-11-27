# Find My Citers

by [Graham Neubig](http://www.phontron.com), modified by TataKKKL

This is a script that helps find people who have cited your papers, which can be useful to find recommendation letter writers for job or visa applications.

It is based on the [Semantic Scholar API](https://api.semanticscholar.org/api-docs/).

## Usage

Install requirements, mostly `pys2`,
a python library for the [Semantic Scholar (S2) API](api.semanticscholar.org/).

```bash
python3.11 -m venv venv
. venv/bin/activate
pip3.11 install -r requirements.txt
```

Find your semantic scholar profile, and copy-paste the number from the URL. For example, if the URL is `https://www.semanticscholar.org/author/Graham-Neubig/1700325` then the number is `1700325`.

```bash
python3.11 detailed_citations.py --author_id AUTHOR_ID
```
Note I modified Graham Neubig's original code to generate a CSV file for conducting further data manipulation.

The CSV file contains the following columns:
- Rank
- Citing Author
- Author ID
- Total Citations
- Author Paper Count
- Cited Papers and Citing Papers

I also added error handling to api call retry since we need to pull citers information like number of papers. 