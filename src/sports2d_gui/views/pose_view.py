from __future__ import annotations

import json
from typing import Any
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDoubleSpinBox, QFormLayout, QGridLayout, QLabel,
    QScrollArea, QSpinBox, QVBoxLayout, QWidget,
)

from ..widgets.card import CardWidget


class PoseView(QScrollArea):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QScrollArea.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # 1. Pose Model & Performance Settings Card
        card_model = CardWidget(
            "🦴 姿勢推定モデル & 推論エンジン",
            "姿勢検出モデルの種類、処理スピード・精度モード、CPU/GPUデバイスを設定します。"
        )
        grid_model = QGridLayout()
        grid_model.setHorizontalSpacing(16)
        grid_model.setVerticalSpacing(10)

        self.pose_model = QComboBox()
        self.pose_model.addItems([
            "body_with_feet (全身+足部・標準)",
            "whole_body_wrist (全身+手首詳細)",
            "whole_body (全身)",
            "lower_body (下半身のみ)",
            "body (上半身+下半身)",
            "hand (手部のみ)",
            "face (顔面のみ)",
            "animal (動物モデル)"
        ])
        self.pose_model.setToolTip("使用する姿勢推定骨格モデル")

        self.mode = QComboBox()
        self.mode.addItems([
            "balanced (バランス・推奨)",
            "performance (高精度・高負荷)",
            "lightweight (軽量・高速)"
        ])
        self.mode.setToolTip("モデルの処理精度と計算速度のバランス")

        self.device = QComboBox()
        self.device.addItems(["auto (自動検出)", "cpu (CPUモード)", "cuda (NVIDIA GPU)", "mps (Apple Silicon Mac)", "rocm (AMD GPU)"])
        self.device.setToolTip("計算に使用するアクセラレータデバイス")

        self.backend = QComboBox()
        self.backend.addItems(["auto (自動)", "openvino (Intel CPU最適化)", "onnxruntime (ONNX)", "opencv (OpenCV)"])
        self.backend.setToolTip("推論エンジンのバックエンド")

        self.det_freq = QSpinBox()
        self.det_freq.setRange(1, 1000)
        self.det_freq.setValue(4)
        self.det_freq.setSuffix(" フレームごと")
        self.det_freq.setToolTip("キーポイント検出を何フレームごとに実行するか (1なら毎フレーム)")

        grid_model.addWidget(QLabel("Pose Model:"), 0, 0)
        grid_model.addWidget(self.pose_model, 0, 1)

        grid_model.addWidget(QLabel("精度モード (Mode):"), 0, 2)
        grid_model.addWidget(self.mode, 0, 3)

        grid_model.addWidget(QLabel("実行デバイス:"), 1, 0)
        grid_model.addWidget(self.device, 1, 1)

        grid_model.addWidget(QLabel("推論バックエンド:"), 1, 2)
        grid_model.addWidget(self.backend, 1, 3)

        grid_model.addWidget(QLabel("検出頻度 (det_frequency):"), 2, 0)
        grid_model.addWidget(self.det_freq, 2, 1)

        card_model.add_layout(grid_model)
        layout.addWidget(card_model)

        # 2. Tracking Card
        card_track = CardWidget(
            "🏃 人物トラッキング (Tracking)",
            "フレーム間での人物の動きの追跡およびID維持の設定を行います。"
        )
        grid_track = QGridLayout()
        grid_track.setHorizontalSpacing(16)
        grid_track.setVerticalSpacing(10)

        self.tracking_mode = QComboBox()
        self.tracking_mode.addItems(["sports2d (標準軽量トラッカー)", "deepsort (DeepSORTトラッカー)"])
        self.tracking_mode.setToolTip("人物追跡アルゴリズム")

        self.predict_displacement = QCheckBox("移動予測を適用 (predict_displacement)")
        self.predict_displacement.setToolTip("前後のフレームから人物の移動位置を予測して追跡精度を上げます")

        self.match_by = QComboBox()
        self.match_by.addItems(["keypoints (キーポイント一致)", "centroid (重心位置一致)", "bbox (バウンディングボックス一致)"])

        self.max_distance = QSpinBox()
        self.max_distance.setRange(1, 10000)
        self.max_distance.setValue(250)
        self.max_distance.setSuffix(" px")
        self.max_distance.setToolTip("フレーム間で同一人物と判定する最大移動距離 [ピクセル]")

        self.min_iou = QDoubleSpinBox()
        self.min_iou.setRange(0.0, 1.0)
        self.min_iou.setSingleStep(0.05)
        self.min_iou.setValue(0.2)

        self.max_unseen = QDoubleSpinBox()
        self.max_unseen.setRange(0.0, 1000.0)
        self.max_unseen.setValue(1.0)
        self.max_unseen.setSuffix(" 秒")

        grid_track.addWidget(QLabel("トラッキング手法:"), 0, 0)
        grid_track.addWidget(self.tracking_mode, 0, 1)

        grid_track.addWidget(QLabel("位置予測:"), 0, 2)
        grid_track.addWidget(self.predict_displacement, 0, 3)

        grid_track.addWidget(QLabel("一致判定基準:"), 1, 0)
        grid_track.addWidget(self.match_by, 1, 1)

        grid_track.addWidget(QLabel("最大許容移動距離:"), 1, 2)
        grid_track.addWidget(self.max_distance, 1, 3)

        grid_track.addWidget(QLabel("最小 IoU 閾値:"), 2, 0)
        grid_track.addWidget(self.min_iou, 2, 1)

        grid_track.addWidget(QLabel("消失許容時間:"), 2, 2)
        grid_track.addWidget(self.max_unseen, 2, 3)

        card_track.add_layout(grid_track)
        layout.addWidget(card_track)

        # 3. Thresholds Card
        card_thr = CardWidget(
            "🎯 信頼度閾値 (Thresholds)",
            "ノイズとなる誤検出キーポイントを除外するための閾値設定です。"
        )
        grid_thr = QGridLayout()
        grid_thr.setHorizontalSpacing(16)
        grid_thr.setVerticalSpacing(10)

        self.kp_thr = QDoubleSpinBox(); self.kp_thr.setRange(0.0, 1.0); self.kp_thr.setSingleStep(0.05); self.kp_thr.setValue(0.3)
        self.kp_thr.setToolTip("単一キーポイントの最小信頼度 (0.0〜1.0)")

        self.avg_thr = QDoubleSpinBox(); self.avg_thr.setRange(0.0, 1.0); self.avg_thr.setSingleStep(0.05); self.avg_thr.setValue(0.5)
        self.avg_thr.setToolTip("人物全体での平均キーポイント最小信頼度 (0.0〜1.0)")

        self.kn_thr = QDoubleSpinBox(); self.kn_thr.setRange(0.0, 1.0); self.kn_thr.setSingleStep(0.05); self.kn_thr.setValue(0.3)
        self.kn_thr.setToolTip("有効とみなす最低キーポイント検出数の割合 (0.0〜1.0)")

        grid_thr.addWidget(QLabel("キーポイント最小尤度:"), 0, 0)
        grid_thr.addWidget(self.kp_thr, 0, 1)

        grid_thr.addWidget(QLabel("人物平均最小尤度:"), 0, 2)
        grid_thr.addWidget(self.avg_thr, 0, 3)

        grid_thr.addWidget(QLabel("有効キーポイント数割合:"), 1, 0)
        grid_thr.addWidget(self.kn_thr, 1, 1)

        card_thr.add_layout(grid_thr)
        layout.addWidget(card_thr)

        layout.addStretch()
        self.setWidget(container)

    def load_config(self, cfg: dict[str, Any]) -> None:
        p = cfg.get("pose", {})

        pm_val = str(p.get("pose_model", "body_with_feet"))
        for i in range(self.pose_model.count()):
            if pm_val in self.pose_model.itemText(i):
                self.pose_model.setCurrentIndex(i)
                break

        mode_val = str(p.get("mode", "balanced"))
        for i in range(self.mode.count()):
            if mode_val in self.mode.itemText(i):
                self.mode.setCurrentIndex(i)
                break

        dev_val = str(p.get("device", "auto"))
        for i in range(self.device.count()):
            if dev_val in self.device.itemText(i):
                self.device.setCurrentIndex(i)
                break

        back_val = str(p.get("backend", "auto"))
        for i in range(self.backend.count()):
            if back_val in self.backend.itemText(i):
                self.backend.setCurrentIndex(i)
                break

        self.det_freq.setValue(int(p.get("det_frequency", 4)))

        tr_val = str(p.get("tracking_mode", "sports2d"))
        for i in range(self.tracking_mode.count()):
            if tr_val in self.tracking_mode.itemText(i):
                self.tracking_mode.setCurrentIndex(i)
                break

        self.predict_displacement.setChecked(bool(p.get("predict_displacement", False)))

        mb_val = str(p.get("match_by", "keypoints"))
        for i in range(self.match_by.count()):
            if mb_val in self.match_by.itemText(i):
                self.match_by.setCurrentIndex(i)
                break

        self.max_distance.setValue(int(p.get("max_distance", 250) or 250))
        self.min_iou.setValue(float(p.get("min_iou", 0.2)))
        self.max_unseen.setValue(float(p.get("max_unseen_time", 1.0)))

        self.kp_thr.setValue(float(p.get("keypoint_likelihood_threshold", 0.3)))
        self.avg_thr.setValue(float(p.get("average_likelihood_threshold", 0.5)))
        self.kn_thr.setValue(float(p.get("keypoint_number_threshold", 0.3)))

    def save_config(self, cfg: dict[str, Any]) -> None:
        p = cfg.setdefault("pose", {})
        p["pose_model"] = self.pose_model.currentText().split()[0]
        p["mode"] = self.mode.currentText().split()[0]
        p["device"] = self.device.currentText().split()[0]
        p["backend"] = self.backend.currentText().split()[0]
        p["det_frequency"] = self.det_freq.value()

        p["tracking_mode"] = self.tracking_mode.currentText().split()[0]
        p["predict_displacement"] = self.predict_displacement.isChecked()
        p["match_by"] = self.match_by.currentText().split()[0]
        p["max_distance"] = self.max_distance.value()
        p["min_iou"] = self.min_iou.value()
        p["max_unseen_time"] = self.max_unseen.value()

        p["keypoint_likelihood_threshold"] = self.kp_thr.value()
        p["average_likelihood_threshold"] = self.avg_thr.value()
        p["keypoint_number_threshold"] = self.kn_thr.value()
