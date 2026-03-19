import warnings
from typing import List, Optional

from doctorate_reader.schemas import Paper


def filter_and_rank_papers(
    papers: List[Paper],
    max_results: int = 20,
    min_year: Optional[int] = None,
    only_open_access: bool = False,
    user_vector: Optional[List[float]] = None,
) -> List[Paper]:
    """Filtra y ordena papers por criterios simples.

    - Filtra por año mínimo si se indica.
    - Filtra por open access si se solicita.
    - Si user_vector se provee, ordena por similitud semántica (desc) y citas (desc).
    - De lo contrario, ordena por citas (desc) y año (desc).
    """

    filtered: List[Paper] = []
    for p in papers:
        if min_year is not None:
            if p.year is None or p.year < min_year:
                continue
        if only_open_access and not p.open_access:
            continue
        filtered.append(p)

    if user_vector is not None:
        from doctorate_reader.skills.embeddings import embed_paper, score_paper

        def _semantic_key(p: Paper):
            try:
                vec = embed_paper(p.title, p.abstract)
                sim = score_paper(vec, user_vector)
            except Exception as exc:
                warnings.warn(
                    f"Embedding failed for paper '{p.title[:60]}': {exc}. "
                    "Falling back to similarity=0.0 for this paper."
                )
                sim = 0.0
            return (sim, p.citations or 0)

        filtered.sort(key=_semantic_key, reverse=True)
    else:
        filtered.sort(
            key=lambda p: (p.citations or 0, p.year or 0),
            reverse=True,
        )

    return filtered[:max_results]


