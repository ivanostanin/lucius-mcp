# AGENTS.md

Project instructions for agents working in `lucius-mcp`.

## Start Here

Before making any code, spec, or test changes:

1. Read [`docs/development.md`](/home/node/.openclaw/codespaces/lucius-mcp-change-tracking/docs/development.md).
2. Check current git state so you understand the active branch and any in-flight work.
3. Prefer existing project docs and specs over guesswork.

Do not skip step 1.

## Python Environment

- Use `uv`, not bare `python`/`pip`, for project environment setup and commands.
- Sync dependencies with:

```bash
uv sync --all-extras
```

- Run project commands with `uv run`, for example:

```bash
uv run pytest tests/unit tests/integration
uv run ruff check .
uv run mypy src
```

- If a task needs Python 3.13+, use `uv` to provision and run the correct interpreter instead of falling back to the system `python3`.

## Change Discipline

- Keep changes scoped to the requested task.
- Do not use throwaway clones in `/tmp` for normal repo work; use this persistent checkout under `/home/node/.openclaw/codespaces/`.
- When touching telemetry, preserve the privacy constraints documented in `docs/development.md`.
- When updating stories or sprint artifacts, keep them consistent with the code and tests.

## Validation

- Run the smallest relevant checks first.
- If full validation is too heavy, run focused checks on touched areas and say what was not run.
- Do not claim tests passed unless you actually ran them in this repo.
