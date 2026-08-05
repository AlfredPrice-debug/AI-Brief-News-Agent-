# AI Brief — Daily Routine (Instructions for Claude Code) — v2

This is the step-by-step routine Claude Code follows to produce the **Impact Makers AI Brief**: a curated, brand-styled PDF built **twice a day** so nothing that lands mid-day is missed. Follow it top to bottom. Never build an empty or duplicate brief.

> **Goal:** Turn the newsletters sitting in one Outlook folder into a 2-page brief — **page 1: AI Tips + AI News**, **page 2: Beyond AI** (general business/world awareness) — for Alfred Price (Product Manager / Consultant at Impact Makers), who reads it on his phone away from his desk.

This runs as a **Claude Code Remote Routine in a cloud environment**, not on Alfred's laptop — there is no local filesystem to save a copy to, and no Outlook "send mail" tool available. Delivery is entirely **git push to this repo** plus **the run's own final chat reply**, which the Routine platform turns into its completion notification (email/push) to Alfred. See **Delivery** below.

---

## 0. Prerequisites (one-time)

- **Microsoft 365 / Outlook connector** enabled, with **read** access to mail (`outlook_email_search`). There is currently no send-mail tool — do not attempt to email the brief; see **Delivery**.
- A dedicated Outlook mail folder named exactly `Claude AI News Recap` that newsletters route into.
- A Chromium/Chrome binary available in the run environment — used to render the PDF (auto-detected by `build/build_brief.py`; override with `CHROME_PATH`).
- **Python 3** with `pypdf` (`pip install pypdf`) — used for the page-count check.
- Read access to the Impact Makers brand assets folder (colors, typefaces, logo).
- This repo cloned locally to the run environment. Fonts are bundled in `fonts/` (Poppins — the !m brand font) as the fallback if the brand folder is unreadable.

## CONFIG

| Setting | Value |
|---|---|
| Outlook source folder | `Claude AI News Recap` (read-only; query only this folder) |
| Expected senders | No fixed list — read and classify whatever newsletter(s) actually land in the folder, from any sender |
| PDF output | This repo's `briefs/` folder only (no local desktop folder — see **Delivery**) |
| Reader lens | Product Manager / Consultant (Alfred Price, Impact Makers) |
| Time zone | America/New_York for all schedule references |
| Runs per day | 8:00 AM, 4:00 PM Eastern |

---

## 1. Load run state

Read `state/run-log.json` (create it with `{"days": {}}` if absent — see `state/README.md` for the schema). Determine:
- **Run number** for today (1 or 2) and the **timestamp of the last successful run** to search mail "since." On the very first run of the day, use the previous calendar day's run-2 (4:00 PM) timestamp so overnight sends are caught.
- Today's `covered` array of story fingerprints already published so far today (empty if this is run 1).

## 2. Pull newsletters since the last run

Query the `Claude AI News Recap` folder only, newest first, for messages received since the timestamp from step 1:

```
outlook_email_search(folderName="Claude AI News Recap", order="newest", since=<last_run_timestamp>)
```

Read-only. Never modify, move, flag, or mark-as-read. Never touch Junk or Deleted Items. Never search any other folder.

**If zero new messages:** append a skipped entry to `state/run-log.json` (run number, timestamp, `"status": "skipped_no_mail"`), push nothing, and reply `"No new newsletters since [last run time]."` Stop here.

For each message, extract the readable body. If a body is large HTML that would overflow context, save it to a temp file and hand it to a **subagent**: slice the file into roughly 80,000-character spans with Python and summarize headlines, facts, any skill/tip of the day with verbatim prompts, and notable tools. Do not read raw HTML into the main context.

## 3. Classify

Classify every extracted item into one of three buckets, discarding ads, sponsor blocks, and newsletter housekeeping as you go:

- **AI Tips** — helps Alfred use AI better or signals a change to act on.
- **AI News** — broader AI developments.
- **Beyond AI** — general business/world awareness, from Morning Brew or any other non-AI newsletter in the folder.

## 4. Deduplicate by story, not by newsletter

Build a fingerprint per story from its core claim: `entity|action|object` (e.g. `anthropic|releases|computer-use-ga`). If a fingerprint is already in today's `covered` array (from an earlier run today), drop the item even if a different newsletter is reporting it. Fingerprints reset at midnight.

**If fewer than 2 items survive dedup across all three sections combined:** the run is thin. Skip delivery, roll the surviving items forward into the next run's candidate pool (note them in the run-log skip entry so the next run's model context can consider them), and report the skip. Do not pad with model knowledge to hit a quota.

## 5. Rank and curate to the page budget

- **Page 1 / Section A — AI Tips** (target 3, minimum 2): short imperative title; numbered 2–4 step how-to that stands alone without the source; any copy-paste prompt reproduced **verbatim** in a monospace block (never paraphrase); source attribution.
- **Page 1 / Section B — AI News** (target 3–4): headline stating the news; 1–2 sentences of fact (what happened, who, when, any figure that matters); a **"What it means for you"** line through the PM/consultant lens; source attribution; set `"low": true` on items worth knowing but not worth acting on.
- **Page 2 — Beyond AI** (target 4–5): headline; 1–2 sentences of fact; a **"PM angle"** line — a concrete connection to product management, consulting, client industries, budgets, hiring, or the tech market, OR plainly "No direct relevance to your work, general awareness only" when it doesn't connect (this is the correct answer more often than not — never manufacture a strained tie-in); a **"Conversation starter"** line Alfred could actually say out loud to a client, colleague, or in standup (a question or a point-of-view observation, not a restatement of the headline). Mix items that touch his work with pure situational-awareness items.

Cut by impact ranking, lowest first, when content exceeds the page budget. Never shrink type below the template minimum to force a fit. A third page is permitted only on a genuinely heavy news day (at least 3 items that would each individually be the lead story on a normal day) — never add one just because material exists.

## 6. Write the title and TL;DR

- **Title:** eye-catching, summarizes the day's 2–3 biggest items, no date. This is also the headline of the run's final reply (see **Delivery**).
- **TL;DR:** three one-line bullets, the three highest-impact items across both pages, readable in ten seconds.

## 7. Save the content JSON

Save to `content/YYYY-MM-DD-run<N>.json`, following the schema in `content/2026-07-24-run1.json` (the example), with `run`, `runTime`, and `fingerprints` fields populated. See that file for the exact shape (`tldr`, `tips`, `news`, `beyond_ai`, `sources`, etc.).

## 8. Build the PDF

```bash
python build/build_brief.py content/YYYY-MM-DD-run<N>.json
```

By default this writes straight into `briefs/`. The script reads brand colors/fonts from `build/brand.json` if present (see **Brand styling** below), falling back to the bundled Poppins/IM palette otherwise.

## 9. Verify before delivering

```bash
python -c "from pypdf import PdfReader; print(len(PdfReader(r'<path>').pages))"
```

Confirm the page count matches the rules in step 5 (2 pages, or 3 only on a heavy day). If the build failed or the page count is wrong, fix the content or template and rebuild. **Never deliver an unverified PDF.**

## 10. Push to GitHub — directly onto `main`

`git add`, `git commit` the new PDF (already in `briefs/` from step 8) plus the updated `content/*.json` and `state/run-log.json`. Commit message format:

```
brief: YYYY-MM-DD run <N> - <title>
```

**Each Routine firing starts on its own throwaway branch checked out from `main`.** If you `git push -u origin <that-branch-name>` (or just `git push`), the commit lands on that disposable branch and is never seen again once the session ends — it will NOT show up in `briefs/` on `main`, and the GitHub link in your reply (step 11) would be dead or point nowhere useful. You must push straight onto `main`:

```
git push origin HEAD:main
```

If that's rejected (a concurrent run landed first), `git fetch origin main && git rebase origin/main` and retry — **up to 5 times**, not just once. Concurrent firings racing to push are expected, not exceptional; giving up after a single retry has repeatedly stranded real briefs on disposable branches (recovered after the fact in PRs #6-#9). Only after 5 failed attempts should you report the git failure clearly in the final reply — the brief still exists in this run's workspace, it just isn't on `main` yet, and whoever reads the reply needs to know to go recover it.

On success, append the run entry and every published fingerprint to `state/run-log.json` and commit it alongside the PDF (same commit is fine).

## 11. Delivery: the final reply *is* the delivery mechanism

There is no send-mail tool available, so **do not** attempt to email the brief. Instead, the run's final chat reply is what the Claude Code Remote Routine turns into its completion notification (email and/or push) to Alfred — so it needs to stand alone as something worth reading on a phone:

- Lead with the **title**.
- The three **TL;DR** bullets.
- A direct GitHub link to the pushed PDF (`https://github.com/<owner>/<repo>/blob/main/briefs/<filename>`).
- Run number and time, how many newsletters were read, how many items were deduplicated out.
- Any fallback notes (brand folder unreadable, git push failed, etc).

Keep it tight — this is read as a notification, not a report.

---

## Content JSON schema (v2)

```json
{
  "run": 2,
  "runTime": "2026-07-28T13:00:00-04:00",
  "title": "Eye-catching headline, no date",
  "date_display": "Tuesday, July 28, 2026",
  "date_slug": "7_28_26",
  "sources": "<b>Superhuman AI</b>, <b>The Rundown AI</b>, <b>Morning Brew</b> (Jul 28)",
  "tldr": [
    "One-line highest-impact item.",
    "One-line second highest-impact item.",
    "One-line third highest-impact item."
  ],
  "tips": [
    { "heading": "Imperative title", "steps": ["Step one …", "Step two …"], "prompt": "verbatim copy-paste prompt, optional", "source": "The Rundown AI" }
  ],
  "news": [
    { "body": "<b>Headline.</b> Fact sentence(s).", "means": "What it means for you …", "source": "Superhuman AI", "low": false }
  ],
  "beyond_ai": [
    { "body": "<b>Headline.</b> Fact sentence(s).", "angle": "PM angle line, or the plain no-relevance line.", "starter": "Conversation starter line.", "source": "Morning Brew" }
  ],
  "fingerprints": ["anthropic|releases|computer-use-ga", "openai|raises|series-f"]
}
```

Notes:
- `steps`, `body`, `means`, `angle`, and `starter` accept inline HTML (`<b>`, `<i>`).
- A tip with a `prompt` spans the full width of the tips grid and renders the prompt verbatim in a monospace block.
- `date_slug` is `M_D_YY`.
- `fingerprints` is the full list of story fingerprints published in *this* run — the build/delivery step appends these to `state/run-log.json`.

## `state/run-log.json` schema

See `state/README.md`. Summary: one entry per calendar date, containing an array of run records (`run`, `timestamp`, `status`: `delivered` | `skipped_no_mail` | `skipped_thin`, and `covered`: the fingerprints published by that run).

---

## Brand styling

- Read the Impact Makers brand assets (primary/secondary/accent hex, heading/body typefaces, logo file) from the designated brand folder at run time — never hardcode them.
- Cache the extracted values to `build/brand.json` (gitignored — cache local to the run environment; see `build/brand.example.json` for the shape). On each run, re-check the brand folder's modified date and refresh the cache if it changed.
- Applied to the PDF: logo in the header, brand primary for section headers/rules, brand accent for the TL;DR block and the "What it means for you" / "PM angle" labels, brand typefaces throughout.
- **If the brand folder is missing or unreadable:** fall back to the bundled template (Poppins; Gold `#D8A928`, Black `#262626`, Dark Blue `#264966`), note the fallback in the final reply, and continue. Never guess at brand colors.

## Safety notes

- **Read-only on the mailbox.** The routine searches and reads `Claude AI News Recap` only; it never deletes, moves, flags, or marks messages read, and **it never sends any mail** — there is no send-mail tool available, and delivery does not require one (see **Delivery**).
- **Never read Junk or Deleted Items**, under any circumstance.
- **Never search the Inbox** or any folder other than `Claude AI News Recap`.
- **Never supplement thin source material** with model knowledge or web search. If the day is quiet, ship a short brief or skip the run per step 4.
- Reproduce prompts, code, model names, version numbers, prices, and dates exactly as written in the source. If two sources conflict on a fact, state both and name each source.
- Prose style: no em dashes, sentence case headings, active voice, no emoji.
- No ads, sponsored segments, affiliate placements, or newsletter self-promotion in the brief.
