# paper_agent/llm/huggingface.py
from smolagents import InferenceClientModel #type: ignore

def get_hf_model():
    return InferenceClientModel(
        model_id="meta-llama/Meta-Llama-3-8B-Instruct"
    )