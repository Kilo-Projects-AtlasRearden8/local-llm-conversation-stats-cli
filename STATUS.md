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
- `pyproject.toml` — optional packaging with a `chat-stats` console script
- `LICENSE` — MIT License, copyright line exactly
  `Copyright (c) 2026 Asdale Dynamics, LLC`
- `README.md` — usage guide crediting Asdale Dynamics, LLC
- `STATUS.md` — this file

## How to run

Requires Python 3.8+ (tested on Python 3.13.5). No `pip install` needed.

```bash
# Human-readable summary
python chat_stats.py path/to/chat-log.json

# JSON output
python chat_stats.py path/to/chat-log.json --output json

# Top 5 topics only
python chat_stats.py path/to/chat-log.json --top-topics 5

# Demo with the bundled sample
python chat_stats.py sample_chat_log.json
```

## Tests

```bash
python -m pytest tests/          # 22 passed
python -m unittest discover -s tests  # 22 passed
```

## Verification results (2026-10-28)

- `python -m pytest tests/` — 22 passed, 0 failed
- `python chat_stats.py sample_chat_log.json` — runs cleanly, prints text
  summary with message counts, role breakdown, estimated tokens, top topics,
  daily activity
- `python chat_stats.py sample_chat_log.json --output json --top-topics 3` —
  prints valid JSON
- Missing file and malformed JSON exit non-zero with an error message
- No dependencies beyond the Python standard library; runs fully offline

## Known gaps

- Token estimates use a fixed ~4 chars/token heuristic; real tokenizers vary
  by model (documented in the README and output).
- Top topics uses a small hard-coded English stop-word list; other languages
  are not optimized.
- Timestamps must be ISO-8601; unparseable timestamps are grouped under
  "unknown" rather than failing.
- Only JSON input is supported; no chat-app importers (e.g. Obsidian,
  ChatGPT export, etc.).
- Packaging (`pyproject.toml`) is present but not published to PyPI — this is
  intentional (local-first, no publishing).
