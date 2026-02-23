from smolagents import LiteLLMModel

def get_ollama_model():
    return LiteLLMModel(
        model="ollama/qwen2:7b",
        model_id="qwen2:7b"
    )