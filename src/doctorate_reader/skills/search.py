from typing import List, Optional

from doctorate_reader.tools.openalex import search_papers
from doctorate_reader.schemas import Paper


def search_papers_skill(
    topic: str,
    num_results: int = 20,
    recent_only: bool = True,
    journals: Optional[List[str]] = None,
) -> List[Paper]:
    """Envuelve la tool de OpenAlex y la adapta a nuestro modelo `Paper`.

    Esta capa será el punto natural para añadir en el futuro lógica de
    almacenamiento (BD / vector store) de los resultados descargados.
    """

    raw_results = search_papers(
        query=topic,
        num_results=num_results,
        recent_only=recent_only,
        journals=journals,
    )

    papers: List[Paper] = []
    for r in raw_results:
        journal_raw = r.get("journal")
        journal_name: Optional[str] = None
        if isinstance(journal_raw, dict):
            journal_name = journal_raw.get("display_name")

        paper = Paper(
            title=r.get("title") or "",
            authors=r.get("authors", []),
            year=r.get("year"),
            abstract=r.get("abstract"),
            journal=journal_name,
            citations=r.get("citations"),
            doi=r.get("doi"),
            open_access=r.get("open_access"),
            link=r.get("link"),
        )
        papers.append(paper)

    return papers


