from __future__ import annotations

import os
import platform
import subprocess
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFileDialog, QHBoxLayout, QHeaderView, QLabel, QListWidget, QListWidgetItem,
    QMessageBox, QPushButton, QSplitter, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from ..widgets.card import CardWidget


class ResultsView(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # Header card
        card_top = CardWidget("📊 解析結果・生成物ビューア", "Sports2D により出力された動画・画像・数値データファイルを確認・閲覧できます")
        h_layout = QHBoxLayout()

        self.btn_select_dir = QPushButton("フォルダを選択…")
        self.btn_open_folder = QPushButton("OSでフォルダを開く")
        self.btn_refresh = QPushButton("更新")
        self.btn_open_folder.setObjectName("accentButton")

        h_layout.addWidget(self.btn_select_dir)
        h_layout.addWidget(self.btn_open_folder)
        h_layout.addWidget(self.btn_refresh)
        h_layout.addStretch()

        self.dir_label = QLabel("結果フォルダ: (未指定)")
        self.dir_label.setStyleSheet("font-weight: 600; color: #a0aec0;")
        h_layout.addWidget(self.dir_label)

        card_top.add_layout(h_layout)
        layout.addWidget(card_top)

        # Splitter: File list table (Left) vs Preview panel (Right)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ファイル名", "種別", "サイズ"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        splitter.addWidget(self.table)

        # Right Preview Container
        preview_card = CardWidget("🖼️ プレビュー", "画像・グラフ・情報ファイルを表示")
        self.preview_label = QLabel("ファイルを選択するとここにプレビューが表示されます")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("color: #a0aec0; border: 1px dashed #4a5568; border-radius: 8px;")
        self.preview_label.setMinimumSize(320, 240)
        self.preview_label.setScaledContents(True)

        preview_card.add_widget(self.preview_label)
        splitter.addWidget(preview_card)

        splitter.setSizes([550, 450])
        layout.addWidget(splitter, 1)

        self.current_dir: Path | None = None

        self.btn_select_dir.clicked.connect(self._select_directory)
        self.btn_open_folder.clicked.connect(self._open_in_os)
        self.btn_refresh.clicked.connect(self.refresh)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)

    def set_result_directory(self, dir_path: str | Path) -> None:
        path = Path(dir_path).resolve()
        if path.exists() and path.is_dir():
            self.current_dir = path
            self.dir_label.setText(f"結果フォルダ: {path}")
            self.refresh()

    def _select_directory(self) -> None:
        start = str(self.current_dir or Path.cwd())
        path = QFileDialog.getExistingDirectory(self, "結果フォルダを選択", start)
        if path:
            self.set_result_directory(path)

    def _open_in_os(self) -> None:
        if not self.current_dir or not self.current_dir.exists():
            QMessageBox.warning(self, "エラー", "フォルダが存在しません。")
            return

        target = str(self.current_dir)
        try:
            if platform.system() == "Darwin":  # macOS
                subprocess.run(["open", target], check=False)
            elif platform.system() == "Windows":
                os.startfile(target)
            else:  # Linux
                subprocess.run(["xdg-open", target], check=False)
        except Exception as exc:
            QMessageBox.critical(self, "エラー", f"フォルダを開けませんでした:\n{exc}")

    def refresh(self) -> None:
        self.table.setRowCount(0)
        if not self.current_dir or not self.current_dir.exists():
            return

        files = sorted(list(self.current_dir.rglob("*")), key=lambda p: p.name.lower())
        row = 0
        for f in files:
            if f.is_file() and not f.name.startswith("."):
                self.table.insertRow(row)

                # Name item
                rel_path = f.relative_to(self.current_dir)
                name_item = QTableWidgetItem(str(rel_path))
                name_item.setData(Qt.ItemDataRole.UserRole, str(f))

                # Ext / Category
                ext = f.suffix.lower()
                if ext in [".mp4", ".avi", ".mov"]:
                    cat = "🎬 動画"
                elif ext in [".png", ".jpg", ".jpeg"]:
                    cat = "🖼️ 画像/グラフ"
                elif ext in [".trc", ".mot", ".c3d"]:
                    cat = "📐 動作データ"
                elif ext in [".toml", ".json", ".txt"]:
                    cat = "📄 設定・ログ"
                else:
                    cat = "📁 その他"

                cat_item = QTableWidgetItem(cat)

                # Size
                size_kb = f.stat().st_size / 1024
                size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.2f} MB"
                size_item = QTableWidgetItem(size_str)
                size_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

                self.table.setItem(row, 0, name_item)
                self.table.setItem(row, 1, cat_item)
                self.table.setItem(row, 2, size_item)
                row += 1

    def _on_selection_changed(self) -> None:
        items = self.table.selectedItems()
        if not items:
            return
        file_path_str = self.table.item(items[0].row(), 0).data(Qt.ItemDataRole.UserRole)
        if not file_path_str:
            return

        path = Path(file_path_str)
        ext = path.suffix.lower()

        if ext in [".png", ".jpg", ".jpeg"]:
            pixmap = QPixmap(str(path))
            if not pixmap.isNull():
                self.preview_label.setPixmap(pixmap.scaled(
                    self.preview_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                ))
            else:
                self.preview_label.setText("画像を読み込めませんでした")
        elif ext in [".toml", ".json", ".txt", ".csv", ".trc", ".mot"]:
            try:
                content = path.read_text(encoding="utf-8", errors="replace")[:1500]
                self.preview_label.setText(f"--- {path.name} 先頭プレビュー ---\n\n{content}")
            except Exception as exc:
                self.preview_label.setText(f"テキスト読み込みエラー: {exc}")
        elif ext in [".mp4", ".avi", ".mov"]:
            self.preview_label.setText(f"🎬 動画ファイル:\n{path.name}\n\n「OSでフォルダを開く」から再生できます")
        else:
            self.preview_label.setText(f"ファイル: {path.name}")
