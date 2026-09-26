from __future__ import annotations

from typing import Any
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDoubleSpinBox, QFormLayout, QGridLayout, QLabel, QLineEdit,
    QScrollArea, QSpinBox, QVBoxLayout, QWidget,
)

from ..widgets.card import CardWidget
from ..widgets.drag_drop import DragDropPathEdit


class KinematicsView(QScrollArea):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QScrollArea.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # 1. OpenSim & IK Card
        card_ik = CardWidget(
            "🏃 逆運動学 (Inverse Kinematics / OpenSim)",
            "3D推定へのキーポイント拡張(Augmentation)および OpenSim 筋肉骨格モデル連動解析です。"
        )
        grid_ik = QGridLayout()
        grid_ik.setHorizontalSpacing(16)
        grid_ik.setVerticalSpacing(10)

        self.augmentation = QCheckBox("Keypoint Augmentation 拡張実行 (do_augmentation)")
        self.ik = QCheckBox("Inverse Kinematics (IK) 逆運動学計算 (do_ik)")
        self.filter_ik = QCheckBox("IK計算結果を平滑化フィルタリング (filter_ik)")

        self.ik_filter_type = QComboBox()
        self.ik_filter_type.addItems(["acc_minimizing", "butterworth", "kalman", "one_euro", "gcv_spline"])

        self.feet_floor = QCheckBox("両足を床面に接地拘束 (feet_on_floor)")
        self.simple_model = QCheckBox("簡易骨格モデルを使用 (use_simple_model)")
        self.symmetry = QCheckBox("左右対称身体パラメータ (right_left_symmetry)")

        grid_ik.addWidget(self.augmentation, 0, 0, 1, 2)
        grid_ik.addWidget(self.ik, 0, 2, 1, 2)

        grid_ik.addWidget(self.filter_ik, 1, 0, 1, 2)
        grid_ik.addWidget(QLabel("IKフィルタ種類:"), 1, 2)
        grid_ik.addWidget(self.ik_filter_type, 1, 3)

        grid_ik.addWidget(self.feet_floor, 2, 0, 1, 2)
        grid_ik.addWidget(self.simple_model, 2, 2, 1, 2)
        grid_ik.addWidget(self.symmetry, 3, 0, 1, 2)

        card_ik.add_layout(grid_ik)
        layout.addWidget(card_ik)

        # 2. Physical Parameters Card
        card_params = CardWidget(
            "🏋️ 被験者身体パラメータ & OpenSimパス",
            "物理シミュレーションに必要な体重・デフォルト身長およびモデル構成ファイルのパスです。"
        )
        f_params = QFormLayout()

        self.participant_mass = QLineEdit("55.0 67.0")
        self.participant_mass.setPlaceholderText("半角スペース区切りで体重 [kg] を指定 (例: 65.0)")

        self.default_height = QDoubleSpinBox()
        self.default_height.setRange(0.1, 3.0)
        self.default_height.setSingleStep(0.05)
        self.default_height.setValue(1.70)
        self.default_height.setSuffix(" m")

        self.workers = QLineEdit("auto")
        self.workers.setPlaceholderText("auto または スレッド数 (例: 4)")

        self.large_angle = QDoubleSpinBox()
        self.large_angle.setRange(0.0, 180.0)
        self.large_angle.setValue(135.0)
        self.large_angle.setSuffix(" deg")

        self.trimmed_percent = QSpinBox()
        self.trimmed_percent.setRange(0, 100)
        self.trimmed_percent.setValue(50)
        self.trimmed_percent.setSuffix(" %")

        self.remove_scale = QCheckBox("個別 Scaling Setup ファイルを自動削除")
        self.remove_ik = QCheckBox("個別 IK Setup ファイルを自動削除")

        self.osim_path = DragDropPathEdit(directory=True, placeholder="OpenSim テンプレート定義のディレクトリパス")

        f_params.addRow("被験者体重 [kg]:", self.participant_mass)
        f_params.addRow("デフォルト身長:", self.default_height)
        f_params.addRow("並列計算ワーカー数:", self.workers)
        f_params.addRow("股・膝大屈曲角 [度]:", self.large_angle)
        f_params.addRow("トリミング割合:", self.trimmed_percent)
        f_params.addRow("Scaling Setup削除:", self.remove_scale)
        f_params.addRow("IK Setup削除:", self.remove_ik)
        f_params.addRow("OpenSim Setup Path:", self.osim_path)

        card_params.add_layout(f_params)
        layout.addWidget(card_params)

        layout.addStretch()
        self.setWidget(container)

    def load_config(self, cfg: dict[str, Any]) -> None:
        k = cfg.get("kinematics", {})
        self.augmentation.setChecked(bool(k.get("do_augmentation", False)))
        self.ik.setChecked(bool(k.get("do_ik", False)))
        self.filter_ik.setChecked(bool(k.get("filter_ik", False)))
        self.ik_filter_type.setCurrentText(str(k.get("ik_filter_type", "acc_minimizing")))
        self.feet_floor.setChecked(bool(k.get("feet_on_floor", False)))
        self.simple_model.setChecked(bool(k.get("use_simple_model", False)))
        self.symmetry.setChecked(bool(k.get("right_left_symmetry", True)))

        pm = k.get("participant_mass", [55.0, 67.0])
        if isinstance(pm, list):
            self.participant_mass.setText(" ".join(map(str, pm)))
        else:
            self.participant_mass.setText(str(pm))

        self.default_height.setValue(float(k.get("default_height", 1.70)))
        self.workers.setText(str(k.get("parallel_workers_kinematics", "auto")))
        self.large_angle.setValue(float(k.get("large_hip_knee_angles", 135.0)))
        self.trimmed_percent.setValue(int(k.get("trimmed_extrema_percent", 50)))
        self.remove_scale.setChecked(bool(k.get("remove_individual_scaling_setup", True)))
        self.remove_ik.setChecked(bool(k.get("remove_individual_ik_setup", True)))
        self.osim_path.setText(str(k.get("osim_setup_path", "../OpenSim_setup")))

    def save_config(self, cfg: dict[str, Any]) -> None:
        k = cfg.setdefault("kinematics", {})
        k["do_augmentation"] = self.augmentation.isChecked()
        k["do_ik"] = self.ik.isChecked()
        k["filter_ik"] = self.filter_ik.isChecked()
        k["ik_filter_type"] = self.ik_filter_type.currentText()
        k["feet_on_floor"] = self.feet_floor.isChecked()
        k["use_simple_model"] = self.simple_model.isChecked()
        k["right_left_symmetry"] = self.symmetry.isChecked()

        pm_text = self.participant_mass.text().strip()
        k["participant_mass"] = [float(x) for x in pm_text.split() if x]

        k["default_height"] = self.default_height.value()
        w_text = self.workers.text().strip()
        k["parallel_workers_kinematics"] = int(w_text) if w_text.isdigit() else (w_text or "auto")

        k["large_hip_knee_angles"] = self.large_angle.value()
        k["trimmed_extrema_percent"] = self.trimmed_percent.value()
        k["remove_individual_scaling_setup"] = self.remove_scale.isChecked()
        k["remove_individual_ik_setup"] = self.remove_ik.isChecked()
        k["osim_setup_path"] = self.osim_path.text()
