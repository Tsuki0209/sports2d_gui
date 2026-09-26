from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDoubleSpinBox, QFileDialog, QFormLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QPushButton,
    QSpinBox, QVBoxLayout, QWidget,
)


class PathEdit(QWidget):
    def __init__(self, parent=None, *, file=False, directory=False, filter="All files (*)"):
        super().__init__(parent)
        self.edit = QLineEdit()
        self.button = QPushButton("参照")
        self.button.clicked.connect(self.browse)
        self.file = file
        self.directory = directory
        self.filter = filter
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.edit, 1)
        layout.addWidget(self.button)

    def browse(self):
        if self.directory:
            path = QFileDialog.getExistingDirectory(self, "フォルダを選択", self.edit.text() or str(Path.cwd()))
        else:
            path, _ = QFileDialog.getOpenFileName(self, "ファイルを選択", self.edit.text() or str(Path.cwd()), self.filter)
        if path:
            self.edit.setText(path)

    def text(self) -> str:
        return self.edit.text().strip()

    def setText(self, value: str):
        self.edit.setText(value)


class CheckRow(QWidget):
    def __init__(self, label: str, checked=False, parent=None):
        super().__init__(parent)
        self.checkbox = QCheckBox(label)
        self.checkbox.setChecked(checked)
        l = QHBoxLayout(self)
        l.setContentsMargins(0, 0, 0, 0)
        l.addWidget(self.checkbox)
        l.addStretch()


class MultiSelectList(QListWidget):
    def __init__(self, items: Iterable[str], selected: Iterable[str] = (), parent=None):
        super().__init__(parent)
        selected = set(selected)
        for text in items:
            item = QListWidgetItem(text)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked if text in selected else Qt.CheckState.Unchecked)
            self.addItem(item)
        self.setMaximumHeight(180)

    def values(self) -> list[str]:
        return [self.item(i).text() for i in range(self.count()) if self.item(i).checkState() == Qt.CheckState.Checked]


class FormField:
    def __init__(self, widget, getter, setter):
        self.widget = widget
        self.getter = getter
        self.setter = setter

    def get(self):
        return self.getter()

    def set(self, value):
        self.setter(value)


def line(default: str = "") -> FormField:
    w = QLineEdit(default)
    return FormField(w, w.text, w.setText)


def integer(default: int, minimum: int = -999999, maximum: int = 999999) -> FormField:
    w = QSpinBox()
    w.setRange(minimum, maximum)
    w.setValue(default)
    return FormField(w, w.value, w.setValue)


def number(default: float, minimum: float = -1e9, maximum: float = 1e9, decimals: int = 4) -> FormField:
    w = QDoubleSpinBox()
    w.setRange(minimum, maximum)
    w.setDecimals(decimals)
    w.setValue(default)
    return FormField(w, w.value, w.setValue)


def combo(items: list[str], default: str) -> FormField:
    w = QComboBox()
    w.addItems(items)
    idx = w.findText(str(default))
    if idx >= 0:
        w.setCurrentIndex(idx)
    return FormField(w, w.currentText, lambda v: w.setCurrentText(str(v)))


def boolean(default: bool) -> FormField:
    w = QCheckBox()
    w.setChecked(default)
    return FormField(w, w.isChecked, w.setChecked)
