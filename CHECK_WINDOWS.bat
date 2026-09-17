@echo off
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
    python -m cutguard doctor
) else (
    py -3 -m cutguard doctor
)
echo.
echo Copy the result if you need help. This check does not change your PC.
pause
