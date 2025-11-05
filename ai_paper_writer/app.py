import streamlit as st
import io
import zipfile
import pypandoc
import requests

from arxiv_api import get_related_papers            # Fetches related papers from arXiv
from gpt_generator import generate_sections         # Uses Gemini to generate paper sections
from latex_generator import create_latex_file       # Generates LaTeX code from sections
from docx_generator import create_docx_bytes        # Generates Word DOCX from sections

# ------------------ Helper Function: Markdown Generator ------------------ #
def create_markdown(topic, sections, bib_entries):
    """Generates Markdown content from paper sections and references."""
    md = f"# {topic}\n\n"
    for sec, txt in sections.items():
        md += f"## {sec.capitalize()}\n{txt}\n\n"
    md += "## References\n" + "\n".join(bib_entries)
    return md

# ------------------ Page Configuration ------------------ #
st.set_page_config(page_title="AI-Powered Research Paper Writer", layout="wide")

# ------------------ Custom CSS Styling ------------------ #
st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-family: 'Segoe UI', sans-serif;
            background-color: #f9fafc;
            color: #333;
        }
        h1 {
            color: #264653;
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }
        .stTextInput > div > div > input {
            padding: 0.75rem;
            font-size: 1.1rem;
            border: 2px solid #ccc;
            border-radius: 8px;
            background-color: #fff;
        }
        .stButton > button {
            background-color: #2a9d8f;
            color: white;
            padding: 0.75rem 1.5rem;
            font-size: 1rem;
            border-radius: 8px;
            border: none;
            transition: background-color 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #21867a;
        }
        .stDownloadButton > button {
            background-color: #e9c46a;
            color: #000;
            border: none;
            padding: 0.6rem 1.2rem;
            font-size: 0.95rem;
            border-radius: 6px;
            margin-top: 0.5rem;
            transition: all 0.3s ease;
        }
        .stDownloadButton > button:hover {
            background-color: #d4b157;
        }
        section[data-testid="stSidebar"] {
            background-color: #f0f4f8;
            border-right: 2px solid #ccc;
        }
        .stSidebar .stInfo {
            background-color: #e3f2fd;
            padding: 0.75rem;
            border-radius: 8px;
        }
        .block-container {
            padding: 2rem 3rem;
            min-height: 90vh;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        h2 {
            color: #1d3557;
        }
        /* Fixed bottom footer */
        .footer {
            width: 100%;
            text-align: center;
            padding: 12px 0;
            background-color: #f0f0f0;
            color: #444;
            font-size: 0.9rem;
            border-top: 1px solid #ccc;
            position: fixed;
            bottom: 0;
            left: 0;
            z-index: 999;
        }
    </style>
""", unsafe_allow_html=True)


# ------------------ Sidebar Content ------------------ #
st.sidebar.markdown("<h1>ℹ️ Research Paper AI</h1>", unsafe_allow_html=True)
st.sidebar.info("""
This AI-powered app helps you generate structured research papers 
based on your topic using **ArXiv** and **Gemini (Google LLM)**.

**✨ Key Features:**
- Automatically fetches related papers
- Writes Abstract, Introduction, Related Work, etc.
- Exports to **LaTeX**, **DOCX**, **PDF**, **Markdown**, **ZIP**
""")
st.sidebar.markdown("---")
st.sidebar.markdown("💡 **Tip:** Enter a clear research topic above and click **Generate Paper** for instant results!")

# ------------------ Main Page Content ------------------ #
with st.container():
    st.markdown("<h1 style='text-align:center;'>📝 AI-Powered Research Paper Writer</h1>", unsafe_allow_html=True)
    st.markdown("---")

    # ----------- User Input Section ----------- #
    topic = st.text_input("🔍 Enter your research topic:")
    generate = st.button("🚀 Generate Paper")

    if generate and topic:

        # ----------- Step 1: Fetch Related Papers ----------- #
        with st.spinner("📚 Fetching related papers..."):
            papers, bib_entries = get_related_papers(topic)

        # ----------- Step 2: Generate Paper Sections ----------- #
        with st.spinner("📝 Generating paper sections..."):
            sections, bib_entries = generate_sections(topic, papers)

        # ----------- Step 3: Format Outputs ----------- #
        latex_code = create_latex_file(sections, bib_entries)
        docx_bytes = create_docx_bytes(sections, bib_entries)
        markdown = create_markdown(topic, sections, bib_entries)

        st.success("✅ Paper generated successfully!")
        st.markdown("### 📥 Download Options")

        # ----------- Download Buttons ----------- #
        col1, col2, col3 = st.columns(3)

        # LaTeX and Markdown Downloads
        with col1:
            st.download_button(
                label="📄 LaTeX (.tex)",
                data=latex_code,
                file_name=f"{topic.replace(' ', '_')}.tex",
                mime="text/x-tex"
            )
            st.download_button(
                label="📝 Markdown (.md)",
                data=markdown,
                file_name=f"{topic.replace(' ', '_')}.md",
                mime="text/markdown"
            )

        # DOCX Download
        with col2:
            st.download_button(
                label="🧾 DOCX (.docx)",
                data=docx_bytes,
                file_name=f"{topic.replace(' ', '_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

        # PDF Download using pypandoc (LaTeX to PDF)
        with col3:
            try:
                pdf_bytes = pypandoc.convert_text(latex_code, 'pdf', format='latex')
                st.download_button(
                    label="📕 PDF (.pdf)",
                    data=pdf_bytes,
                    file_name=f"{topic.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
            except Exception:
                st.warning("⚠️ PDF conversion unavailable. Install `pypandoc` and a LaTeX engine.")

        # ----------- ZIP Download (All LaTeX Sections Separately) ----------- #
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            zf.writestr(f"{topic.replace(' ', '_')}.tex", latex_code)
            for sec, txt in sections.items():
                section_content = f"\\section{{{sec.capitalize()}}}\n{txt}\n"
                zf.writestr(f"{sec}.tex", section_content)
        zip_buffer.seek(0)

        st.download_button(
            label="🗜️ ZIP (All LaTeX Files)",
            data=zip_buffer,
            file_name=f"{topic.replace(' ', '_')}_latex.zip",
            mime="application/zip"
        )

# ------------------ Footer ------------------ #
# ------------------ Footer Styling ------------------ #
st.markdown("""
    <style>
        .footer {
            width: 100%;
            text-align: center;
            padding: 12px 0;
            background-color: #f0f0f0;
            color: #444;
            font-size: 0.9rem;
            border-top: 1px solid #ccc;
            position: fixed;
            bottom: 0;
            left: 0;
            z-index: 999;
        }
        .footer a {
            color: #2a9d8f;
            text-decoration: none;
            font-weight: bold;
        }
        .footer a:hover {
            text-decoration: underline;
            color: #21867a;
        }
    </style>

    <div class='footer'>
        🚀 Developed by <strong><a href="https://sarathkio.github.io/Sarath_Profile/" target="_blank">Sarathkumar R</a></strong>
    </div>
""", unsafe_allow_html=True)

