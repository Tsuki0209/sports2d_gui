from __future__ import annotations

from typing import Any
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QFormLayout, QGridLayout, QHBoxLayout, QLabel, QScrollArea, QSpinBox, QVBoxLayout, QWidget,
)

from ..widgets.card import CardWidget
from ..widgets.filter_widget import FilterConfigWidget


class PostView(QScrollArea):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QScrollArea.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # 1. Interpolation & Outliers Card
        card_interp = CardWidget(
            "✂️ データ補間 & 欠損・外れ値処理",
            "姿勢検出のブレやオクルージョン（隠れ）による欠損値の穴埋め・外れ値除去を設定します。"
        )
        grid_interp = QGridLayout()
        grid_interp.setHorizontalSpacing(16)
        grid_interp.setVerticalSpacing(10)

        self.interpolate = QCheckBox("欠損フレームの自動補間 (interpolate)")
        self.interpolate.setToolTip("検出できなかったフレームを直線・スプラインでスムーズに繋ぎます")

        self.interp_gap = QSpinBox()
        self.interp_gap.setRange(1, 100000)
        self.interp_gap.setValue(100)
        self.interp_gap.setSuffix(" フレーム")
        self.interp_gap.setToolTip("これ以上長い欠損区間は補間せずそのままにします")

        self.fill_gaps = QComboBox()
        self.fill_gaps.addItems([
            "last_value (直前の値で埋める)",
            "nan (NaN空欄にする)",
            "zeros (0で埋める)"
        ])

        self.sections_to_keep = QComboBox()
        self.sections_to_keep.addItems([
            "all (すべての有効区間を保持)",
            "largest (最大連続データ区間のみ)",
            "first (最初の区間のみ)",
            "last (最後の区間のみ)"
        ])

        self.min_chunk = QSpinBox()
        self.min_chunk.setRange(1, 100000)
        self.min_chunk.setValue(10)
        self.min_chunk.setSuffix(" フレーム")

        self.reject_outliers = QCheckBox("外れ値（異常なスパイク座標）を自動除去 (reject_outliers)")

        grid_interp.addWidget(self.interpolate, 0, 0, 1, 2)
        grid_interp.addWidget(self.reject_outliers, 0, 2, 1, 2)

        grid_interp.addWidget(QLabel("最大許容欠損幅:"), 1, 0)
        grid_interp.addWidget(self.interp_gap, 1, 1)

        grid_interp.addWidget(QLabel("大ギャップ埋め方:"), 1, 2)
        grid_interp.addWidget(self.fill_gaps, 1, 3)

        grid_interp.addWidget(QLabel("保持区間ルール:"), 2, 0)
        grid_interp.addWidget(self.sections_to_keep, 2, 1)

        grid_interp.addWidget(QLabel("最小チャンク長:"), 2, 2)
        grid_interp.addWidget(self.min_chunk, 2, 3)

        card_interp.add_layout(grid_interp)
        layout.addWidget(card_interp)

        # 2. Filtering Card
        card_filter = CardWidget(
            "🎛️ 信号処理フィルタ (Filtering)",
            "関節軌跡のガタつきを滑らかにする平滑化フィルタの種類とパラメータです。"
        )
        f_filter = QHBoxLayout()
        self.filter_enabled = QCheckBox("フィルタ処理を実行 (filter)")
        self.show_graphs = QCheckBox("処理前後グラフを表示 (show_graphs)")
        self.save_graphs = QCheckBox("処理前後グラフ画像を保存 (save_graphs)")

        f_filter.addWidget(self.filter_enabled)
        f_filter.addWidget(self.show_graphs)
        f_filter.addWidget(self.save_graphs)
        f_filter.addStretch()

        card_filter.add_layout(f_filter)

        self.filter_config = FilterConfigWidget()
        card_filter.add_widget(self.filter_config)

        layout.addWidget(card_filter)
        layout.addStretch()
        self.setWidget(container)

    def load_config(self, cfg: dict[str, Any]) -> None:
        pp = cfg.get("post-processing", {})
        self.interpolate.setChecked(bool(pp.get("interpolate", True)))
        self.interp_gap.setValue(int(pp.get("interp_gap_smaller_than", 100)))

        fg_val = str(pp.get("fill_large_gaps_with", "last_value"))
        for i in range(self.fill_gaps.count()):
            if fg_val in self.fill_gaps.itemText(i):
                self.fill_gaps.setCurrentIndex(i)
                break

        sk_val = str(pp.get("sections_to_keep", "all"))
        for i in range(self.sections_to_keep.count()):
            if sk_val in self.sections_to_keep.itemText(i):
                self.sections_to_keep.setCurrentIndex(i)
                break

        self.min_chunk.setValue(int(pp.get("min_chunk_size", 10)))
        self.reject_outliers.setChecked(bool(pp.get("reject_outliers", True)))

        self.filter_enabled.setChecked(bool(pp.get("filter", True)))
        self.show_graphs.setChecked(bool(pp.get("show_graphs", True)))
        self.save_graphs.setChecked(bool(pp.get("save_graphs", True)))

        self.filter_config.set_params_dict(pp)

    def save_config(self, cfg: dict[str, Any]) -> None:
        pp = cfg.setdefault("post-processing", {})
        pp["interpolate"] = self.interpolate.isChecked()
        pp["interp_gap_smaller_than"] = self.interp_gap.value()
        pp["fill_large_gaps_with"] = self.fill_gaps.currentText().split()[0]
        pp["sections_to_keep"] = self.sections_to_keep.currentText().split()[0]
        pp["min_chunk_size"] = self.min_chunk.value()
        pp["reject_outliers"] = self.reject_outliers.isChecked()

        pp["filter"] = self.filter_enabled.isChecked()
        pp["show_graphs"] = self.show_graphs.isChecked()
        pp["save_graphs"] = self.save_graphs.isChecked()

        f_params = self.filter_config.get_params_dict()
        pp.update(f_params)
