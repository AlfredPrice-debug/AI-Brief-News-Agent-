---
description: Send the most recently published Impact Makers AI Brief PDF into this chat.
---

Find the most recently published AI Brief PDF in this repo's `briefs/` folder and send it into this chat. Don't generate a new brief — that's what `/ai-brief` is for.

1. Make sure the local checkout has the latest `main`: `git fetch origin main`, then bring your working branch up to date with it (merge or reset as appropriate — check `git status` first and don't discard uncommitted work if any exists).
2. Find the latest brief PDF: `git log -1 --format=%H -- 'briefs/*.pdf'` to get the most recent commit that touched a PDF under `briefs/` on `origin/main`, then `git show --name-only --pretty=format: <that-commit> -- 'briefs/*.pdf'` to get its exact filename. (Commits that skip delivery never touch `briefs/`, so this naturally skips over them to the last real brief.)
3. Use the SendUserFile tool to send that PDF into the chat (status: "normal"). Caption it with the brief's title and date — pull both from the commit message (`brief: YYYY-MM-DD run <N> - <title>`) via `git log -1 --format=%s -- 'briefs/*.pdf'`.
4. If `briefs/` has no PDFs at all, say so plainly instead of sending anything.
