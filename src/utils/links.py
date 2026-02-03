from __future__ import annotations

from collections.abc import Sequence


def normalize_links(items: Sequence[object]) -> list[tuple[str | None, str | None, str | None]]:
    normalized: list[tuple[str | None, str | None, str | None]] = []
    for item in items:
        if isinstance(item, dict):
            normalized.append((item.get("name"), item.get("url"), item.get("type")))
        else:
            normalized.append((getattr(item, "name", None), getattr(item, "url", None), getattr(item, "type", None)))
    return normalized
