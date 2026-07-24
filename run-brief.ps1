# run-brief.ps1
# Runs the daily AI Brief unattended via the Claude Code CLI.
# Called by the "AI Brief Daily" scheduled task (see install-task.ps1).
#
# PERMISSIONS: an unattended run has no one to approve tool use (reading mail,
# running Python, git push, sending the self-email). You must pre-authorize those,
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
