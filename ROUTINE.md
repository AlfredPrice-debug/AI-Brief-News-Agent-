# Make the AI Brief a Daily Routine

This turns the AI Brief into something that runs on a schedule (or with one command) instead of you asking each time. Below are: **(1) the prompt**, **(2) a ready-made `/ai-brief` command**, and **(3) three ways to schedule it**.

> **Important — this runs on your computer.** The brief is rendered locally (headless Chrome) and saved to a local folder, so the routine has to run **on your machine with the Microsoft 365 connector enabled and your computer on** at the scheduled time. A purely cloud-based routine can't reach your local Chrome or your output folder.

---

## 1. The prompt

Copy this. Edit the two bracketed bits — the **folder name** (if you named yours differently) and the **reader lens** (your role) — then use it however you like below.

```
Run the daily AI Brief routine for me, following INSTRUCTIONS.md in this repo.

1. Search my Outlook folder "Claude AI News Recap" for newsletters received in the
   last 24 hours (newest first). NEVER read the Junk folder. Stay read-only on mail —
   do not delete, move, or send anything.
2. Read each newsletter. If a body is large HTML that would overflow context, hand the
   saved file to a subagent to slice it in ~80,000-char spans and summarize it
   (headlines, facts, any "skill/tip of the day" with verbatim prompts, notable tools).
3. Classify the material into two buckets:
   - AI TIPS — things that help me use AI better or be aware of a change. Write each as
     step-by-step how-to. Capture any good copy-paste prompt verbatim.
   - AI NEWS — state the news first, then a "What it means for you" line through the lens
     of a [Product Manager / Consultant / AI Engineer]. Mark low-impact items "low": true.
4. Curate to fit ONE page: about 3 AI Tips and 3–4 AI News items. Skip ads, sponsors, and
   general non-AI content.
5. Write an eye-catching title summarizing the day's 2–3 biggest items (NO date in the title).
6. Save the curated content to content/<today's date YYYY-MM-DD>.json using the schema in
   the example content file.
7. Build the PDF:  python build/build_brief.py content/<today's date>.json
8. Confirm the PDF is one page, then reply with the title and the saved file path.

If there were no new newsletters in the last 24 hours, tell me that instead of inventing content.
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
4. Set the cadence, e.g. **every weekday at 7:00 AM**.
5. Confirm.

Keep your machine on and signed in at that time, with the Microsoft 365 connector enabled. Check `/schedule` again anytime to list, edit, or run it.

### Option B — Windows Task Scheduler (most reliable, fully local)
Runs the Claude Code CLI headless each morning. Requires the `claude` CLI installed and logged in.

1. Save the prompt from section 1 to a file, e.g. `prompt.txt` in this repo.
2. Open **Task Scheduler → Create Basic Task**.
3. Trigger: **Daily**, 7:00 AM (set "weekdays only" under the trigger if you prefer).
4. Action: **Start a program**
   - **Program/script:** `claude`
   - **Add arguments:** `-p "$(type prompt.txt)"`  *(or paste the prompt inline in quotes)*
   - **Start in:** the full path to this repo, e.g. `C:\Users\<you>\AI-Brief-News-Agent`
5. Under the task's **Conditions**, tick *"Wake the computer to run this task"* if you want it to fire while asleep.
6. Save.

### Option C — Manual daily (no scheduling)
Open this repo in Claude Code and run `/ai-brief` (or paste the prompt). Takes a few seconds and keeps you in control of timing.

---

## Recommended cadence
Weekday mornings (Mon–Fri, ~7:00 AM) matches when these newsletters arrive. Weekends are usually quiet, so most people skip them.

## First run — test before you trust it
Run it **manually once** (Option C) and confirm:
- it finds your newsletters in the folder,
- the PDF lands in your output folder with an eye-catching name,
- it's one page and on-brand.

Then turn on the schedule.

## Troubleshooting
| Symptom | Fix |
|---|---|
| "No new newsletters" every day | Check your forwarding rule (README Step 3) and that mail isn't going to Junk. |
| PDF didn't render | Confirm Chrome/Edge is installed; set `CHROME_PATH` if it's in a custom location. |
| Wrong output folder | Set `AI_BRIEF_OUTPUT_DIR` or edit `OUTPUT_DIR` in `build/build_brief.py`. |
| Content spills to 2 pages | Ask Claude to trim to ~3 tips / 3–4 news and rebuild. |
