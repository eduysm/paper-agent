from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from readerAI.tools.OpenAlex_searcher import search_papers

resultados = search_papers(query='Evaluation of economic policy and public policies', num_results=3)
print(resultados)