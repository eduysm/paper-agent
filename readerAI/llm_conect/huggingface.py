# paper_agent/llm/huggingface.py
from smolagents import HfApiModel #type: ignore

def get_hf_model():
    return HfApiModel(
        model_id="meta-llama/Meta-Llama-3-8B-Instruct"
    )