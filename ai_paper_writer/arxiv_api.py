import requests

def get_related_papers(topic, max_results=3):
    query = f"search_query=all:{topic}&start=0&max_results={max_results}"
    url = f"http://export.arxiv.org/api/query?{query}"

    response = requests.get(url)
    # Parse XML response manually or use feedparser
    import feedparser
    feed = feedparser.parse(response.text)

    papers = []
    for entry in feed.entries:
        title = entry.title
        summary = entry.summary
        # Prepare a basic BibTeX entry
        authors = ", ".join(author.name for author in entry.authors)
        year = entry.published[:4]
        bibtex = f"@article{{{authors.split(',')[0].lower()}{year}, title={{ {title} }}, author={{ {authors} }}, year={{ {year} }}}}"
        papers.append({"title": title, "summary": summary, "bibtex": bibtex})

    bib_entries = [p["bibtex"] for p in papers]
    return papers, bib_entries
