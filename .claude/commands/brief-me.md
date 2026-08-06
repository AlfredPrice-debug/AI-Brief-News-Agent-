---
description: Save the most recently published Impact Makers AI Brief PDF to the AI News & Tips folder and link it on GitHub.
---

Deliver the most recently published AI Brief PDF from the repo's `briefs/` folder by **saving a copy to a local folder** and reporting the link. Don't generate a new brief — that's what `/ai-brief` is for. **Do not open the PDF** — no `Invoke-Item`, no `start`, no launching a viewer. Just place the file and report.

**Destination folder:**
```
C:\Users\AlfredPrice\OneDrive - IM\Desktop\All Things Code\AI News & Tips
```

1. **Locate the repo.** This command may be invoked from a folder that isn't the checkout (or isn't a git repo at all), so never assume the working directory. Run `git rev-parse --show-toplevel`; if that succeeds AND the result contains a `briefs/` folder, use it. Otherwise fall back to the known local checkout:
   `C:\Users\AlfredPrice\OneDrive - IM\Desktop\All Things Code\AI News & Tips\Ai Briefs Repo`
   Run every git command below against that path (`git -C "<repo>" ...`). If neither resolves to a real checkout, say so and stop.
2. **Sync.** `git -C "<repo>" fetch origin main`. Check `git -C "<repo>" status --short --branch` first — if the working tree is dirty or the branch is ahead, leave it alone and just read from `origin/main`; never discard uncommitted work to satisfy this command.
3. **Find the latest brief.** `git -C "<repo>" log -1 --format='%H%n%s' origin/main -- 'briefs/*.pdf'` gives the commit hash and its subject line (format: `brief: YYYY-MM-DD run <N> - <title>`). Then `git -C "<repo>" show --name-only --pretty=format: <hash> -- 'briefs/*.pdf'` gives the exact filename. Reading from `origin/main` means commits that skipped delivery — which never touch `briefs/` — are naturally passed over.
4. **Place the PDF in the destination folder**, keeping its published filename. Read it straight out of `origin/main` so a stale working tree can't hand you an older file:
   ```
   git -C "<repo>" show origin/main:"briefs/<filename>" > "<destination>\<filename>"
   ```
   Use `-LiteralPath` on any PowerShell path handling — the filenames contain commas, apostrophes, and `$`, which break ordinary path parsing. If the file is already there with identical content, leave it and say so rather than rewriting it. Confirm the written file is a valid non-empty PDF (starts with `%PDF`, size matches the blob) before reporting success.
5. **Report**, in a few lines:
   - the title and date parsed from the commit subject, plus run number and short commit hash
   - the full local path where you saved it
   - the GitHub link: `https://github.com/AlfredPrice-debug/AI-Brief-News-Agent-/blob/main/briefs/<filename>`, filename percent-encoded (`python -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "<filename>"`)
6. If `briefs/` holds no PDFs at all, say so plainly instead of saving anything.
