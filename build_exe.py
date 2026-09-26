#!/usr/bin/env python3
"""
Sports2D GUI - Executable Builder Script
Usage: python build_exe.py
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def main():
    print("=" * 60)
    print(" Sports2D GUI Executable Builder")
    print("=" * 60)

    # 1. Ensure pyinstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("[!] PyInstaller is not installed. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # 2. Path preparation
    root_dir = Path(__file__).parent.resolve()
    spec_file = root_dir / "sports2d_gui.spec"

    if not spec_file.exists():
        print(f"[!] Spec file not found: {spec_file}")
        sys.exit(1)

    print(f"[*] Building executable using {spec_file.name}...")

    # 3. Run PyInstaller
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        str(spec_file),
    ]

    res = subprocess.run(cmd, cwd=root_dir)

    if res.returncode == 0:
        print("\n" + "=" * 60)
        print(" Build Success!")
        output_dir = root_dir / "dist" / "Sports2D_GUI"
        print(f" Executable directory: {output_dir}")
        print("=" * 60)
    else:
        print(f"\n[!] Build failed with return code {res.returncode}")
        sys.exit(res.returncode)


if __name__ == "__main__":
    main()
