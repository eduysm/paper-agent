from datetime import date
from typing import List, Optional

from doctorate_reader.skills.search import search_papers_skill
from doctorate_reader.skills.filtering import filter_and_rank_papers
from doctorate_reader.skills.summarization import summarize_paper
from doctorate_reader.skills.composition import compose_newsletter_html


def build_newsletter_html(
    topic: str,
    num_results: int = 20,
    top_n: int = 5,
    recent_only: bool = True,
    journals: Optional[List[str]] = None,
    min_year: Optional[int] = None,
    only_open_access: bool = False,
) -> str:
    """Orquesta la generación de la newsletter en HTML.

    1. Busca papers en OpenAlex.
    2. Filtra/ordena según criterios simples.
    3. Genera resúmenes con el LLM.
    4. Compone un HTML sencillo listo para copiar/pegar.
    """

    papers = search_papers_skill(
        topic=topic,
        num_results=num_results,
        recent_only=recent_only,
        journals=journals,
    )

    ranked = filter_and_rank_papers(
        papers,
        max_results=num_results,
        min_year=min_year,
        only_open_access=only_open_access,
    )

    top = ranked[:top_n]
    others = ranked[top_n:]

    summarized_top = [(p, summarize_paper(p, topic, max_words=120)) for p in top]
    summarized_others = [
        (p, summarize_paper(p, topic, max_words=60)) for p in others
    ]

    html = compose_newsletter_html(
        topic=topic,
        today=date.today(),
        summarized_top=summarized_top,
        summarized_others=summarized_others,
    )

    return html


