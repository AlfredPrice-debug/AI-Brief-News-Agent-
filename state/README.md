# state/run-log.json

Tracks what's already been published today so the 7 AM / 1 PM / 5 PM runs never duplicate a story or re-query mail they've already seen. Read and updated by Claude Code directly as part of `INSTRUCTIONS.md` steps 1 and 11 — there is no separate build step for it.

## Schema

```json
{
  "days": {
    "2026-07-28": {
      "runs": [
        {
          "run": 1,
          "timestamp": "2026-07-28T07:00:00-04:00",
          "status": "delivered",
          "covered": ["anthropic|releases|computer-use-ga", "openai|raises|series-f"]
        },
        {
          "run": 2,
          "timestamp": "2026-07-28T13:00:00-04:00",
          "status": "skipped_no_mail",
          "covered": []
        }
      ]
    }
  }
}
```

- Keyed by calendar date (`YYYY-MM-DD`, America/New_York).
- `runs` is append-only, one entry per run attempt for that date, in order.
- `status` is one of:
  - `delivered` — a brief was built, verified, delivered, and pushed. `covered` lists every fingerprint published in that run.
  - `skipped_no_mail` — zero new messages since the last successful run. `covered` is empty.
  - `skipped_thin` — new mail existed but fewer than 2 items survived dedup. `covered` is empty; note any rolled-forward items in a `rollover` array if you want the next run to see them explicitly (optional — the next run's own mail query will re-surface them anyway since nothing was marked covered).
- To find "today's covered fingerprints" for step 4 dedup, concatenate `covered` across every entry in `days[today].runs`.
- To find "the last successful run's timestamp" for step 2's mail query, take the `timestamp` of the most recent entry with `status: "delivered"` across today and, if none yet today, yesterday's last entry (falls back further if a whole day was skipped).
- Fingerprints reset at midnight simply because a new date key starts empty.

Committed to the repo alongside each brief's PDF (`INSTRUCTIONS.md` step 11), including skip-only runs, so the log survives across machines/sessions.
