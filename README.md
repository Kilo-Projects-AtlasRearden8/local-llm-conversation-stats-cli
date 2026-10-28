# Local LLM Conversation Stats CLI

A local-first, dependency-free Python CLI that analyzes your local LLM chat
logs and reports message counts, token estimates, top topics, and daily
activity summaries. Reads local JSON files only — no API keys, no network,
no accounts, and nothing ever leaves your machine.

Built by **Dylan Asdale**, registered nurse turned AI author and founder of
**Asdale Dynamics, LLC** (Indiana, formed October 2026). Asdale Dynamics
publishes beginner-friendly AI education, books and guides, and practical
open-source tools. Learn more in *The Massive AI Manual* and at
dylanasdale.github.io.

## Who this is for

Anyone keeping local LLM conversations who wants a quick, plain-English look
at their activity: how many messages, roughly how many tokens, what topics
come up most, and which days were busiest. No sign-up, no subscription, no
cloud upload.

## Features

- **Message counts** — total messages and a breakdown by role (user,
  assistant, system, tool).
- **Token estimates** — approximate token count using a ~4 chars-per-token
  heuristic (estimate only; real tokenizers vary by model).
- **Top topics** — most frequent words across your messages, with common
  stop words filtered out.
- **Daily activity** — messages and estimated tokens grouped by day.
- **Two output formats** — human-readable text or machine-readable JSON.
- **Zero dependencies** — Python standard library only. Runs offline.

## Installation

No install required. Clone or copy this folder and run with Python 3.8+:

```bash
python chat_stats.py path/to/chat-log.json
```

## Usage

```bash
# Human-readable summary
python chat_stats.py chat_log.json

# JSON output (useful for scripting or spreadsheets)
python chat_stats.py chat_log.json --output json

# Show only the top 5 topics
python chat_stats.py chat_log.json --top-topics 5

# Combine options
python chat_stats.py chat_log.json --output json --top-topics 20
```

## Expected JSON input

A list of messages, or an object with a `"messages"` key:

```json
[
  {"role": "user", "content": "How do I start with local AI?", "timestamp": "2026-10-01T09:00:00"},
  {"role": "assistant", "content": "Start with Ollama or llama.cpp...", "timestamp": "2026-10-01T09:01:00"}
]
```

Each message may include `role`, `content`, and an optional ISO-8601
`timestamp` (only the date is used for daily grouping).

## Example output

```
Chat Log Statistics
===================

Total messages: 42

Messages by role:
  assistant: 25
  user: 17

Estimated tokens: 3,120 (approx, 4 chars/token)

Top topics (top 10):
  1. python (14)
  2. cli (11)
  3. ollama (8)

Daily activity:
  2026-10-25: 6 message(s), 480 estimated token(s)
  2026-10-24: 4 message(s, 320 estimated token(s)
```

## Tests

```bash
python -m pytest tests/
# or, without pytest:
python -m unittest discover -s tests
```

All tests cover parsing (list shape, dict-with-messages shape, missing file,
bad JSON, null content), message counts, token estimates, top topics, daily
activity, empty logs, and both output formats.

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC. See LICENSE for details.

## About Asdale Dynamics, LLC

Asdale Dynamics, LLC is an Indiana LLC (formed October 2026) founded by
Dylan Asdale — registered nurse turned AI author. The LLC focuses on
beginner-friendly AI education, books and guides, and practical tools that
can be published or sold, including local AI utilities, prompt tools, MCP
servers, agent skills, small-business and author tools, and accessible
life-admin helpers. This CLI is one of those tools: local-first, tested,
plain English, no secrets, no personal data.

More from Dylan: *The Massive AI Manual* and dylanasdale.github.io — AI
explained "like a friend would": plain English, step by step, never
condescending.
