@echo off
echo === DriftCoach Video Analysis Setup ===
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Install from https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python found

:: Install anthropic
echo Installing anthropic SDK...
pip install anthropic
echo [OK] anthropic installed

:: Check for choco
choco --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Chocolatey not found. Installing ffmpeg manually...
    echo Download ffmpeg from https://www.gyan.dev/ffmpeg/builds/
    echo Extract it and add the bin folder to your PATH
    echo Then re-run this script.
    pause
    exit /b 1
)

:: Install ffmpeg via choco
echo Installing ffmpeg...
choco install ffmpeg -y
echo [OK] ffmpeg installed

echo.
echo === Setup Complete ===
echo.
echo Next steps:
echo 1. Set your Anthropic API key:
echo    set ANTHROPIC_API_KEY=your-key-here
echo.
echo 2. Record a clip in AC, then run:
echo    python tools\analyze_video.py your_clip.mp4 --output reference\analysis.txt
echo.
pause
