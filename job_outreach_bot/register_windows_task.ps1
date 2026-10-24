# Create Windows Task Scheduler job to run Job Outreach Agent daily at 9:30 AM
$Action = New-ScheduledTaskAction -Execute "$PSScriptRoot\..\venv\Scripts\python.exe" -Argument "$PSScriptRoot\scheduler_daemon.py --now" -WorkingDirectory "$PSScriptRoot"
$Trigger = New-ScheduledTaskTrigger -Daily -At 9:30AM
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

Register-ScheduledTask -TaskName "DailyJobOutreachAgent" -Action $Action -Trigger $Trigger -Settings $Settings -Description "Automated 200/day Job Application Outreach Agent" -Force

Write-Host "✅ Successfully registered 'DailyJobOutreachAgent' in Windows Task Scheduler!"
Write-Host "The agent will automatically wake up and send 200 applications every morning at 9:30 AM."
