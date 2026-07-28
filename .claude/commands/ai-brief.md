---
description: Build this run's 2-page Impact Makers AI Brief PDF (AI Tips/News + Beyond AI) from newsletters in Outlook, and push it to GitHub.
---

Run the AI Brief routine for me, following INSTRUCTIONS.md in this repo (v2). This runs in the cloud with no local desktop and no send-mail tool: delivery is git push plus your final reply, which becomes the completion notification — do not attempt to email anything.

1. Read state/run-log.json (create it as {"days": {}} if absent). Work out today's run number and the timestamp of the last successful run — on the very first run of the day, use yesterday's 5:00 PM run instead, so overnight sends are caught.
2. Search ONLY my Outlook folder "Claude AI News Recap" for messages received since that timestamp, newest first. NEVER read Junk or Deleted Items. NEVER search the Inbox or any other folder. Stay read-only on existing mail.
3. If there are zero new messages: log a skipped run, push nothing, and reply "No new newsletters since [last run time]." Stop.
4. Read each newsletter (hand large HTML bodies to a subagent to slice and summarize). Discard ads, sponsor blocks, and newsletter housekeeping.
5. Classify into AI TIPS (imperative title + 2-4 numbered steps, verbatim prompt if present), AI NEWS (headline + facts + "What it means for you," mark low-impact "low": true), and BEYOND AI (headline + facts + "PM angle," which may correctly say "No direct relevance to your work, general awareness only," + "Conversation starter").
6. Deduplicate by story fingerprint (entity|action|object) against today's covered list — drop repeats even from a different newsletter. If fewer than 2 items survive, skip the run and roll items forward.
7. Curate to page 1 (AI Tips + AI News) and page 2 (Beyond AI). A third page only on a genuinely heavy news day. Cut lowest-impact items first.
8. Write a title (no date) and three TL;DR bullets.
9. Save to content/<today YYYY-MM-DD>-run<N>.json using the schema in content/2026-07-24-run1.json.
10. Build: python build/build_brief.py content/<file>.json — writes into briefs/.
11. Verify the page count before delivering — never ship an unverified PDF.
12. git add/commit ("brief: YYYY-MM-DD run <N> - <title>")/push the PDF, content JSON, and state/run-log.json.
13. Reply with the title, TL;DR bullets, a GitHub link to the PDF, run number/time, newsletters read, and items deduped out — kept tight, since this becomes the notification.

Never supplement thin source material with model knowledge or web search — if the day is quiet, ship a short brief or skip the run.
