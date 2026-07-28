# Make the AI Brief a Daily Routine

This turns the AI Brief into something that runs **three times a day** (7:00 AM, 1:00 PM, 5:00 PM Eastern, weekdays) instead of you asking each time — so nothing that lands mid-day is missed. Below are: **(1) the prompt**, **(2) a ready-made `/ai-brief` command**, and **(3) three ways to schedule it**.

Each run reads `state/run-log.json` to figure out its own run number and what's already been covered today, so the three runs never duplicate a story — a run with no new mail, or too little material to be worth sending, skips delivery on its own (see `INSTRUCTIONS.md`).

> **Important — this runs on your computer.** The brief is rendered locally (headless Chrome) and saved to a local folder, so the routine has to run **on your machine with the Microsoft 365 connector enabled and your computer on** at the scheduled time. A purely cloud-based routine can't reach your local Chrome or your output folder.

## Reading briefs while you're away

Every brief is saved to a **OneDrive** folder, so it syncs to the cloud automatically — view it at **onedrive.com** or the **OneDrive mobile app** on your phone. The routine also emails you a copy and pushes the PDF to GitHub (step 9 of the prompt). But a brief is only *generated* if your computer is running the routine. So if you'll be away:

- ✅ **Leave the laptop ON, plugged in, and LOGGED IN with the screen locked** (`Win`+`L`). Locking keeps your session — and OneDrive — alive.
- 🚫 **Do NOT sign out / log off.** That ends your user session: OneDrive stops syncing and per-user scheduled tasks won't run, so the brief won't be made or won't reach the cloud.
- 💤 **Disable sleep/hibernate** for those days (Settings → Power → *put to sleep = Never* while plugged in), or tick *"Wake the computer to run this task"* on the scheduled task (Option B below).

If leaving the laptop on isn't possible, the local routine can't produce briefs while away — that needs an always-on/cloud setup, which is a separate, larger project (it requires server-side mailbox access via Microsoft Graph and an Anthropic API key).

---

## 1. The prompt

This is also `prompt.txt` in this repo (used verbatim by the scheduled runs — see Option B). Paste it into Claude Code, or just run `/ai-brief`:

```
Run the AI Brief routine for me, following INSTRUCTIONS.md in this repo (v2).

This routine runs three times on weekdays: 7:00 AM, 1:00 PM, and 5:00 PM Eastern
(America/New_York). Figure out which run this is and act accordingly — do not assume
it's the first run of the day.

1. Read state/run-log.json (create it as {"days": {}} if absent). Work out today's run
   number and the timestamp of the last successful run — on the very first run of the
   day, use yesterday's 5:00 PM run instead, so overnight sends are caught.
2. Search ONLY my Outlook folder "Claude AI News Recap" for messages received since that
   timestamp, newest first. NEVER read Junk or Deleted Items. NEVER search the Inbox or
   any other folder. Stay read-only on existing mail — do not delete, move, flag, or mark
   anything read. (The only message you may send is the single delivery email in step 10.)
3. If there are zero new messages: log a skipped run to state/run-log.json, send nothing,
   push nothing, and tell me "No new newsletters since [last run time]." Stop.
4. Read each newsletter. If a body is large HTML that would overflow context, hand the
   saved file to a subagent to slice it in ~80,000-char spans and summarize it (headlines,
   facts, any skill/tip of the day with verbatim prompts, notable tools). Discard ads,
   sponsor blocks, and newsletter housekeeping.
5. Classify into three buckets:
   - AI TIPS — imperative title + 2-4 numbered steps that stand alone without the source.
     Capture any copy-paste prompt verbatim in a monospace block — never paraphrase it.
   - AI NEWS — headline + 1-2 sentences of fact, then a "What it means for you" line
     through my lens as a [Product Manager / Consultant]. Mark low-impact items "low": true.
   - BEYOND AI (Morning Brew, 1440, or any other non-AI newsletter) — headline + facts, a
     "PM angle" line (a concrete tie to my work, OR plainly "No direct relevance to your
     work, general awareness only" — don't force a stretch), and a "Conversation starter"
     line I could actually say out loud to a client, colleague, or in standup.
6. Deduplicate by STORY, not by newsletter: fingerprint each story (entity|action|object)
   and drop anything already covered today, even from a different newsletter. If fewer
   than 2 items survive across all sections, skip delivery, roll items forward, and report
   the skip.
7. Curate to the page budget: page 1 = AI Tips (target 3, min 2) + AI News (target 3-4);
   page 2 = Beyond AI (target 4-5). A third page only on a genuinely heavy news day. Cut
   lowest-impact items first; never shrink type to force a fit.
8. Write a title (no date — it's also the email subject) and three TL;DR bullets.
9. Save to content/<today YYYY-MM-DD>-run<N>.json using the schema in
   content/2026-07-24-run1.json, with run, runTime, and fingerprints filled in.
10. Build:  python build/build_brief.py content/<file>.json
11. Verify the page count before delivering anything — never ship an unverified PDF.
12. Copy the PDF to whichever configured desktop folder(s) exist on this machine (both if
    both exist; create the second and note it if neither exists).
13. Copy it into this repo's briefs/ folder, then git add, commit
    ("brief: YYYY-MM-DD run <N> - <title>"), and push — retry once with pull --rebase if
    rejected. Update state/run-log.json with this run's entry and fingerprints.
14. Email me ONE HTML copy: title as subject, PDF attached, GitHub link at the bottom.
15. Reply with the title, run number/time, newsletters read, items deduped out, local
    path(s), and confirmation of email/attachment/push.

Never supplement thin source material with model knowledge or web search — if the day is
quiet, ship a short brief or skip the run per step 6.
```

---

## 2. Ready-made command (`/ai-brief`)

This repo ships a slash command at `.claude/commands/ai-brief.md`. Because it lives under `.claude/commands/`, Claude Code picks it up automatically when you open this repo. Just type:

```
/ai-brief
```

…and Claude runs the prompt above. This is the simplest daily habit — open the repo each morning and run `/ai-brief`.

---

## 3. Schedule it

### Option A — Claude Code's `/schedule` (easiest)
1. In Claude Code (opened in this repo), run:
   ```
   /schedule
   ```
2. Choose **create a new routine**.
3. Paste **the prompt** from section 1 as the task.
4. Set the cadence to **three separate routines**: weekdays at 7:00 AM, 1:00 PM, and 5:00 PM Eastern. (`/schedule` creates one routine per cadence — repeat steps 2-5 three times, same prompt each time.)
5. Confirm.

Keep your machine on and signed in at those times, with the Microsoft 365 connector enabled. Check `/schedule` again anytime to list, edit, or run them. Each run reads `state/run-log.json` to know its own run number, so it doesn't matter which routine fires — the prompt figures out run 1/2/3 for itself.

### Option B — Windows Task Scheduler (runs even with Claude Code closed)
This starts a fresh headless `claude` process each morning, so **you don't need to keep a Claude Code window open.** Requires: the `claude` CLI installed & logged in, the machine on + logged in (locked is fine), and the tools pre-authorized (see *Permissions* below).

**Easiest — the bundled installer** (run once, from this repo folder; no admin needed):
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install-task.ps1
```
It registers a task named **"AI Brief 3x Daily"** with three weekday triggers — **7:00 AM, 1:00 PM, and 5:00 PM** — that all run `run-brief.ps1` (which calls Claude with `prompt.txt`; the prompt itself works out the run number from `state/run-log.json`, so the same script serves all three firings). Test it right away:
```powershell
Start-ScheduledTask -TaskName "AI Brief 3x Daily"
```
Then check `briefs\run-log.txt` and your output folder(s). Remove it anytime:
```powershell
Unregister-ScheduledTask -TaskName "AI Brief 3x Daily" -Confirm:$false
```

**Or by hand (Task Scheduler GUI):**
1. Open **Task Scheduler → Create Task…** (not "Basic Task").
2. **General:** name it `AI Brief 3x Daily`; select **Run only when user is logged on**.
3. **Triggers → New:** *Weekly*, Mon–Fri, **7:00 AM** — then add two more triggers the same way for **1:00 PM** and **5:00 PM**.
4. **Actions → New:** *Start a program* →
   - **Program/script:** `powershell.exe`
   - **Add arguments:** `-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "run-brief.ps1"`
   - **Start in:** the full path to this repo (e.g. `C:\Users\<you>\AI-Brief-News-Agent`).
5. **Conditions:** tick **Wake the computer to run this task**; untick *Start the task only if on AC power* if you want it on battery.
6. Save.

**Permissions for unattended runs.** With no one to click "approve", pre-authorize the routine's tools ONE of two ways:
- **Scoped allowlist (safer):** run it manually once with `/ai-brief` and choose **"always allow"** for each tool — that records an allowlist your future runs reuse.
- **Full bypass (simplest, less safe):** add `--dangerously-skip-permissions` to the `claude` line in `run-brief.ps1`. Only if you accept the run can use any tool unprompted.

> **You can close Claude Code.** The task launches its own `claude` process — no interactive window needed. You DO need to stay **logged in** (locked is fine) so OneDrive and the mail connector are available.

### Option C — Manual daily (no scheduling)
Open this repo in Claude Code and run `/ai-brief` (or paste the prompt). Takes a few seconds and keeps you in control of timing.

---

## Recommended cadence
Weekdays, 7:00 AM / 1:00 PM / 5:00 PM Eastern — matches when Superhuman AI and Morning Brew tend to land mid-day, which a single morning run would miss. Weekends are usually quiet, so most people skip them.

## First run — test before you trust it
Run it **manually once** (Option C) and confirm:
- it finds your newsletters in the folder,
- the PDF lands in your output folder(s) with an eye-catching name,
- it's 2 pages (page 1 AI, page 2 Beyond AI) and on-brand,
- `state/run-log.json` picked up a new entry for the run.

Then turn on the schedule. Run it a second time later the same day to confirm dedup works (it should report 0 new items, or only genuinely new stories, not repeats).

## Troubleshooting
| Symptom | Fix |
|---|---|
| "No new newsletters" every run | Check your forwarding rule (README Step 3) and that mail isn't going to Junk. |
| Same story shows up twice in one day | Check `state/run-log.json` — the day's `covered` fingerprints should include it after the first run. |
| PDF didn't render | Confirm Chrome/Edge is installed; set `CHROME_PATH` if it's in a custom location. |
| Wrong output folder | Set `AI_BRIEF_OUTPUT_DIR` (colon/semicolon-separated list) or edit `DEFAULT_OUTPUT_DIRS` in `build/build_brief.py`. |
| Content spills to a 3rd page on a normal day | Ask Claude to re-check the heavy-day test and trim to the page budget in `INSTRUCTIONS.md`. |
| Brand colors look wrong / fell back to defaults | Check the run report for a brand-folder fallback note; confirm `build/brand.json` and the brand folder are both readable. |
