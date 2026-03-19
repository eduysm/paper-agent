from doctorate_reader.schemas import Paper
from doctorate_reader.llm import complete


def summarize_paper(
    paper: Paper,
    topic: str,
    audience: str = "investigadores en economía",
    language: str = "es",
    max_words: int = 120,
) -> str:
    """Genera un resumen breve de un paper enfocado a newsletter."""

    authors = ", ".join(paper.authors) if paper.authors else "Autor/es desconocidos"

    prompt = f"""
Eres un asistente que escribe resúmenes breves para una newsletter de investigación.

Tema general de la newsletter: "{topic}".
Audiencia: {audience}.
Idioma: {language}.

A partir del siguiente paper, escribe un resumen de máximo {max_words} palabras, claro y atractivo, que explique:
- De qué trata el paper.
- Por qué puede interesar a investigadores en este tema.

Paper:
Título: {paper.title}
Autores: {authors}
Año: {paper.year}
Journal: {paper.journal}
Abstract: {paper.abstract}
"""

    return complete(prompt, max_tokens=max_words * 3)




