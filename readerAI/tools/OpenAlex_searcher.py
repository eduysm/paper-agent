import requests
from typing import List, Dict, Optional
from smolagents import tool
from datetime import datetime

def reconstruct_abstract(inverted_index: dict) -> str:
    """
    OpenAlex devuelve el abstract como inverted index.
    Esta función lo reconstruye a texto normal.
    """
    if not inverted_index:
        return None #type: ignore

    words = []
    for word, positions in inverted_index.items():
        for pos in positions:
            words.append((pos, word))

    words_sorted = sorted(words)
    return " ".join(word for _, word in words_sorted)

@tool
def search_papers(
    query: str,
    num_results: int = 5,
    recent_only: bool = True,
    journals: Optional[List[str]] = None,
    sort_by: str = "cited_by_count:desc",
    ) -> List[Dict]:
    """
    Busca papers académicos utilizando OpenAlex.
    Devuelve title, authors, year, abstract completo, journal, citations, doi, open_access, link en formato lista/diccionario

    Args:
        query: Consulta que se realiza por parte del usuario para hallar papers
        num_results: el número de papers que se quiere buscar en la consulta, por defecto, 5 papers
        recent_only: si True → últimos 12 meses
        journals: lista de revistas de interés
        sort_by: criterio de ordenación
    """


    url = "https://api.openalex.org/works"

    current_year = datetime.now().year
    last_year = current_year - 1

    filters = []

    # 🔹 Filtro por fecha reciente (último año)
    if recent_only:
        filters.append(f"publication_year:{last_year}-{current_year}")

    # 🔹 Filtro por revistas
    if journals:
        journal_filters = [
            f"primary_location.source.display_name:{journal}"
            for journal in journals
        ]
        filters.extend(journal_filters)

    params = {
        "search": query,
        "per-page": num_results,
        "sort": sort_by,
    }

    if filters:
        params["filter"] = ",".join(filters)

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    papers = []

    for result in data.get("results", []):
        abstract = reconstruct_abstract(result.get("abstract_inverted_index"))

        authors = [
            author["author"]["display_name"]
            for author in result.get("authorships", [])
        ]

        papers.append({
            "title": result.get("display_name"),
            "authors": authors,
            "year": result.get("publication_year"),
            "abstract": abstract,
            "journal": result.get("primary_location", {})
                             .get("source", {})
                             .get("display_name"),
            "citations": result.get("cited_by_count"),
            "doi": result.get("doi"),
            "open_access": result.get("open_access", {})
                                  .get("is_oa"),
            "link": result.get("primary_location", {})
                          .get("landing_page_url"),
        })

    return papers