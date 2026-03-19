from smolagents import CodeAgent

from doctorate_reader.schemas import Paper
from readerAI.llm_conect.base import get_model


def summarize_paper(
    paper: Paper,
    topic: str,
    audience: str = "investigadores en economía",
    language: str = "es",
    max_words: int = 120,
) -> str:
    """Genera un resumen breve de un paper enfocado a newsletter.

    Delegamos en el modelo configurado vía `get_model()`.
    """

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

    # Creamos un CodeAgent mínimo sin tools para reutilizar la infraestructura
    # de smolagents y obtener directamente un string como salida.
    model = get_model()
    agent = CodeAgent(tools=[], model=model)
    return agent.run(prompt, max_steps=1)




