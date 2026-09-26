from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget


class CardWidget(QFrame):
    def __init__(self, title: str | None = None, subtitle: str | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            CardWidget {
                background-color: #1a1d28;
                border: 1px solid #2d3748;
                border-radius: 12px;
            }
        """)
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(18, 18, 18, 18)
        self._main_layout.setSpacing(12)

        if title:
            self.header_label = QLabel(title)
            self.header_label.setStyleSheet("font-size: 15px; font-weight: 700; color: #63b3ed;")
            self._main_layout.addWidget(self.header_label)

        if subtitle:
            self.sub_label = QLabel(subtitle)
            self.sub_label.setStyleSheet("font-size: 12px; color: #a0aec0; margin-bottom: 4px;")
            self.sub_label.setWordWrap(True)
            self._main_layout.addWidget(self.sub_label)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(10)
        self._main_layout.addWidget(self.content_widget)

    def add_widget(self, widget: QWidget) -> None:
        self.content_layout.addWidget(widget)

    def add_layout(self, layout) -> None:
        self.content_layout.addLayout(layout)
