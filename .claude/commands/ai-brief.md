---
description: Build this run's 2-page Impact Makers AI Brief PDF (AI Tips/News + Beyond AI) from newsletters in Outlook.
---

Run the AI Brief routine for me, following INSTRUCTIONS.md in this repo (v2).

1. Read state/run-log.json (create it as {"days": {}} if absent). Work out today's run number and the timestamp of the last successful run — on the very first run of the day, use yesterday's 5:00 PM run instead, so overnight sends are caught.
2. Search ONLY my Outlook folder "Claude AI News Recap" for messages received since that timestamp, newest first. NEVER read Junk or Deleted Items. NEVER search the Inbox or any other folder. Stay read-only on existing mail. (The only message you may send is the single delivery email in step 10.)
3. If there are zero new messages: log a skipped run, send nothing, push nothing, and tell me "No new newsletters since [last run time]." Stop.
4. Read each newsletter (hand large HTML bodies to a subagent to slice and summarize). Discard ads, sponsor blocks, and newsletter housekeeping.
5. Classify into AI TIPS (imperative title + 2-4 numbered steps, verbatim prompt if present), AI NEWS (headline + facts + "What it means for you," mark low-impact "low": true), and BEYOND AI (headline + facts + "PM angle," which may correctly say "No direct relevance to your work, general awareness only," + "Conversation starter").
6. Deduplicate by story fingerprint (entity|action|object) against today's covered list — drop repeats even from a different newsletter. If fewer than 2 items survive, skip the run and roll items forward.
7. Curate to page 1 (AI Tips + AI News) and page 2 (Beyond AI). A third page only on a genuinely heavy news day. Cut lowest-impact items first.
8. Write a title (no date) and three TL;DR bullets.
9. Save to content/<today YYYY-MM-DD>-run<N>.json using the schema in content/2026-07-24-run1.json.
10. Build: python build/build_brief.py content/<file>.json
11. Verify the page count before delivering — never ship an unverified PDF.
12. Copy the PDF to whichever configured desktop folder(s) exist on this machine.
13. Copy it into briefs/, then git add/commit ("brief: YYYY-MM-DD run <N> - <title>")/push, and update state/run-log.json.
14. Email me one HTML copy (title as subject, PDF attached, GitHub link at the bottom).
15. Reply with the title, run number/time, newsletters read, items deduped out, local path(s), and confirmation of email/attachment/push.

Never supplement thin source material with model knowledge or web search — if the day is quiet, ship a short brief or skip the run.
