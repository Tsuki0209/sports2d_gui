from __future__ import annotations

from typing import Iterable
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QVBoxLayout, QWidget,
)


class MultiSelectListWidget(QWidget):
    selectionChanged = Signal()

    def __init__(
        self,
        items: Iterable[str],
        selected: Iterable[str] = (),
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        btn_bar = QHBoxLayout()
        self.btn_select_all = QPushButton("全選択")
        self.btn_clear_all = QPushButton("全解除")
        self.btn_select_all.setFixedHeight(26)
        self.btn_clear_all.setFixedHeight(26)
        btn_bar.addWidget(self.btn_select_all)
        btn_bar.addWidget(self.btn_clear_all)
        btn_bar.addStretch()

        self.list_widget = QListWidget()
        self.list_widget.setMaximumHeight(160)
        selected_set = set(selected)

        for text in items:
            item = QListWidgetItem(text)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(
                Qt.CheckState.Checked if text in selected_set else Qt.CheckState.Unchecked
            )
            self.list_widget.addItem(item)

        layout.addLayout(btn_bar)
        layout.addWidget(self.list_widget)

        self.btn_select_all.clicked.connect(self.select_all)
        self.btn_clear_all.clicked.connect(self.clear_all)
        self.list_widget.itemChanged.connect(lambda _: self.selectionChanged.emit())

    def values(self) -> list[str]:
        res = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                res.append(item.text())
        return res

    def set_values(self, selected: Iterable[str]) -> None:
        self.list_widget.blockSignals(True)
        selected_set = set(selected)
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setCheckState(
                Qt.CheckState.Checked if item.text() in selected_set else Qt.CheckState.Unchecked
            )
        self.list_widget.blockSignals(False)
        self.selectionChanged.emit()

    def select_all(self) -> None:
        self.list_widget.blockSignals(True)
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setCheckState(Qt.CheckState.Checked)
        self.list_widget.blockSignals(False)
        self.selectionChanged.emit()

    def clear_all(self) -> None:
        self.list_widget.blockSignals(True)
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setCheckState(Qt.CheckState.Unchecked)
        self.list_widget.blockSignals(False)
        self.selectionChanged.emit()


class MultiSelectChipWidget(MultiSelectListWidget):
    """Alias for multi select with clean layout"""
    pass
