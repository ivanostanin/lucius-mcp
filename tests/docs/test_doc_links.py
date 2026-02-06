import re
from pathlib import Path

import pytest


def get_project_root() -> Path:
    """Returns the project root directory."""
    return Path(__file__).parent.parent.parent


def get_markdown_files() -> list[Path]:
    """Find README.md and all files in the docs/ directory."""
    root = get_project_root()
    md_files = []

    # 1. Include root README.md
    readme = root / "README.md"
    if readme.exists():
        md_files.append(readme)

    # 2. Include everything in docs/
    docs_dir = root / "docs"
    if docs_dir.exists():
        md_files.extend(docs_dir.rglob("*.md"))

    return md_files


def extract_links(content: str) -> list[str]:
    """Extract markdown links: [text](target)."""
    # Regex to find links, ignoring image links ![]()
    # Matches [label](url) but not ![label](url)
    # Uses negative lookbehind (?<!\!) to avoid image tags
    return re.findall(r"(?<!\!)\[.*?\]\((.*?)\)", content)


# Generate list of markdown files at collection time for pytest parametrization
MD_FILES = get_markdown_files()


@pytest.mark.parametrize("md_file", MD_FILES, ids=lambda x: str(x.relative_to(get_project_root())))
def test_doc_links_exist(md_file: Path):
    """Verify that all internal links in a markdown file point to existing files."""
    content = md_file.read_text(encoding="utf-8")
    links = extract_links(content)

    broken_links = []

    for link in links:
        # Skip external links
        if link.startswith(("http://", "https://", "mailto:", "tel:", "irc:")):
            continue

        # Enforce relative paths
        if link.startswith("file://") or link.startswith("/"):
            broken_links.append(f"Absolute link found: {link} (Internal links MUST be relative)")
            continue

        # Relative links
        # Remove fragment if present
        base_link = link.split("#")[0]
        if not base_link:  # Link to an anchor in the same file
            continue

        # Target path relative to the directory of the current md_file
        target_path = (md_file.parent / base_link).resolve()

        if not target_path.exists():
            broken_links.append(f"Link points to non-existent file: {link} (Resolved to: {target_path})")

    if broken_links:
        pytest.fail(f"Broken links found in {md_file}:\n" + "\n".join(broken_links))
