import os
from typing import Optional

import yaml

from doctorate_reader.schemas import UserProfile


def load_profile(path: str) -> UserProfile:
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Profile not found at '{path}'. "
            "Create one with: python -m doctorate_reader.cli --setup-profile <path>"
        )
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict) or "interests" not in data:
        raise ValueError(
            f"Invalid profile at '{path}': must be a YAML mapping with an 'interests' list."
        )
    interests = data["interests"]
    if not isinstance(interests, list) or not interests:
        raise ValueError(
            f"Invalid profile at '{path}': 'interests' must be a non-empty list of strings."
        )
    return UserProfile(
        interests=[str(i) for i in interests],
        research_line=data.get("research_line") or None,
        example_docs=[str(d) for d in data.get("example_docs") or []],
    )


def save_profile(profile: UserProfile, path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    data = {"interests": profile.interests}
    if profile.research_line:
        data["research_line"] = profile.research_line
    if profile.example_docs:
        data["example_docs"] = profile.example_docs
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)


def setup_profile_interactive() -> UserProfile:
    print("=== Doctorate Reader — Profile Setup ===\n")

    raw_interests = input(
        "Enter your research interests (comma-separated, required):\n> "
    ).strip()
    if not raw_interests:
        raise ValueError("At least one research interest is required.")
    interests = [i.strip() for i in raw_interests.split(",") if i.strip()]

    print("\nDescribe your research line in free text (press Enter to skip):")
    research_line: Optional[str] = input("> ").strip() or None

    print(
        "\nPaste up to 3 short excerpts from your own papers (Enter a blank line after each; "
        "press Enter immediately to skip):"
    )
    example_docs = []
    for i in range(1, 4):
        print(f"  Excerpt {i} (Enter to finish):")
        lines = []
        while True:
            line = input("    ")
            if not line:
                break
            lines.append(line)
        if lines:
            example_docs.append(" ".join(lines))
        else:
            break

    return UserProfile(
        interests=interests,
        research_line=research_line,
        example_docs=example_docs if example_docs else None,
    )
