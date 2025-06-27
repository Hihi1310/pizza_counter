@echo off
setlocal enabledelayedexpansion
REM Simple Pizza Counter Helper for Windows

if "%1"=="setup" goto :setup
if "%1"=="zone" goto :zone
if "%1"=="build" goto :build
if "%1"=="process" goto :process
if "%1"=="clean" goto :clean
goto :usage

:usage
echo 🍕 Pizza Counter Helper
echo Usage: %0 [COMMAND]
echo.
echo Commands:
echo   setup     - Create directories
echo   zone      - Set up counting zone
echo   build     - Build Docker image
echo   process   - Process video (place in input\ first)
echo   clean     - Clean output files
echo.
goto :end

:setup
echo Creating directories...
if not exist "input" mkdir input
if not exist "output" mkdir output
if not exist "logs" mkdir logs
echo ✅ Done! Place videos in input\ folder
goto :end

:zone
echo Setting up counting zone...
python zone_setup.py
goto :end

:build
echo Building Docker image...
docker-compose build pizza-counter
echo ✅ Build complete!
goto :end

:process
echo Checking for videos in input directory...
dir /b input\*.mp4 input\*.avi input\*.mov input\*.mkv >nul 2>&1
if errorlevel 1 (
    echo ❌ No videos found in input\ directory
    exit /b 1
)
echo Processing videos...
for %%f in (input\*.mp4 input\*.avi input\*.mov input\*.mkv) do (
    echo 📹 Processing: %%f
    set "filename=%%~nxf"
    docker-compose run --rm pizza-counter python app.py --video "/app/input/!filename!" --save-video
)
echo ✅ Processing complete! Check output\ folder
goto :end

:clean
set /p "confirm=Delete all output files? (y/N): "
if /i "%confirm%"=="y" (
    if exist "output" rmdir /s /q output
    if exist "logs" rmdir /s /q logs
    mkdir output
    mkdir logs
    echo ✅ Cleaned up!
)
goto :end

:end
