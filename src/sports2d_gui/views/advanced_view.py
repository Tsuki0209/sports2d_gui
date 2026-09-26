from __future__ import annotations

from typing import Any
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QMessageBox, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget,
)

from ..config import parse_toml_text, toml_text
from ..widgets.card import CardWidget


class AdvancedView(QWidget):
    formToTomlRequested = Signal()
    tomlToFormRequested = Signal(dict)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        card = CardWidget(
            "📝 Advanced TOML エディタ",
            "Sports2Dに渡されるTOMLテキストを直接参照・編集します。GUIフォームにない未知のパラメータもここで記述・保持できます。"
        )

        self.toml_edit = QPlainTextEdit()
        self.toml_edit.setPlaceholderText("# Sports2D TOML Config...")
        card.add_widget(self.toml_edit)

        btn_box = QHBoxLayout()
        self.btn_sync_from_form = QPushButton("フォームの値 → TOMLに反映")
        self.btn_sync_to_form = QPushButton("TOMLテキスト → フォームに適用")
        self.btn_sync_from_form.setObjectName("accentButton")

        btn_box.addWidget(self.btn_sync_from_form)
        btn_box.addWidget(self.btn_sync_to_form)
        btn_box.addStretch()

        card.add_layout(btn_box)
        layout.addWidget(card, 1)

        self.btn_sync_from_form.clicked.connect(self.formToTomlRequested.emit)
        self.btn_sync_to_form.clicked.connect(self._apply_toml_to_form)

    def set_toml_text(self, text: str) -> None:
        self.toml_edit.setPlainText(text)

    def get_toml_text(self) -> str:
        return self.toml_edit.toPlainText()

    def get_config_dict(self) -> dict[str, Any]:
        return parse_toml_text(self.toml_edit.toPlainText())

    def _apply_toml_to_form(self) -> None:
        try:
            cfg = self.get_config_dict()
            self.tomlToFormRequested.emit(cfg)
        except Exception as exc:
            QMessageBox.critical(self, "TOML構文エラー", f"TOMLの読み込みに失敗しました:\n{exc}")
