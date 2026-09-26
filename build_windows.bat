@echo off
echo ============================================================
echo   Sports2D GUI - Windows EXE Build Script
echo ============================================================

REM Check python or py launcher
set PYTHON_CMD=python
where python >nul 2>nul
if %errorlevel% neq 0 (
    where py >nul 2>nul
    if %errorlevel% equ 0 (
        set PYTHON_CMD=py
    ) else (
        echo [ERROR] Python が検出されませんでした。
        echo Python のインストール時に「Add Python to PATH」にチェックを入れてください。
        pause
        exit /b 1
    )
)

echo [*] Using Python: %PYTHON_CMD%

%PYTHON_CMD% -m pip install --upgrade pip
%PYTHON_CMD% -m pip install -e .
%PYTHON_CMD% -m pip install pyinstaller

%PYTHON_CMD% build_exe.py

echo.
echo ============================================================
echo   Done! Check dist\Sports2D_GUI\
echo ============================================================
pause
