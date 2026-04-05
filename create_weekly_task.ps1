# 创建每周定时任务（中文报告）
$python = "D:\CoPaw\copaw-env\Scripts\python.exe"
$script = "D:\GitHub\meta-harness\weekly_report.py"
$outputDir = "D:\CoPaw\OB-CoPaw\周报"

# 中文报告
$arg = "$script --lang zh --days 7 --output `"$outputDir\%DATE:~0,4%-%DATE:~5,2%-%DATE:~8,2%_质量周报.txt`""

$action = New-ScheduledTaskAction -Execute $python -Argument $arg
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 9am
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# 先删除旧任务
Unregister-ScheduledTask -TaskName "Meta-Harness-周报" -Confirm:$false -ErrorAction SilentlyContinue

# 创建新任务
Register-ScheduledTask -TaskName "Meta-Harness-周报" -Action $action -Trigger $trigger -Settings $settings -Description "每周一生成 Meta-Harness 质量周报（中文）"

Write-Host "✅ 定时任务已更新为中文报告！每周一 9:00 自动生成"