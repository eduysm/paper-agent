from typing import List, Optional

from doctorate_reader.schemas import Paper


def filter_and_rank_papers(
    papers: List[Paper],
    max_results: int = 20,
    min_year: Optional[int] = None,
    only_open_access: bool = False,
) -> List[Paper]:
    """Filtra y ordena papers por criterios simples.

    - Filtra por año mínimo si se indica.
    - Filtra por open access si se solicita.
    - Ordena por número de citas (desc) y año (desc).
    """

    filtered: List[Paper] = []
    for p in papers:
        if min_year is not None:
            if p.year is None or p.year < min_year:
                continue
        if only_open_access and not p.open_access:
            continue
        filtered.append(p)

    filtered.sort(
        key=lambda p: (
            p.citations or 0,
            p.year or 0,
        ),
        reverse=True,
    )

    return filtered[:max_results]


