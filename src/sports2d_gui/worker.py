from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QThread, Signal


class Sports2DWorker(QThread):
    log_line = Signal(str)
    status = Signal(str)
    finished_ok = Signal(int, str)

    def __init__(self, config_path: str | Path, cwd: str | Path | None = None) -> None:
        super().__init__()
        self.config_path = str(Path(config_path).resolve())
        self.cwd = str(Path(cwd).resolve()) if cwd else str(Path(self.config_path).parent)
        self.process: subprocess.Popen[str] | None = None

    def run(self) -> None:
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        exe = shutil.which("sports2d")
        if exe:
            cmd = [exe, "--config", self.config_path]
        else:
            cmd = [sys.executable, "-m", "Sports2D.Sports2D", "--config", self.config_path]
        self.status.emit("Sports2D を起動しています…")
        try:
            self.process = subprocess.Popen(
                cmd,
                cwd=self.cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                env=env,
            )
        except Exception as exc:
            self.log_line.emit(f"[GUI] 起動失敗: {exc}")
            self.finished_ok.emit(-1, "Sports2D process could not be started")
            return

        assert self.process.stdout is not None
        for line in self.process.stdout:
            line = line.rstrip("\n")
            self.log_line.emit(line)
            if line.startswith("Processing "):
                self.status.emit(line)
        code = self.process.wait()
        self.status.emit("解析終了" if code == 0 else f"Sports2D が終了コード {code} で終了")
        self.finished_ok.emit(code, "completed" if code == 0 else "failed")

    def stop(self) -> None:
        if self.process is None or self.process.poll() is not None:
            return
        self.status.emit("停止しています…")
        self.process.terminate()
        try:
            self.process.wait(timeout=4)
        except subprocess.TimeoutExpired:
            self.process.kill()
