@echo off
echo Starting build process...
if not exist "assets" (
    echo Error: assets directory not found!
    pause
    exit /b
)

echo Cleaning up previous builds...
rmdir /s /q build dist
del /q *.spec

echo Building EXE...
pyinstaller --noconsole --onefile --name "mmticktock" --add-data "assets;assets" main.py

if %errorlevel% neq 0 (
    echo Build failed!
    pause
    exit /b
)

echo.
echo Build successful!
echo The executable is located in the "dist" folder.
echo.
pause
