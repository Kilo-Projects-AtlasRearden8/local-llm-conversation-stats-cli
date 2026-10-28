"""Local-first CLI to analyze local LLM chat logs.

Reads local JSON chat logs and reports message counts, token estimates,
top topics, and daily activity summaries. No API keys, no network, no
personal data is collected or transmitted.

Usage:
    python chat_stats.py <file.json> [--top-topics N] [--output {text,json}]

JSON input shapes accepted:
    - A list of message objects: [{"role": "user", "content": "...", "timestamp": "..."}]
    - An object with a "messages" key: {"messages": [...]}

Each message may include:
    - role:    "user", "assistant", "system", "tool" (default "unknown")
    - content: message text (default "")
    - timestamp: ISO-8601 string; only the date portion is used for daily grouping
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, date
from typing import Any, Iterable, List, Mapping, Optional, Tuple


# Rough heuristic: ~4 characters per token for English text. This is an
# estimate only; real tokenizers vary by model. Kept dependency-free so the
# tool works fully offline with no installs beyond the standard library.
CHARS_PER_TOKEN = 4


# Common English stop words filtered out when surfacing "top topics". Small,
# hand-picked list keeps this dependency-free and transparent.
STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has",
    "he", "in", "is", "it", "its", "of", "on", "or", "that", "the", "to",
    "was", "were", "will", "with", "you", "your", "i", "me", "my", "we",
    "our", "us", "this", "that", "these", "those", "can", "could", "would",
    "should", "do", "does", "did", "have", "had", "not", "no", "yes", "ok",
    "okay", "please", "thanks", "thank", "hi", "hello", "hey",
}


def estimate_tokens(text: str) -> int:
    """Estimate token count for a string using a character heuristic."""
    if not text:
        return 0
    return max(1, len(text) // CHARS_PER_TOKEN)


def _normalize_topic(word: str) -> str:
    word = word.lower()
    word = re.sub(r"[^a-z0-9'+]", "", word)
    return word


def extract_topics(text: str) -> Iterable[str]:
    """Yield candidate topic words from a message body."""
    for raw in re.split(r"\s+", text):
        word = _normalize_topic(raw)
        if len(word) >= 3 and word not in STOP_WORDS:
            yield word


def _parse_timestamp(value: Any) -> Optional[date]:
    """Parse a timestamp value into a date. Returns None if unparsable."""
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    # Try ISO-8601 full datetime first, then date-only.
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    # Fallback: fromisoformat handles offsets like +00:00 in 3.11+.
    try:
        return datetime.fromisoformat(text).date()
    except ValueError:
        return None


def load_messages(path: str) -> List[dict]:
    """Load and normalize messages from a JSON chat log file."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Chat log file not found: {path}")

    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)

    raw_messages: List[Mapping[str, Any]]
    if isinstance(data, list):
        raw_messages = data
    elif isinstance(data, dict):
        raw_messages = list(data.get("messages", []))
    else:
        raise ValueError(
            "Unsupported JSON shape: expected a list of messages or an "
            "object with a 'messages' key"
        )

    messages: List[dict] = []
    for entry in raw_messages:
        if not isinstance(entry, Mapping):
            continue
        content = entry.get("content", "")
        if content is None:
            content = ""
        messages.append(
            {
                "role": str(entry.get("role", "unknown")).lower(),
                "content": str(content),
                "timestamp": entry.get("timestamp"),
            }
        )
    return messages


def analyze(messages: List[dict]) -> dict:
    """Compute statistics for a list of normalized messages."""
    total = len(messages)
    by_role: Counter[str] = Counter()
    total_chars = 0
    total_tokens = 0
    topic_counter: Counter[str] = Counter()
    daily: dict[date, dict[str, int]] = defaultdict(lambda: {"messages": 0, "tokens": 0})

    for message in messages:
        role = message.get("role", "unknown")
        by_role[role] += 1

        content = message.get("content", "")
        total_chars += len(content)
        tokens = estimate_tokens(content)
        total_tokens += tokens

        for topic in extract_topics(content):
            topic_counter[topic] += 1

        day = _parse_timestamp(message.get("timestamp"))
        if day is not None:
            daily[day]["messages"] += 1
            daily[day]["tokens"] += tokens
        else:
            # Un-dated messages still count under a "unknown" bucket.
            daily_none = daily.setdefault(None, {"messages": 0, "tokens": 0})  # type: ignore[arg-type]
            daily_none["messages"] += 1  # type: ignore[union-attr]
            daily_none["tokens"] += tokens  # type: ignore[union-attr]

    top_topics = topic_counter.most_common()

    daily_summary: List[dict] = []
    for day in sorted(daily.keys(), key=lambda d: (d is None, str(d))):
        entry = daily[day]
        daily_summary.append(
            {
                "date": str(day) if day is not None else "unknown",
                "messages": entry["messages"],
                "tokens": entry["tokens"],
            }
        )

    return {
        "total_messages": total,
        "messages_by_role": dict(by_role),
        "total_characters": total_chars,
        "estimated_tokens": total_tokens,
        "chars_per_token": CHARS_PER_TOKEN,
        "top_topics": [{"topic": topic, "count": count} for topic, count in top_topics],
        "daily_activity": daily_summary,
    }


def format_text(stats: dict, top_topics: int = 10) -> str:
    """Render statistics as human-readable text."""
    lines: List[str] = []
    lines.append("Chat Log Statistics")
    lines.append("===================")
    lines.append("")
    lines.append(f"Total messages: {stats['total_messages']}")
    lines.append("")

    lines.append("Messages by role:")
    for role, count in sorted(stats["messages_by_role"].items()):
        lines.append(f"  {role}: {count}")
    lines.append("")

    lines.append(
        f"Estimated tokens: {stats['estimated_tokens']:,} "
        f"(approx, {stats['chars_per_token']} chars/token)"
    )
    lines.append("")

    lines.append(f"Top topics (top {top_topics}):")
    for idx, item in enumerate(stats["top_topics"][:top_topics], start=1):
        lines.append(f"  {idx}. {item['topic']} ({item['count']})")
    lines.append("")

    lines.append("Daily activity:")
    for entry in stats["daily_activity"]:
        lines.append(
            f"  {entry['date']}: {entry['messages']} message(s), "
            f"{entry['tokens']} estimated token(s)"
        )
    lines.append("")
    return "\n".join(lines)


def format_json(stats: dict) -> str:
    """Render statistics as JSON text."""
    return json.dumps(stats, indent=2, sort_keys=True) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="chat_stats",
        description="Analyze local LLM chat logs: message counts, token "
        "estimates, top topics, and daily activity summaries.",
    )
    parser.add_argument(
        "file",
        help="Path to the chat log JSON file to analyze.",
    )
    parser.add_argument(
        "--top-topics",
        type=int,
        default=10,
        metavar="N",
        help="Number of top topics to display (default: 10).",
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        messages = load_messages(args.file)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    stats = analyze(messages)

    if args.output == "json":
        print(format_json(stats), end="")
    else:
        print(format_text(stats, top_topics=args.top_topics))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
