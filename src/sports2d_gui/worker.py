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
    progress_percent = Signal(int)  # 0 to 100 or -1 for unknown
    finished_ok = Signal(int, str)

    def __init__(self, config_path: str | Path, cwd: str | Path | None = None) -> None:
        super().__init__()
        self.config_path = str(Path(config_path).resolve())
        self.cwd = str(Path(cwd).resolve()) if cwd else str(Path(self.config_path).parent)
        self.process: subprocess.Popen[str] | None = None

    def run(self) -> None:
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"

        exe = shutil.which("sports2d")
        if exe:
            cmd = [exe, "--config", self.config_path]
        else:
            cmd = [sys.executable, "-m", "Sports2D.Sports2D", "--config", self.config_path]

        self.status.emit("Sports2D プロセスを開始しています…")
        self.log_line.emit(f"[GUI] コマンド実行: {' '.join(cmd)}")
        self.log_line.emit(f"[GUI] 作業ディレクトリ: {self.cwd}")

        try:
            self.process = subprocess.Popen(
                cmd,
                cwd=self.cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                env=env,
            )
        except Exception as exc:
            self.log_line.emit(f"[GUI ERROR] 起動失敗: {exc}")
            self.finished_ok.emit(-1, f"Failed to launch Sports2D: {exc}")
            return

        assert self.process.stdout is not None
        for line in self.process.stdout:
            line = line.rstrip("\r\n")
            self.log_line.emit(line)

            # Detect status & progress patterns
            if "Processing " in line:
                self.status.emit(line)
            elif "Saved" in line:
                self.status.emit(line)
            elif "DONE" in line or "Finished" in line:
                self.status.emit("処理完了")

        code = self.process.wait()
        status_msg = "正常終了" if code == 0 else f"終了コード {code}"
        self.status.emit(status_msg)
        self.finished_ok.emit(code, "completed" if code == 0 else f"failed with exit code {code}")

    def stop(self) -> None:
        if self.process is None or self.process.poll() is not None:
            return
        self.status.emit("停止処理中…")
        self.log_line.emit("[GUI] ユーザー要求によりプロセスを中断します…")
        try:
            self.process.terminate()
            self.process.wait(timeout=3)
        except (subprocess.TimeoutExpired, Exception):
            if self.process:
                self.process.kill()
