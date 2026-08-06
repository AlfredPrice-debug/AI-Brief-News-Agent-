---
description: Open the most recently published Impact Makers AI Brief PDF and link it on GitHub.
---

Deliver the most recently published AI Brief PDF from the repo's `briefs/` folder. Don't generate a new brief — that's what `/ai-brief` is for.

1. **Locate the repo.** This command may be invoked from a folder that isn't the checkout (or isn't a git repo at all), so never assume the working directory. Run `git rev-parse --show-toplevel`; if that succeeds AND the result contains a `briefs/` folder, use it. Otherwise fall back to the known local checkout:
   `C:\Users\AlfredPrice\OneDrive - IM\Desktop\All Things Code\AI News & Tips\Ai Briefs Repo`
   Run every git command below against that path (`git -C "<repo>" ...`). If neither resolves to a real checkout, say so and stop.
2. **Sync.** `git -C "<repo>" fetch origin main`. Check `git -C "<repo>" status --short --branch` first — if the working tree is dirty or the branch is ahead, leave it alone and just read from `origin/main`; never discard uncommitted work to satisfy this command.
3. **Find the latest brief.** `git -C "<repo>" log -1 --format='%H%n%s' origin/main -- 'briefs/*.pdf'` gives the commit hash and its subject line (format: `brief: YYYY-MM-DD run <N> - <title>`). Then `git -C "<repo>" show --name-only --pretty=format: <hash> -- 'briefs/*.pdf'` gives the exact filename. Reading from `origin/main` means commits that skipped delivery — which never touch `briefs/` — are naturally passed over.
4. **Deliver it.** There is no tool in this environment for attaching a file to the chat, so do both of these instead:
   - **Open it locally:** `Invoke-Item -LiteralPath "<repo>\briefs\<filename>"` via PowerShell (use `-LiteralPath` — the filenames contain commas, apostrophes, and `$`, which break ordinary path parsing). If the file isn't in the working tree — e.g. the checkout is behind — pull it out with `git -C "<repo>" show origin/main:"briefs/<filename>" > "<some temp path>"` and open that.
   - **Link it on GitHub:** `https://github.com/AlfredPrice-debug/AI-Brief-News-Agent-/blob/main/briefs/<filename>`, with the filename percent-encoded (`python -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "<filename>"`).
5. **Report** the title and date parsed out of the commit subject, the run number, and the commit hash — then the link. Keep it short.
6. If `briefs/` holds no PDFs at all, say so plainly instead of sending anything.
