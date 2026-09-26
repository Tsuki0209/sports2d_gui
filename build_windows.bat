@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo   Sports2D GUI - Windows EXE Build Script
echo ============================================================

REM 1. Check Python installation
where python >nul 2>nul
if %errorlevel% neq 0 (
    where py >nul 2>nul
    if %errorlevel% neq 0 (
        echo [ERROR] Python not found in PATH!
        echo Please install Python 3.11+ and check "Add python.exe to PATH"
        goto error
    ) else (
        set PYCMD=py -3
    )
) else (
    set PYCMD=python
)

echo [*] Using Python command: !PYCMD!

REM 2. Create and activate venv if not exists
if not exist .venv (
    echo [*] Creating virtual environment .venv...
    !PYCMD! -m venv .venv
    if %errorlevel% neq 0 goto error
)

set VENV_PYTHON=.venv\Scripts\python.exe

REM 3. Install/Upgrade dependencies
echo [*] Installing dependencies...
!VENV_PYTHON! -m pip install --upgrade pip
if %errorlevel% neq 0 goto error

!VENV_PYTHON! -m pip install pyinstaller tomlkit PySide6 sports2d
if %errorlevel% neq 0 goto error

!VENV_PYTHON! -m pip install -e .
if %errorlevel% neq 0 goto error

REM 4. Build EXE
echo [*] Running PyInstaller build...
!VENV_PYTHON! build_exe.py
if %errorlevel% neq 0 goto error

echo.
echo ============================================================
echo   [SUCCESS] Build Completed! 
echo   Executable location: dist\Sports2D_GUI\Sports2D_GUI.exe
echo ============================================================
pause
exit /b 0

:error
echo.
echo ============================================================
echo   [ERROR] Build failed! Check error messages above.
echo ============================================================
pause
exit /b 1
