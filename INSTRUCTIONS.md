# AI Brief — Daily Routine (Instructions for Claude Code)

This is the step-by-step routine Claude Code follows to produce the one-page **Impact Makers AI Brief** PDF each day. Follow it top to bottom.

> **Goal:** Turn the AI newsletters sitting in an Outlook folder into a single, brand-styled, one-page PDF split into **AI Tips** (how-to) and **AI News** (news + "what it means for you"), saved with an eye-catching, content-based filename.

---

## 0. Prerequisites (one-time)

- **Microsoft 365 / Outlook connector** enabled in Claude (read access to mail).
- A dedicated Outlook mail folder that AI newsletters are forwarded into. See `CONFIG` below.
- **Google Chrome** (or Edge) installed — used to render the PDF.
- **Python 3** with `pypdf` (`pip install pypdf`) — only needed if you want the page-count sanity check.
- This repo cloned locally. Fonts are bundled in `fonts/` (Poppins — the !m brand font).

## CONFIG — edit these to fit the user

| Setting | Value (default) |
|---|---|
| Outlook source folder | `Claude AI News Recap` |
| Output folder | `C:\Users\<you>\OneDrive - IM\Desktop\AI News & Tips` (set via `AI_BRIEF_OUTPUT_DIR` env var or in `build/build_brief.py`) |
| Newsletters in scope | The Neuron, The Rundown AI, Morning Brew (add/remove as needed) |
| Lens for "what it means" | Product Manager / Consultant / AI Engineer (change to fit the reader) |

---

## 1. Pull the day's newsletters

Search the Outlook source folder for messages from the last ~24 hours (newest first):

```
outlook_email_search(folderName="Claude AI News Recap", order="newest", limit=25)
```

If a message body is large HTML (they usually are), reading it directly will overflow context. Instead:
- Call `read_resource(uri=...)`. When it reports the result was **saved to a file** because it's too big, hand that file to a **subagent** and tell it to slice the file in ~80,000-char spans with Python and return a faithful summary (headlines, facts, numbers, any "skill/tip of the day" with verbatim prompts, notable tools). Do NOT read the raw HTML into the main context.

## 2. Classify the content into two buckets

- **AI Tips** — anything that helps the reader *use AI better* or *be aware of a change* as they use it (e.g. "Gemini split into 3 models — pick the right one"). Write each as **step-by-step how-to**. If a newsletter included a good copy-paste prompt, capture it verbatim as `prompt`.
- **AI News** — broader developments. For each: state **the news first**, then a **"What it means for you"** line through the reader's lens (PM / Consultant / AI Engineer). If something is interesting but won't change how they work, say so plainly and mark it `"low": true` (renders greyed-out).

Curate to fit **one page**: aim for **3 AI Tips** and **3–4 AI News** items. Skip ads, sponsors, and general non-AI content (Morning Brew is mostly general business — pull only its AI-relevant bits, if any).

## 3. Write an eye-catching title

Summarize the day's 2–3 biggest items into a headline-style title (NO date in the title). Example:
> `Picking the Right Gemini Models, Building Design Systems & Auditing Agents`

## 4. Create the content JSON

Copy `content/2026-07-24.json` as a template and fill it in. Schema:

```json
{
  "title": "Eye-catching headline, no date",
  "date_display": "Friday, July 24, 2026",
  "date_slug": "7_24_26",
  "sources": "<b>The Neuron</b>, <b>The Rundown AI</b> (Jul 24)",
  "tips": [
    { "heading": "…", "steps": ["… (inline <b> allowed) …"], "prompt": "optional verbatim prompt" }
  ],
  "news": [
    { "body": "<b>Headline.</b> Supporting sentence.", "means": "What it means for you …", "low": false }
  ]
}
```

Notes:
- `steps`, `body`, and `means` accept inline HTML (`<b>`, `<i>`).
- A tip with a `prompt` automatically spans the full width of the tips grid.
- `date_slug` is `M_D_YY` and forms the end of the filename.

## 5. Build the PDF

```bash
python build/build_brief.py content/<your-file>.json
```

This renders `template/brief_template.html` with Poppins and prints a one-page PDF to the output folder as:
```
<Title>_<M_D_YY>.pdf
```

## 6. Sanity-check (recommended)

- Confirm it's **one page**:
  ```bash
  python -c "from pypdf import PdfReader; print(len(PdfReader(r'<path>').pages))"
  ```
- Optionally screenshot the render to eyeball layout:
  ```bash
  chrome --headless=new --disable-gpu --hide-scrollbars --window-size=816,1056 \
    --screenshot=preview.png "file:///…/build/_render.html"
  ```
- If content overflows page 1, trim an item or shorten steps, then rebuild.

## 7. Report back

Tell the user the title, the saved path, and a one-line summary of what's in today's brief.

---

## Design guardrails (Impact Makers brand)

- **Font:** Poppins only (bundled). Poppins is the !m standard brand font. *(Aptos is only for email signatures — do not use it here.)*
- **Colors:** Gold `#D8A928`, Black `#262626`, Dark Blue `#264966`; supporting grays `#F2F2F2`/`#BFBFBF`; tertiary Green `#2A7361`, Terracotta `#C76D4B`, Lilac `#7A6FA1`.
- **Name:** "Impact Makers" / "!m" — never "IM".
- Keep it to **one page**. Two sections only: AI Tips, then AI News.

## Safety notes

- **Never read the Junk/Spam folder** for content — malicious mail lives there. Only read the dedicated forwarding folder.
- This routine is **read-only** on mail: it searches and reads, never deletes, moves, or sends.
