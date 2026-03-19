"""Tests for user profile save/load roundtrip."""
import os
import tempfile

import pytest

from doctorate_reader.schemas import UserProfile
from doctorate_reader.skills.user_profile import load_profile, save_profile


def test_roundtrip_full_profile(tmp_path):
    path = str(tmp_path / "profile.yaml")
    original = UserProfile(
        interests=["fiscal policy", "inequality"],
        research_line="I study how government transfers affect income distribution.",
        example_docs=["Excerpt from paper A.", "Excerpt from paper B."],
    )
    save_profile(original, path)
    loaded = load_profile(path)

    assert loaded.interests == original.interests
    assert loaded.research_line == original.research_line
    assert loaded.example_docs == original.example_docs


def test_roundtrip_minimal_profile(tmp_path):
    path = str(tmp_path / "minimal.yaml")
    original = UserProfile(interests=["monetary policy"])
    save_profile(original, path)
    loaded = load_profile(path)

    assert loaded.interests == ["monetary policy"]
    assert loaded.research_line is None
    assert loaded.example_docs == []


def test_load_missing_file():
    with pytest.raises(FileNotFoundError):
        load_profile("/nonexistent/path/profile.yaml")


def test_load_invalid_yaml(tmp_path):
    path = str(tmp_path / "bad.yaml")
    with open(path, "w") as f:
        f.write("not_interests: foo\n")
    with pytest.raises(ValueError):
        load_profile(path)
