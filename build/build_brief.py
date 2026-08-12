#!/usr/bin/env python3
"""
Build the Impact Makers "AI Brief" PDF from a content JSON file.

Usage:
    python build/build_brief.py content/2026-07-28-run1.json

What it does:
  1. Loads the run's content (title, TL;DR, AI Tips, AI News, Beyond AI, sources).
  2. Loads brand colors/fonts from build/brand.json if present, else the bundled
     Impact Makers defaults (Poppins; gold/black/dark-blue).
  3. Renders template/brief_template.html and prints it to PDF via headless Chrome.
     Sheet 1: dark cover band (logo, title, TL;DR hook) + AI News.
     Sheet 2: AI Tips.  Sheet 3: Beyond AI.  Empty sheets are dropped and the
     remaining ones are renumbered, so a light run is 2 pages and a full run is 3.
  4. Saves it into this repo's briefs/ folder (or every folder configured via
     AI_BRIEF_OUTPUT_DIR, colon/semicolon-separated, if you want extra copies),
     using an eye-catching, content-based filename: "<Title>_<M_D_YY>_run<N>.pdf"

Content schema is unchanged from v2 — news/beyond items still carry a single
`body` string whose leading <b>…</b> is the headline; the builder splits on that
closing tag to typeset the headline as the card's lead line.

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
    "logo_path": "",        # full-colour lockup (kept for backwards compatibility)
    "logo_white_path": "",  # white-knockout lockup — used on the dark cover band
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
    """The masthead now sits on the black band, so prefer the white-knockout
    lockup; fall back to the full-colour file, then to a white text wordmark."""
    for key in ("logo_white_path", "logo_path"):
        p = brand.get(key) or ""
        if p and Path(p).is_file():
            return f'<img class="logo" src="{Path(p).as_uri()}" alt="Impact Makers">'
    return ('<div class="wordmark"><span>!</span><span class="g">m</span>'
            '&nbsp;<span>impact</span><span class="g">makers</span></div>')


def img_src(path_or_url: str) -> str:
    """Content JSON may point at a local file (relative to the repo root) or an
    http(s) URL. Local files become file:// URIs so headless Chrome can read them."""
    if not path_or_url:
        return ""
    if re.match(r"^(https?:|data:|file:)", path_or_url):
        return path_or_url
    p = Path(path_or_url)
    if not p.is_absolute():
        p = REPO / p
    return p.as_uri() if p.is_file() else ""


def card_art(item: dict) -> str:
    """Optional per-item lead art. Absent `image` -> nothing renders and the card
    keeps its current layout, so old content files are unaffected."""
    src = img_src(item.get("image", ""))
    if not src:
        return ""
    alt = esc(item.get("image_alt", ""))
    return f'\n            <div class="cardart"><img src="{src}" alt="{alt}"></div>'


def split_lead(body: str) -> tuple:
    """'<b>Headline.</b> Rest of it.' -> ('Headline.', 'Rest of it.')"""
    m = re.match(r"\s*<b>(.*?)</b>\s*(.*)$", body, flags=re.DOTALL)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return body.strip(), ""


def render_tldr(items: list) -> str:
    rows = []
    for i, item in enumerate(items, 1):
        txt = esc(item) if isinstance(item, str) else item
        rows.append(f'        <div class="row"><div class="num">{i}</div>'
                    f'<div class="txt">{txt}</div></div>')
    return "\n".join(rows)


def render_tips(tips: list) -> str:
    blocks = []
    for i, t in enumerate(tips, 1):
        steps = "\n".join(
            f'            <div class="row"><div class="num">{j}.</div>'
            f'<div class="txt">{s}</div></div>'
            for j, s in enumerate(t.get("steps", []), 1)
        )
        prompt = ""
        if t.get("prompt"):
            prompt = ('\n          <div class="prompt"><div class="lbl">Paste-ready prompt</div>'
                      f'<div class="txt">{esc(t["prompt"])}</div></div>')
        src = f'\n          <div class="src">{t["source"]}</div>' if t.get("source") else ""
        blocks.append(
            f'        <div class="card tip">\n'
            f'          <div class="disc">{i}</div>\n'
            f'          <div>{card_art(t)}\n'
            f'            <div class="lead">{t["heading"]}</div>\n'
            f'            <div class="steps">\n{steps}\n            </div>{prompt}{src}\n'
            f'          </div>\n'
            f'        </div>'
        )
    return "\n".join(blocks)


def render_news(news: list) -> str:
    blocks = []
    for i, n in enumerate(news, 1):
        lead, rest = split_lead(n["body"])
        rest_html = f'\n            <div class="rest">{rest}</div>' if rest else ""
        src = f'\n            <div class="src">{n["source"]}</div>' if n.get("source") else ""
        blocks.append(
            f'        <div class="card news">\n'
            f'          <div class="disc">{i}</div>\n'
            f'          <div>\n'
            f'            <div class="lead">{lead}</div>{rest_html}\n'
            f'            <div class="inset means"><div class="lbl">What it means for you</div>'
            f'<div class="txt">{n["means"]}</div></div>{src}\n'
            f'          </div>\n'
            f'        </div>'
        )
    return "\n".join(blocks)


def render_beyond(items: list) -> str:
    blocks = []
    for i, b in enumerate(items, 1):
        lead, rest = split_lead(b["body"])
        rest_html = f'\n            <div class="rest">{rest}</div>' if rest else ""
        src = f'\n            <div class="src">{b["source"]}</div>' if b.get("source") else ""
        blocks.append(
            f'        <div class="card beyond">\n'
            f'          <div class="disc">{i}</div>\n'
            f'          <div>{card_art(b)}\n'
            f'            <div class="lead">{lead}</div>{rest_html}\n'
            f'            <div class="inset angle"><div class="lbl">PM angle</div>'
            f'<div class="txt">{b["angle"]}</div></div>\n'
            f'            <div class="starter"><div class="q">&ldquo;</div>'
            f'<div class="txt">{b["starter"]}</div></div>{src}\n'
            f'          </div>\n'
            f'        </div>'
        )
    return "\n".join(blocks)


def drop_sheet(html: str, n: int) -> str:
    return re.sub(rf"\s*<!--SHEET{n}_START-->.*?<!--SHEET{n}_END-->\s*", "\n", html, flags=re.DOTALL)


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

    font_url = FONT_DIR.as_uri()
    html = TEMPLATE.read_text(encoding="utf-8")

    # Sheet 1 always exists (cover + news). Sheets 2 and 3 are dropped when the
    # run has no tips / no Beyond AI, and the survivors are renumbered so the
    # footer reads "1 / 2" instead of "1 / 3".
    has_tips = bool(content.get("tips"))
    has_beyond = bool(content.get("beyond_ai"))
    if not has_tips:
        html = drop_sheet(html, 2)
    if not has_beyond:
        html = drop_sheet(html, 3)
    total = 1 + int(has_tips) + int(has_beyond)
    page_no = 1
    for key, present in (("PN1", True), ("PN2", has_tips), ("PN3", has_beyond)):
        html = html.replace("{{" + key + "}}", str(page_no) if present else "")
        if present:
            page_no += 1

    # Optional lead-story art on the cover band. No hero_image -> the band
    # collapses to a single full-width headline column, exactly as before.
    hero = img_src(content.get("hero_image", ""))
    hero_alt = esc(content.get("hero_image_alt", ""))
    html = (html
            .replace("{{ART_CLASS}}", "" if hero else " noart")
            .replace("{{HERO_HTML}}", f'<img src="{hero}" alt="{hero_alt}">' if hero else ""))

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
            .replace("{{PTOTAL}}", str(total))
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
