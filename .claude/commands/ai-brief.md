---
description: Build today's one-page Impact Makers AI Brief PDF from newsletters in Outlook.
---

Run the daily AI Brief routine for me, following INSTRUCTIONS.md in this repo.

1. Search my Outlook folder "Claude AI News Recap" for newsletters received in the last 24 hours (newest first). NEVER read the Junk folder. Stay read-only on existing mail — do not delete or move anything. (The only message you may send is the delivery email to my own work address in step 9.)
2. Read each newsletter. If a body is large HTML that would overflow context, hand the saved file to a subagent to slice it in ~80,000-char spans and summarize it (headlines, facts, any "skill/tip of the day" with verbatim prompts, notable tools).
3. Classify the material into two buckets:
   - AI TIPS — things that help me use AI better or be aware of a change. Write each as step-by-step how-to. Capture any good copy-paste prompt verbatim.
   - AI NEWS — state the news first, then a "What it means for you" line through the lens of a Product Manager / Consultant / AI Engineer. Mark low-impact items "low": true.
4. Curate to fit ONE page: about 3 AI Tips and 3–4 AI News items. Skip ads, sponsors, and general non-AI content.
5. Write an eye-catching title summarizing the day's 2–3 biggest items (NO date in the title).
6. Save the curated content to content/<today's date YYYY-MM-DD>.json using the schema in the example content file.
7. Build the PDF:  python build/build_brief.py content/<today's date>.json
8. Confirm the PDF is one page.
9. Deliver it (so I can read it away from my desk):
   a) EMAIL: send me an HTML copy at my own work address. Use the eye-catching title as the subject, and put the AI Tips + AI News as a clean HTML body (headings, bold, and lists only — email strips CSS, so don't rely on styling; this is a readable text version, not the styled PDF).
   b) GITHUB: copy the PDF into this repo's `briefs/` folder, then `git add`, `git commit`, and `git push` so it's downloadable from GitHub on any device.
10. Reply with the title, the saved local path, and confirm the email was sent and the PDF pushed to GitHub.

If there were no new newsletters in the last 24 hours, tell me that instead of inventing content — and do not send an email or push anything.
