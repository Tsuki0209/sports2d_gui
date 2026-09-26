from __future__ import annotations

from typing import Any
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDoubleSpinBox, QFormLayout, QGridLayout, QHBoxLayout, QLabel,
    QScrollArea, QVBoxLayout, QWidget,
)

from ..widgets.card import CardWidget
from ..widgets.multi_select import MultiSelectListWidget

JOINTS = [
    "Right ankle", "Left ankle", "Right knee", "Left knee", "Right hip", "Left hip",
    "Right shoulder", "Left shoulder", "Right elbow", "Left elbow", "Right wrist", "Left wrist",
]
SEGMENTS = [
    "Right foot", "Left foot", "Right shank", "Left shank", "Right thigh", "Left thigh", "Pelvis",
    "Trunk", "Shoulders", "Head", "Right arm", "Left arm", "Right forearm", "Left forearm",
]


class AnglesView(QScrollArea):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QScrollArea.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # 1. Display Options Card
        card_disp = CardWidget(
            "📈 角度描画 & オーバーレイ設定",
            "出力される動画・画像の上に関節角度や体幹角度の数値を描画表示する設定です。"
        )
        grid_disp = QGridLayout()
        grid_disp.setHorizontalSpacing(16)
        grid_disp.setVerticalSpacing(10)

        self.angle_display = QComboBox()
        self.angle_display.addItems([
            "body,list (身体上 + 左側リスト両方描画)",
            "body (身体関節の位置に描画)",
            "list (画面左側のリスト表示のみ)",
            "none (角度の描画なし・計算のみ)"
        ])

        self.font_size = QDoubleSpinBox()
        self.font_size.setRange(0.01, 3.0)
        self.font_size.setDecimals(3)
        self.font_size.setValue(0.3)
        self.font_size.setToolTip("動画上に描画されるテキストのフォントサイズ")

        self.flip_lr = QCheckBox("左右判定を自動判定・反転 (flip_left_right)")
        self.correct_angles = QCheckBox("床面角度でセグメント角度を自動補正 (correct_segment_angles_with_floor_angle)")

        grid_disp.addWidget(QLabel("角度描画スタイル:"), 0, 0)
        grid_disp.addWidget(self.angle_display, 0, 1)

        grid_disp.addWidget(QLabel("文字サイズ (fontSize):"), 0, 2)
        grid_disp.addWidget(self.font_size, 0, 3)

        grid_disp.addWidget(self.flip_lr, 1, 0, 1, 2)
        grid_disp.addWidget(self.correct_angles, 1, 2, 1, 2)

        card_disp.add_layout(grid_disp)
        layout.addWidget(card_disp)

        # 2. Side-by-side Layout for Joints & Segments Selection
        selection_layout = QHBoxLayout()
        selection_layout.setSpacing(16)

        # Joint Angles Card
        card_joints = CardWidget("🦵 関節角度 (Joint Angles)", "計算する関節を選択")
        self.joints_widget = MultiSelectListWidget(JOINTS)
        card_joints.add_widget(self.joints_widget)
        selection_layout.addWidget(card_joints)

        # Segment Angles Card
        card_segments = CardWidget("🧍 セグメント角度 (Segment Angles)", "計算する体幹・身体部を選択")
        self.segments_widget = MultiSelectListWidget(SEGMENTS)
        card_segments.add_widget(self.segments_widget)
        selection_layout.addWidget(card_segments)

        layout.addLayout(selection_layout)
        layout.addStretch()
        self.setWidget(container)

    def load_config(self, cfg: dict[str, Any]) -> None:
        a = cfg.get("angles", {})

        disp = a.get("display_angle_values_on", ["body", "list"])
        if isinstance(disp, list):
            if set(disp) == {"body", "list"}:
                d_str = "body,list"
            elif disp:
                d_str = str(disp[0])
            else:
                d_str = "none"
        else:
            d_str = str(disp)

        for i in range(self.angle_display.count()):
            if d_str in self.angle_display.itemText(i):
                self.angle_display.setCurrentIndex(i)
                break

        self.font_size.setValue(float(a.get("fontSize", 0.3)))
        self.flip_lr.setChecked(bool(a.get("flip_left_right", True)))
        self.correct_angles.setChecked(bool(a.get("correct_segment_angles_with_floor_angle", True)))

        self.joints_widget.set_values(a.get("joint_angles", JOINTS))
        self.segments_widget.set_values(a.get("segment_angles", SEGMENTS))

    def save_config(self, cfg: dict[str, Any]) -> None:
        a = cfg.setdefault("angles", {})

        d_text = self.angle_display.currentText().split()[0]
        if d_text == "body,list":
            a["display_angle_values_on"] = ["body", "list"]
        elif d_text == "none":
            a["display_angle_values_on"] = []
        else:
            a["display_angle_values_on"] = [d_text]

        a["fontSize"] = self.font_size.value()
        a["flip_left_right"] = self.flip_lr.isChecked()
        a["correct_segment_angles_with_floor_angle"] = self.correct_angles.isChecked()

        a["joint_angles"] = self.joints_widget.values()
        a["segment_angles"] = self.segments_widget.values()
