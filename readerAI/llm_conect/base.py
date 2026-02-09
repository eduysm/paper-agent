# paper_agent/llm/base.py
import os
from .ollama import get_ollama_model
from .huggingface import get_hf_model

def get_model():
    backend = os.getenv("MODEL_BACKEND", "ollama")
    if backend == "hf":
        return get_hf_model()
    return get_ollama_model()