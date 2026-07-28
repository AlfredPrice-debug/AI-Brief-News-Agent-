# install-task.ps1
# Registers a Windows Scheduled Task that runs the AI Brief three times each weekday:
# 7:00 AM, 1:00 PM, and 5:00 PM Eastern, so nothing that lands mid-day is missed.
#
# Run it once, from this repo folder, in PowerShell:
#     powershell -NoProfile -ExecutionPolicy Bypass -File .\install-task.ps1
#
# It does NOT require admin (runs as you, only while you're logged on).
# To change the times or days, edit the $Times / $Days values below.
# To remove the task later:  Unregister-ScheduledTask -TaskName "AI Brief 3x Daily" -Confirm:$false

$TaskName = "AI Brief 3x Daily"
$Times    = "07:00","13:00","17:00"                             # 7 AM, 1 PM, 5 PM
$Days     = "Monday","Tuesday","Wednesday","Thursday","Friday"  # weekdays only

$repo   = Split-Path -Parent $MyInvocation.MyCommand.Definition
$runner = Join-Path $repo "run-brief.ps1"

if (-not (Test-Path $runner)) { throw "run-brief.ps1 not found next to this script." }

$action = New-ScheduledTaskAction -Execute "powershell.exe" `
  -Argument ("-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"{0}`"" -f $runner)

# One trigger per time-of-day; run-brief.ps1 / prompt.txt work out the run number
# themselves from state/run-log.json, so all three triggers share the same action.
$triggers = $Times | ForEach-Object { New-ScheduledTaskTrigger -Weekly -DaysOfWeek $Days -At ([datetime]$_) }

# Runs in your interactive session (so OneDrive + the connector are available).
# StartWhenAvailable catches up if the machine was busy; WakeToRun wakes it from sleep.
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -WakeToRun `
  -DontStopIfGoingOnBatteries -AllowStartIfOnBatteries -MultipleInstances IgnoreNew

$principal = New-ScheduledTaskPrincipal -UserId ("{0}\{1}" -f $env:USERDOMAIN, $env:USERNAME) `
  -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $triggers `
  -Settings $settings -Principal $principal `
  -Description "Builds the Impact Makers AI Brief three times each weekday (7 AM / 1 PM / 5 PM)." -Force | Out-Null

Write-Host "Installed scheduled task '$TaskName' — weekdays at $($Times -join ', ')."
Write-Host "Test it now with:  Start-ScheduledTask -TaskName '$TaskName'"
Write-Host "Then check briefs\run-log.txt, state\run-log.json, and your output folder(s)."
