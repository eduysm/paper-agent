from smolagents import CodeAgent
from dotenv import load_dotenv
from llm_conect.base import get_model
from tools.OpenAlex_searcher import search_papers
import yaml
from pathlib import Path
import logging


logging.basicConfig(level=logging.INFO)

load_dotenv()

PROMPTS_PATH = Path(__file__).parent / "prompts" / "system.yaml"

def load_prompts(path=PROMPTS_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def run_agent(system_prompt: str, user_prompt: str):
    agent = CodeAgent(
        tools=[search_papers],
        model=get_model(),
    )

    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    return agent.run(full_prompt, max_steps=1)


if __name__ == "__main__":
    prompts = load_prompts()

    topic = "Evaluación de la política económica y de las políticas públicas"

    system_prompt = prompts["system"]
    user_prompt = prompts["search_instruction"].format(topic=topic)

    result = run_agent(system_prompt, user_prompt)
    print(result)