# STATUS

## What was built

A local-first, dependency-free Python CLI for analyzing local LLM chat logs:
`chat_stats.py`. It reads local JSON chat logs (no API keys, no network, no
cloud upload) and reports:

- Total message count and breakdown by role (user, assistant, system, tool)
- Estimated token count (~4 chars per token heuristic; estimate only)
- Top topics across messages (stop words filtered, punctuation stripped)
- Daily activity summary (messages and estimated tokens per day)
- Text or JSON output (`--output text|json`, `--top-topics N`)

Also included:
- `tests/test_chat_stats.py` — 22 tests covering parsing (list shape,
  dict-with-`messages` shape, missing file, bad JSON, null content), message
  counts, token estimates, top topics, daily activity, empty logs, both
  output formats, and CLI exit codes
- `sample_chat_log.json` — sample chat log for manual demo
- `pyproject.toml` — packaging with a `chat-stats` console script (verified
  build + editable install + console script run)
- `LICENSE` — MIT License, copyright line exactly
  `Copyright (c) 2026 Asdale Dynamics, LLC`
- `README.md` — beginner-friendly usage guide crediting Asdale Dynamics, LLC
- `STATUS.md` — this file

## How to run

Requires Python 3.8+ (tested on Python 3.13.5). No `pip install` needed.

```bash
# Human-readable summary
python3 chat_stats.py path/to/chat-log.json

# JSON output
python3 chat_stats.py path/to/chat-log.json --output json

# Top 5 topics only
python3 chat_stats.py path/to/chat-log.json --top-topics 5

# Demo with the bundled sample
python3 chat_stats.py sample_chat_log.json
```

Optional: install as a command with `pip3 install -e .`, then run
`chat-stats path/to/chat-log.json`.

## Tests

```bash
python3 -m pytest tests/          # 22 passed
python3 -m unittest discover -s tests  # 22 passed
```

## Verification results (2026-10-28)

- `python3 -m pytest tests/` — 22 passed, 0 failed
- `python3 -m unittest discover -s tests` — 22 passed, 0 failed
- `python3 chat_stats.py sample_chat_log.json` — runs cleanly, prints text
  summary with message counts, role breakdown, estimated tokens, top topics,
  daily activity
- `python3 chat_stats.py sample_chat_log.json --output json --top-topics 3` —
  prints valid JSON
- Missing file and malformed JSON exit non-zero with an error message
- `pip3 install -e .` (in a fresh venv) — builds and installs successfully
- `chat-stats` console script — runs, text and JSON output both valid
- No dependencies beyond the Python standard library; runs fully offline
- Secret/personal-data scan — no API keys, passwords, or secrets found

## Known gaps

- Token estimates use a fixed ~4 chars/token heuristic; real tokenizers vary
  by model (documented in the README and output).
- Top topics uses a small hard-coded English stop-word list; other languages
  are not optimized.
- Timestamps must be ISO-8601; unparseable timestamps are grouped under
  "unknown" rather than failing.
- Only JSON input is supported; no chat-app importers (e.g. Obsidian,
  ChatGPT export, etc.).
- Packaging is present but not published to PyPI — intentional (local-first,
  no publishing).
- System-wide `pip3 install -e .` is blocked by PEP 668 on this OS; use a
  virtual environment or run `python3 chat_stats.py` directly.
