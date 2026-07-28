# AI Brief News Agent

A routine for **Claude Code** that turns the newsletters in one Outlook folder into a **2-page, brand-styled PDF**, delivered **three times a day** (7 AM / 1 PM / 5 PM Eastern, weekdays) so nothing that lands mid-day is missed. Page 1 is **AI** — **AI Tips** (step-by-step how-to) and **AI News** (the news + *what it means for you* as a Product Manager / Consultant); page 2 is **Beyond AI** — general business/world awareness, each item paired with a **PM angle** and a **conversation starter**. Built for Alfred Price at Impact Makers as a personal-development habit.

![Sample brief](docs/sample.png)

## What you get
A 2-page, Impact Makers–branded PDF (brand fonts/colors, read live from the brand folder — Poppins/gold-black-blue as the bundled fallback) saved to a folder of your choice, named for the run's content, e.g.
`Picking the Right Gemini Models, Building Design Systems & Auditing Agents_7_24_26_run1.pdf`

Every run also deduplicates against everything already published *that day* — via `state/run-log.json` — so the same story never appears twice across the day's three briefs, and a run with too little new material (or no new mail at all) skips delivery on its own rather than sending something thin or repeated.

---

## ⚠️ Before it can work: you must feed it newsletters

**The agent does not browse the web.** It only reads AI newsletters that land in one dedicated Outlook folder. So the quality of your brief depends entirely on this setup. Do these one-time steps first.

### Step 1 — Subscribe to a few newsletters
Pick a handful so there's material for all three runs. Recommended (all free) — this list isn't fixed, the routine treats anything that lands in the folder as a candidate source:
| Newsletter | Focus | Sign up |
|---|---|---|
| **Superhuman AI** | Daily AI news + practical tips (lands mid-morning) | superhuman.ai |
| **The Rundown AI** | Daily AI news + tools + how-tos | therundown.ai |
| **TLDR AI** | Short, technical AI/ML news | tldr.tech/ai |
| **Morning Brew** | General business (feeds page 2, Beyond AI) | morningbrew.com |
| **1440** | General news roundup (feeds page 2, Beyond AI) | join1440.com |

> Tip: subscribe using the **email address you'll route from** (see Step 3).

### Step 2 — Create a dedicated Outlook folder
In your **work** Outlook, make a folder named exactly **`Claude AI News Recap`** (Right-click your mailbox → *Create new folder*). This is the only folder the agent reads.

### Step 3 — Route the newsletters into that folder
Choose whichever matches where you subscribed:

**A) You subscribed with your personal Outlook** — create a forwarding rule:
1. outlook.com → ⚙️ → **Mail → Rules → + Add new rule**.
2. Name it `Forward AI News`.
3. Condition **From** = your newsletter senders (add each one).
4. Action **Forward to** = your work address.
5. Save. *(New mail only; forwarding rules can't run on old mail.)*

**B) You subscribed with Gmail** — Gmail → ⚙️ **See all settings → Forwarding and POP/IMAP → Add a forwarding address** (verify it), then **Filters → Create filter** (From = the senders) → **Forward it to** your work address.

**C) You subscribed with your work email directly** — just add an inbox rule that **moves** messages from those senders into `Claude AI News Recap`.

### Step 4 — Keep them out of Junk
If a newsletter lands in Junk, right-click it → **Junk → Never block sender**, or add the sender to **Safe Senders**.
🔒 *The agent never reads your Junk folder — that's deliberate, for security — so anything stuck in Junk is invisible to it.*

---

## Technical setup (one-time)
1. **Clone this repo.**
2. **Enable the Microsoft 365 connector** in Claude (read access to mail).
3. **Install Google Chrome** (or Edge) — used to render the PDF.
4. *(Optional)* `pip install pypdf` for a page-count sanity check.
5. **Choose the folder(s) on your computer where the PDFs will be saved.** These are local folders on *your* machine — create them wherever you'd like your briefs to collect. The routine writes to whichever of two configured defaults exist (see `DEFAULT_OUTPUT_DIRS` in `build/build_brief.py`), or override with the `AI_BRIEF_OUTPUT_DIR` environment variable (colon/semicolon-separated to target more than one).
   - *If neither folder exists yet, the build script creates the second default automatically and notes it in the run report.*
6. *(Optional)* Point the routine at your Impact Makers brand-assets folder so it can read live colors/fonts/logo instead of the bundled defaults — see **Brand & safety** below.

## Using it
Tell Claude Code:
> "Run the AI Brief for me."

Claude follows [`INSTRUCTIONS.md`](INSTRUCTIONS.md): reads new mail from the folder since the last run, classifies into AI Tips / AI News / Beyond AI, deduplicates against everything already published today, writes `content/<date>-run<N>.json`, and builds the 2-page PDF. To re-render an existing content file yourself:
```bash
python build/build_brief.py content/2026-07-24-run1.json
```

**Reading it away from your desk.** The routine also **emails you a copy**, **pushes the PDF to `briefs/` on GitHub**, and if the output folder is in OneDrive the PDF **syncs to the cloud** automatically — so you can read the brief on your phone via email, GitHub, or the OneDrive app.

**Want it to run automatically, three times a day?** See **[ROUTINE.md](ROUTINE.md)** — it has the copy-paste prompt, scheduling instructions for 7 AM / 1 PM / 5 PM Eastern (including a ready-made `/ai-brief` command), and how to keep it running while you're away (leave the laptop on and locked — don't log out).

## Repo layout
| Path | Purpose |
|---|---|
| `INSTRUCTIONS.md` | The routine Claude Code follows on every run (v2: 3x/day, 2-page, dedup). |
| `ROUTINE.md` | How to run it as a scheduled routine + the prompt. |
| `template/brief_template.html` | 2-page layout (AI page + Beyond AI page) + brand CSS. |
| `build/build_brief.py` | Renders a content JSON → branded PDF via headless Chrome. |
| `build/brand.example.json` | Shape of the brand-folder cache (`build/brand.json`, gitignored). |
| `content/2026-07-24-run1.json` | Example of a run's content (v2 schema). |
| `state/run-log.json` | Per-day run/dedup state; read and updated on every run. |
| `.claude/commands/ai-brief.md` | Bundled `/ai-brief` slash command. |
| `briefs/` | Generated PDFs pushed here for remote access. |
| `fonts/` | Poppins (SIL Open Font License) — the !m brand font, used as the fallback. |

## Customizing
- **Reader lens:** change "Product Manager / Consultant" in `INSTRUCTIONS.md` and the template subtitle.
- **Sources:** add/remove newsletters in `INSTRUCTIONS.md` → CONFIG and in your forwarding rule.
- **Styling:** the template reads brand colors/fonts from `build/brand.json` at build time (see below); structural CSS lives in `template/brief_template.html`.

## Brand & safety
- **Brand assets are read live**, not hardcoded: colors, typefaces, and the logo are read from the Impact Makers brand folder at run time and cached to `build/brand.json` (see `build/brand.example.json`; refreshed whenever the brand folder's modified date changes).
- **Fallback:** if the brand folder is missing or unreadable, the bundled defaults apply — Poppins; Gold `#D8A928` · Black `#262626` · Dark Blue `#264966` (+ supporting grays; terracotta accent) — and the run report notes the fallback.
- **Read-only mail:** the routine searches and reads only the `Claude AI News Recap` folder; it never deletes, moves, flags, or marks messages, and never reads Junk/Deleted Items or any other folder.

## License
Code and templates: internal Impact Makers use. Poppins font: [SIL Open Font License 1.1](fonts/).
