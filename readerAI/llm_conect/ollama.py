# paper_agent/llm/ollama.py
from smolagents import OpenAIModel

def get_ollama_model():
    return OpenAIModel(
        model_id="mistral",
        base_url="http://localhost:11434/v1",
        api_key="ollama"
    )