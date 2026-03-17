@echo off
REM Silver Tier - Task Scheduler Setup
REM Run this file as Administrator to complete Silver Tier requirement #7

echo ============================================================
echo Silver Tier - Task Scheduler Setup
echo ============================================================
echo.
echo This will create scheduled tasks for all AI Employee watchers.
echo.

echo Creating WhatsApp Watcher task...
schtasks /create /tn "AI_Watcher_WhatsApp" /tr "python C:\Users\PMLS\Desktop\Hackathon-0\Silver-tier\AI_Employee_Vault\scripts\whatsapp_watcher.py" /sc ONSTART /rl HIGHEST /f

echo Creating LinkedIn Watcher task...
schtasks /create /tn "AI_Watcher_LinkedIn" /tr "python C:\Users\PMLS\Desktop\Hackathon-0\Silver-tier\AI_Employee_Vault\scripts\linkedin_watcher.py" /sc ONSTART /rl HIGHEST /f

echo Creating Gmail Watcher task...
schtasks /create /tn "AI_Watcher_Gmail" /tr "python C:\Users\PMLS\Desktop\Hackathon-0\Silver-tier\AI_Employee_Vault\scripts\gmail_watcher.py" /sc ONSTART /rl HIGHEST /f

echo Creating Email MCP Server task...
schtasks /create /tn "AI_MCP_Email" /tr "node C:\Users\PMLS\Desktop\Hackathon-0\Silver-tier\mcp\email_mcp.js" /sc ONSTART /rl HIGHEST /f

echo.
echo ============================================================
echo Verifying tasks...
echo ============================================================
schtasks /query /fo LIST | findstr "AI_"

echo.
echo ============================================================
echo Setup Complete!
echo ============================================================
echo.
echo To run tasks manually:
echo   schtasks /run /tn "AI_Watcher_WhatsApp"
echo   schtasks /run /tn "AI_Watcher_LinkedIn"
echo   schtasks /run /tn "AI_Watcher_Gmail"
echo   schtasks /run /tn "AI_MCP_Email"
echo.
echo To delete tasks:
echo   schtasks /delete /tn "AI_Watcher_WhatsApp" /f
echo.
pause
