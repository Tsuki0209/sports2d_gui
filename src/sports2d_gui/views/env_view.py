from __future__ import annotations

import shutil
import sys
from typing import Any
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QComboBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton,
    QScrollArea, QVBoxLayout, QWidget,
)

from ..config import PRESETS, get_preset
from ..widgets.card import CardWidget


class EnvView(QScrollArea):
    presetSelected = Signal(dict)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QScrollArea.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # 1. Quick Presets Card
        card_preset = CardWidget(
            "⚡ クイックプリセット (Quick Presets)",
            "解析の目的に合わせて推奨されるパラメータ構成を一括読み込み・反映します。"
        )
        f_preset = QHBoxLayout()

        self.combo_preset = QComboBox()
        self.combo_preset.addItems(list(PRESETS.keys()))

        self.btn_apply_preset = QPushButton("このプリセットを適用")
        self.btn_apply_preset.setObjectName("accentButton")

        f_preset.addWidget(self.combo_preset, 1)
        f_preset.addWidget(self.btn_apply_preset)

        card_preset.add_layout(f_preset)
        layout.addWidget(card_preset)

        # 2. Environment Info Card
        card_env = CardWidget(
            "⚙️ システム & ライブラリ環境",
            "現在使用中の Python ディレクトリおよび Sports2D パッケージの検出状態です。"
        )
        f_env = QFormLayout()

        self.py_executable = QLineEdit(sys.executable)
        self.py_executable.setReadOnly(True)

        self.sports2d_exe = QLineEdit()
        self.sports2d_exe.setReadOnly(True)

        self.sports2d_version = QLineEdit()
        self.sports2d_version.setReadOnly(True)

        self.pyside_version = QLineEdit()
        self.pyside_version.setReadOnly(True)

        self.btn_recheck = QPushButton("環境状態を再確認")

        f_env.addRow("Python 実行パス:", self.py_executable)
        f_env.addRow("Sports2D コマンド:", self.sports2d_exe)
        f_env.addRow("Sports2D バージョン:", self.sports2d_version)
        f_env.addRow("PySide6 GUIバージョン:", self.pyside_version)
        f_env.addRow(self.btn_recheck)

        card_env.add_layout(f_env)
        layout.addWidget(card_env)

        layout.addStretch()
        self.setWidget(container)

        self.btn_apply_preset.clicked.connect(self._on_apply_preset)
        self.btn_recheck.clicked.connect(self.update_environment)

        self.update_environment()

    def _on_apply_preset(self) -> None:
        preset_name = self.combo_preset.currentText()
        cfg = get_preset(preset_name)
        self.presetSelected.emit(cfg)
        QMessageBox.information(self, "プリセット適用完了", f"「{preset_name}」の設定を全画面に反映しました。")

    def update_environment(self) -> None:
        exe = shutil.which("sports2d") or ""
        self.sports2d_exe.setText(exe or "PATH未検出 (python -m Sports2D.Sports2D でフォールバック)")

        try:
            import sports2d
            ver = getattr(sports2d, "__version__", "1.0")
            self.sports2d_version.setText(f"検出済 (v{ver})" if ver else "検出済")
        except Exception as exc:
            self.sports2d_version.setText(f"未検出 ({exc})")

        try:
            import PySide6
            self.pyside_version.setText(f"v{PySide6.__version__}")
        except Exception:
            self.pyside_version.setText("unknown")
