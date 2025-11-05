import os
import re
from dotenv import load_dotenv
from typing import Tuple, List, Dict
import google.generativeai as genai

# Load API key from .env
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def extract_section(section_name: str, text: str) -> str:
    """
    Extract a specific section from the generated content using regex.
    """
    pattern = rf"{section_name}[\s\n]*[:\-]?\s*(.*?)(?=\n\s*(?:[A-Z][a-z]+|[1-9]\.?\s?[A-Z]|References|$))"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if not match:
        print(f"[WARN] Section '{section_name}' not found.")
        return ""
    return match.group(1).strip()


def generate_sections(topic: str, papers: List[Dict]) -> Tuple[Dict[str, str], List[str]]:
    """
    Generate structured research paper sections based on a custom template using Gemini.
    """
    model = genai.GenerativeModel("gemini-2.0-flash-001")

    # Combine paper summaries
    summaries = "\n\n".join(f"- {p['title']}: {p['summary']}" for p in papers)

    # Prompt with detailed structure
    prompt = f"""
You are an expert academic researcher. Write a formal research paper on the topic: "{topic}".

Incorporate relevant ideas from the following related papers:
{summaries}

Follow this structure:

1. **Introduction** – General background and topic overview.
2. **Aim of the Study** – Clearly state the objective.
3. **Problem Statement** – Define the specific problem addressed.
4. **Literature Survey** – Review of related studies with citations like [1], [2].
5. **Case Studies** – Real-life or simulated case examples.
6. **Statistical Analysis** – Include interpretation, data summaries, or assumptions.
7. **Findings and Recommendations** – Key results and expert suggestions.
8. **Conclusion** – Summary and future scope.
9. **Acknowledgement** – Mention institutions, individuals, or tools used.
10. **References** – List the cited papers using IEEE-style BibTeX references.

Use clear headings, academic paragraphs, and IEEE tone. All sections are mandatory.
"""

    try:
        response = model.generate_content(prompt)
        content = response.text
    except Exception as e:
        print(f"[ERROR] Gemini API call failed: {e}")
        return {"error": str(e)}, []

    # Define section names
    section_names = [
        "Introduction",
        "Aim of the Study",
        "Problem Statement",
        "Literature Survey",
        "Case Studies",
        "Statistical Analysis",
        "Findings and Recommendations",
        "Conclusion",
        "Acknowledgement",
        "References"
    ]

    # Extract each section content
    sections = {name: extract_section(name, content) for name in section_names}
    sections["Full Content"] = content  # For export

    # Extract BibTeX entries (for appending to References if needed)
    bibtex_entries = [p.get("bibtex", "") for p in papers if p.get("bibtex")]

    return sections, bibtex_entries
