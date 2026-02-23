import os
import requests
from smolagents import tool

SERPAPI_KEY = os.getenv("SERPAPI_API_KEY")

if not SERPAPI_KEY:
    raise ValueError("SERPAPI_KEY no está configurada")

@tool
def search_papers(query: str, num_results: int = 5) -> list:
    """
    Busca papers académicos en Google Scholar.
    Devuelve título, autores, año, abstract y link.

    Args:
        query: Consulta que se realiza por parte del usuario para hallar papers
        num_results: el número de papers que se quiere buscar en la consulta, por defecto, 5 papers
    """
    params = {
        "engine": "google_scholar",
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": num_results,
    }

    response = requests.get("https://serpapi.com/search", params=params)
    response.raise_for_status()
    data = response.json()

    papers = []
    for result in data.get("organic_results", []):
        papers.append({
            "title": result.get("title"),
            "authors": result.get("publication_info", {}).get("authors"),
            "year": result.get("publication_info", {}).get("year"),
            "abstract": result.get("snippet"),
            "link": result.get("link"),
        })

    return papers