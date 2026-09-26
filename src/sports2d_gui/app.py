from __future__ import annotations

import json
import sys
import tempfile
from enum import Enum
from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QFileDialog, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QMainWindow, QMessageBox, QPlainTextEdit, QProgressBar, QPushButton, QSplitter,
    QStackedWidget, QVBoxLayout, QWidget,
)

from .config import default_config, dump_toml, load_toml, parse_toml_text, toml_text, validate_config
from .theme import DARK_THEME_QSS
from .views import (
    AdvancedView, AnglesView, CalibView, EnvView, KinematicsView,
    OutputView, PoseView, PostView, ProjectView, ResultsView,
)
from .worker import Sports2DWorker


class AppState(Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    FINISHED = "FINISHED"


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Sports2D Studio GUI")
        self.resize(1180, 740)
        self.setMinimumSize(920, 620)

        self.state = AppState.IDLE
        self.config = default_config()
        self.current_config_path: Path | None = None
        self.worker: Sports2DWorker | None = None

        self._init_ui()
        self._load_config_to_views(self.config)
        self._update_state_ui(AppState.IDLE)

    def _init_ui(self) -> None:
        self.setStyleSheet(DARK_THEME_QSS)

        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1. Clean Top Header Bar
        header_widget = QWidget()
        header_widget.setObjectName("topHeaderBar")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(14, 10, 14, 10)
        header_layout.setSpacing(10)

        # File actions
        self.btn_new = QPushButton("📄 新規")
        self.btn_open = QPushButton("📂 開く…")
        self.btn_save = QPushButton("💾 保存")
        self.btn_validate = QPushButton("🔍 検証")

        header_layout.addWidget(self.btn_new)
        header_layout.addWidget(self.btn_open)
        header_layout.addWidget(self.btn_save)
        header_layout.addWidget(self.btn_validate)

        header_layout.addSpacing(16)

        # Primary Execution Button & Stop Button (State controlled)
        self.btn_run = QPushButton("▶ 解析を開始")
        self.btn_run.setObjectName("runButton")
        self.btn_stop = QPushButton("⏹ 停止")
        self.btn_stop.setObjectName("stopButton")
        self.btn_stop.setEnabled(False)

        header_layout.addWidget(self.btn_run)
        header_layout.addWidget(self.btn_stop)

        header_layout.addStretch()

        # Tools & Log Toggle
        self.btn_results = QPushButton("📁 結果フォルダ")
        self.btn_toggle_log = QPushButton("📜 ログ表示")
        header_layout.addWidget(self.btn_results)
        header_layout.addWidget(self.btn_toggle_log)

        # Status Banner
        self.status_banner = QLabel("準備完了")
        self.status_banner.setObjectName("statusBanner")
        self.status_banner.setStyleSheet("font-weight: 600; color: #60a5fa;")
        header_layout.addWidget(self.status_banner)

        root_layout.addWidget(header_widget)

        # 2. Main Vertical Splitter (Content vs Console)
        self.main_splitter = QSplitter(Qt.Orientation.Vertical)
        root_layout.addWidget(self.main_splitter, 1)

        # Horizontal Splitter (Sidebar vs Views)
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.addWidget(content_splitter)

        # Sidebar with structured step groups
        self.sidebar = QListWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(220)

        self.nav_items = [
            ("1. 🎬 入力動画・カメラ", ProjectView),
            ("2. 👤 姿勢モデル & 追跡", PoseView),
            ("3. 📐 座標変換 & 校正", CalibView),
            ("4. 🦴 関節・体幹角度", AnglesView),
            ("5. 🧹 フィルタ & 前処理", PostView),
            ("6. 🏃 逆運動学 OpenSim", KinematicsView),
            ("7. 📊 出力ファイル設定", OutputView),
            ("📊 解析結果ビューア", ResultsView),
            ("📝 TOML直接編集", AdvancedView),
            ("⚙️ プリセット & 環境", EnvView),
        ]

        self.stack = QStackedWidget()
        self.views: dict[str, QWidget] = {}

        for name, cls in self.nav_items:
            item = QListWidgetItem(name)
            self.sidebar.addItem(item)
            view_instance = cls()
            self.stack.addWidget(view_instance)
            self.views[name] = view_instance

        content_splitter.addWidget(self.sidebar)
        content_splitter.addWidget(self.stack)
        content_splitter.setSizes([220, 960])

        # 3. Bottom Console Panel (Collapsible)
        self.console_widget = QWidget()
        console_layout = QVBoxLayout(self.console_widget)
        console_layout.setContentsMargins(14, 6, 14, 6)
        console_layout.setSpacing(4)

        c_header = QHBoxLayout()
        c_title = QLabel("📜 実行ログ & プロセス出力")
        c_title.setStyleSheet("font-weight: 600; color: #94a3b8; font-size: 12px;")
        c_header.addWidget(c_title)
        c_header.addStretch()

        btn_clear_log = QPushButton("ログ消去")
        btn_clear_log.setFixedHeight(22)
        btn_clear_log.setStyleSheet("font-size: 11px; padding: 2px 8px;")
        btn_clear_log.clicked.connect(lambda: self.log_edit.clear())
        c_header.addWidget(btn_clear_log)

        console_layout.addLayout(c_header)

        self.log_edit = QPlainTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setMaximumHeight(200)
        self.log_edit.setPlaceholderText("Sports2D の実行ログがリアルタイム表示されます…")
        console_layout.addWidget(self.log_edit)

        self.main_splitter.addWidget(self.console_widget)
        self.main_splitter.setSizes([560, 140])

        # Status Bar
        self.statusBar().showMessage("準備完了 - 設定を行って [▶ 解析を開始] を押してください")

        # Signal Connections
        self.sidebar.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.sidebar.setCurrentRow(0)

        self.btn_new.clicked.connect(self.new_project)
        self.btn_open.clicked.connect(self.open_toml)
        self.btn_save.clicked.connect(self.save_toml)
        self.btn_validate.clicked.connect(self.validate_current)
        self.btn_run.clicked.connect(self.start_run)
        self.btn_stop.clicked.connect(self.stop_run)
        self.btn_results.clicked.connect(self._goto_results_tab)
        self.btn_toggle_log.clicked.connect(self._toggle_log_console)

        # AdvancedView signals
        adv_view: AdvancedView = self.views["📝 TOML直接編集"]  # type: ignore
        adv_view.formToTomlRequested.connect(self._sync_form_to_toml_view)
        adv_view.tomlToFormRequested.connect(self._load_config_to_views)

        # EnvView signals
        env_view: EnvView = self.views["⚙️ プリセット & 環境"]  # type: ignore
        env_view.presetSelected.connect(self._load_config_to_views)

    def _update_state_ui(self, state: AppState, message: str = "") -> None:
        self.state = state
        if state == AppState.RUNNING:
            # Prevent double click and lock form edits
            self.btn_run.setEnabled(False)
            self.btn_run.setText("⌛ 解析実行中…")
            self.btn_stop.setEnabled(True)

            self.btn_new.setEnabled(False)
            self.btn_open.setEnabled(False)
            self.btn_save.setEnabled(False)
            self.btn_validate.setEnabled(False)

            self.status_banner.setText("解析実行中…")
            self.status_banner.setStyleSheet("font-weight: 600; color: #ffffff; background-color: #991b1b; border: 1px solid #ef4444; border-radius: 8px; padding: 6px 14px;")
            self.stack.setEnabled(False)  # Lock settings during execution
        elif state == AppState.IDLE:
            self.btn_run.setEnabled(True)
            self.btn_run.setText("▶ 解析を開始")
            self.btn_stop.setEnabled(False)

            self.btn_new.setEnabled(True)
            self.btn_open.setEnabled(True)
            self.btn_save.setEnabled(True)
            self.btn_validate.setEnabled(True)

            self.status_banner.setText("準備完了")
            self.status_banner.setStyleSheet("font-weight: 600; color: #60a5fa; background-color: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 6px 14px;")
            self.stack.setEnabled(True)
        elif state == AppState.FINISHED:
            self.btn_run.setEnabled(True)
            self.btn_run.setText("▶ 解析を開始")
            self.btn_stop.setEnabled(False)

            self.btn_new.setEnabled(True)
            self.btn_open.setEnabled(True)
            self.btn_save.setEnabled(True)
            self.btn_validate.setEnabled(True)

            self.status_banner.setText("解析完了 🎉")
            self.status_banner.setStyleSheet("font-weight: 600; color: #ffffff; background-color: #166534; border: 1px solid #22c55e; border-radius: 8px; padding: 6px 14px;")
            self.stack.setEnabled(True)

    def _toggle_log_console(self) -> None:
        visible = self.console_widget.isVisible()
        self.console_widget.setVisible(not visible)

    def _sync_form_to_toml_view(self) -> None:
        cfg = self._collect_config_from_views()
        adv_view: AdvancedView = self.views["📝 TOML直接編集"]  # type: ignore
        adv_view.set_toml_text(toml_text(cfg))
        self.statusBar().showMessage("最新設定をTOMLテキストに反映しました")

    def _collect_config_from_views(self) -> dict[str, Any]:
        cfg = default_config()
        for name, view in self.views.items():
            if hasattr(view, "save_config"):
                view.save_config(cfg)
        return cfg

    def _load_config_to_views(self, cfg: dict[str, Any]) -> None:
        self.config = cfg
        for name, view in self.views.items():
            if hasattr(view, "load_config"):
                view.load_config(cfg)
        adv_view: AdvancedView = self.views["📝 TOML直接編集"]  # type: ignore
        adv_view.set_toml_text(toml_text(cfg))

    def _goto_results_tab(self) -> None:
        idx = [i for i, (n, _) in enumerate(self.nav_items) if "結果" in n][0]
        self.sidebar.setCurrentRow(idx)

    def new_project(self) -> None:
        if self.state == AppState.RUNNING:
            return
        self.config = default_config()
        self.current_config_path = None
        self._load_config_to_views(self.config)
        self.log_edit.clear()
        self.statusBar().showMessage("新規プロジェクトを作成しました")
        self._update_state_ui(AppState.IDLE)

    def open_toml(self) -> None:
        if self.state == AppState.RUNNING:
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "TOML設定ファイルを開く", str(Path.cwd()), "TOML files (*.toml);;All files (*)"
        )
        if not path:
            return
        try:
            self.config = load_toml(path)
            self.current_config_path = Path(path)
            self._load_config_to_views(self.config)
            self.statusBar().showMessage(f"読み込み成功: {path}")
            self._update_state_ui(AppState.IDLE)
        except Exception as exc:
            QMessageBox.critical(self, "読み込みエラー", f"設定ファイルの読み込みに失敗しました:\n{exc}")

    def save_toml(self) -> None:
        if self.current_config_path is None:
            path, _ = QFileDialog.getSaveFileName(
                self, "TOML設定ファイルを保存", str(Path.cwd() / "Sports2D_GUI.toml"), "TOML files (*.toml)"
            )
            if not path:
                return
            self.current_config_path = Path(path)

        try:
            cfg = self._collect_config_from_views()
            dump_toml(cfg, self.current_config_path)
            self.statusBar().showMessage(f"保存成功: {self.current_config_path}")
        except Exception as exc:
            QMessageBox.critical(self, "保存エラー", f"ファイルの保存に失敗しました:\n{exc}")

    def validate_current(self) -> None:
        cfg = self._collect_config_from_views()
        issues = validate_config(cfg)
        if issues:
            QMessageBox.warning(self, "設定項目の確認", "\n".join(f"• {x}" for x in issues))
        else:
            QMessageBox.information(self, "設定検証完了", "設定項目の検証を通過しました！\n[▶ 解析を開始] ボタンを押して処理を実行できます。")

    def start_run(self) -> None:
        if self.state == AppState.RUNNING:
            return  # Strict double-trigger guard

        cfg = self._collect_config_from_views()
        issues = validate_config(cfg)
        if issues:
            QMessageBox.warning(self, "設定エラー", "\n".join(f"• {x}" for x in issues))
            return

        # Ensure log panel is visible
        self.console_widget.setVisible(True)

        if self.current_config_path is None:
            temp_dir = Path(tempfile.mkdtemp(prefix="sports2d_gui_"))
            self.current_config_path = temp_dir / "Sports2D_GUI.toml"

        dump_toml(cfg, self.current_config_path)

        res_dir_setting = cfg.get("base", {}).get("result_dir", "")
        if res_dir_setting:
            work_dir = Path(res_dir_setting)
        else:
            work_dir = self.current_config_path.parent / "Sports2D_Results"

        work_dir.mkdir(parents=True, exist_ok=True)

        self.log_edit.clear()
        self._update_state_ui(AppState.RUNNING)

        self.worker = Sports2DWorker(self.current_config_path, work_dir)
        self.worker.log_line.connect(self.log_edit.appendPlainText)
        self.worker.status.connect(self.statusBar().showMessage)
        self.worker.finished_ok.connect(self._on_run_finished)
        self.worker.start()

    def stop_run(self) -> None:
        if self.worker and self.state == AppState.RUNNING:
            self.worker.stop()

    def _on_run_finished(self, code: int, status_msg: str) -> None:
        if code == 0:
            self._update_state_ui(AppState.FINISHED)
            self.statusBar().showMessage("解析が正常に終了しました")

            cfg = self._collect_config_from_views()
            res_dir_setting = cfg.get("base", {}).get("result_dir", "")
            target_dir = Path(res_dir_setting) if res_dir_setting else (self.current_config_path.parent / "Sports2D_Results" if self.current_config_path else Path.cwd())

            res_view: ResultsView = self.views["📊 解析結果ビューア"]  # type: ignore
            res_view.set_result_directory(target_dir)

            ans = QMessageBox.information(
                self,
                "解析完了 🎉",
                "Sports2D の解析が正常に完了しました。\n解析結果ビューア画面に移動しますか？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            if ans == QMessageBox.StandardButton.Yes:
                self._goto_results_tab()
        else:
            self._update_state_ui(AppState.IDLE)
            QMessageBox.warning(self, "解析中断・エラー", f"Sports2D の実行が失敗または中断されました (終了コード {code})。\nログコンソールを確認してください。")

        self.worker = None

    def closeEvent(self, event) -> None:
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(3000)
        event.accept()


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Sports2D Studio GUI")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
