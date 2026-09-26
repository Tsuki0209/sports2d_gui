@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

echo ============================================================
echo   Sports2D GUI - Windows EXE Build Script
echo ============================================================

echo [*] Python と pip の動作確認中...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python が検出されませんでした。Python (3.11以上) をインストールし、PATH を通してください。
    goto ERROR_END
)

echo [*] 必要なパッケージをインストールしています...
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install pyinstaller
if errorlevel 1 (
    echo [ERROR] パッケージのインストールに失敗しました。
    goto ERROR_END
)

echo [*] PyInstaller を実行して EXE をビルドしています...
python build_exe.py
if errorlevel 1 (
    echo [ERROR] EXE のビルド中にエラーが発生しました。上のエラーログを確認してください。
    goto ERROR_END
)

if exist "dist\Sports2D_GUI\Sports2D_GUI.exe" (
    echo.
    echo ============================================================
    echo   [SUCCESS] ビルド成功！
    echo   dist\Sports2D_GUI\Sports2D_GUI.exe が作成されました。
    echo ============================================================
    explorer "dist\Sports2D_GUI"
) else (
    echo [ERROR] ビルド処理は終了しましたが、dist\Sports2D_GUI\Sports2D_GUI.exe が見つかりません。
    goto ERROR_END
)

goto END

:ERROR_END
echo.
echo ============================================================
echo   [BUILD FAILED] ビルドに失敗しました。
echo ============================================================

:END
pause
