import requests
from typing import List, Dict, Optional
from smolagents import tool
from datetime import datetime
import json

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

def get_journal_ids(journals: List[str]) -> List[str]:
    """
    Convierte nombres de revistas en IDs de OpenAlex (Sxxxx).
    """
    source_url = "https://api.openalex.org/sources"
    ids = []

    for journal in journals:
        response = requests.get(
            source_url,
            params={"search": journal, "per-page": 1},
            timeout=10,
        )
        response.raise_for_status()
        results = response.json().get("results", [])
        if results:
            ids.append(results[0]["id"].split("/")[-1])  # extrae Sxxxx

    return ids

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
    filters = []

    # ✅ Filtro últimos 12 meses (forma correcta)
    if recent_only:
        today = datetime.now().date()
        last_year_date = today.replace(year=today.year - 1)
        filters.append(
            f"from_publication_date:{last_year_date},to_publication_date:{today}"
        )

    # ✅ Filtro por revistas (usando IDs correctos)
    if journals:
        journal_ids = get_journal_ids(journals)
        if journal_ids:
            journal_filter = "primary_location.source.id:" + "|".join(journal_ids)
            filters.append(journal_filter)

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
            if author.get("author")
        ]

        papers.append({
            "title": result.get("display_name"),
            "authors": authors,
            "year": result.get("publication_year"),
            "abstract": abstract,
            "journal": result.get("primary_location", {})
                             .get("source", {}),
         #                    .get("display_name"),
            "citations": result.get("cited_by_count"),
            "doi": result.get("doi"),
            "open_access": result.get("open_access", {}).get("is_oa"),
            "link": result.get("primary_location", {}).get("landing_page_url"),
        })
    
    print(json.dumps(papers, indent=4, ensure_ascii=False))
    return papers