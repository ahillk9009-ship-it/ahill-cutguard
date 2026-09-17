@echo off
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
    python -m cutguard gui
) else (
    py -3 -m cutguard gui
)
if errorlevel 1 pause
