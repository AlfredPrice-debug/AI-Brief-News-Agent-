# Make the AI Brief a Daily Routine

This turns the AI Brief into something that runs on a schedule (or with one command) instead of you asking each time. Below are: **(1) the prompt**, **(2) a ready-made `/ai-brief` command**, and **(3) three ways to schedule it**.

> **Important — this runs on your computer.** The brief is rendered locally (headless Chrome) and saved to a local folder, so the routine has to run **on your machine with the Microsoft 365 connector enabled and your computer on** at the scheduled time. A purely cloud-based routine can't reach your local Chrome or your output folder.

## Reading briefs while you're away

Every brief is saved to a **OneDrive** folder, so it syncs to the cloud automatically — view it at **onedrive.com** or the **OneDrive mobile app** on your phone. The routine also emails you a copy and pushes the PDF to GitHub (step 9 of the prompt). But a brief is only *generated* if your computer is running the routine. So if you'll be away:

- ✅ **Leave the laptop ON, plugged in, and LOGGED IN with the screen locked** (`Win`+`L`). Locking keeps your session — and OneDrive — alive.
- 🚫 **Do NOT sign out / log off.** That ends your user session: OneDrive stops syncing and per-user scheduled tasks won't run, so the brief won't be made or won't reach the cloud.
- 💤 **Disable sleep/hibernate** for those days (Settings → Power → *put to sleep = Never* while plugged in), or tick *"Wake the computer to run this task"* on the scheduled task (Option B below).

If leaving the laptop on isn't possible, the local routine can't produce briefs while away — that needs an always-on/cloud setup, which is a separate, larger project (it requires server-side mailbox access via Microsoft Graph and an Anthropic API key).

---

## 1. The prompt

Copy this. Edit the two bracketed bits — the **folder name** (if you named yours differently) and the **reader lens** (your role) — then use it however you like below.

```
Run the daily AI Brief routine for me, following INSTRUCTIONS.md in this repo.

1. Search my Outlook folder "Claude AI News Recap" for newsletters received in the
   last 24 hours (newest first). NEVER read the Junk folder. Stay read-only on existing
   mail — do not delete or move anything. (The only message you may send is the delivery
   email to my own work address in step 9.)
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
8. Confirm the PDF is one page.
9. Deliver it (so I can read it away from my desk):
   a) EMAIL: send me an HTML copy at my own work address. Use the title as the subject and
      the AI Tips + AI News as a clean HTML body (headings, bold, lists only — email strips
      CSS, so this is a readable text version, not the styled PDF).
   b) GITHUB: copy the PDF into this repo's briefs/ folder, then git add, commit, and push
      so it's downloadable from GitHub on any device.
10. Reply with the title, the saved local path, and confirm the email + GitHub push.

If there were no new newsletters in the last 24 hours, tell me that instead of inventing
content — and do not send an email or push anything.
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

### Option B — Windows Task Scheduler (runs even with Claude Code closed)
This starts a fresh headless `claude` process each morning, so **you don't need to keep a Claude Code window open.** Requires: the `claude` CLI installed & logged in, the machine on + logged in (locked is fine), and the tools pre-authorized (see *Permissions* below).

**Easiest — the bundled installer** (run once, from this repo folder; no admin needed):
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install-task.ps1
```
It registers a task named **"AI Brief Daily"** for weekdays at 7:00 AM that runs `run-brief.ps1` (which calls Claude with `prompt.txt`). Test it right away:
```powershell
Start-ScheduledTask -TaskName "AI Brief Daily"
```
Then check `briefs\run-log.txt` and your output folder. Remove it anytime:
```powershell
Unregister-ScheduledTask -TaskName "AI Brief Daily" -Confirm:$false
```

**Or by hand (Task Scheduler GUI):**
1. Open **Task Scheduler → Create Task…** (not "Basic Task").
2. **General:** name it `AI Brief Daily`; select **Run only when user is logged on**.
3. **Triggers → New:** *Weekly*, Mon–Fri, **7:00 AM**.
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
