from smolagents import CodeAgent
from dotenv import load_dotenv
from readerAI.llm_conect.base import get_model
from readerAI.tools.scholar_searcher import search_papers

load_dotenv()

def run_agent(system_prompt: str, topic: str):
    agent = CodeAgent(
        tools=[search_papers],
        model=get_model(),
        system_prompt=system_prompt,
    )

    query = f"""
    Busca papers sobre el siguiente tema:
    {topic}

    Devuelve un resumen de cada paper.
    """

    return agent.run(query)


if __name__ == "__main__":
    with open("paper_agent/prompts/system.txt") as f:
        system_prompt = f.read()

    topic = "Evaluación de la política económica y de las políticas públicas"
    result = run_agent(system_prompt, topic)
    print(result)