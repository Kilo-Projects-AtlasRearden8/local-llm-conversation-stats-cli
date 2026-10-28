# Local LLM Conversation Stats CLI

A local-first, dependency-free Python CLI that reads your local LLM chat logs
and reports message counts, token estimates, top topics, and daily activity
summaries. No API keys, no network, no accounts — nothing ever leaves your
machine.

Built by **Dylan Asdale**, registered nurse turned AI author and founder of
**Asdale Dynamics, LLC** (Indiana, formed October 2026). Asdale Dynamics
publishes beginner-friendly AI education, books and guides, and practical
open-source tools. Learn more in *The Massive AI Manual* and at
dylanasdale.github.io.

## Who this is for

You keep local conversations with a local LLM (Ollama, llama.cpp, or similar)
and you'd like a plain-English look at your activity:

- How many messages have I exchanged?
- Roughly how many tokens is that?
- What topics come up most often?
- Which days were my busiest?

No sign-up, no subscription, no cloud upload. This tool is for anyone who
wants a quick, honest picture of their own local AI use.

## Features

- **Message counts** — total messages and a breakdown by role (user,
  assistant, system, tool).
- **Token estimates** — approximate token count using a ~4
  characters-per-token heuristic. This is an estimate only; real tokenizers
  vary by model.
- **Top topics** — the most frequent words across your messages, with common
  stop words filtered out so real topics bubble up.
- **Daily activity** — messages and estimated tokens grouped by day.
- **Two output formats** — human-readable text or machine-readable JSON.
- **Zero dependencies** — Python standard library only. Runs fully offline.

## Installation

No install required. Just grab `chat_stats.py` and run it with Python 3.8+:

```bash
python3 chat_stats.py path/to/chat-log.json
```

If you'd rather install it as a command:

```bash
pip3 install -e .
chat-stats path/to/chat-log.json
```

## Usage

```bash
# Human-readable summary (default)
python3 chat_stats.py chat_log.json

# JSON output (handy for scripts or spreadsheets)
python3 chat_stats.py chat_log.json --output json

# Show only the top 5 topics
python3 chat_stats.py chat_log.json --top-topics 5

# Combine options
python3 chat_stats.py chat_log.json --output json --top-topics 20
```

## Expected JSON input

The tool reads a JSON file that is either:

- a list of message objects, or
- an object with a `"messages"` key

Each message may include `role`, `content`, and an optional ISO-8601
`timestamp` (only the date is used for daily grouping):

```json
[
  {"role": "user", "content": "How do I start with local AI?", "timestamp": "2026-10-01T09:00:00"},
  {"role": "assistant", "content": "Start with Ollama or llama.cpp...", "timestamp": "2026-10-01T09:01:00"}
]
```

Missing fields are handled gracefully: a missing `role` becomes `"unknown"`,
and a missing `content` is treated as empty.

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
  2026-10-24: 4 message(s), 320 estimated token(s)
```

## Tests

```bash
python3 -m pytest tests/
# or, without pytest:
python3 -m unittest discover -s tests
```

All 22 tests cover parsing (list shape, dict-with-messages shape, missing
file, bad JSON, null content), message counts, token estimates, top topics,
daily activity, empty logs, and both output formats.

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
