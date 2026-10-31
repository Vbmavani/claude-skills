#!/usr/bin/env python3
"""Join saved debate rounds into one complete transcript with random neutral labels."""
import argparse
import random
import re
from pathlib import Path

ROUNDS = (("opening", "Opening"), ("cross", "Cross-examination"), ("closing", "Closing"))
LEAK_WORDS = re.compile(r"\b(agent [ab]|position [ab]|my opponent is claude|the human|the user|as an ai)\b", re.I)


def round_files(folder, side):
    """Return (heading, path) for each round this side saved, in debate order."""
    found = []
    for key, heading in ROUNDS:
        path = folder / f"{side}-{key}.md"
        if path.exists():
            found.append((heading, path))
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds-dir", required=True, type=Path, help="folder holding a-opening.md, b-opening.md and so on")
    parser.add_argument("--brief", required=True, type=Path)
    parser.add_argument("--review-dir", required=True, type=Path)
    parser.add_argument("--key-file", required=True, type=Path)
    args = parser.parse_args()

    if args.review_dir.resolve() in args.key_file.resolve().parents:
        parser.error("--key-file must be outside --review-dir")
    if (args.review_dir / "transcript.md").exists():
        parser.error(f"transcript.md already exists in {args.review_dir}")

    a_rounds = round_files(args.rounds_dir, "a")
    b_rounds = round_files(args.rounds_dir, "b")
    if not a_rounds or [h for h, _ in a_rounds] != [h for h, _ in b_rounds]:
        parser.error("both sides need files for the same rounds, starting with a-opening.md and b-opening.md")

    labels = ["Side 1", "Side 2"]
    random.SystemRandom().shuffle(labels)
    label_for = {"a": labels[0], "b": labels[1]}
    order = sorted(("a", "b"), key=lambda side: label_for[side])

    parts = [f"# Debate transcript\n\n## Question and brief\n\n{args.brief.read_text(encoding='utf-8').strip()}\n"]
    rounds_by_side = {"a": a_rounds, "b": b_rounds}
    for index, (heading, _) in enumerate(a_rounds):
        parts.append(f"## {heading}\n")
        for side in order:
            text = rounds_by_side[side][index][1].read_text(encoding="utf-8").strip()
            parts.append(f"### {label_for[side]}\n\n{text}\n")
    transcript = "\n".join(parts)
    for side, label in label_for.items():
        transcript = re.sub(rf"\bside {side}\b", label, transcript, flags=re.I)

    args.review_dir.mkdir(parents=True, exist_ok=True)
    (args.review_dir / "transcript.md").write_text(transcript, encoding="utf-8")
    args.key_file.parent.mkdir(parents=True, exist_ok=True)
    args.key_file.write_text(f"a={label_for['a']}\nb={label_for['b']}\n", encoding="utf-8")

    leaks = 0
    for number, line in enumerate(transcript.splitlines(), 1):
        if LEAK_WORDS.search(line):
            leaks += 1
            print(f"possible leak at line {number}: {line[:100]}")
    print(f"Wrote {args.review_dir / 'transcript.md'} with {len(a_rounds)} round(s), {len(transcript.split())} words. Possible leaks: {leaks}. The key is saved; don't open it yet.")


if __name__ == "__main__":
    main()
