from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from readerAI.tools.OpenAlex_searcher import search_papers

print(search_papers(query='Control de precios de alquiler inmobiliario', num_results=3))