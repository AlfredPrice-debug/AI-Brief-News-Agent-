#!/usr/bin/env python3
"""
Build the Impact Makers "AI Brief" PDF from a content JSON file.

Usage:
    python build/build_brief.py content/2026-07-28-run1.json

What it does:
  1. Loads the run's content (title, TL;DR, AI Tips, AI News, Beyond AI, sources).
  2. Loads brand colors/fonts from build/brand.json if present, else the bundled
     Impact Makers defaults (Poppins; gold/black/dark-blue).
  3. Renders template/brief_template.html (page 1: AI Tips + AI News;
     page 2: Beyond AI) and prints it to PDF via headless Chrome/Chromium.
  4. Saves it into this repo's briefs/ folder (or every folder configured via
     AI_BRIEF_OUTPUT_DIR, colon/semicolon-separated, if you want extra copies),
     using an eye-catching, content-based filename:
        "<Title>_<M_D_YY>_run<N>.pdf"

This runs as a cloud Routine — there's no local desktop to save a copy to, so
briefs/ (committed and pushed to GitHub) is the only delivery surface. Chrome:
auto-detected; override with CHROME_PATH.
"""
import json, os, re, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TEMPLATE = REPO / "template" / "brief_template.html"
FONT_DIR = REPO / "fonts"
BRAND_CACHE = REPO / "build" / "brand.json"

# Default output folder: this repo's briefs/, which gets committed and pushed.
# Override (or add extra copies) with AI_BRIEF_OUTPUT_DIR (colon/semicolon separated).
DEFAULT_OUTPUT_DIRS = [str(REPO / "briefs")]

# Bundled Impact Makers brand defaults, used when build/brand.json is absent
# or the brand folder couldn't be read (see INSTRUCTIONS.md > Brand styling).
BRAND_DEFAULTS = {
    "primary": "#D8A928",
    "secondary": "#264966",
    "accent": "#C76D4B",
    "black": "#262626",
    "light_gray": "#F2F2F2",
    "dark_gray": "#BFBFBF",
    "heading_font": "Poppins",
    "body_font": "Poppins",
    "logo_path": "",
}

CHROME_CANDIDATES = [
    os.environ.get("CHROME_PATH", ""),
    # Linux / cloud run environment
    shutil.which("google-chrome") or "",
    shutil.which("google-chrome-stable") or "",
    shutil.which("chromium") or "",
    shutil.which("chromium-browser") or "",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    # Windows (only relevant if this is ever run locally instead of in the cloud)
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
    # Playwright-bundled Chromium (present in some cloud run environments)
    for base in (Path("/opt/pw-browsers"),):
        if base.is_dir():
            for candidate in sorted(base.glob("chromium-*/chrome-linux/chrome")):
                return str(candidate)
    sys.exit("ERROR: Chrome/Chromium not found. Set CHROME_PATH env var.")


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def load_brand() -> dict:
    """Brand values are extracted from the Impact Makers brand folder at run time
    by Claude Code and cached to build/brand.json (see build/brand.example.json).
    Falls back to BRAND_DEFAULTS if the cache is missing or unreadable."""
    brand = dict(BRAND_DEFAULTS)
    if BRAND_CACHE.is_file():
        try:
            brand.update(json.loads(BRAND_CACHE.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            print("WARNING: build/brand.json unreadable, using bundled defaults.", file=sys.stderr)
    return brand


def logo_html(brand: dict) -> str:
    logo_path = brand.get("logo_path") or ""
    if logo_path and Path(logo_path).is_file():
        return f'<img class="logo" src="{Path(logo_path).as_uri()}" alt="Impact Makers">'
    # Fallback: text wordmark
    return ('<div class="wordmark"><span class="bang">!</span><span class="m">m</span>'
            '&nbsp;<span class="i">impact</span><span class="m">makers</span></div>')


def render_tldr(items: list) -> str:
    return "\n".join(f"        <li>{esc(i) if isinstance(i, str) else i}</li>" for i in items)


def render_tips(tips: list) -> str:
    blocks = []
    for t in tips:
        full = " full" if t.get("prompt") or t.get("full") else ""
        steps = "\n".join(f'        <li>{s}</li>' for s in t.get("steps", []))
        prompt = ""
        if t.get("prompt"):
            prompt = f'\n      <div class="prompt"><b>Paste-ready:</b> {esc(t["prompt"])}</div>'
        src = f'\n      <div class="src">Source: {t["source"]}</div>' if t.get("source") else ""
        blocks.append(
            f'    <div class="tip{full}">\n'
            f'      <h3>{t["heading"]}</h3>\n'
            f'      <ul class="steps">\n{steps}\n      </ul>{prompt}{src}\n'
            f'    </div>'
        )
    return "\n".join(blocks)


def render_news(news: list) -> str:
    blocks = []
    for n in news:
        low = " low" if n.get("low") else ""
        src = f'\n    <div class="src">Source: {n["source"]}</div>' if n.get("source") else ""
        blocks.append(
            f'  <div class="news-item{low}">\n'
            f'    <div class="n">{n["body"]}</div>\n'
            f'    <div class="mean"><span class="lbl">What it means for you:</span> {n["means"]}</div>{src}\n'
            f'  </div>'
        )
    return "\n".join(blocks)


def render_beyond(items: list) -> str:
    blocks = []
    for b in items:
        src = f'\n    <div class="src">Source: {b["source"]}</div>' if b.get("source") else ""
        blocks.append(
            f'  <div class="beyond-item">\n'
            f'    <div class="n">{b["body"]}</div>\n'
            f'    <div class="angle"><span class="lbl">PM angle:</span> {b["angle"]}</div>\n'
            f'    <div class="starter"><span class="lbl">Conversation starter:</span> {b["starter"]}</div>{src}\n'
            f'  </div>'
        )
    return "\n".join(blocks)


def run_label(content: dict) -> str:
    run = content.get("run")
    run_time = content.get("runTime", "")
    time_part = ""
    if run_time:
        try:
            time_part = datetime.fromisoformat(run_time).strftime("%-I:%M %p ET")
        except ValueError:
            time_part = ""
    if run and time_part:
        return f"Run {run} &middot; {time_part}"
    if run:
        return f"Run {run}"
    return ""


def safe_filename(title: str, slug: str, run) -> str:
    # Strip characters Windows forbids in filenames: \ / : * ? " < > |
    clean = re.sub(r'[\\/:*?"<>|]', "", title).strip()
    clean = re.sub(r"\s+", " ", clean)
    run_part = f"_run{run}" if run else ""
    return f"{clean}_{slug}{run_part}.pdf"


def output_dirs() -> list:
    env = os.environ.get("AI_BRIEF_OUTPUT_DIR", "")
    if env:
        return [p for p in re.split(r"[:;](?!\\)", env) if p]
    return list(DEFAULT_OUTPUT_DIRS)


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: python build/build_brief.py <content.json>")
    content = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    brand = load_brand()

    font_url = FONT_DIR.as_uri()  # file:///C:/.../fonts
    html = TEMPLATE.read_text(encoding="utf-8")
    html = (html
            .replace("{{FONT_DIR}}", font_url)
            .replace("{{DATE}}", content["date_display"])
            .replace("{{RUN_LABEL}}", run_label(content))
            .replace("{{TITLE}}", content["title"])
            .replace("{{TLDR_HTML}}", render_tldr(content.get("tldr", [])))
            .replace("{{TIPS_HTML}}", render_tips(content.get("tips", [])))
            .replace("{{NEWS_HTML}}", render_news(content.get("news", [])))
            .replace("{{BEYOND_HTML}}", render_beyond(content.get("beyond_ai", [])))
            .replace("{{SOURCES}}", content.get("sources", ""))
            .replace("{{LOGO_HTML}}", logo_html(brand))
            .replace("{{BRAND_PRIMARY}}", brand["primary"])
            .replace("{{BRAND_SECONDARY}}", brand["secondary"])
            .replace("{{BRAND_ACCENT}}", brand["accent"])
            .replace("{{BRAND_BLACK}}", brand["black"])
            .replace("{{BRAND_LGRAY}}", brand["light_gray"])
            .replace("{{BRAND_DGRAY}}", brand["dark_gray"])
            .replace("{{HEADING_FONT}}", brand["heading_font"])
            .replace("{{BODY_FONT}}", brand["body_font"]))

    tmp_html = REPO / "build" / "_render.html"
    tmp_html.write_text(html, encoding="utf-8")

    filename = safe_filename(content["title"], content["date_slug"], content.get("run"))
    chrome = find_chrome()

    dirs = output_dirs()
    existing = [d for d in dirs if Path(d).is_dir()]
    targets = existing if existing else [dirs[-1]]
    if not existing:
        os.makedirs(targets[0], exist_ok=True)
        print(f"NOTE: no configured output folder existed; created {targets[0]}")

    # --no-sandbox is required when this runs as root in a cloud container (the
    # common case for the scheduled Routine); harmless otherwise. Safe here since
    # we're only rendering a static file:// page we generated ourselves, not
    # arbitrary/untrusted web content.
    for d in targets:
        os.makedirs(d, exist_ok=True)
        out_pdf = Path(d) / filename
        subprocess.run(
            [chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
             f"--print-to-pdf={out_pdf}", tmp_html.as_uri()],
            check=True, capture_output=True,
        )
        print(f"Saved: {out_pdf}")


if __name__ == "__main__":
    main()
