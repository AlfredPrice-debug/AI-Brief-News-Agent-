#!/usr/bin/env python3
"""
Build the Impact Makers one-page "AI Brief" PDF from a content JSON file.

Usage:
    python build/build_brief.py content/2026-07-24.json

What it does:
  1. Loads the day's content (title, date, AI Tips, AI News, sources).
  2. Renders template/brief_template.html with Poppins (the !m brand font, bundled in fonts/).
  3. Prints it to a one-page PDF via headless Chrome.
  4. Saves it to the output folder using an eye-catching, content-based filename:
        "<Title>_<M_D_YY>.pdf"

Config: edit OUTPUT_DIR below, or set env var AI_BRIEF_OUTPUT_DIR.
Chrome: auto-detected; override with env var CHROME_PATH.
"""
import json, os, re, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TEMPLATE = REPO / "template" / "brief_template.html"
FONT_DIR = REPO / "fonts"

# Default output folder (personal-development briefs). Override with env var.
OUTPUT_DIR = os.environ.get(
    "AI_BRIEF_OUTPUT_DIR",
    r"C:\Users\AlfredPrice\OneDrive - IM\Desktop\AI News & Tips",
)

CHROME_CANDIDATES = [
    os.environ.get("CHROME_PATH", ""),
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]


def find_chrome() -> str:
    for c in CHROME_CANDIDATES:
        if c and Path(c).is_file():
            return c
    sys.exit("ERROR: Chrome/Edge not found. Set CHROME_PATH env var.")


def esc(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def render_tips(tips: list) -> str:
    blocks = []
    for t in tips:
        full = " full" if t.get("prompt") or t.get("full") else ""
        steps = "\n".join(f'        <li>{s}</li>' for s in t.get("steps", []))
        prompt = ""
        if t.get("prompt"):
            prompt = f'\n      <div class="prompt"><b>Paste-ready:</b> {esc(t["prompt"])}</div>'
        blocks.append(
            f'    <div class="tip{full}">\n'
            f'      <h3>{t["heading"]}</h3>\n'
            f'      <ul class="steps">\n{steps}\n      </ul>{prompt}\n'
            f'    </div>'
        )
    return "\n".join(blocks)


def render_news(news: list) -> str:
    blocks = []
    for n in news:
        low = " low" if n.get("low") else ""
        blocks.append(
            f'  <div class="news-item{low}">\n'
            f'    <div class="n">{n["body"]}</div>\n'
            f'    <div class="mean"><span class="lbl">What it means for you:</span> {n["means"]}</div>\n'
            f'  </div>'
        )
    return "\n".join(blocks)


def safe_filename(title: str, slug: str) -> str:
    # Strip characters Windows forbids in filenames: \ / : * ? " < > |
    clean = re.sub(r'[\\/:*?"<>|]', "", title).strip()
    clean = re.sub(r"\s+", " ", clean)
    return f"{clean}_{slug}.pdf"


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: python build/build_brief.py <content.json>")
    content = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))

    font_url = FONT_DIR.as_uri()  # file:///C:/.../fonts
    html = TEMPLATE.read_text(encoding="utf-8")
    html = (html
            .replace("{{FONT_DIR}}", font_url)
            .replace("{{DATE}}", content["date_display"])
            .replace("{{TITLE}}", content["title"])
            .replace("{{TIPS_HTML}}", render_tips(content.get("tips", [])))
            .replace("{{NEWS_HTML}}", render_news(content.get("news", [])))
            .replace("{{SOURCES}}", content.get("sources", "")))

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tmp_html = REPO / "build" / "_render.html"
    tmp_html.write_text(html, encoding="utf-8")

    out_pdf = Path(OUTPUT_DIR) / safe_filename(content["title"], content["date_slug"])
    chrome = find_chrome()
    subprocess.run(
        [chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
         f"--print-to-pdf={out_pdf}", tmp_html.as_uri()],
        check=True, capture_output=True,
    )
    print(f"Saved: {out_pdf}")


if __name__ == "__main__":
    main()
