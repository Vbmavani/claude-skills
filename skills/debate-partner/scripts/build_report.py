#!/usr/bin/env python3
"""Fill the debate report template from saved rounds and the judge's JSON result."""
import argparse
import html
import json
import re
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "report_template.html"
ROUNDS = (("opening", "Opening"), ("cross", "Cross-examination"), ("closing", "Closing"))
CRITERIA = ("evidence", "reasoning", "honesty")
TIE_GAP = 2
TIE_CONFIDENCE = 60


def esc(value):
    return html.escape(str(value), quote=True)


def inline(text):
    """Escape text, then restore bold and plain links."""
    text = esc(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return re.sub(r"(https?://[^\s<)]+)", r'<a href="\1">\1</a>', text)


def to_html(markdown):
    """Render the small Markdown subset agents write: headings, bullets, paragraphs."""
    out, bullets = [], []

    def flush():
        if bullets:
            out.append("<ul>" + "".join(f"<li>{b}</li>" for b in bullets) + "</ul>")
            bullets.clear()

    for raw in markdown.splitlines():
        line = raw.strip()
        if re.match(r"^[-*] ", line):
            bullets.append(inline(line[2:]))
            continue
        flush()
        if line.startswith("#"):
            out.append(f"<h4>{inline(line.lstrip('#').strip())}</h4>")
        elif line:
            out.append(f"<p>{inline(line)}</p>")
    flush()
    return "\n".join(out)


def bullet_list(items):
    return "<ul>" + "".join(f"<li>{inline(item)}</li>" for item in items) + "</ul>"


def score_rows(judge, names):
    rows = []
    for side in ("a", "b"):
        scores = judge["scores"][side]
        cells = "".join(f'<td class="score">{int(scores[c])}</td>' for c in CRITERIA)
        total = sum(int(scores[c]) for c in CRITERIA)
        rows.append(f'<tr><td class="{side}-text"><strong>{esc(names[side])}</strong></td>{cells}'
                    f'<td class="score">{total}</td><td>{inline(scores["reason"])}</td></tr>')
    return "\n".join(rows)


def round_blocks(rounds_dir, names):
    blocks = []
    for key, heading in ROUNDS:
        a_file, b_file = rounds_dir / f"a-{key}.md", rounds_dir / f"b-{key}.md"
        if not (a_file.exists() and b_file.exists()):
            continue
        pair = "".join(
            f'<div class="side {side}"><span class="who">{esc(names[side])}</span>{to_html(path.read_text(encoding="utf-8"))}</div>'
            for side, path in (("a", a_file), ("b", b_file)))
        blocks.append(f'<div class="round"><h3>{heading}</h3><div class="pair">{pair}</div></div>')
    return "\n".join(blocks)


def optional_section(heading, path):
    if not path:
        return ""
    return f'<section><h2>{heading}</h2><div class="panel">{to_html(path.read_text(encoding="utf-8"))}</div></section>'


def unblind(judge, key_file):
    """Swap the judge's Side 1 and Side 2 labels for a and b using the saved key."""
    pairs = dict(line.split("=", 1) for line in key_file.read_text(encoding="utf-8").split("\n") if line)
    side_for = {pairs[side].lower().replace(" ", "_"): side for side in ("a", "b")}
    judge = dict(judge)
    judge["scores"] = {side_for[label]: scores for label, scores in judge["scores"].items()}
    judge["winner"] = side_for.get(judge["winner"], "tie")
    return judge


def verdict_label(judge, names):
    """Apply the tie rule, so a thin gap can't be reported as a win."""
    totals = {s: sum(int(judge["scores"][s][c]) for c in CRITERIA) for s in ("a", "b")}
    winner = judge["winner"]
    if winner == "tie" or abs(totals["a"] - totals["b"]) < TIE_GAP or int(judge["confidence"]) < TIE_CONFIDENCE:
        return f"Tie on the scores ({totals['a']} to {totals['b']})"
    return f"{names[winner]} leads, {totals[winner]} to {totals['a' if winner == 'b' else 'b']}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds-dir", required=True, type=Path)
    parser.add_argument("--judge", required=True, type=Path)
    parser.add_argument("--key-file", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--title", required=True)
    parser.add_argument("--question", required=True)
    parser.add_argument("--name-a", required=True, help="short name for side a's position")
    parser.add_argument("--name-b", required=True, help="short name for side b's position")
    parser.add_argument("--coaching", type=Path, help="optional Markdown coaching notes for a debate against the user")
    parser.add_argument("--third-voice", type=Path, help="optional Markdown from the deep-mode third voice")
    parser.add_argument("--note", default="", help="anything that went wrong or limits the result")
    args = parser.parse_args()

    judge = unblind(json.loads(args.judge.read_text(encoding="utf-8")), args.key_file)
    names = {"a": args.name_a, "b": args.name_b}
    coaching = optional_section("Coaching notes", args.coaching)
    third_voice = optional_section("An option neither side raised", args.third_voice)
    note = f'<p class="note">{inline(args.note)}</p>' if args.note else ""

    values = {
        "TITLE": esc(args.title),
        "QUESTION": esc(args.question),
        "VERDICT_LABEL": esc(verdict_label(judge, names)),
        "CONFIDENCE": esc(judge["confidence"]),
        "VERDICT": inline(judge["verdict"]),
        "REMAINING_DISAGREEMENT": inline(judge["remaining_disagreement"]),
        "SCORE_ROWS": score_rows(judge, names),
        "NOTE": note,
        "ROUNDS": round_blocks(args.rounds_dir, names),
        "CHANGE_VERDICT": bullet_list(judge["what_would_change_it"]),
        "NEXT_STEP": inline(judge["next_step"]),
        "SOURCES_CHECKED": bullet_list(judge["source_check"]["checked"]),
        "SOURCES_UNCHECKED": bullet_list(judge["source_check"]["unchecked"] or ["None"]),
        "COACHING": coaching,
        "THIRD_VOICE": third_voice,
    }
    page = TEMPLATE.read_text(encoding="utf-8")
    for key, value in values.items():
        page = page.replace(f"{{{{{key}}}}}", value)
    left = re.findall(r"\{\{[A-Z_]+\}\}", page)
    if left:
        parser.error(f"unfilled placeholders: {left}")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(page, encoding="utf-8")
    print(f"Wrote {args.out}. Verdict label: {verdict_label(judge, names)}")


if __name__ == "__main__":
    main()
