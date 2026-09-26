from __future__ import annotations

from pathlib import Path
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QFileDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget,
)


class DragDropPathEdit(QWidget):
    pathChanged = Signal(str)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        file: bool = False,
        directory: bool = False,
        filter_str: str = "All files (*)",
        placeholder: str = "",
    ) -> None:
        super().__init__(parent)
        self.file = file
        self.directory = directory
        self.filter_str = filter_str

        self.setAcceptDrops(True)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.line_edit = QLineEdit()
        if placeholder:
            self.line_edit.setPlaceholderText(placeholder)
        self.line_edit.textChanged.connect(self.pathChanged.emit)

        self.btn_browse = QPushButton("参照…")
        self.btn_browse.clicked.connect(self.browse)

        layout.addWidget(self.line_edit, 1)
        layout.addWidget(self.btn_browse)

    def text(self) -> str:
        return self.line_edit.text().strip()

    def setText(self, value: str) -> None:
        self.line_edit.setText(value)

    def browse(self) -> None:
        start_dir = self.text() or str(Path.cwd())
        if self.directory:
            path = QFileDialog.getExistingDirectory(self, "フォルダを選択", start_dir)
        else:
            path, _ = QFileDialog.getOpenFileName(self, "ファイルを選択", start_dir, self.filter_str)
        if path:
            self.line_edit.setText(path)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            self.line_edit.setText(path)
            event.acceptProposedAction()


class VideoDropZone(QWidget):
    videosDropped = Signal(list)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("dropZone")
        self.setAcceptDrops(True)
        self.setMinimumHeight(100)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.icon_label = QLabel("🎬 動画ファイルをここにドラッグ＆ドロップ")
        self.icon_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #63b3ed;")
        self.sub_label = QLabel("または下のテキストボックスにファイルパスを入力・複数指定")
        self.sub_label.setStyleSheet("font-size: 11px; color: #a0aec0;")

        layout.addWidget(self.icon_label, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.sub_label, 0, Qt.AlignmentFlag.AlignCenter)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            self.setProperty("dragOver", True)
            self.style().unpolish(self)
            self.style().polish(self)
            event.acceptProposedAction()

    def dragLeaveEvent(self, event) -> None:
        self.setProperty("dragOver", False)
        self.style().unpolish(self)
        self.style().polish(self)

    def dropEvent(self, event: QDropEvent) -> None:
        self.setProperty("dragOver", False)
        self.style().unpolish(self)
        self.style().polish(self)
        urls = event.mimeData().urls()
        paths = [u.toLocalFile() for u in urls if u.toLocalFile()]
        if paths:
            self.videosDropped.emit(paths)
            event.acceptProposedAction()
