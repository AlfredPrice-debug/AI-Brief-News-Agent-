# AI Brief News Agent

A lightweight routine for **Claude Code** that turns the AI newsletters in your Outlook into a single, brand-styled **one-page PDF** — split into **AI Tips** (how-to) and **AI News** (the news + what it means for *you*). Built for the Impact Makers team as a personal-development habit.

![One page. Two sections. On brand.](docs/sample.png)

## What it produces

A one-page PDF in Impact Makers brand style (Poppins font; gold / black / dark-blue palette) containing:

- **AI Tips** — step-by-step ways to use AI better, pulled from that day's newsletters (with copy-paste prompts where useful).
- **AI News** — each item states the news, then *"What it means for you"* through a Product Manager / Consultant / AI Engineer lens.

Files are named for the day's content so they catch the eye in your folder, e.g.:
> `Picking the Right Gemini Models, Building Design Systems & Auditing Agents_7_24_26.pdf`

## How it works

```
Outlook folder (forwarded newsletters)
        │   Claude Code reads & classifies (AI Tips / AI News)
        ▼
content/<date>.json   ← the day's curated content
        │   build/build_brief.py  +  template/brief_template.html  +  fonts/Poppins
        ▼
One-page PDF  →  your "AI News & Tips" folder
```

The heavy lifting (reading mail, judging what matters, writing the "what it means for you" lines, and crafting the title) is done by Claude Code following **[INSTRUCTIONS.md](INSTRUCTIONS.md)**. The Python script just renders the curated content into the branded PDF.

## Setup

1. **Clone this repo.**
2. **Forward your AI newsletters into one Outlook folder.** In your personal Outlook, create a rule: *From = your newsletter senders → Forward to your work address*, and (optionally) file them into a dedicated folder like `Claude AI News Recap`.
   - ⚠️ Keep newsletters out of Junk — the agent never reads Junk for safety.
3. **Enable the Microsoft 365 connector** in Claude (read access to mail).
4. **Install Chrome** (or Edge) — used to render the PDF.
5. *(Optional)* `pip install pypdf` for the one-page sanity check.
6. **Set your output folder** — edit `OUTPUT_DIR` in `build/build_brief.py`, or set the `AI_BRIEF_OUTPUT_DIR` environment variable.

## Usage

Ask Claude Code:

> "Run the AI Brief routine for today."

Claude will follow `INSTRUCTIONS.md`: pull the day's newsletters, classify them, write today's `content/<date>.json`, and build the PDF. Or run the render step yourself once the JSON exists:

```bash
python build/build_brief.py content/2026-07-24.json
```

## Repo layout

| Path | Purpose |
|---|---|
| `INSTRUCTIONS.md` | The daily routine Claude Code follows (start here). |
| `template/brief_template.html` | The one-page layout + brand CSS (`{{placeholders}}`). |
| `build/build_brief.py` | Renders a content JSON → branded one-page PDF via headless Chrome. |
| `content/2026-07-24.json` | Example / template of the day's content. |
| `fonts/` | Poppins (SIL Open Font License) — the !m brand font, bundled for portability. |

## Customizing

- **Reader lens:** change "PM / Consultant / AI Engineer" in `INSTRUCTIONS.md` and the template subtitle to fit whoever's reading.
- **Sources:** add/remove newsletters in `INSTRUCTIONS.md` → CONFIG.
- **Styling:** all colors, spacing, and fonts live in `template/brief_template.html`.

## Brand & safety

- **Font:** Poppins only (the !m standard brand font). Aptos is reserved for email signatures.
- **Colors:** Gold `#D8A928` · Black `#262626` · Dark Blue `#264966` (+ supporting grays and tertiary green/terracotta/lilac).
- **Read-only mail:** the routine searches and reads mail; it never deletes, moves, or sends. It never reads the Junk folder.

## License

Code and templates: internal Impact Makers use. Poppins font: [SIL Open Font License 1.1](fonts/).
