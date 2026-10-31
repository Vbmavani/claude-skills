#!/usr/bin/env python3
"""Copy two outputs into a review folder under random blind labels."""
import argparse
import random
import re
import shutil
from pathlib import Path

LEAK_WORDS = re.compile(r"\b(skills?|plugins?|session[ -]?[12]|with-skill|no-skill|without skill)\b", re.I)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brief", required=True, type=Path)
    parser.add_argument("--with", dest="with_skill", required=True, type=Path)
    parser.add_argument("--without", required=True, type=Path)
    parser.add_argument("--review-dir", required=True, type=Path)
    parser.add_argument("--key-file", required=True, type=Path)
    args = parser.parse_args()

    if args.review_dir.resolve() in args.key_file.resolve().parents:
        parser.error("--key-file must be outside --review-dir")
    for name in ("set-x.md", "set-y.md"):
        if (args.review_dir / name).exists():
            parser.error(f"{name} already exists in {args.review_dir}")

    args.review_dir.mkdir(parents=True, exist_ok=True)
    labels = ["set-x.md", "set-y.md"]
    random.SystemRandom().shuffle(labels)

    shutil.copy(args.brief, args.review_dir / "brief.md")
    shutil.copy(args.with_skill, args.review_dir / labels[0])
    shutil.copy(args.without, args.review_dir / labels[1])
    args.key_file.parent.mkdir(parents=True, exist_ok=True)
    args.key_file.write_text(f"with_skill={labels[0]}\nwithout_skill={labels[1]}\n", encoding="utf-8")

    leaks = 0
    for label in labels:
        text = (args.review_dir / label).read_text(encoding="utf-8")
        for number, line in enumerate(text.splitlines(), 1):
            if LEAK_WORDS.search(line):
                leaks += 1
                print(f"possible leak in {label}:{number}: {line[:100]}")
    print(f"Blinded into {args.review_dir}. Possible leaks: {leaks}. The key is saved; don't open it yet.")


if __name__ == "__main__":
    main()
