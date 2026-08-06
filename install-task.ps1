# install-task.ps1
# OPTIONAL LOCAL ALTERNATIVE — the live setup runs as a cloud Claude Code Remote
# Routine (see ROUTINE.md). Use this only if you want to run the brief on your
# own machine instead (e.g. for a locally-synced copy) rather than the cloud.
#
# Registers a Windows Scheduled Task that runs the AI Brief twice a day:
# 8:00 AM and 4:00 PM Eastern, so nothing that lands mid-day is missed. This
# mirrors the two cloud Routines in ROUTINE.md.
#
# Run it once, from this repo folder, in PowerShell:
#     powershell -NoProfile -ExecutionPolicy Bypass -File .\install-task.ps1
#
# It does NOT require admin (runs as you, only while you're logged on).
# To change the times, edit the $Times value below.
# To remove the task later:  Unregister-ScheduledTask -TaskName "AI Brief 2x Daily" -Confirm:$false

$TaskName = "AI Brief 2x Daily"
$Times    = "08:00","16:00"    # 8 AM (run 1), 4 PM (run 2)

$repo   = Split-Path -Parent $MyInvocation.MyCommand.Definition
$runner = Join-Path $repo "run-brief.ps1"

if (-not (Test-Path $runner)) { throw "run-brief.ps1 not found next to this script." }

$action = New-ScheduledTaskAction -Execute "powershell.exe" `
  -Argument ("-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"{0}`"" -f $runner)

# One trigger per time-of-day; run-brief.ps1 picks prompt-morning.txt or
# prompt-afternoon.txt by the clock, so both triggers share the same action.
$triggers = $Times | ForEach-Object { New-ScheduledTaskTrigger -Daily -At ([datetime]$_) }

# Runs in your interactive session (so OneDrive + the connector are available).
# StartWhenAvailable catches up if the machine was busy; WakeToRun wakes it from sleep.
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -WakeToRun `
  -DontStopIfGoingOnBatteries -AllowStartIfOnBatteries -MultipleInstances IgnoreNew

$principal = New-ScheduledTaskPrincipal -UserId ("{0}\{1}" -f $env:USERDOMAIN, $env:USERNAME) `
  -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $triggers `
  -Settings $settings -Principal $principal `
  -Description "Builds the Impact Makers AI Brief twice a day (8 AM / 4 PM)." -Force | Out-Null

Write-Host "Installed scheduled task '$TaskName' — daily at $($Times -join ', ')."
Write-Host "Test it now with:  Start-ScheduledTask -TaskName '$TaskName'"
Write-Host "Then check briefs\run-log.txt, state\run-log.json, and your output folder(s)."
