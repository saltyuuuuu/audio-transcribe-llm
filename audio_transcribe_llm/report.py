from __future__ import annotations

import argparse
import hashlib
import html
import os
import re
import shutil
import subprocess
from pathlib import Path

from .prompts import REPORT_FOOTER


def has_failed_segments(raw_transcript: str) -> bool:
    failed_markers = ["[API错误", "[处理超时]", "**失败**: "]
    if any(marker in raw_transcript for marker in failed_markers):
        match = re.search(r"\*\*成功\*\*:\s*(\d+)/(\d+)", raw_transcript)
        if match and match.group(1) != match.group(2):
            return True
    return False


def build_markdown_report(
    title: str,
    model_line: str,
    duration: str,
    raw_transcript: str,
    corrected: str,
    summary: str,
    source_path: str,
) -> str:
    failure_note = ""
    if has_failed_segments(raw_transcript):
        failure_note = (
            "\n\n> **转写完整性警告**：原始转写中存在失败分段。"
            "报告保留失败标记，不用上下文推断替代未成功听取的音频。"
        )
    return f"""# {title} - 语音转写报告

**使用模型**：{model_line}
**音频时长**：{duration}
**音频来源**：`{source_path}`
**说话人**：由转写模型和文本模型根据音色、称呼与上下文推断

---

## 目录

- [一、原始转写](#raw-transcript)
- [二、修正版](#corrected-transcript)
- [三、摘要总结](#summary)

---

<a id="raw-transcript"></a>

# 一、原始转写

> 以下内容为模型原始输出，仅做排版整理，未修改任何文字。{failure_note}

{raw_transcript}

---

<a id="corrected-transcript"></a>

# 二、修正版

> 以下内容经过修正：纠正明显识别错误、同音字/近音词、专业术语和口误。保留说话人的原意与表达风格。

{corrected}

---

<a id="summary"></a>

# 三、摘要总结

{summary}

{REPORT_FOOTER}
"""


MAIN_SECTION_IDS = {
    "一、原始转写": "raw-transcript",
    "二、修正版": "corrected-transcript",
    "三、摘要总结": "summary",
}

REPORT_META_RE = re.compile(r"^\*\*(?P<key>[^*]{1,32})\*\*\s*[：:]\s*(?P<value>.*)$")
REPORT_META_KEYS = {"转写时间", "使用模型", "音频时长", "音频来源", "说话人"}


def inline_md(text: str) -> str:
    placeholders: dict[str, str] = {}

    def keep_code(match: re.Match[str]) -> str:
        key = f"@@CODE{len(placeholders)}@@"
        placeholders[key] = f"<code>{html.escape(match.group(1))}</code>"
        return key

    escaped = re.sub(r"`([^`]+)`", keep_code, html.escape(text))
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">{m.group(1)}</a>',
        escaped,
    )
    for key, value in placeholders.items():
        escaped = escaped.replace(key, value)
    return escaped


def slugify(text: str, used: set[str]) -> str:
    clean = re.sub(r"<[^>]+>", "", text).strip()
    base = MAIN_SECTION_IDS.get(clean)
    if not base:
        base = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", clean, flags=re.UNICODE)
        base = re.sub(r"-+", "-", base).strip("-").lower() or "section"
    candidate = base
    suffix = 2
    while candidate in used:
        candidate = f"{base}-{suffix}"
        suffix += 1
    used.add(candidate)
    return candidate


def is_table_separator(line: str) -> bool:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell or "") for cell in cells)


def markdown_to_html_body(markdown: str) -> str:
    used: set[str] = set()
    out: list[str] = []
    lines = markdown.splitlines()
    i = 0
    in_code = False
    code_lang = ""
    code_lines: list[str] = []
    in_list: str | None = None

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            out.append(f"</{in_list}>")
            in_list = None

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```"):
            if in_code:
                out.append(
                    f'<pre><code class="language-{html.escape(code_lang)}">'
                    + html.escape("\n".join(code_lines))
                    + "</code></pre>"
                )
                in_code = False
                code_lang = ""
                code_lines = []
            else:
                close_list()
                in_code = True
                code_lang = stripped[3:].strip()
                code_lines = []
            i += 1
            continue

        if in_code:
            code_lines.append(line)
            i += 1
            continue

        if not stripped:
            close_list()
            i += 1
            continue

        if re.fullmatch(r'<a\s+id="[^"]+"></a>', stripped):
            close_list()
            out.append(stripped)
            i += 1
            continue

        meta = REPORT_META_RE.match(stripped)
        if meta and meta.group("key").strip() in REPORT_META_KEYS:
            close_list()
            out.append('<dl class="report-meta">')
            while i < len(lines):
                match = REPORT_META_RE.match(lines[i].strip())
                if not match or match.group("key").strip() not in REPORT_META_KEYS:
                    break
                out.append(f"<dt>{html.escape(match.group('key').strip())}</dt>")
                out.append(f"<dd>{inline_md(match.group('value').strip())}</dd>")
                i += 1
            out.append("</dl>")
            continue

        if i + 1 < len(lines) and "|" in line and is_table_separator(lines[i + 1]):
            close_list()
            table_lines = [line, lines[i + 1]]
            i += 2
            while i < len(lines) and "|" in lines[i].strip() and lines[i].strip():
                table_lines.append(lines[i])
                i += 1
            rows = [[cell.strip() for cell in row.strip().strip("|").split("|")] for row in table_lines]
            out.append("<table><thead><tr>")
            out.extend(f"<th>{inline_md(cell)}</th>" for cell in rows[0])
            out.append("</tr></thead><tbody>")
            for row in rows[2:]:
                out.append("<tr>")
                out.extend(f"<td>{inline_md(cell)}</td>" for cell in row)
                out.append("</tr>")
            out.append("</tbody></table>")
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading:
            close_list()
            level = len(heading.group(1))
            text = heading.group(2).strip()
            section_id = slugify(text, used)
            out.append(f'<h{level} id="{section_id}">{inline_md(text)}</h{level}>')
            i += 1
            continue

        if re.fullmatch(r"-{3,}|\*{3,}|_{3,}", stripped):
            close_list()
            out.append("<hr>")
            i += 1
            continue

        quote = re.match(r"^>\s?(.*)$", stripped)
        if quote:
            close_list()
            parts = [quote.group(1)]
            i += 1
            while i < len(lines):
                next_quote = re.match(r"^>\s?(.*)$", lines[i].strip())
                if not next_quote:
                    break
                parts.append(next_quote.group(1))
                i += 1
            out.append("<blockquote>" + "".join(f"<p>{inline_md(p)}</p>" for p in parts if p.strip()) + "</blockquote>")
            continue

        unordered = re.match(r"^[-*]\s+(.+)$", stripped)
        ordered = re.match(r"^\d+\.\s+(.+)$", stripped)
        if unordered or ordered:
            tag = "ul" if unordered else "ol"
            if in_list != tag:
                close_list()
                out.append(f"<{tag}>")
                in_list = tag
            out.append(f"<li>{inline_md((unordered or ordered).group(1))}</li>")
            i += 1
            continue

        close_list()
        paragraph = [stripped]
        i += 1
        while i < len(lines):
            next_line = lines[i].strip()
            if (
                not next_line
                or next_line.startswith("```")
                or re.match(r"^(#{1,6})\s+", next_line)
                or re.match(r"^>\s?", next_line)
                or re.match(r"^[-*]\s+", next_line)
                or re.match(r"^\d+\.\s+", next_line)
                or re.fullmatch(r"-{3,}|\*{3,}|_{3,}", next_line)
                or (i + 1 < len(lines) and "|" in next_line and is_table_separator(lines[i + 1]))
            ):
                break
            paragraph.append(next_line)
            i += 1
        out.append(f"<p>{inline_md(' '.join(paragraph))}</p>")

    close_list()
    if in_code:
        out.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
    return "\n".join(out)


def build_html(markdown: str, title: str) -> str:
    body = markdown_to_html_body(markdown)
    css = """
    :root { color: #182018; background: #f7f5ef; font-family: "Microsoft YaHei", "Noto Sans CJK SC", sans-serif; }
    body { margin: 0; background: #f7f5ef; }
    main { max-width: 980px; margin: 0 auto; min-height: 100vh; padding: 48px 56px 72px; background: white; box-shadow: 0 20px 70px rgba(0,0,0,.08); }
    h1 { font-size: 30px; border-bottom: 3px solid #4f8b61; padding-bottom: 10px; margin-top: 40px; color: #15391d; }
    h2 { font-size: 22px; margin-top: 32px; border-left: 6px solid #c08a36; padding-left: 12px; color: #15391d; }
    h3 { font-size: 18px; margin-top: 24px; color: #243c24; }
    p, li { line-height: 1.82; font-size: 15px; }
    a { color: #276940; text-decoration: none; border-bottom: 1px solid rgba(39,105,64,.25); }
    blockquote { margin: 18px 0; padding: 12px 18px; border-left: 5px solid #8fb78a; background: #f3f8f1; color: #364936; }
    .report-meta { display: grid; grid-template-columns: max-content minmax(0, 1fr); gap: 8px 14px; padding: 16px 18px; border: 1px solid #d8ddd1; border-radius: 10px; background: #fffaf0; }
    .report-meta dt { font-weight: 800; color: #284f2f; }
    .report-meta dd { margin: 0; overflow-wrap: anywhere; }
    table { border-collapse: collapse; width: 100%; margin: 18px 0; font-size: 13px; }
    th, td { border: 1px solid #d8ddd1; padding: 8px 10px; vertical-align: top; }
    th { background: #edf4e9; }
    pre { padding: 16px; overflow-x: auto; background: #172018; color: #f8f3e8; border-radius: 8px; }
    code { font-family: Consolas, monospace; background: #f1eadc; border-radius: 4px; padding: 1px 5px; }
    pre code { background: transparent; color: inherit; padding: 0; }
    @page { size: A4; margin: 18mm 16mm; }
    @media print { main { box-shadow: none; padding: 0; max-width: none; } body { background: white; } }
    """
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>{css}</style>
</head>
<body>
  <main>{body}</main>
</body>
</html>
"""


def find_browser() -> str | None:
    candidates = [
        os.environ.get("CHROME_PATH"),
        os.environ.get("EDGE_PATH"),
        shutil.which("msedge"),
        shutil.which("msedge.exe"),
        shutil.which("chrome"),
        shutil.which("chrome.exe"),
        shutil.which("chromium"),
        shutil.which("chromium.exe"),
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(candidate)
    return None


def export_html_pdf(md_path: str | Path, no_pdf: bool = False) -> tuple[Path, Path | None]:
    md = Path(md_path)
    html_path = md.with_suffix(".html")
    pdf_path = md.with_suffix(".pdf")
    markdown = md.read_text(encoding="utf-8")
    html_path.write_text(build_html(markdown, md.stem), encoding="utf-8")
    if no_pdf:
        return html_path, None
    browser = find_browser()
    if not browser:
        raise RuntimeError("No Chromium browser found. Install Edge/Chrome or set CHROME_PATH/EDGE_PATH.")
    proc = subprocess.run(
        [
            browser,
            "--headless",
            "--disable-gpu",
            "--disable-extensions",
            "--no-first-run",
            f"--print-to-pdf={pdf_path}",
            str(html_path.resolve().as_uri()),
        ],
        capture_output=True,
        text=True,
        timeout=180,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout or "PDF export failed")
    return html_path, pdf_path


def md_to_pdf_main() -> int:
    parser = argparse.ArgumentParser(description="Render audio-transcribe Markdown report to HTML/PDF.")
    parser.add_argument("markdown")
    parser.add_argument("--no-pdf", action="store_true")
    args = parser.parse_args()
    html_path, pdf_path = export_html_pdf(args.markdown, no_pdf=args.no_pdf)
    print(f"HTML: {html_path}")
    if pdf_path:
        print(f"PDF: {pdf_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(md_to_pdf_main())

