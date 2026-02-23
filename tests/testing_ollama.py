# test_ollama.py
from smolagents import CodeAgent, LiteLLMModel
import logging


logging.basicConfig(level=logging.INFO)

model = LiteLLMModel(
    model="ollama/qwen2:7b",
    model_id="qwen2:7b"
    )

agent = CodeAgent(
    tools=[],
    model=model,
)

print(agent.run("Di hola en español", max_steps=1))