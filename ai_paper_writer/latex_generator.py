def create_latex_file(sections, bib_entries):
    # Join bib entries into the body of thebibliography
    bib_items = "\n".join(f"\\bibitem{{}} {entry}" for entry in bib_entries)

    # Raw string to preserve backslashes
    latex_template = r"""
\documentclass[conference]{IEEEtran}
\usepackage[utf8]{inputenc}
\usepackage{cite}

\title{Generated Research Paper}
\author{AI Researcher}

\begin{document}

\maketitle

\begin{abstract}
""" + sections.get('abstract', '') + r"""
\end{abstract}

\section{Introduction}
""" + sections.get('introduction', '') + r"""

\section{Related Work}
""" + sections.get('related_work', '') + r"""

\section{Methodology}
""" + sections.get('methodology', '') + r"""

\section{Conclusion}
""" + sections.get('conclusion', '') + r"""

\begin{thebibliography}{99}
""" + bib_items + r"""
\end{thebibliography}

\end{document}
"""
    return latex_template
