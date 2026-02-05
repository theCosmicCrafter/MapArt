@echo off
echo === SYSTEM TEST ===
echo.

echo 1. Checking directories...
if exist "themes" (
    echo    ✓ themes/ exists
) else (
    echo    ✗ themes/ missing
)

if exist "assets\fonts" (
    echo    ✓ assets/fonts/ exists
) else (
    echo    ✗ assets/fonts/ missing
)

if exist "outputs" (
    echo    ✓ outputs/ exists
) else (
    echo    ✗ outputs/ missing
    mkdir outputs
    echo    Created outputs/
)

echo.
echo 2. Checking main files...
if exist "create_map_poster.py" (
    echo    ✓ create_map_poster.py exists
) else (
    echo    ✗ create_map_poster.py missing
)

if exist "main.js" (
    echo    ✓ main.js exists
) else (
    echo    ✗ main.js missing
)

echo.
echo 3. Checking theme files...
dir /b themes\*.json 2>nul | find /c /v "" > temp_count.txt
set /p theme_count=<temp_count.txt
del temp_count.txt
echo    Found %theme_count% theme files

echo.
echo 4. Checking Python...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo    ✓ Python available
) else (
    echo    ✗ Python not found
)

echo.
echo 5. Checking Node.js...
node --version >nul 2>&1
if %errorlevel% equ 0 (
    echo    ✓ Node.js available
) else (
    echo    ✗ Node.js not found
)

echo.
echo === TEST COMPLETE ===
echo.
echo To run the application:
echo   npm start
echo   or
echo   launch_app.bat
pause
