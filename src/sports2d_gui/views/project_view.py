from __future__ import annotations

import json
from typing import Any
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QDoubleSpinBox, QFormLayout, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QPlainTextEdit, QScrollArea, QSpinBox, QVBoxLayout, QWidget,
)

from ..widgets.card import CardWidget
from ..widgets.drag_drop import DragDropPathEdit, VideoDropZone


class ProjectView(QScrollArea):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QScrollArea.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # 1. Video Input Card
        card_video = CardWidget(
            "🎬 動画・カメラ入力",
            "解析する動画ファイル（.mp4/.avi等）を選択、またはWebcamを指定します。"
        )
        drop_zone = VideoDropZone()
        drop_zone.videosDropped.connect(self._on_videos_dropped)
        card_video.add_widget(drop_zone)

        self.videos_edit = QPlainTextEdit()
        self.videos_edit.setPlaceholderText("例: /path/to/video.mp4\n(Webcamを使用する場合は 'webcam' とだけ入力)")
        self.videos_edit.setMaximumHeight(70)
        self.videos_edit.setToolTip("1行に1つのファイルパスを入力。複数動画を連続処理できます。")

        card_video.add_widget(QLabel("動画ファイルリスト (1行1ファイル):"))
        card_video.add_widget(self.videos_edit)

        f_video = QFormLayout()
        f_video.setContentsMargins(0, 4, 0, 0)
        self.video_dir = DragDropPathEdit(directory=True, placeholder="動画が存在するフォルダ（省略可）")
        self.video_dir.setToolTip("動画の絶対パスを指定しない場合の基準フォルダ")
        f_video.addRow("検索用フォルダ (video_dir):", self.video_dir)
        card_video.add_layout(f_video)
        layout.addWidget(card_video)

        # 2. Target & People Settings Card (Grid Layout for compact view)
        card_target = CardWidget(
            "👤 検出対象と並び順",
            "動画内の人数や、複数人が映っている場合の優先順序を設定します。"
        )
        grid_target = QGridLayout()
        grid_target.setHorizontalSpacing(16)
        grid_target.setVerticalSpacing(10)

        self.nb_people = QLineEdit("all")
        self.nb_people.setToolTip("検出する人数。'all' で全員、'1' や '2' で指定人数に制限します。")

        self.ordering = QComboBox()
        self.ordering.addItems([
            "on_click (クリック選択)",
            "highest_likelihood (最高信頼度順)",
            "largest_size (身体サイズが大きい順)",
            "smallest_size (身体サイズが小さい順)",
            "greatest_displacement (移動量が大きい順)",
            "least_displacement (移動量が小さい順)",
            "first_detected (最初に検出された順)",
            "last_detected (最後に検出された順)"
        ])
        self.ordering.setToolTip("人物にIDを割り当てる際の優先ルール")

        self.first_height = QDoubleSpinBox()
        self.first_height.setRange(0.1, 3.0)
        self.first_height.setSingleStep(0.05)
        self.first_height.setValue(1.65)
        self.first_height.setSuffix(" m")
        self.first_height.setToolTip("1人目の推定身長。スケーリングの基準値として使用されます。")

        self.visible_side = QLineEdit("auto front none")
        self.visible_side.setToolTip("解析・可視化する側面 ('auto', 'front', 'back', 'left', 'right', 'none')")

        self.time_range = QLineEdit("")
        self.time_range.setPlaceholderText("例: 0 5.0 (0秒から5秒間だけ解析)")
        self.time_range.setToolTip("解析を行う時間範囲 [秒]。空欄なら全編解析します。")

        grid_target.addWidget(QLabel("検出人数 (nb_persons):"), 0, 0)
        grid_target.addWidget(self.nb_people, 0, 1)

        grid_target.addWidget(QLabel("人物優先順序 (ordering):"), 0, 2)
        grid_target.addWidget(self.ordering, 0, 3)

        grid_target.addWidget(QLabel("基準身長:"), 1, 0)
        grid_target.addWidget(self.first_height, 1, 1)

        grid_target.addWidget(QLabel("可視化側 (visible_side):"), 1, 2)
        grid_target.addWidget(self.visible_side, 1, 3)

        grid_target.addWidget(QLabel("解析時間範囲 [秒]:"), 2, 0)
        grid_target.addWidget(self.time_range, 2, 1, 1, 3)

        card_target.add_layout(grid_target)
        layout.addWidget(card_target)

        # 3. Webcam & Resolution Options Card
        card_cam = CardWidget(
            "📷 Webcam & 解像度詳細",
            "Webcam使用時のデバイスIDや入力画面の解像度を指定します。"
        )
        grid_cam = QGridLayout()
        grid_cam.setHorizontalSpacing(16)
        grid_cam.setVerticalSpacing(10)

        self.webcam_id = QSpinBox()
        self.webcam_id.setRange(0, 99)
        self.webcam_id.setValue(0)
        self.webcam_id.setToolTip("PCに接続されているWebcamのインデックス (通常 0)")

        self.combo_res = QComboBox()
        self.combo_res.addItems([
            "1280 × 720 (HD Standard)",
            "1920 × 1080 (Full HD)",
            "640 × 480 (SD Fast)",
            "カスタム指定"
        ])

        size_widget = QWidget()
        sz_layout = QHBoxLayout(size_widget)
        sz_layout.setContentsMargins(0, 0, 0, 0)
        self.input_w = QSpinBox(); self.input_w.setRange(64, 7680); self.input_w.setValue(1280)
        self.input_h = QSpinBox(); self.input_h.setRange(64, 4320); self.input_h.setValue(720)
        sz_layout.addWidget(self.input_w)
        sz_layout.addWidget(QLabel("×"))
        sz_layout.addWidget(self.input_h)

        self.combo_res.currentIndexChanged.connect(self._on_res_preset_changed)

        grid_cam.addWidget(QLabel("Webcam ID:"), 0, 0)
        grid_cam.addWidget(self.webcam_id, 0, 1)

        grid_cam.addWidget(QLabel("解像度プリセット:"), 0, 2)
        grid_cam.addWidget(self.combo_res, 0, 3)

        grid_cam.addWidget(QLabel("入力幅×高さ:"), 1, 0)
        grid_cam.addWidget(size_widget, 1, 1, 1, 3)

        card_cam.add_layout(grid_cam)
        layout.addWidget(card_cam)

        layout.addStretch()
        self.setWidget(container)

    def _on_res_preset_changed(self, index: int) -> None:
        if index == 0:
            self.input_w.setValue(1280); self.input_h.setValue(720)
        elif index == 1:
            self.input_w.setValue(1920); self.input_h.setValue(1080)
        elif index == 2:
            self.input_w.setValue(640); self.input_h.setValue(480)

    def _on_videos_dropped(self, paths: list[str]) -> None:
        curr = [line.strip() for line in self.videos_edit.toPlainText().splitlines() if line.strip()]
        for p in paths:
            if p not in curr:
                curr.append(p)
        self.videos_edit.setPlainText("\n".join(curr))

    def load_config(self, cfg: dict[str, Any]) -> None:
        b = cfg.get("base", {})
        vids = b.get("video_input", ["demo.mp4"])
        if isinstance(vids, list):
            self.videos_edit.setPlainText("\n".join(map(str, vids)))
        else:
            self.videos_edit.setPlainText(str(vids))

        self.nb_people.setText(str(b.get("nb_persons_to_detect", "all")))

        ord_val = str(b.get("person_ordering_method", "on_click"))
        for i in range(self.ordering.count()):
            if ord_val in self.ordering.itemText(i):
                self.ordering.setCurrentIndex(i)
                break

        self.first_height.setValue(float(b.get("first_person_height", 1.65)))

        vs = b.get("visible_side", ["auto", "front", "none"])
        if isinstance(vs, list):
            self.visible_side.setText(" ".join(map(str, vs)))
        else:
            self.visible_side.setText(str(vs))

        tr = b.get("time_range", [])
        if isinstance(tr, list) and all(not isinstance(x, list) for x in tr):
            self.time_range.setText(" ".join(map(str, tr)))
        else:
            self.time_range.setText(json.dumps(tr) if tr else "")

        self.video_dir.setText(str(b.get("video_dir", "")))
        self.webcam_id.setValue(int(b.get("webcam_id", 0)))
        sz = b.get("input_size", [1280, 720])
        if isinstance(sz, list) and len(sz) >= 2:
            self.input_w.setValue(int(sz[0]))
            self.input_h.setValue(int(sz[1]))

    def save_config(self, cfg: dict[str, Any]) -> None:
        b = cfg.setdefault("base", {})
        raw_vids = [line.strip() for line in self.videos_edit.toPlainText().splitlines() if line.strip()]
        b["video_input"] = raw_vids[0] if len(raw_vids) == 1 else raw_vids

        npv = self.nb_people.text().strip()
        b["nb_persons_to_detect"] = npv if npv == "all" else (int(npv) if npv.isdigit() else npv)

        # Extract order key
        raw_ord = self.ordering.currentText()
        b["person_ordering_method"] = raw_ord.split()[0]
        b["first_person_height"] = self.first_height.value()

        b["visible_side"] = self.visible_side.text().strip().split()
        tr_text = self.time_range.text().strip()
        if not tr_text:
            b["time_range"] = []
        elif tr_text.startswith("["):
            try:
                b["time_range"] = json.loads(tr_text)
            except Exception:
                b["time_range"] = []
        else:
            b["time_range"] = [float(x) for x in tr_text.split() if x]

        b["video_dir"] = self.video_dir.text()
        b["webcam_id"] = self.webcam_id.value()
        b["input_size"] = [self.input_w.value(), self.input_h.value()]
