#!/usr/bin/env python3
"""Build the three-tab comparison page from Markdown outputs and an HTML fragment."""
import argparse
import html
import re
from pathlib import Path

LIST_RE = re.compile(r"^(\s*)(-|\d+\.)\s+(.*)$")
STATUS = {"Pass": "ok", "Warning": "warn", "Fail": "bad", "Not measured": "none"}


def inline(text):
    codes = []

    def stash(match):
        codes.append("<code>" + html.escape(match.group(1), quote=False) + "</code>")
        return f"\x00{len(codes) - 1}\x00"

    text = re.sub(r"`([^`]+)`", stash, text)
    text = html.escape(text, quote=False)
    text = re.sub(r"\[([^\]]+)\]\(#[^)]*\)", r"\1", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\*\w])\*([^*\s][^*<]*?)\*(?![\*\w])", r"<em>\1</em>", text)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2" rel="noopener">\1</a>', text)
    text = re.sub(r"\[(M|O|E)\]", lambda m: f'<span class="ev ev-{m.group(1)}">{m.group(1)}</span>', text)
    return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], text)


def split_row(line):
    cells, current, in_code = [], "", False
    for char in line.strip().strip("|"):
        if char == "`":
            in_code = not in_code
        if char == "|" and not in_code:
            cells.append(current.strip())
            current = ""
        else:
            current += char
    cells.append(current.strip())
    return cells


def cell(text):
    bare = text.strip("*")
    if bare in STATUS:
        return f'<span class="st st-{STATUS[bare]}">{bare}</span>'
    return inline(text)


def table(rows):
    head, body = rows[0], rows[2:]
    parts = ['<div class="tw"><table><thead><tr>']
    parts += [f"<th>{inline(c)}</th>" for c in head]
    parts.append("</tr></thead><tbody>")
    for row in body:
        parts.append("<tr>" + "".join(f"<td>{cell(c)}</td>" for c in row) + "</tr>")
    parts.append("</tbody></table></div>")
    return "".join(parts)


def list_html(items):
    result, stack = [], []
    for indent, marker, text in items:
        tag = "ul" if marker == "-" else "ol"
        if not stack or indent > stack[-1][0]:
            result.append(f"<{tag}>")
            stack.append((indent, tag))
        else:
            while len(stack) > 1 and stack[-1][0] > indent:
                result.append(f"</li></{stack[-1][1]}>")
                stack.pop()
            result.append("</li>")
        result.append(f"<li>{inline(text)}")
    while stack:
        result.append(f"</li></{stack[-1][1]}>")
        stack.pop()
    return "".join(result)


def render(markdown):
    fences = []

    def stash_fence(match):
        fences.append("<pre><code>" + html.escape(match.group(1), quote=False) + "</code></pre>")
        return f"\x01{len(fences) - 1}\x01"

    markdown = re.sub(r"```[^\n]*\n(.*?)```", stash_fence, markdown, flags=re.S)
    lines, index, output = markdown.split("\n"), 0, []
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
        elif re.fullmatch(r"\x01\d+\x01", line.strip()):
            output.append(fences[int(line.strip().strip("\x01"))])
            index += 1
        elif line.strip() == "---":
            output.append("<hr>")
            index += 1
        elif line.startswith("#"):
            level = min(len(line) - len(line.lstrip("#")) + 1, 6)
            output.append(f"<h{level}>{inline(line.lstrip('#').strip())}</h{level}>")
            index += 1
        elif line.startswith("|"):
            rows = []
            while index < len(lines) and lines[index].startswith("|"):
                rows.append(split_row(lines[index]))
                index += 1
            output.append(table(rows))
        elif LIST_RE.match(line):
            items = []
            while index < len(lines) and LIST_RE.match(lines[index]):
                indent, marker, text = LIST_RE.match(lines[index]).groups()
                items.append((len(indent), "-" if marker == "-" else "1", text))
                index += 1
            output.append(list_html(items))
        else:
            paragraph = []
            while (
                index < len(lines)
                and lines[index].strip()
                and lines[index].strip() != "---"
                and not lines[index].startswith(("#", "|", "\x01"))
                and not LIST_RE.match(lines[index])
            ):
                paragraph.append(inline(lines[index].strip()))
                index += 1
            output.append("<p>" + "<br>".join(paragraph) + "</p>")
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--title", required=True)
    parser.add_argument("--heading", required=True)
    parser.add_argument("--lede", required=True)
    parser.add_argument("--eyebrow", required=True)
    parser.add_argument("--with", dest="with_skill", required=True, type=Path)
    parser.add_argument("--without", required=True, type=Path)
    parser.add_argument("--combined", required=True, type=Path)
    parser.add_argument("--review", required=True, type=Path)
    parser.add_argument("--label-with", default="Session 1")
    parser.add_argument("--label-without", default="Session 2")
    parser.add_argument("--note-with", default="with skill")
    parser.add_argument("--note-without", default="no skill")
    args = parser.parse_args()

    template = (Path(__file__).parent.parent / "assets" / "report_template.html").read_text(encoding="utf-8")
    values = {
        "TITLE": html.escape(args.title),
        "HEADING": html.escape(args.heading),
        "LEDE": html.escape(args.lede),
        "EYEBROW": html.escape(args.eyebrow),
        "LABEL_WITH": html.escape(args.label_with),
        "LABEL_WITHOUT": html.escape(args.label_without),
        "NOTE_WITH": html.escape(args.note_with),
        "NOTE_WITHOUT": html.escape(args.note_without),
        "COMBINED": args.combined.read_text(encoding="utf-8"),
        "REVIEW": render(args.review.read_text(encoding="utf-8")),
        "WITH": render(args.with_skill.read_text(encoding="utf-8")),
        "WITHOUT": render(args.without.read_text(encoding="utf-8")),
    }
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    args.out.write_text(template, encoding="utf-8")
    print(f"Wrote {args.out} ({len(template):,} characters)")


if __name__ == "__main__":
    main()
