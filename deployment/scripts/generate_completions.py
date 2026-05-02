#!/usr/bin/env python3
"""Write generated shell completion scripts for the lucius CLI."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.cli.completions import (  # noqa: E402
    completion_data,
    generate_bash_completion,
    generate_fish_completion,
    generate_powershell_completion,
    generate_zsh_completion,
)

COMPLETION_DIR = PROJECT_ROOT / "deployment" / "shell-completions"


def _completion_data() -> tuple[list[str], dict[str, str], dict[str, list[str]]]:
    """Backward-compatible wrapper for tests and release scripts."""
    return completion_data()


def main() -> None:
    """Generate all completion scripts."""
    print("Generating shell completion scripts...")

    entities, alias_to_canonical, actions_by_entity = _completion_data()
    print(f"Found {len(entities)} entity aliases across {len(actions_by_entity)} canonical entities")

    COMPLETION_DIR.mkdir(parents=True, exist_ok=True)

    outputs = {
        "lucius.bash": generate_bash_completion(entities, alias_to_canonical, actions_by_entity),
        "lucius.zsh": generate_zsh_completion(entities, alias_to_canonical, actions_by_entity),
        "lucius.fish": generate_fish_completion(entities, alias_to_canonical, actions_by_entity),
        "lucius.ps1": generate_powershell_completion(entities, alias_to_canonical, actions_by_entity),
    }
    for filename, content in outputs.items():
        path = COMPLETION_DIR / filename
        path.write_text(content, encoding="utf-8")
        print(f"Generated: {path}")

    print("\nShell completion scripts generated successfully.")
    print("\nTo enable completion, run:")
    print("  lucius install-completions")
    print("  lucius install-completions --shell bash|zsh|fish|powershell")


if __name__ == "__main__":
    main()
