# install-task.ps1
# Registers a Windows Scheduled Task that runs the AI Brief every weekday morning.
#
# Run it once, from this repo folder, in PowerShell:
#     powershell -NoProfile -ExecutionPolicy Bypass -File .\install-task.ps1
#
# It does NOT require admin (runs as you, only while you're logged on).
# To change the time or days, edit the $At / $Days values below.
# To remove the task later:  Unregister-ScheduledTask -TaskName "AI Brief Daily" -Confirm:$false

$TaskName = "AI Brief Daily"
$At       = "07:00"                                             # 7:00 AM
$Days     = "Monday","Tuesday","Wednesday","Thursday","Friday"  # weekdays only

$repo   = Split-Path -Parent $MyInvocation.MyCommand.Definition
$runner = Join-Path $repo "run-brief.ps1"

if (-not (Test-Path $runner)) { throw "run-brief.ps1 not found next to this script." }

$action = New-ScheduledTaskAction -Execute "powershell.exe" `
  -Argument ("-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"{0}`"" -f $runner)

$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $Days -At ([datetime]$At)

# Runs in your interactive session (so OneDrive + the connector are available).
# StartWhenAvailable catches up if the machine was busy; WakeToRun wakes it from sleep.
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -WakeToRun `
  -DontStopIfGoingOnBatteries -AllowStartIfOnBatteries

$principal = New-ScheduledTaskPrincipal -UserId ("{0}\{1}" -f $env:USERDOMAIN, $env:USERNAME) `
  -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger `
  -Settings $settings -Principal $principal `
  -Description "Builds the Impact Makers AI Brief each weekday morning." -Force | Out-Null

Write-Host "Installed scheduled task '$TaskName' — weekdays at $At."
Write-Host "Test it now with:  Start-ScheduledTask -TaskName '$TaskName'"
Write-Host "Then check briefs\run-log.txt and your output folder."
