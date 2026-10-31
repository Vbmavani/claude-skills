#!/usr/bin/env python3
"""Sum time, tool calls and tokens for session logs, including their subagents."""
import argparse
import json
from datetime import datetime
from pathlib import Path

TOKEN_FIELDS = (
    "input_tokens",
    "output_tokens",
    "cache_read_input_tokens",
    "cache_creation_input_tokens",
)


def read_log(path):
    seen = set()
    totals = {"messages": 0, "web_calls": 0, "output_tokens": 0, "total_tokens": 0}
    stamps = []
    for line in path.open(errors="ignore"):
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("timestamp"):
            stamps.append(event["timestamp"])
        message = event.get("message")
        if not isinstance(message, dict):
            continue
        content = message.get("content")
        if isinstance(content, list):
            totals["web_calls"] += sum(
                1
                for block in content
                if isinstance(block, dict)
                and block.get("type") == "tool_use"
                and block.get("name") in ("WebSearch", "WebFetch")
            )
        usage = message.get("usage")
        if not usage or message.get("id") in seen:
            continue
        seen.add(message.get("id"))
        totals["messages"] += 1
        totals["output_tokens"] += usage.get("output_tokens", 0)
        totals["total_tokens"] += sum(usage.get(field, 0) for field in TOKEN_FIELDS)
    return totals, stamps


def summarize(path):
    totals, stamps = read_log(path)
    subagents = sorted(path.with_suffix("").glob("subagents/*.jsonl"))
    for subagent in subagents:
        extra, extra_stamps = read_log(subagent)
        stamps += extra_stamps
        for key in totals:
            totals[key] += extra[key]
    minutes = None
    if stamps:
        parse = lambda stamp: datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        minutes = round((parse(max(stamps)) - parse(min(stamps))).total_seconds() / 60, 1)
    return {"log": path.name, "subagents": len(subagents), "minutes": minutes, **totals}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", nargs="+", type=Path)
    args = parser.parse_args()
    for log in args.logs:
        print(json.dumps(summarize(log)))


if __name__ == "__main__":
    main()
