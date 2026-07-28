# run-brief.ps1
# OPTIONAL LOCAL ALTERNATIVE — the live setup runs as a cloud Claude Code Remote
# Routine (see ROUTINE.md); this script is only for running the brief unattended
# on your own machine instead. Note that INSTRUCTIONS.md / build_brief.py are
# currently written for the cloud setup (no local-folder-copy step, no email
# step) — adapt those first if you want this local path to save a desktop copy
# or send mail.
#
# Runs one AI Brief pass unattended via the Claude Code CLI. Fires 3x/weekday
# (7 AM / 1 PM / 5 PM) — the prompt itself works out which run this is from
# state/run-log.json, so this script doesn't need to know or pass a run number.
# Called by the "AI Brief 3x Daily" scheduled task (see install-task.ps1).
#
# PERMISSIONS: an unattended run has no one to approve tool use (reading mail,
# running Python, git push). You must pre-authorize those,
# in ONE of two ways — pick what you're comfortable with:
#   (A) SCOPED ALLOWLIST (safer): keep a .claude/settings.json in this repo that
#       pre-approves only the specific tools the routine needs. See ROUTINE.md.
#   (B) FULL BYPASS (simplest, less safe): append the skip-permissions flag to the
#       claude command below yourself. Only do this if you accept that the run can
#       use any tool without asking. Do NOT enable it until you've tested manually.
# Until you choose one, an unattended run may stall on the first permission prompt.

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $repo

$log = Join-Path $repo "briefs\run-log.txt"
function Log($m) { "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $m | Out-File -Append -Encoding utf8 $log }

$claude = (Get-Command claude -ErrorAction SilentlyContinue).Source
if (-not $claude) {
  Log "ERROR: 'claude' CLI not found on PATH. Install Claude Code or add it to PATH."
  exit 1
}

$prompt = Get-Content (Join-Path $repo "prompt.txt") -Raw

Log "Starting AI Brief run using $claude"
& $claude -p $prompt *>> $log     # <-- add your chosen permission flag here (see header)
Log "Finished (exit code $LASTEXITCODE)"
exit $LASTEXITCODE
