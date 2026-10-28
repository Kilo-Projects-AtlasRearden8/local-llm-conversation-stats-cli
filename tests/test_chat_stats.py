"""Tests for chat_stats parsing and statistics."""

from __future__ import annotations

import json
import os
import tempfile
import unittest

from chat_stats import (
    CHARS_PER_TOKEN,
    STOP_WORDS,
    analyze,
    estimate_tokens,
    extract_topics,
    format_json,
    format_text,
    load_messages,
    main,
)


def write_temp_json(data) -> str:
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        json.dump(data, handle)
    return path


class TestTokenEstimation(unittest.TestCase):
    def test_empty_string(self):
        self.assertEqual(estimate_tokens(""), 0)

    def test_short_text(self):
        self.assertEqual(estimate_tokens("hi"), 1)

    def test_heuristic(self):
        text = "a" * 8
        self.assertEqual(estimate_tokens(text), 2)


class TestTopicExtraction(unittest.TestCase):
    def test_stop_words_filtered(self):
        topics = list(extract_topics("the and is of a to"))
        self.assertEqual(topics, [])

    def test_punctuation_stripped(self):
        topics = list(extract_topics("Python!!! CLI, tool."))
        self.assertIn("python", topics)
        self.assertIn("cli", topics)
        self.assertIn("tool", topics)

    def test_case_normalized(self):
        topics = list(extract_topics("PYTHON python Python"))
        self.assertEqual(topics, ["python", "python", "python"])


class TestLoading(unittest.TestCase):
    def test_list_shape(self):
        path = write_temp_json(
            [
                {"role": "user", "content": "hello", "timestamp": "2026-01-01"},
                {"role": "assistant", "content": "hi there"},
            ]
        )
        try:
            messages = load_messages(path)
            self.assertEqual(len(messages), 2)
            self.assertEqual(messages[0]["role"], "user")
            self.assertEqual(messages[1]["role"], "assistant")
        finally:
            os.unlink(path)

    def test_dict_with_messages_shape(self):
        path = write_temp_json(
            {"messages": [{"role": "user", "content": "x"}]}
        )
        try:
            messages = load_messages(path)
            self.assertEqual(len(messages), 1)
        finally:
            os.unlink(path)

    def test_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            load_messages("/nonexistent/path.json")

    def test_bad_json(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w") as handle:
            handle.write("{not valid json")
        try:
            with self.assertRaises(Exception):
                load_messages(path)
        finally:
            os.unlink(path)

    def test_null_content_normalized(self):
        path = write_temp_json([{"role": "user", "content": None}])
        try:
            messages = load_messages(path)
            self.assertEqual(messages[0]["content"], "")
        finally:
            os.unlink(path)


class TestAnalysis(unittest.TestCase):
    def setUp(self):
        self.messages = [
            {"role": "user", "content": "I love Python and CLI tools", "timestamp": "2026-10-01T09:00:00"},
            {"role": "assistant", "content": "Python is great for automation", "timestamp": "2026-10-01T09:05:00"},
            {"role": "user", "content": "Let's build a CLI tool in Python", "timestamp": "2026-10-02T10:00:00"},
        ]

    def test_counts(self):
        stats = analyze(self.messages)
        self.assertEqual(stats["total_messages"], 3)
        self.assertEqual(stats["messages_by_role"]["user"], 2)
        self.assertEqual(stats["messages_by_role"]["assistant"], 1)

    def test_token_estimate(self):
        stats = analyze(self.messages)
        expected = sum(estimate_tokens(m["content"]) for m in self.messages)
        self.assertEqual(stats["estimated_tokens"], expected)

    def test_top_topics(self):
        stats = analyze(self.messages)
        topics = [item["topic"] for item in stats["top_topics"]]
        self.assertIn("python", topics)
        self.assertIn("cli", topics)
        self.assertNotIn("the", topics)

    def test_daily_activity(self):
        stats = analyze(self.messages)
        dates = [entry["date"] for entry in stats["daily_activity"]]
        self.assertIn("2026-10-01", dates)
        self.assertIn("2026-10-02", dates)
        oct1 = next(e for e in stats["daily_activity"] if e["date"] == "2026-10-01")
        self.assertEqual(oct1["messages"], 2)

    def test_empty(self):
        stats = analyze([])
        self.assertEqual(stats["total_messages"], 0)
        self.assertEqual(stats["estimated_tokens"], 0)
        self.assertEqual(stats["top_topics"], [])
        self.assertEqual(stats["daily_activity"], [])


class TestFormatting(unittest.TestCase):
    def test_text_output(self):
        stats = analyze(
            [
                {"role": "user", "content": "hello world", "timestamp": "2026-01-01"},
            ]
        )
        text = format_text(stats)
        self.assertIn("Chat Log Statistics", text)
        self.assertIn("Total messages: 1", text)
        self.assertIn("user: 1", text)

    def test_json_output(self):
        stats = analyze(
            [
                {"role": "user", "content": "hello world"},
            ]
        )
        text = format_json(stats)
        parsed = json.loads(text)
        self.assertEqual(parsed["total_messages"], 1)


class TestCLI(unittest.TestCase):
    def run_cli(self, *args):
        return main(list(args))

    def test_text_output_exit_zero(self):
        path = write_temp_json(
            [{"role": "user", "content": "hello world", "timestamp": "2026-01-01"}]
        )
        try:
            code = self.run_cli(path)
            self.assertEqual(code, 0)
        finally:
            os.unlink(path)

    def test_json_output_exit_zero(self):
        path = write_temp_json([{"role": "user", "content": "hi"}])
        try:
            code = self.run_cli(path, "--output", "json")
            self.assertEqual(code, 0)
        finally:
            os.unlink(path)

    def test_missing_file_exit_nonzero(self):
        code = self.run_cli("/nonexistent/file.json")
        self.assertNotEqual(code, 0)

    def test_top_topics_flag(self):
        path = write_temp_json(
            [{"role": "user", "content": "Python CLI tools are fun", "timestamp": "2026-01-01"}]
        )
        try:
            code = self.run_cli(path, "--top-topics", "1")
            self.assertEqual(code, 0)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
