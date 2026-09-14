#!/usr/bin/env python3
"""Post a newly published AI Brief into Discord as plain text.

Usage:
    python build/notify_discord.py <content.json> [pdf_relpath] [owner/repo]

Posts the brief's full text -- title, TL;DR, and every Tips/News/Beyond AI
item -- as a sequence of plain Discord messages, splitting on item
boundaries so nothing is ever truncated. The PDF is linked on the last
message, never uploaded.

Environment:
    DISCORD_WEBHOOK_URL  (required) webhook URL for the target channel.
    DISCORD_ROLE_ID      (optional) role to ping on the first message.
                         Unset means the brief posts with no ping.
    DISCORD_USERNAME     (optional) display name, defaults to the bot name.
    DRY_RUN=1            (optional) print the messages instead of posting.

Invoked by .github/workflows/discord-notify.yml on every push that adds a
new content/*.json, and on demand via that workflow's manual trigger.
"""
import glob
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# Discord caps a message's content at 2000 characters. Pack to a little under
# that so a block never lands right on the boundary.
MSG_LIMIT = 1900
DEFAULT_USERNAME = "Corduroy the Claude Bot"
SUPPRESS_EMBEDS = 1 << 2  # keep the PDF link from expanding into a preview card
PAUSE_BETWEEN_POSTS = 0.7  # webhooks allow ~5 requests per 2 seconds
# Discord is fronted by Cloudflare, which 403s urllib's default
# "Python-urllib/3.x" agent string outright -- especially from datacenter IPs
# like GitHub Actions runners. Discord documents this header's shape.
USER_AGENT = "DiscordBot (https://github.com/AlfredPrice-debug/AI-Brief-News-Agent-, 1.0)"


def md(s: str) -> str:
    """HTML from the content JSON -> Discord markdown."""
    if not s:
        return ""
    s = re.sub(r"</?b>", "**", s)
    s = re.sub(r"</?i>", "*", s)
    s = re.sub(r"<[^>]+>", "", s)
    return s.strip()


def plain(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s or "").strip()


def split_headline(body_html: str):
    """Pull the leading <b>...</b> out of an item body as its headline."""
    m = re.match(r"\s*<b>(.*?)</b>\s*(.*)", body_html or "", re.S)
    if m:
        return md(m.group(1)), md(m.group(2))
    return None, md(body_html)


def check_webhook(url: str) -> None:
    """Catch the common mixup of pasting the channel link (the address you see
    in a browser) instead of the webhook URL (the thing that can post)."""
    if re.match(r"https://(?:ptb\.|canary\.)?discord(?:app)?\.com/api/(?:v\d+/)?webhooks/\d+/\S+", url):
        return
    if "/channels/" in url:
        sys.exit(
            "DISCORD_WEBHOOK_URL looks like a Discord channel link, not a webhook URL. "
            "A webhook URL looks like https://discord.com/api/webhooks/<id>/<token> and comes "
            "from the channel's Settings > Integrations > Webhooks > Copy Webhook URL."
        )
    sys.exit(
        "DISCORD_WEBHOOK_URL does not look like a Discord webhook URL "
        "(expected https://discord.com/api/webhooks/<id>/<token>)."
    )


def gh_blob_url(repo: str, path: str) -> str:
    quoted = "/".join(urllib.parse.quote(part) for part in path.split("/"))
    return f"https://github.com/{repo}/blob/main/{quoted}"


def find_pdf(content: dict) -> str:
    """Locate this run's PDF in briefs/ when the caller didn't name one.

    build_brief.py writes '<Title>_<M_D_YY>_run<N>.pdf', so the date slug and
    run number identify it without having to re-derive the sanitized title.
    """
    slug = content.get("date_slug")
    run = content.get("run")
    if not slug:
        return ""
    pattern = f"briefs/*_{slug}_run{run}.pdf" if run else f"briefs/*_{slug}.pdf"
    matches = sorted(glob.glob(pattern))
    return matches[0] if matches else ""


def build_blocks(content: dict) -> list:
    """The brief as a list of atomic chunks. A chunk is never split across
    messages unless it is single-handedly too big for one."""
    blocks = []

    title = md(content.get("title", "")) or "Impact Makers AI Brief"
    head = f"## {title}"
    tldr = [md(b) for b in content.get("tldr", []) if md(b)]
    if tldr:
        head += "\n" + "\n".join(f"- {b}" for b in tldr)
    blocks.append(head)

    for t in content.get("tips", []):
        heading = md(t.get("heading", ""))
        parts = [f"### AI TIP: {heading}" if heading else "### AI TIP"]
        steps = [md(s) for s in t.get("steps", []) if md(s)]
        if steps:
            parts.append("\n".join(f"{i + 1}. {s}" for i, s in enumerate(steps)))
        if t.get("prompt"):
            parts.append(f"```\n{t['prompt']}\n```")
        if t.get("source"):
            parts.append(f"-# Source: {md(t['source'])}")
        blocks.append("\n".join(parts))

    for n in content.get("news", []):
        headline, rest = split_headline(n.get("body", ""))
        label = "AI NEWS (low impact)" if n.get("low") else "AI NEWS"
        parts = [f"### {label}: {headline}" if headline else f"### {label}"]
        if rest:
            parts.append(rest)
        if n.get("means"):
            parts.append(f"**What it means for you:** {md(n['means'])}")
        if n.get("source"):
            parts.append(f"-# Source: {md(n['source'])}")
        blocks.append("\n".join(parts))

    for b in content.get("beyond_ai", []):
        headline, rest = split_headline(b.get("body", ""))
        parts = [f"### BEYOND AI: {headline}" if headline else "### BEYOND AI"]
        if rest:
            parts.append(rest)
        if b.get("angle"):
            parts.append(f"**PM angle:** {md(b['angle'])}")
        if b.get("starter"):
            parts.append(f"**Conversation starter:** {md(b['starter'])}")
        if b.get("source"):
            parts.append(f"-# Source: {md(b['source'])}")
        blocks.append("\n".join(parts))

    return blocks


def build_footer(content: dict, pdf_url: str) -> str:
    lines = []
    if pdf_url:
        lines.append(f"[Full PDF]({pdf_url})")
    run = content.get("run")
    # date_display ("Sunday, September 13, 2026") reads better here than the
    # raw ISO runTime the content JSON carries for the PDF build.
    meta = [f"Run {run}" if run else "", content.get("date_display", ""), plain(content.get("sources", ""))]
    meta = " · ".join(x for x in meta if x)
    if meta:
        lines.append(f"-# {meta}")
    return "\n".join(lines)


def hard_split(block: str, limit: int) -> list:
    """Last resort for a single chunk that exceeds one message on its own.
    Breaks on line boundaries first, then mid-line only if a line is itself
    longer than the limit."""
    out, buf = [], ""
    for line in block.split("\n"):
        while len(line) > limit:
            out.append((buf + "\n" + line[:limit]).strip() if buf else line[:limit])
            buf, line = "", line[limit:]
        candidate = f"{buf}\n{line}" if buf else line
        if len(candidate) > limit:
            out.append(buf)
            buf = line
        else:
            buf = candidate
    if buf:
        out.append(buf)
    return out


def pack(blocks: list, limit: int = MSG_LIMIT) -> list:
    """Greedily fit whole blocks into messages, largest-first order preserved."""
    messages, buf = [], ""
    for block in blocks:
        if not block:
            continue
        if len(block) > limit:
            if buf:
                messages.append(buf)
                buf = ""
            messages.extend(hard_split(block, limit))
            continue
        candidate = f"{buf}\n\n{block}" if buf else block
        if len(candidate) > limit:
            messages.append(buf)
            buf = block
        else:
            buf = candidate
    if buf:
        messages.append(buf)
    return messages


def post(webhook: str, body: dict) -> None:
    """POST one message, honoring Discord's rate-limit backoff."""
    url = webhook + ("&" if "?" in webhook else "?") + "wait=true"
    data = json.dumps(body).encode("utf-8")
    for attempt in range(5):
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json", "User-Agent": USER_AGENT},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req) as resp:
                print(f"  posted ({resp.status})")
                return
        except urllib.error.HTTPError as e:
            payload = e.read().decode("utf-8", "replace")
            if e.code == 429:
                try:
                    wait = float(json.loads(payload).get("retry_after", 1))
                except (ValueError, AttributeError):
                    wait = 1.0
                print(f"  rate limited, retrying in {wait:.1f}s")
                time.sleep(wait + 0.1)
                continue
            snippet = payload.strip()[:400] or "(empty response body)"
            hint = ""
            if e.code == 403 and "<html" in payload.lower():
                hint = (
                    "\nThis looks like a Cloudflare block rather than Discord itself "
                    "rejecting the post. Check that the request sets a User-Agent header."
                )
            elif e.code in (401, 404):
                hint = (
                    "\nDiscord did not recognize the webhook. The URL in DISCORD_WEBHOOK_URL "
                    "is probably wrong, or the webhook was deleted in the channel's "
                    "Settings > Integrations > Webhooks."
                )
            sys.exit(f"Discord rejected the post, HTTP {e.code}: {snippet}{hint}")
    raise SystemExit("Gave up after repeated Discord rate limits.")


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: notify_discord.py <content.json> [pdf_relpath] [owner/repo]")
    content_path = sys.argv[1]
    pdf_relpath = sys.argv[2] if len(sys.argv) > 2 else ""
    repo = sys.argv[3] if len(sys.argv) > 3 else os.environ.get("GITHUB_REPOSITORY", "")

    dry_run = os.environ.get("DRY_RUN") == "1"
    webhook = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
    if not webhook:
        if not dry_run:
            sys.exit(
                "DISCORD_WEBHOOK_URL is not set. Add it as a repo secret: "
                "Settings > Secrets and variables > Actions > New repository secret."
            )
        print("DISCORD_WEBHOOK_URL: not set (dry run, so nothing would be posted).")
    else:
        # Shape only. The value itself is a credential and is never printed.
        check_webhook(webhook)
        print("DISCORD_WEBHOOK_URL: set, and its shape looks like a webhook URL.")

    with open(content_path, encoding="utf-8") as f:
        content = json.load(f)

    if not pdf_relpath:
        pdf_relpath = find_pdf(content)
        if pdf_relpath:
            print(f"Resolved PDF: {pdf_relpath}")
    pdf_url = gh_blob_url(repo, pdf_relpath) if (pdf_relpath and repo) else ""
    if pdf_relpath and not repo:
        print("NOTE: no owner/repo given, so the PDF link is omitted.")

    blocks = build_blocks(content)
    footer = build_footer(content, pdf_url)
    if footer:
        blocks.append(footer)
    messages = pack(blocks)

    role_id = (os.environ.get("DISCORD_ROLE_ID") or "").strip()
    username = os.environ.get("DISCORD_USERNAME") or DEFAULT_USERNAME
    # parse:[] blocks every mention Discord would otherwise infer from the
    # text; the explicit roles list is the only thing allowed to ping.
    allowed = {"parse": [], "roles": [role_id]} if role_id else {"parse": []}
    if role_id:
        messages[0] = f"<@&{role_id}>\n{messages[0]}"
    else:
        print("NOTE: DISCORD_ROLE_ID is not set, posting without a ping.")

    print(f"{len(messages)} message(s) to post as '{username}'.")
    for i, msg in enumerate(messages, 1):
        if dry_run:
            print(f"\n----- message {i}/{len(messages)} ({len(msg)} chars) -----\n{msg}")
            continue
        print(f"Posting message {i}/{len(messages)} ({len(msg)} chars)")
        post(webhook, {
            "content": msg,
            "username": username,
            "allowed_mentions": allowed,
            "flags": SUPPRESS_EMBEDS,
        })
        if i < len(messages):
            time.sleep(PAUSE_BETWEEN_POSTS)


if __name__ == "__main__":
    main()
