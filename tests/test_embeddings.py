"""Tests for the embeddings skill.

Requires Ollama running with nomic-embed-text pulled:
    ollama pull nomic-embed-text
"""
import pytest

from doctorate_reader.skills.embeddings import _embed, _cosine_similarity


def test_related_texts_more_similar_than_unrelated():
    text_a = "fiscal policy and government spending effects on inequality"
    text_b = "fiscal multipliers and public expenditure redistribution"
    text_unrelated = "neural networks for image classification benchmarks"

    vec_a = _embed(text_a)
    vec_b = _embed(text_b)
    vec_unrelated = _embed(text_unrelated)

    sim_related = _cosine_similarity(vec_a, vec_b)
    sim_unrelated = _cosine_similarity(vec_a, vec_unrelated)

    assert sim_related > sim_unrelated, (
        f"Expected sim_related ({sim_related:.4f}) > sim_unrelated ({sim_unrelated:.4f})"
    )


def test_cosine_similarity_zero_vector():
    assert _cosine_similarity([0.0, 0.0], [1.0, 2.0]) == 0.0
    assert _cosine_similarity([1.0, 2.0], [0.0, 0.0]) == 0.0


def test_cosine_similarity_identical():
    v = [1.0, 2.0, 3.0]
    sim = _cosine_similarity(v, v)
    assert abs(sim - 1.0) < 1e-6
