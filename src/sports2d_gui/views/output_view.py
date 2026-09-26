from __future__ import annotations

from typing import Any
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox, QDoubleSpinBox, QFormLayout, QGridLayout, QLabel, QScrollArea, QVBoxLayout, QWidget,
)

from ..widgets.card import CardWidget
from ..widgets.drag_drop import DragDropPathEdit


class OutputView(QScrollArea):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QScrollArea.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # 1. Output Files & Realtime Card
        card_out = CardWidget(
            "📁 出力ファイル & 画面表示オプション",
            "解析完了時に出力保存するファイルの種別（動画・画像・数値データ）と画面表示を設定します。"
        )
        grid_out = QGridLayout()
        grid_out.setHorizontalSpacing(16)
        grid_out.setVerticalSpacing(10)

        self.show_realtime = QCheckBox("リアルタイム画面表示 (show_realtime_results)")
        self.show_realtime.setToolTip("解析実行中の骨格描画ウィンドウを画面にリアルタイム表示します")

        self.save_vid = QCheckBox("解析結果動画 (.mp4) を保存 (save_vid)")
        self.save_img = QCheckBox("各フレーム画像 (.png) を保存 (save_img)")

        self.save_pose = QCheckBox("姿勢データ (.trc / .json) を保存 (save_pose)")
        self.calculate_angles = QCheckBox("角度計算を実行 (calculate_angles)")
        self.save_angles = QCheckBox("角度データ (.mot / .trc) を保存 (save_angles)")
        self.compare = QCheckBox("比較表示モード (compare)")

        self.slowmo = QDoubleSpinBox()
        self.slowmo.setRange(0.01, 100.0)
        self.slowmo.setValue(1.0)
        self.slowmo.setToolTip("動画生成時のスローモーション再生倍率")

        grid_out.addWidget(self.show_realtime, 0, 0, 1, 2)
        grid_out.addWidget(self.save_vid, 0, 2, 1, 2)

        grid_out.addWidget(self.save_img, 1, 0, 1, 2)
        grid_out.addWidget(self.save_pose, 1, 2, 1, 2)

        grid_out.addWidget(self.calculate_angles, 2, 0, 1, 2)
        grid_out.addWidget(self.save_angles, 2, 2, 1, 2)

        grid_out.addWidget(self.compare, 3, 0, 1, 2)
        grid_out.addWidget(QLabel("スローモーション倍率:"), 3, 2)
        grid_out.addWidget(self.slowmo, 3, 3)

        card_out.add_layout(grid_out)
        layout.addWidget(card_out)

        # 2. Output Paths Card
        card_paths = CardWidget(
            "💾 保存先フォルダ & TRC読み込み",
            "解析結果の保存先ディレクトリおよび過去の事前TRCデータの読み込み設定です。"
        )
        f_paths = QFormLayout()

        self.result_dir = DragDropPathEdit(directory=True, placeholder="指定しない場合は Sports2D_Results フォルダを自動生成")
        self.load_trc = DragDropPathEdit(file=True, filter_str="TRC files (*.trc);;All files (*)", placeholder="事前抽出済みのピクセルTRCファイル（任意）")

        f_paths.addRow("出力先フォルダ (result_dir):", self.result_dir)
        f_paths.addRow("TRC読み込み (load_trc_px):", self.load_trc)

        card_paths.add_layout(f_paths)
        layout.addWidget(card_paths)

        layout.addStretch()
        self.setWidget(container)

    def load_config(self, cfg: dict[str, Any]) -> None:
        b = cfg.get("base", {})
        p = cfg.get("pose", {})

        self.show_realtime.setChecked(bool(b.get("show_realtime_results", True)))
        self.save_vid.setChecked(bool(b.get("save_vid", True)))
        self.save_img.setChecked(bool(b.get("save_img", True)))
        self.save_pose.setChecked(bool(b.get("save_pose", True)))
        self.calculate_angles.setChecked(bool(b.get("calculate_angles", True)))
        self.save_angles.setChecked(bool(b.get("save_angles", True)))
        self.compare.setChecked(bool(b.get("compare", False)))

        self.slowmo.setValue(float(p.get("slowmo_factor", 1.0)))

        self.result_dir.setText(str(b.get("result_dir", "")))
        self.load_trc.setText(str(b.get("load_trc_px", "")))

    def save_config(self, cfg: dict[str, Any]) -> None:
        b = cfg.setdefault("base", {})
        p = cfg.setdefault("pose", {})

        b["show_realtime_results"] = self.show_realtime.isChecked()
        b["save_vid"] = self.save_vid.isChecked()
        b["save_img"] = self.save_img.isChecked()
        b["save_pose"] = self.save_pose.isChecked()
        b["calculate_angles"] = self.calculate_angles.isChecked()
        b["save_angles"] = self.save_angles.isChecked()
        b["compare"] = self.compare.isChecked()

        p["slowmo_factor"] = self.slowmo.value()

        b["result_dir"] = self.result_dir.text()
        b["load_trc_px"] = self.load_trc.text()
