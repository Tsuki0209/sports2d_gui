from __future__ import annotations

import json
from typing import Any
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDoubleSpinBox, QFormLayout, QGridLayout, QLabel, QLineEdit,
    QScrollArea, QVBoxLayout, QWidget,
)

from ..widgets.card import CardWidget
from ..widgets.drag_drop import DragDropPathEdit


class CalibView(QScrollArea):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QScrollArea.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # 1. Scale & Convert Card
        card_scale = CardWidget(
            "📐 座標変換 & 単位スケーリング",
            "画面上のピクセル(px)単位から、実空間のメートル(m)単位への変換および遠近補正を行います。"
        )
        grid_scale = QGridLayout()
        grid_scale.setHorizontalSpacing(16)
        grid_scale.setVerticalSpacing(10)

        self.to_meters = QCheckBox("実空間メートル(m)単位に変換 (to_meters)")
        self.to_meters.setToolTip("ONにすると座標データをピクセルからメートルに変換します")

        self.make_c3d = QCheckBox("C3Dバイナリファイルを出力 (make_c3d)")
        self.make_c3d.setToolTip("動作解析標準フォーマット .c3d を生成します")

        self.save_calib = QCheckBox("校正パラメータをTOML保存 (save_calib)")

        self.perspective_value = QDoubleSpinBox()
        self.perspective_value.setRange(0.0, 1e6)
        self.perspective_value.setDecimals(4)
        self.perspective_value.setValue(10.0)

        self.perspective_unit = QComboBox()
        self.perspective_unit.addItems([
            "distance_m (被写体までの距離 [m])",
            "f_px (カメラ焦点距離 [px])",
            "fov_deg (画角 [度])",
            "fov_rad (画角 [ラジアン])",
            "from_calib (校正ファイルから読み込み)"
        ])

        grid_scale.addWidget(self.to_meters, 0, 0, 1, 2)
        grid_scale.addWidget(self.make_c3d, 0, 2, 1, 2)
        grid_scale.addWidget(self.save_calib, 1, 0, 1, 2)

        grid_scale.addWidget(QLabel("遠近補正基準値 (perspective_value):"), 2, 0)
        grid_scale.addWidget(self.perspective_value, 2, 1)

        grid_scale.addWidget(QLabel("基準値の単位 (perspective_unit):"), 2, 2)
        grid_scale.addWidget(self.perspective_unit, 2, 3)

        card_scale.add_layout(grid_scale)
        layout.addWidget(card_scale)

        # 2. Calibration & Floor Angle Card
        card_calib = CardWidget(
            "🏁 キャリブレーション & 原点・床角設定",
            "撮影カメラの原点位置、床面の傾き補正、レンズ歪み係数を設定します。"
        )
        f_calib = QFormLayout()

        self.floor_angle = QLineEdit("auto")
        self.floor_angle.setPlaceholderText("auto または 数値 (度)")
        self.floor_angle.setToolTip("床面の傾き角度 [度]。'auto' で自動検出")

        self.xy_origin = QLineEdit('["auto"]')
        self.xy_origin.setPlaceholderText("例: [\"auto\"] または [0, 0]")
        self.xy_origin.setToolTip("原点とするピクセル座標またはキーポイント")

        self.distortions = QLineEdit("[0.0, 0.0, 0.0, 0.0, 0.0]")
        self.distortions.setPlaceholderText("レンズ歪み係数 5要素のリスト")

        self.calib_file = DragDropPathEdit(file=True, filter_str="TOML files (*.toml);;All files (*)", placeholder="既存の校正TOMLファイル（省略可）")

        f_calib.addRow("床面角度 (floor_angle):", self.floor_angle)
        f_calib.addRow("XY座標原点 (xy_origin):", self.xy_origin)
        f_calib.addRow("レンズ歪み係数 (distortions):", self.distortions)
        f_calib.addRow("校正ファイル (calib_file):", self.calib_file)

        card_calib.add_layout(f_calib)
        layout.addWidget(card_calib)

        layout.addStretch()
        self.setWidget(container)

    def load_config(self, cfg: dict[str, Any]) -> None:
        px = cfg.get("px_to_meters_conversion", {})
        self.to_meters.setChecked(bool(px.get("to_meters", True)))
        self.make_c3d.setChecked(bool(px.get("make_c3d", True)))
        self.save_calib.setChecked(bool(px.get("save_calib", True)))

        self.perspective_value.setValue(float(px.get("perspective_value", 10.0)))

        pu_val = str(px.get("perspective_unit", "distance_m"))
        for i in range(self.perspective_unit.count()):
            if pu_val in self.perspective_unit.itemText(i):
                self.perspective_unit.setCurrentIndex(i)
                break

        self.floor_angle.setText(str(px.get("floor_angle", "auto")))

        xy = px.get("xy_origin", ["auto"])
        self.xy_origin.setText(json.dumps(xy) if isinstance(xy, (list, dict)) else str(xy))

        dist = px.get("distortions", [0, 0, 0, 0, 0])
        self.distortions.setText(json.dumps(dist) if isinstance(dist, (list, dict)) else str(dist))

        self.calib_file.setText(str(px.get("calib_file", "")))

    def save_config(self, cfg: dict[str, Any]) -> None:
        px = cfg.setdefault("px_to_meters_conversion", {})
        px["to_meters"] = self.to_meters.isChecked()
        px["make_c3d"] = self.make_c3d.isChecked()
        px["save_calib"] = self.save_calib.isChecked()

        px["perspective_value"] = self.perspective_value.value()
        px["perspective_unit"] = self.perspective_unit.currentText().split()[0]

        fa = self.floor_angle.text().strip()
        px["floor_angle"] = fa if fa else "auto"

        xy_text = self.xy_origin.text().strip()
        if xy_text.startswith("["):
            try:
                px["xy_origin"] = json.loads(xy_text)
            except Exception:
                px["xy_origin"] = [xy_text]
        else:
            px["xy_origin"] = [xy_text]

        dist_text = self.distortions.text().strip()
        if dist_text.startswith("["):
            try:
                px["distortions"] = json.loads(dist_text)
            except Exception:
                px["distortions"] = [0.0, 0.0, 0.0, 0.0, 0.0]
        else:
            px["distortions"] = [0.0, 0.0, 0.0, 0.0, 0.0]

        px["calib_file"] = self.calib_file.text()
