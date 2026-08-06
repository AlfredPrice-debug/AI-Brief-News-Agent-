# Make the AI Brief a Daily Routine

This turns the AI Brief into something that runs **twice a day** (8:00 AM, 4:00 PM Eastern, every day) instead of you asking each time — so nothing that lands mid-day is missed. It's set up as **two separate Routines**, one per firing time. Below are: **(1) the two prompts**, **(2) a ready-made `/ai-brief` command**, and **(3) how they're scheduled**.

Each Routine knows which run it is — the morning one is run 1, the afternoon one is run 2 — and still reads `state/run-log.json` to see what's already been covered today, so the two runs never duplicate a story. A run with no new mail, or too little material to be worth sending, skips delivery on its own (see `INSTRUCTIONS.md`).

> **This runs in the cloud, not on your laptop.** It's set up as two Claude Code Remote **Routines** — scheduled jobs that fire in an Anthropic-hosted cloud environment. That means: no local Chrome, no local desktop folder, and (as of this setup) no send-mail tool available on the Microsoft 365 connector. Delivery is **git push straight onto `main`** (each run's own throwaway session branch is never merged — see `INSTRUCTIONS.md` > *Push to GitHub*) to `briefs/` in this repo, plus **the run's own final reply**, which the Routine platform turns into its completion notification (email today; you can also turn on push) — see `INSTRUCTIONS.md` > *Delivery*.

## Reading briefs while you're away

Every run pushes the PDF straight to `briefs/` in this repo — open it on GitHub from your phone any time, no laptop required. You'll also get a notification (currently email, from the Routine itself) each time either one fires, with the title, the TL;DR, and a link straight to the pushed PDF. Because this runs in the cloud, it fires on schedule whether or not your laptop is on.

---

## 1. The two prompts

Each Routine gets its own prompt — they're identical except for the header and step 1, which pin the run number and the "search mail since" window. Both are also stored in this repo as `prompt-morning.txt` and `prompt-afternoon.txt`. Copy the matching block into each Routine.

### Routine A — Morning (8:00 AM Eastern) → `prompt-morning.txt`

```
Run the AI Brief routine for me, following INSTRUCTIONS.md in this repo (v2).

This is the MORNING firing — 8:00 AM Eastern (America/New_York) — and it is today's
run 1. A separate afternoon Routine fires at 4:00 PM as run 2 and will deduplicate
against whatever you publish, so log your fingerprints faithfully. There is no local
desktop and no send-mail tool available: delivery is git push plus your own final
reply, which the Routine turns into its completion notification to me — see the last
step.

1. Read state/run-log.json (create it as {"days": {}} if absent). You are today's
   run 1 — but cross-check the log first: if an entry for today's run 1 already
   exists, this is a re-run, so take the next unused run number. Search mail since
   the timestamp of yesterday's run 2 (4:00 PM), so overnight sends are caught; if
   yesterday has no successful run, fall back to the most recent successful run in
   the log.
2. Search ONLY my Outlook folder "Claude AI News Recap" for messages received since
   that timestamp, newest first. NEVER read Junk or Deleted Items. NEVER search the
   Inbox or any other folder. Stay read-only on existing mail — do not delete, move,
   flag, or mark anything read, and do not send any mail (there's no send-mail tool
   available, and none is needed).
3. If there are zero new messages: log a skipped run to state/run-log.json, push
   nothing, and reply "No new newsletters since [last run time]." Stop.
4. Read each newsletter. If a body is large HTML that would overflow context, hand the
   saved file to a subagent to slice it in ~80,000-char spans and summarize it
   (headlines, facts, any skill/tip of the day with verbatim prompts, notable tools).
   Discard ads, sponsor blocks, and newsletter housekeeping.
5. Classify into three buckets:
   - AI TIPS — things that help me use AI better or signal a change to act on. Write
     each as a short imperative title + 2-4 numbered steps that stand alone without
     the source. Capture any copy-paste prompt verbatim in a monospace block — never
     paraphrase it.
   - AI NEWS — headline + 1-2 sentences of fact, then a "What it means for you" line
     through my lens as a Product Manager / Consultant. Mark low-impact items
     "low": true.
   - BEYOND AI (Morning Brew or any other non-AI newsletter that shows up) — headline
     + facts, a "PM angle" line (a concrete tie to my work, OR plainly "No direct
     relevance to your work, general awareness only" — don't force a stretch), and a
     "Conversation starter" line I could actually say out loud to a client, colleague,
     or in standup.
6. Deduplicate by STORY, not by newsletter: fingerprint each story
   (entity|action|object) and drop anything already covered today, even from a
   different newsletter. If fewer than 2 items survive across all sections, skip
   delivery, roll items forward, and report the skip.
7. Curate to the page budget: page 1 = AI Tips (target 3, min 2) + AI News
   (target 3-4); page 2 = Beyond AI (target 4-5). A third page only on a genuinely
   heavy news day. Cut lowest-impact items first; never shrink type to force a fit.
8. Write a title (no date) and three TL;DR bullets.
9. Save to content/<today YYYY-MM-DD>-run<N>.json using the schema in
   content/2026-07-24-run1.json, with run, runTime, and fingerprints filled in.
10. Build:  python build/build_brief.py content/<file>.json — writes straight into
    briefs/.
11. Verify the page count before delivering anything — never ship an unverified PDF.
12. git add, commit ("brief: YYYY-MM-DD run <N> - <title>") the PDF plus the updated
    content JSON and state/run-log.json. IMPORTANT: each firing starts on its own
    throwaway branch off main — push straight onto main with
    `git push origin HEAD:main`, never a plain `git push` or
    `git push -u origin <branch>` (that strands the commit on a disposable branch,
    invisible in briefs/ on main). Retry with
    `git fetch origin main && git rebase origin/main` up to 5 times if rejected;
    report the git failure clearly only after 5 failed attempts.
13. Reply with the title, the three TL;DR bullets, a GitHub link to the pushed PDF,
    run number/time, newsletters read, and items deduped out. Keep it tight — this
    reply becomes my notification, not an internal report.

Never supplement thin source material with model knowledge or web search — if the day
is quiet, ship a short brief or skip the run per step 6.
```

### Routine B — Afternoon (4:00 PM Eastern) → `prompt-afternoon.txt`

```
Run the AI Brief routine for me, following INSTRUCTIONS.md in this repo (v2).

This is the AFTERNOON firing — 4:00 PM Eastern (America/New_York) — and it is today's
run 2. A separate morning Routine already fired at 8:00 AM as run 1, so treat
everything it published today as already covered and deduplicate against it. There is
no local desktop and no send-mail tool available: delivery is git push plus your own
final reply, which the Routine turns into its completion notification to me — see the
last step.

1. Read state/run-log.json (create it as {"days": {}} if absent). You are today's
   run 2 — but cross-check the log first: if an entry for today's run 2 already
   exists, this is a re-run, so take the next unused run number. Search mail since
   the timestamp of today's run 1; if run 1 never happened or was skipped, fall back
   to the last successful run before it (yesterday's 4:00 PM), so nothing is missed.
2. Search ONLY my Outlook folder "Claude AI News Recap" for messages received since
   that timestamp, newest first. NEVER read Junk or Deleted Items. NEVER search the
   Inbox or any other folder. Stay read-only on existing mail — do not delete, move,
   flag, or mark anything read, and do not send any mail (there's no send-mail tool
   available, and none is needed).
3. If there are zero new messages: log a skipped run to state/run-log.json, push
   nothing, and reply "No new newsletters since [last run time]." Stop.
4. Read each newsletter. If a body is large HTML that would overflow context, hand the
   saved file to a subagent to slice it in ~80,000-char spans and summarize it
   (headlines, facts, any skill/tip of the day with verbatim prompts, notable tools).
   Discard ads, sponsor blocks, and newsletter housekeeping.
5. Classify into three buckets:
   - AI TIPS — things that help me use AI better or signal a change to act on. Write
     each as a short imperative title + 2-4 numbered steps that stand alone without
     the source. Capture any copy-paste prompt verbatim in a monospace block — never
     paraphrase it.
   - AI NEWS — headline + 1-2 sentences of fact, then a "What it means for you" line
     through my lens as a Product Manager / Consultant. Mark low-impact items
     "low": true.
   - BEYOND AI (Morning Brew or any other non-AI newsletter that shows up) — headline
     + facts, a "PM angle" line (a concrete tie to my work, OR plainly "No direct
     relevance to your work, general awareness only" — don't force a stretch), and a
     "Conversation starter" line I could actually say out loud to a client, colleague,
     or in standup.
6. Deduplicate by STORY, not by newsletter: fingerprint each story
   (entity|action|object) and drop anything already covered today by run 1, even from
   a different newsletter. If fewer than 2 items survive across all sections, skip
   delivery, roll items forward, and report the skip.
7. Curate to the page budget: page 1 = AI Tips (target 3, min 2) + AI News
   (target 3-4); page 2 = Beyond AI (target 4-5). A third page only on a genuinely
   heavy news day. Cut lowest-impact items first; never shrink type to force a fit.
8. Write a title (no date) and three TL;DR bullets.
9. Save to content/<today YYYY-MM-DD>-run<N>.json using the schema in
   content/2026-07-24-run1.json, with run, runTime, and fingerprints filled in.
10. Build:  python build/build_brief.py content/<file>.json — writes straight into
    briefs/.
11. Verify the page count before delivering anything — never ship an unverified PDF.
12. git add, commit ("brief: YYYY-MM-DD run <N> - <title>") the PDF plus the updated
    content JSON and state/run-log.json. IMPORTANT: each firing starts on its own
    throwaway branch off main — push straight onto main with
    `git push origin HEAD:main`, never a plain `git push` or
    `git push -u origin <branch>` (that strands the commit on a disposable branch,
    invisible in briefs/ on main). Retry with
    `git fetch origin main && git rebase origin/main` up to 5 times if rejected;
    report the git failure clearly only after 5 failed attempts.
13. Reply with the title, the three TL;DR bullets, a GitHub link to the pushed PDF,
    run number/time, newsletters read, and items deduped out. Keep it tight — this
    reply becomes my notification, not an internal report.

Never supplement thin source material with model knowledge or web search — if the day
is quiet, ship a short brief or skip the run per step 6.
```

---

## 2. Ready-made command (`/ai-brief`)

This repo ships a slash command at `.claude/commands/ai-brief.md`. Because it lives under `.claude/commands/`, Claude Code picks it up automatically when you open this repo. Just type:

```
/ai-brief
```

…and Claude runs the same routine, working out the run number from `state/run-log.json` (it isn't pinned to a firing time, since you can invoke it any time). Handy for a manual test run before trusting the schedule.

---

## 3. How they're scheduled

These are **Claude Code Remote Routines** (not local Task Scheduler jobs) — **two separate triggers**, each pointed at the same cloud environment, each running its own prompt from section 1:

| # | Trigger name | Prompt | Cron (UTC, EDT) | Cron (UTC, EST) | Eastern time |
|---|---|---|---|---|---|
| A | AI Daily News Brief — Morning | `prompt-morning.txt` | `0 12 * * *` | `0 13 * * *` | 8:00 AM, every day |
| B | AI Daily News Brief — Afternoon | `prompt-afternoon.txt` | `0 20 * * *` | `0 21 * * *` | 4:00 PM, every day |

Two triggers rather than one comma-separated cron, so each firing carries its own run number and its own "search mail since" window. That means a run can't misidentify itself, and the afternoon run's dedup instruction is explicit about run 1 rather than inferred. The two never collide: A publishes and logs its fingerprints eight hours before B reads them.

### Daylight Saving Time

Cron triggers run in UTC with no automatic DST adjustment, so the hour has to be nudged manually twice a year. Use the column that matches the current period:

| Period | Trigger A | Trigger B |
|---|---|---|
| **EDT** (Mar 8 – Nov 1, 2026) — UTC-4 | `0 12 * * *` | `0 20 * * *` |
| **EST** (Nov 1, 2026 – Mar 14, 2027) — UTC-5 | `0 13 * * *` | `0 21 * * *` |

**Next change: Sunday, November 1, 2026** — bump both triggers by one hour (to `0 13` and `0 21`). Miss it and the brief simply arrives at 7:00 AM / 3:00 PM Eastern until you fix it — annoying, not broken.

Manage the triggers with `/schedule` in Claude Code, or ask Claude to list/update/delete them directly.

### Alternative: running it locally instead

The repo still ships `install-task.ps1` / `run-brief.ps1` for registering a Windows Task Scheduler job, if you'd rather run this on your own machine (e.g. to also get a copy synced to a local OneDrive folder). **Note:** `INSTRUCTIONS.md` and `build/build_brief.py` are currently written for the cloud setup above — no local-folder-copy step, no email step. If you want a local run to save a copy to a desktop folder and/or actually send mail, you'll need to add those steps back (`build/build_brief.py` accepts `AI_BRIEF_OUTPUT_DIR` for extra output folders, and a real send-mail tool would need to be available in that environment).

---

## First run — test before you trust it

Run it **manually once** (`/ai-brief`) and confirm:
- it finds your newsletters in the folder,
- the PDF lands in `briefs/` with an eye-catching name and gets pushed to GitHub,
- it's 2 pages (page 1 AI, page 2 Beyond AI) and on-brand,
- `state/run-log.json` picked up a new entry for the run,
- the final reply reads well as a notification (title, TL;DR, GitHub link).

Then let the schedule run. Trigger it a second time later the same day to confirm dedup works (it should report 0 new items, or only genuinely new stories, not repeats).

## Troubleshooting
| Symptom | Fix |
|---|---|
| "No new newsletters" every run | Check your forwarding rule (README Step 3) and that mail isn't going to Junk. |
| Same story shows up twice in one day | Check `state/run-log.json` — the day's `covered` fingerprints should include it after the first run. |
| PDF didn't render | Confirm a Chrome/Chromium binary is available in the run environment; set `CHROME_PATH` if it's in a custom location. |
| Content spills to a 3rd page on a normal day | Ask Claude to re-check the heavy-day test and trim to the page budget in `INSTRUCTIONS.md`. |
| Brand colors look wrong / fell back to defaults | Check the run's final reply for a brand-folder fallback note; confirm `build/brand.json` and the brand folder are both readable. |
| Notification says it "could not email" the brief | Expected — there's no send-mail tool on the connector. Delivery is git push + the final reply, not an agent-sent email (see the callout at the top of this file). |
| Only firing once a day, not twice | You need **both** triggers (A and B in section 3) — check each exists, is enabled, and has the right cron. |
| Briefs arriving an hour early or late | DST changed. Shift both triggers by one hour per the DST table in section 3. |
| Both runs numbered "run 1" | The two triggers are running the same prompt. Trigger A must use `prompt-morning.txt`, trigger B `prompt-afternoon.txt`. |
