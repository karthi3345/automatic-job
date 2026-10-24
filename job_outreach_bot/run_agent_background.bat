@echo off
title Job Outreach Agent 24/7 Production Runner
cd /d "%~dp0\.."

echo =======================================================
echo   Starting 24/7 Job Outreach Production Agent
echo =======================================================
echo.

.\venv\Scripts\python.exe job_outreach_bot\scheduler_daemon.py

pause
