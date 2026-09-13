#!/usr/bin/env python3
"""Post a Discord notification for a newly published AI Brief.

Usage:
    python build/notify_discord.py <content.json> <pdf_relpath_or_empty> <owner/repo>

Reads the webhook URL from the DISCORD_WEBHOOK_URL environment variable.
Posts the brief's title, TL;DR, and every Tips/News/Beyond AI item as a
Discord embed (text only -- the PDF itself is linked, never uploaded).
Invoked by .github/workflows/discord-notify.yml on every push that adds a
new content/*.json file.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

BRAND_COLOR = 0xD8A928  # Impact Makers gold
EMBED_BUDGET = 5900  # stay under Discord's 6000-char total-embed limit


def html_to_md(s: str) -> str:
    if not s:
        return ""
    s = re.sub(r"</?b>", "**", s)
    s = re.sub(r"</?i>", "*", s)
    s = re.sub(r"<[^>]+>", "", s)
    return s.strip()


def html_to_plain(s: str) -> str:
    """For embed title/footer, which Discord renders as literal text (no markdown)."""
    if not s:
        return ""
    return re.sub(r"<[^>]+>", "", s).strip()


def truncate(s: str, n: int) -> str:
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def split_headline(body_html: str):
    """Pull the leading <b>...</b> out of an item body as its headline."""
    m = re.match(r"\s*<b>(.*?)</b>\s*(.*)", body_html or "", re.S)
    if m:
        return html_to_md(m.group(1)), html_to_md(m.group(2))
    return None, html_to_md(body_html)


def gh_blob_url(repo: str, path: str) -> str:
    quoted = "/".join(urllib.parse.quote(part) for part in path.split("/"))
    return f"https://github.com/{repo}/blob/main/{quoted}"


def build_fields(content: dict) -> list:
    fields = []

    for t in content.get("tips", []):
        name = truncate(f"\U0001F4A1 {html_to_md(t.get('heading', ''))}", 256)
        steps = [html_to_md(s) for s in t.get("steps", [])]
        value = "\n".join(f"{i + 1}. {s}" for i, s in enumerate(steps))
        if t.get("prompt"):
            value += f"\n```\n{t['prompt']}\n```"
        if t.get("source"):
            value += f"\n_Source: {html_to_md(t['source'])}_"
        fields.append({"name": name, "value": truncate(value, 1024)})

    for n in content.get("news", []):
        headline, rest = split_headline(n.get("body", ""))
        label = "\U0001F5DE️ AI NEWS" + (" (low impact)" if n.get("low") else "")
        name = truncate(f"{label}: {headline}" if headline else label, 256)
        value = rest
        if n.get("means"):
            value += f"\n**What it means for you:** {html_to_md(n['means'])}"
        if n.get("source"):
            value += f"\n_Source: {html_to_md(n['source'])}_"
        fields.append({"name": name, "value": truncate(value, 1024)})

    for b in content.get("beyond_ai", []):
        headline, rest = split_headline(b.get("body", ""))
        name = truncate(f"\U0001F30E BEYOND AI: {headline}" if headline else "\U0001F30E BEYOND AI", 256)
        value = rest
        if b.get("angle"):
            value += f"\n**PM angle:** {html_to_md(b['angle'])}"
        if b.get("starter"):
            value += f"\n**Conversation starter:** {html_to_md(b['starter'])}"
        if b.get("source"):
            value += f"\n_Source: {html_to_md(b['source'])}_"
        fields.append({"name": name, "value": truncate(value, 1024)})

    return fields[:25]  # Discord's hard per-embed field cap


def cap_to_budget(embed: dict) -> None:
    """Drop trailing fields if the embed would exceed Discord's total-char limit."""
    used = len(embed["title"]) + len(embed["description"]) + len(embed["footer"]["text"])
    kept = []
    for f in embed["fields"]:
        size = len(f["name"]) + len(f["value"])
        if used + size > EMBED_BUDGET:
            break
        kept.append(f)
        used += size
    if len(kept) < len(embed["fields"]):
        print(f"NOTE: trimmed {len(embed['fields']) - len(kept)} field(s) to fit Discord's embed size limit.")
    embed["fields"] = kept


def main():
    if len(sys.argv) < 4:
        sys.exit("Usage: notify_discord.py <content.json> <pdf_relpath_or_empty> <owner/repo>")
    content_path, pdf_relpath, repo = sys.argv[1], sys.argv[2], sys.argv[3]

    webhook = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook:
        sys.exit(
            "DISCORD_WEBHOOK_URL is not set. Add it as a repo secret: "
            "Settings > Secrets and variables > Actions > New repository secret."
        )

    with open(content_path, encoding="utf-8") as f:
        content = json.load(f)

    title = content.get("title", "Impact Makers AI Brief")
    tldr = [html_to_md(b) for b in content.get("tldr", [])]
    description = "\n".join(f"• {b}" for b in tldr)

    pdf_url = gh_blob_url(repo, pdf_relpath) if pdf_relpath else None
    if pdf_url:
        description += f"\n\n[\U0001F4C4 Full PDF]({pdf_url})"

    run = content.get("run")
    run_time = content.get("runTime", "")
    sources = html_to_plain(content.get("sources", ""))
    footer_text = " · ".join(x for x in [f"Run {run}" if run else "", run_time, sources] if x)

    embed = {
        "title": truncate(html_to_plain(f"\U0001F4F0 {title}"), 256),
        "description": truncate(description, 4096),
        "color": BRAND_COLOR,
        "fields": build_fields(content),
        "footer": {"text": truncate(footer_text, 2048)},
    }
    if pdf_url:
        embed["url"] = pdf_url
    cap_to_budget(embed)

    payload = {"embeds": [embed]}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(webhook, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"Discord webhook responded: {resp.status}")
    except urllib.error.HTTPError as e:
        print(f"Discord webhook error {e.code}: {e.read().decode('utf-8', 'replace')}", file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
