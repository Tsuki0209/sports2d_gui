from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication, QComboBox, QFileDialog, QFormLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QListWidget, QMainWindow, QMessageBox, QPlainTextEdit,
    QPushButton, QSpinBox, QDoubleSpinBox, QSplitter, QTabWidget, QVBoxLayout, QWidget,
    QCheckBox,
)

from .config import default_config, dump_toml, load_toml, merge_dicts, parse_toml_text, toml_text, validate_config
from .worker import Sports2DWorker
from .widgets import MultiSelectList, PathEdit


JOINTS = [
    "Right ankle", "Left ankle", "Right knee", "Left knee", "Right hip", "Left hip",
    "Right shoulder", "Left shoulder", "Right elbow", "Left elbow", "Right wrist", "Left wrist",
]
SEGMENTS = [
    "Right foot", "Left foot", "Right shank", "Left shank", "Right thigh", "Left thigh", "Pelvis",
    "Trunk", "Shoulders", "Head", "Right arm", "Left arm", "Right forearm", "Left forearm",
]
FILTERS = ["butterworth", "acc_minimizing", "kalman", "one_euro", "gcv_spline", "gaussian", "loess", "median", "butterworth_on_speed"]


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Sports2D GUI")
        self.resize(1320, 880)
        self.config = default_config()
        self.current_config_path: Path | None = None
        self.worker: Sports2DWorker | None = None
        self._building = False
        self.build_ui()
        self.from_config(self.config)
        self.update_environment()

    def build_ui(self):
        self.setStyleSheet("""
            QWidget { font-size: 13px; }
            QGroupBox { font-weight: 600; margin-top: 12px; padding-top: 8px; }
            QTabBar::tab { padding: 8px 14px; }
            QPlainTextEdit { font-family: Consolas, 'SFMono-Regular', monospace; }
            QPushButton { padding: 6px 12px; }
        """)

        central = QWidget()
        root = QVBoxLayout(central)
        self.setCentralWidget(central)

        toolbar = QHBoxLayout()
        self.btn_new = QPushButton("新規")
        self.btn_open = QPushButton("TOMLを開く")
        self.btn_save = QPushButton("TOML保存")
        self.btn_save_as = QPushButton("名前を付けて保存")
        self.btn_validate = QPushButton("検証")
        self.btn_run = QPushButton("解析開始")
        self.btn_stop = QPushButton("停止")
        self.btn_stop.setEnabled(False)
        for w in [self.btn_new, self.btn_open, self.btn_save, self.btn_save_as, self.btn_validate, self.btn_run, self.btn_stop]:
            toolbar.addWidget(w)
        toolbar.addStretch()
        self.env_label = QLabel("Sports2D: 検出中…")
        toolbar.addWidget(self.env_label)
        root.addLayout(toolbar)

        splitter = QSplitter(Qt.Orientation.Vertical)
        root.addWidget(splitter, 1)
        self.tabs = QTabWidget()
        splitter.addWidget(self.tabs)

        self.tab_base = self.make_base_tab()
        self.tab_pose = self.make_pose_tab()
        self.tab_calib = self.make_calib_tab()
        self.tab_angles = self.make_angles_tab()
        self.tab_post = self.make_post_tab()
        self.tab_kin = self.make_kinematics_tab()
        self.tab_output = self.make_output_tab()
        self.tab_adv = self.make_advanced_tab()
        self.tab_env = self.make_environment_tab()
        for name, tab in [
            ("プロジェクト", self.tab_base), ("Pose / Tracking", self.tab_pose), ("座標変換", self.tab_calib),
            ("角度", self.tab_angles), ("Post-processing", self.tab_post), ("Kinematics / IK", self.tab_kin),
            ("出力", self.tab_output), ("Advanced TOML", self.tab_adv), ("環境", self.tab_env),
        ]:
            self.tabs.addTab(tab, name)

        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("Sports2D の実行ログ…")
        splitter.addWidget(self.log)
        splitter.setSizes([630, 250])

        self.statusBar().showMessage("準備完了")
        self.btn_new.clicked.connect(self.new_project)
        self.btn_open.clicked.connect(self.open_toml)
        self.btn_save.clicked.connect(self.save_toml)
        self.btn_save_as.clicked.connect(self.save_as_toml)
        self.btn_validate.clicked.connect(self.validate_current)
        self.btn_run.clicked.connect(self.start_run)
        self.btn_stop.clicked.connect(self.stop_run)

    def form_layout(self):
        w = QWidget(); layout = QFormLayout(w); layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow); return w, layout

    def add_row(self, layout, label, widget):
        layout.addRow(label, widget)
        return widget

    def make_base_tab(self):
        w, f = self.form_layout()
        videos = QPlainTextEdit(); videos.setMaximumHeight(90); videos.setPlaceholderText("1行1ファイル。空なら未指定。webcam を入力するとwebcamモード")
        self.videos = videos
        self.nb_people = QLineEdit("all")
        self.ordering = QComboBox(); self.ordering.addItems(["on_click","highest_likelihood","largest_size","smallest_size","greatest_displacement","least_displacement","first_detected","last_detected"])
        self.height = QDoubleSpinBox(); self.height.setRange(0.1, 3.5); self.height.setDecimals(3)
        self.visible_side = QLineEdit("auto front none")
        self.time_range = QLineEdit(""); self.time_range.setPlaceholderText("例: 0 3.5 / 複数動画: 0 3.5 2 5")
        self.video_dir = PathEdit(directory=True)
        self.webcam_id = QSpinBox(); self.webcam_id.setRange(0, 99)
        self.input_w = QSpinBox(); self.input_w.setRange(64, 10000)
        self.input_h = QSpinBox(); self.input_h.setRange(64, 10000)
        f.addRow("動画入力", videos)
        f.addRow("人数", self.nb_people); f.addRow("人物順序", self.ordering); f.addRow("基準身長 [m]", self.height)
        f.addRow("visible_side", self.visible_side); f.addRow("time_range", self.time_range); f.addRow("video_dir", self.video_dir)
        size = QWidget(); hl=QHBoxLayout(size); hl.setContentsMargins(0,0,0,0); hl.addWidget(self.input_w); hl.addWidget(QLabel("×")); hl.addWidget(self.input_h); f.addRow("入力解像度", size)
        f.addRow("webcam_id", self.webcam_id)
        note = QLabel("動画は1行1本で指定可能。絶対パスでも、video_dirからの相対パスでも構いません。Sports2Dは複数動画と個別time_rangeに対応します。")
        note.setWordWrap(True); f.addRow(note)
        w.setLayout(f); return w

    def make_pose_tab(self):
        w, f = self.form_layout()
        self.pose_model = QComboBox(); self.pose_model.addItems(["body_with_feet","whole_body_wrist","whole_body","lower_body","body","hand","face","animal"])
        self.mode = QComboBox(); self.mode.addItems(["lightweight","balanced","performance"])
        self.mode_custom = QPlainTextEdit(); self.mode_custom.setPlaceholderText("custom mode を使う場合はPython dict表記を入力"); self.mode_custom.setMaximumHeight(65)
        self.det_freq = QSpinBox(); self.det_freq.setRange(1, 10000)
        self.device = QComboBox(); self.device.addItems(["auto","cpu","cuda","mps","rocm"])
        self.backend = QComboBox(); self.backend.addItems(["auto","openvino","onnxruntime","opencv"])
        self.tracking = QComboBox(); self.tracking.addItems(["sports2d","deepsort"])
        self.predict = QCheckBox(); self.match_by = QComboBox(); self.match_by.addItems(["keypoints","centroid","bbox"])
        self.max_distance = QLineEdit(); self.min_iou = QDoubleSpinBox(); self.min_iou.setRange(0,1); self.min_iou.setDecimals(3)
        self.max_unseen = QDoubleSpinBox(); self.max_unseen.setRange(0,1000); self.max_unseen.setDecimals(3)
        self.deepsort = QPlainTextEdit(); self.deepsort.setMaximumHeight(75)
        self.kp_thr = QDoubleSpinBox(); self.kp_thr.setRange(0,1); self.kp_thr.setDecimals(3)
        self.avg_thr = QDoubleSpinBox(); self.avg_thr.setRange(0,1); self.avg_thr.setDecimals(3)
        self.kn_thr = QDoubleSpinBox(); self.kn_thr.setRange(0,1); self.kn_thr.setDecimals(3)
        for label, obj in [("pose_model",self.pose_model),("mode",self.mode),("custom mode",self.mode_custom),("det_frequency",self.det_freq),("device",self.device),("backend",self.backend),("tracking_mode",self.tracking),("predict_displacement",self.predict),("match_by",self.match_by),("max_distance",self.max_distance),("min_iou",self.min_iou),("max_unseen_time",self.max_unseen),("deepsort_params",self.deepsort),("keypoint threshold",self.kp_thr),("average likelihood",self.avg_thr),("keypoint number",self.kn_thr)]: f.addRow(label,obj)
        info = QLabel("custom mode と CUSTOM skeleton、その他の将来項目は Advanced TOML から完全に編集できます。")
        info.setWordWrap(True); f.addRow(info)
        return w

    def make_calib_tab(self):
        w, f = self.form_layout()
        self.to_meters = QCheckBox(); self.c3d = QCheckBox(); self.save_calib=QCheckBox()
        self.perspective_value=QDoubleSpinBox(); self.perspective_value.setRange(0,1e6); self.perspective_value.setDecimals(4)
        self.perspective_unit=QComboBox(); self.perspective_unit.addItems(["distance_m","f_px","fov_deg","fov_rad","from_calib"])
        self.floor_angle=QLineEdit(); self.xy_origin=QLineEdit(); self.distortions=QLineEdit(); self.calib_file=PathEdit(file=True, filter="TOML (*.toml);;All files (*)")
        for label,obj in [("to_meters",self.to_meters),("make_c3d",self.c3d),("save_calib",self.save_calib),("perspective_value",self.perspective_value),("perspective_unit",self.perspective_unit),("floor_angle",self.floor_angle),("xy_origin",self.xy_origin),("distortions",self.distortions),("calib_file",self.calib_file)]: f.addRow(label,obj)
        return w

    def make_angles_tab(self):
        w, root = QWidget(), QVBoxLayout()
        self.angle_display=QComboBox(); self.angle_display.addItems(["none","body","list","body,list"])
        self.joints=MultiSelectList(JOINTS)
        self.segments=MultiSelectList(SEGMENTS)
        self.font_size=QDoubleSpinBox(); self.font_size.setRange(0.01,3.0); self.font_size.setDecimals(3)
        self.correct_angles=QCheckBox()
        top=QFormLayout(); top.addRow("表示",self.angle_display); top.addRow("fontSize",self.font_size); top.addRow("床角で補正",self.correct_angles)
        root.addLayout(top); root.addWidget(QLabel("関節角度")); root.addWidget(self.joints); root.addWidget(QLabel("セグメント角度")); root.addWidget(self.segments); w.setLayout(root); return w

    def make_post_tab(self):
        w, root = QWidget(), QVBoxLayout(); form=QFormLayout()
        self.interpolate=QCheckBox(); self.interp_gap=QSpinBox(); self.interp_gap.setRange(0,100000)
        self.fill_gaps=QComboBox(); self.fill_gaps.addItems(["last_value","nan","zeros"])
        self.sections=QComboBox(); self.sections.addItems(["all","largest","first","last"]); self.min_chunk=QSpinBox(); self.min_chunk.setRange(0,100000)
        self.reject_outliers=QCheckBox(); self.filter_enabled=QCheckBox(); self.show_graphs=QCheckBox(); self.save_graphs=QCheckBox(); self.filter_type=QComboBox(); self.filter_type.addItems(FILTERS)
        for l,o in [("interpolate",self.interpolate),("interp_gap_smaller_than",self.interp_gap),("fill_large_gaps_with",self.fill_gaps),("sections_to_keep",self.sections),("min_chunk_size",self.min_chunk),("reject_outliers",self.reject_outliers),("filter",self.filter_enabled),("show_graphs",self.show_graphs),("save_graphs",self.save_graphs),("filter_type",self.filter_type)]: form.addRow(l,o)
        root.addLayout(form)
        self.filter_params=QPlainTextEdit(); self.filter_params.setPlaceholderText("選択中フィルタのパラメータをTOML風ではなくJSONで指定可。空ならAdvanced TOMLの値を使用")
        self.filter_params.setPlainText(json.dumps({"butterworth":{"cut_off_frequency":6.0,"order":4}}, ensure_ascii=False, indent=2))
        root.addWidget(QLabel("フィルタ詳細（任意のJSON上書き）")); root.addWidget(self.filter_params)
        return w

    def make_kinematics_tab(self):
        w, f = self.form_layout()
        self.augmentation=QCheckBox(); self.ik=QCheckBox(); self.filter_ik=QCheckBox(); self.ik_filter=QComboBox(); self.ik_filter.addItems(FILTERS)
        self.feet_floor=QCheckBox(); self.simple_model=QCheckBox(); self.mass=QLineEdit(); self.workers=QLineEdit("auto"); self.symmetry=QCheckBox(); self.default_height=QDoubleSpinBox(); self.default_height.setRange(0.1,3.5); self.default_height.setDecimals(3)
        self.large_angle=QDoubleSpinBox(); self.large_angle.setRange(0,180); self.large_angle.setDecimals(1); self.trimmed=QSpinBox(); self.trimmed.setRange(0,100)
        self.remove_scale=QCheckBox(); self.remove_ik=QCheckBox(); self.osim_path=PathEdit(directory=True)
        for l,o in [("do_augmentation",self.augmentation),("do_ik",self.ik),("filter_ik",self.filter_ik),("ik_filter_type",self.ik_filter),("feet_on_floor",self.feet_floor),("use_simple_model",self.simple_model),("participant_mass",self.mass),("parallel_workers_kinematics",self.workers),("right_left_symmetry",self.symmetry),("default_height",self.default_height),("large_hip_knee_angles",self.large_angle),("trimmed_extrema_percent",self.trimmed),("remove_individual_scaling_setup",self.remove_scale),("remove_individual_ik_setup",self.remove_ik),("osim_setup_path",self.osim_path)]: f.addRow(l,o)
        return w

    def make_output_tab(self):
        w, f=self.form_layout()
        self.show_realtime=QCheckBox(); self.save_vid=QCheckBox(); self.save_img=QCheckBox(); self.save_pose=QCheckBox(); self.calc_angles=QCheckBox(); self.save_angles=QCheckBox(); self.slowmo=QDoubleSpinBox(); self.slowmo.setRange(0.01,100); self.slowmo.setDecimals(3); self.result_dir=PathEdit(directory=True); self.load_trc=PathEdit(file=True); self.compare=QCheckBox()
        for l,o in [("show_realtime_results",self.show_realtime),("save_vid",self.save_vid),("save_img",self.save_img),("save_pose",self.save_pose),("calculate_angles",self.calc_angles),("save_angles",self.save_angles),("slowmo_factor",self.slowmo),("result_dir",self.result_dir),("load_trc_px",self.load_trc),("compare",self.compare)]: f.addRow(l,o)
        return w

    def make_advanced_tab(self):
        w=QWidget(); l=QVBoxLayout(w)
        self.toml_edit=QPlainTextEdit(); l.addWidget(QLabel("このテキストがSports2Dへ渡す最終TOMLです。ここを編集すれば、GUIフォームにない項目もそのまま利用できます。")); l.addWidget(self.toml_edit,1)
        btns=QHBoxLayout(); self.btn_form_to_toml=QPushButton("フォーム→TOML"); self.btn_toml_to_form=QPushButton("TOML→フォーム"); btns.addWidget(self.btn_form_to_toml); btns.addWidget(self.btn_toml_to_form); btns.addStretch(); l.addLayout(btns)
        self.btn_form_to_toml.clicked.connect(lambda: self.toml_edit.setPlainText(toml_text(self.to_config())))
        self.btn_toml_to_form.clicked.connect(self.import_toml_text)
        return w

    def make_environment_tab(self):
        w, f=self.form_layout()
        self.python_path=QLineEdit(sys.executable); self.sports2d_path=QLineEdit(); self.sports2d_version=QLineEdit(); self.sports2d_version.setReadOnly(True); self.pyside_version=QLineEdit(); self.pyside_version.setReadOnly(True)
        btn=QPushButton("再チェック"); btn.clicked.connect(self.update_environment)
        f.addRow("Python", self.python_path); f.addRow("sports2d executable", self.sports2d_path); f.addRow("Sports2D version", self.sports2d_version); f.addRow("PySide6", self.pyside_version); f.addRow(btn)
        return w

    def from_config(self, cfg: dict[str, Any]):
        self._building=True
        try:
            b=cfg["base"]; p=cfg["pose"]; px=cfg["px_to_meters_conversion"]; a=cfg["angles"]; pp=cfg["post-processing"]; k=cfg["kinematics"]
            vids=b.get("video_input",[]); self.videos.setPlainText("\n".join(vids if isinstance(vids,list) else [str(vids)]))
            self.nb_people.setText(str(b.get("nb_persons_to_detect","all"))); self.ordering.setCurrentText(b.get("person_ordering_method","on_click")); self.height.setValue(float(b.get("first_person_height",1.65)))
            self.visible_side.setText(" ".join(b.get("visible_side",[])) if isinstance(b.get("visible_side"),list) else str(b.get("visible_side","auto")))
            tr=b.get("time_range",[]); self.time_range.setText(" ".join(map(str,tr)) if isinstance(tr,list) and all(not isinstance(x,list) for x in tr) else json.dumps(tr))
            self.video_dir.setText(str(b.get("video_dir",""))); self.webcam_id.setValue(int(b.get("webcam_id",0))); size=b.get("input_size",[1280,720]); self.input_w.setValue(int(size[0])); self.input_h.setValue(int(size[1]))
            self.pose_model.setCurrentText(str(p.get("pose_model","body_with_feet"))); mode=p.get("mode","balanced");
            if isinstance(mode,str) and mode in ["lightweight","balanced","performance"]: self.mode.setCurrentText(mode); self.mode_custom.clear()
            else: self.mode.setCurrentText("balanced"); self.mode_custom.setPlainText(json.dumps(mode, ensure_ascii=False, indent=2) if isinstance(mode,(dict,list)) else str(mode))
            self.det_freq.setValue(int(p.get("det_frequency",4))); self.device.setCurrentText(str(p.get("device","auto"))); self.backend.setCurrentText(str(p.get("backend","auto"))); self.tracking.setCurrentText(str(p.get("tracking_mode","sports2d"))); self.predict.setChecked(bool(p.get("predict_displacement",False))); self.match_by.setCurrentText(str(p.get("match_by","keypoints"))); self.max_distance.setText(str(p.get("max_distance",250))); self.min_iou.setValue(float(p.get("min_iou",.2))); self.max_unseen.setValue(float(p.get("max_unseen_time",1.0))); self.deepsort.setPlainText(str(p.get("deepsort_params",""))); self.kp_thr.setValue(float(p.get("keypoint_likelihood_threshold",.3))); self.avg_thr.setValue(float(p.get("average_likelihood_threshold",.5))); self.kn_thr.setValue(float(p.get("keypoint_number_threshold",.3)))
            self.to_meters.setChecked(bool(px.get("to_meters",True))); self.c3d.setChecked(bool(px.get("make_c3d",True))); self.save_calib.setChecked(bool(px.get("save_calib",True))); self.perspective_value.setValue(float(px.get("perspective_value",10))); self.perspective_unit.setCurrentText(str(px.get("perspective_unit","distance_m"))); self.floor_angle.setText(str(px.get("floor_angle","auto"))); self.xy_origin.setText(json.dumps(px.get("xy_origin",["auto"]), ensure_ascii=False)); self.distortions.setText(json.dumps(px.get("distortions",[0,0,0,0,0]))); self.calib_file.setText(str(px.get("calib_file","")))
            disp=a.get("display_angle_values_on",["body","list"]); disp="body,list" if isinstance(disp,list) and len(disp)>1 else (disp[0] if isinstance(disp,list) and disp else "none"); self.angle_display.setCurrentText(disp if disp in ["none","body","list"] else "body"); self.font_size.setValue(float(a.get("fontSize",.3))); self.correct_angles.setChecked(bool(a.get("correct_segment_angles_with_floor_angle",True))); self.set_multi(self.joints,a.get("joint_angles",JOINTS)); self.set_multi(self.segments,a.get("segment_angles",SEGMENTS))
            self.interpolate.setChecked(bool(pp.get("interpolate",True))); self.interp_gap.setValue(int(pp.get("interp_gap_smaller_than",100))); self.fill_gaps.setCurrentText(str(pp.get("fill_large_gaps_with","last_value"))); self.sections.setCurrentText(str(pp.get("sections_to_keep","all"))); self.min_chunk.setValue(int(pp.get("min_chunk_size",10))); self.reject_outliers.setChecked(bool(pp.get("reject_outliers",True))); self.filter_enabled.setChecked(bool(pp.get("filter",True))); self.show_graphs.setChecked(bool(pp.get("show_graphs",True))); self.save_graphs.setChecked(bool(pp.get("save_graphs",True))); self.filter_type.setCurrentText(str(pp.get("filter_type","butterworth")))
            self.augmentation.setChecked(bool(k.get("do_augmentation",False))); self.ik.setChecked(bool(k.get("do_ik",False))); self.filter_ik.setChecked(bool(k.get("filter_ik",False))); self.ik_filter.setCurrentText(str(k.get("ik_filter_type","acc_minimizing"))); self.feet_floor.setChecked(bool(k.get("feet_on_floor",False))); self.simple_model.setChecked(bool(k.get("use_simple_model",False))); self.mass.setText(" ".join(map(str,k.get("participant_mass",[])))); self.workers.setText(str(k.get("parallel_workers_kinematics","auto"))); self.symmetry.setChecked(bool(k.get("right_left_symmetry",True))); self.default_height.setValue(float(k.get("default_height",1.7))); self.large_angle.setValue(float(k.get("large_hip_knee_angles",135))); self.trimmed.setValue(int(k.get("trimmed_extrema_percent",50))); self.remove_scale.setChecked(bool(k.get("remove_individual_scaling_setup",True))); self.remove_ik.setChecked(bool(k.get("remove_individual_ik_setup",True))); self.osim_path.setText(str(k.get("osim_setup_path","")))
            self.show_realtime.setChecked(bool(b.get("show_realtime_results",True))); self.save_vid.setChecked(bool(b.get("save_vid",True))); self.save_img.setChecked(bool(b.get("save_img",True))); self.save_pose.setChecked(bool(b.get("save_pose",True))); self.calc_angles.setChecked(bool(b.get("calculate_angles",True))); self.save_angles.setChecked(bool(b.get("save_angles",True))); self.slowmo.setValue(float(p.get("slowmo_factor",1))); self.result_dir.setText(str(b.get("result_dir",""))); self.load_trc.setText(str(b.get("load_trc_px",""))); self.compare.setChecked(bool(b.get("compare",False)))
            self.toml_edit.setPlainText(toml_text(cfg))
        finally:
            self._building=False

    def set_multi(self, list_widget, selected):
        selected=set(selected or [])
        for i in range(list_widget.count()): list_widget.item(i).setCheckState(Qt.CheckState.Checked if list_widget.item(i).text() in selected else Qt.CheckState.Unchecked)

    def to_config(self):
        cfg=default_config(); b=cfg["base"]; p=cfg["pose"]; px=cfg["px_to_meters_conversion"]; a=cfg["angles"]; pp=cfg["post-processing"]; k=cfg["kinematics"]
        raw=[x.strip() for x in self.videos.toPlainText().splitlines() if x.strip()]; b["video_input"] = raw[0] if len(raw)==1 else raw
        npv=self.nb_people.text().strip(); b["nb_persons_to_detect"]=npv if npv=="all" else int(npv); b["person_ordering_method"]=self.ordering.currentText(); b["first_person_height"]=self.height.value(); b["visible_side"]=self.visible_side.text().split(); tr=self.time_range.text().strip();
        if not tr: b["time_range"]=[]
        elif tr.startswith("["): b["time_range"]=json.loads(tr)
        else: b["time_range"]= [float(x) for x in tr.split()]
        b["video_dir"]=self.video_dir.text(); b["webcam_id"]=self.webcam_id.value(); b["input_size"]= [self.input_w.value(),self.input_h.value()]
        p["pose_model"]=self.pose_model.currentText(); mode_custom=self.mode_custom.toPlainText().strip(); p["mode"] = json.loads(mode_custom) if mode_custom.startswith(("{","[")) else (mode_custom if mode_custom else self.mode.currentText()); p["det_frequency"]=self.det_freq.value(); p["device"]=self.device.currentText(); p["backend"]=self.backend.currentText(); p["tracking_mode"]=self.tracking.currentText(); p["predict_displacement"]=self.predict.isChecked(); p["match_by"]=self.match_by.currentText(); p["max_distance"]=None if self.max_distance.text().strip().lower()=="none" else int(float(self.max_distance.text())); p["min_iou"]=self.min_iou.value(); p["max_unseen_time"]=self.max_unseen.value(); p["deepsort_params"]=self.deepsort.toPlainText().strip(); p["keypoint_likelihood_threshold"]=self.kp_thr.value(); p["average_likelihood_threshold"]=self.avg_thr.value(); p["keypoint_number_threshold"]=self.kn_thr.value()
        px["to_meters"]=self.to_meters.isChecked(); px["make_c3d"]=self.c3d.isChecked(); px["save_calib"]=self.save_calib.isChecked(); px["perspective_value"]=self.perspective_value.value(); px["perspective_unit"]=self.perspective_unit.currentText(); px["floor_angle"]=self.floor_angle.text().strip() or "auto"; px["xy_origin"]=json.loads(self.xy_origin.text()) if self.xy_origin.text().strip().startswith("[") else [self.xy_origin.text().strip()]; px["distortions"]=json.loads(self.distortions.text()) if self.distortions.text().strip().startswith("[") else self.distortions.text().strip(); px["calib_file"]=self.calib_file.text()
        a["display_angle_values_on"]=["body","list"] if self.angle_display.currentText()=="body,list" else ([self.angle_display.currentText()] if self.angle_display.currentText()!="none" else "none"); a["fontSize"]=self.font_size.value(); a["joint_angles"]=self.joints.values(); a["segment_angles"]=self.segments.values(); a["correct_segment_angles_with_floor_angle"]=self.correct_angles.isChecked()
        pp["interpolate"]=self.interpolate.isChecked(); pp["interp_gap_smaller_than"]=self.interp_gap.value(); pp["fill_large_gaps_with"]=self.fill_gaps.currentText(); pp["sections_to_keep"]=self.sections.currentText(); pp["min_chunk_size"]=self.min_chunk.value(); pp["reject_outliers"]=self.reject_outliers.isChecked(); pp["filter"]=self.filter_enabled.isChecked(); pp["show_graphs"]=self.show_graphs.isChecked(); pp["save_graphs"]=self.save_graphs.isChecked(); pp["filter_type"]=self.filter_type.currentText()
        try:
            overrides=json.loads(self.filter_params.toPlainText())
            merge_dicts(pp,overrides)
        except Exception:
            pass
        k["do_augmentation"]=self.augmentation.isChecked(); k["do_ik"]=self.ik.isChecked(); k["filter_ik"]=self.filter_ik.isChecked(); k["ik_filter_type"]=self.ik_filter.currentText(); k["feet_on_floor"]=self.feet_floor.isChecked(); k["use_simple_model"]=self.simple_model.isChecked(); k["participant_mass"]= [float(x) for x in self.mass.text().split() if x]; k["parallel_workers_kinematics"]= (self.workers.text().strip() if self.workers.text().strip() else "auto"); k["right_left_symmetry"]=self.symmetry.isChecked(); k["default_height"]=self.default_height.value(); k["large_hip_knee_angles"]=self.large_angle.value(); k["trimmed_extrema_percent"]=self.trimmed.value(); k["remove_individual_scaling_setup"]=self.remove_scale.isChecked(); k["remove_individual_ik_setup"]=self.remove_ik.isChecked(); k["osim_setup_path"]=self.osim_path.text()
        b["show_realtime_results"]=self.show_realtime.isChecked(); b["save_vid"]=self.save_vid.isChecked(); b["save_img"]=self.save_img.isChecked(); b["save_pose"]=self.save_pose.isChecked(); b["calculate_angles"]=self.calc_angles.isChecked(); b["save_angles"]=self.save_angles.isChecked(); p["slowmo_factor"]=self.slowmo.value(); b["result_dir"]=self.result_dir.text(); b["load_trc_px"]=self.load_trc.text(); b["compare"]=self.compare.isChecked()
        return cfg

    def import_toml_text(self):
        try:
            cfg=parse_toml_text(self.toml_edit.toPlainText()); base=default_config(); merge_dicts(base,cfg); self.config=base; self.from_config(base); self.statusBar().showMessage("TOMLをフォームへ反映しました")
        except Exception as exc: QMessageBox.critical(self,"TOMLエラー",str(exc))

    def new_project(self):
        self.config=default_config(); self.current_config_path=None; self.from_config(self.config); self.log.clear(); self.statusBar().showMessage("新規プロジェクト")

    def open_toml(self):
        path,_=QFileDialog.getOpenFileName(self,"TOMLを開く",str(Path.cwd()),"TOML (*.toml);;All files (*)")
        if not path: return
        try:
            self.config=load_toml(path); self.current_config_path=Path(path); self.from_config(self.config); self.statusBar().showMessage(f"読み込み: {path}")
        except Exception as exc: QMessageBox.critical(self,"読み込みエラー",str(exc))

    def save_as_toml(self):
        path,_=QFileDialog.getSaveFileName(self,"TOMLを保存",str(self.current_config_path or Path.cwd()/"Sports2D_GUI.toml"),"TOML (*.toml)")
        if path: self.current_config_path=Path(path); self.save_toml()

    def save_toml(self):
        if self.current_config_path is None: return self.save_as_toml()
        try:
            cfg=parse_toml_text(self.toml_edit.toPlainText())
            dump_toml(cfg,self.current_config_path); self.statusBar().showMessage(f"保存: {self.current_config_path}")
        except Exception as exc: QMessageBox.critical(self,"保存エラー",str(exc))

    def validate_current(self):
        try: cfg=parse_toml_text(self.toml_edit.toPlainText())
        except Exception as exc: QMessageBox.critical(self,"TOMLエラー",str(exc)); return
        issues=validate_config(cfg)
        if issues: QMessageBox.warning(self,"検証", "\n".join(f"・{x}" for x in issues))
        else: QMessageBox.information(self,"検証","基本検証を通過しました。Sports2D固有の詳細検証は実行時に行われます。")

    def start_run(self):
        self.form_to_toml()
        try: cfg=parse_toml_text(self.toml_edit.toPlainText())
        except Exception as exc: QMessageBox.critical(self,"TOMLエラー",str(exc)); return
        issues=validate_config(cfg)
        if issues: QMessageBox.warning(self,"設定不備", "\n".join(f"・{x}" for x in issues)); return
        if self.current_config_path is None:
            temp_dir=Path(tempfile.mkdtemp(prefix="sports2d_gui_")); self.current_config_path=temp_dir/"Sports2D_GUI.toml"
        dump_toml(cfg,self.current_config_path)
        cwd=Path(cfg.get("base",{}).get("result_dir") or self.current_config_path.parent)
        cwd.mkdir(parents=True,exist_ok=True)
        self.log.clear(); self.btn_run.setEnabled(False); self.btn_stop.setEnabled(True)
        self.worker=Sports2DWorker(self.current_config_path,cwd)
        self.worker.log_line.connect(self.log.appendPlainText); self.worker.status.connect(self.statusBar().showMessage); self.worker.finished_ok.connect(self.run_finished); self.worker.start()

    def form_to_toml(self):
        try: self.toml_edit.setPlainText(toml_text(self.to_config()))
        except Exception as exc: QMessageBox.critical(self,"設定変換エラー",str(exc))

    def stop_run(self):
        if self.worker: self.worker.stop()

    def run_finished(self, code:int, _status:str):
        self.btn_run.setEnabled(True); self.btn_stop.setEnabled(False); self.statusBar().showMessage("完了" if code==0 else f"終了コード {code}")
        if code==0:
            QMessageBox.information(self,"Sports2D","解析が完了しました。結果フォルダを確認してください。")
        else:
            QMessageBox.warning(self,"Sports2D","解析が失敗または中断されました。下のログを確認してください。")
        self.worker=None

    def update_environment(self):
        exe=shutil.which("sports2d") or ""
        self.sports2d_path.setText(exe)
        try:
            import sports2d
            ver=getattr(sports2d,"__version__","")
            self.sports2d_version.setText(ver or "installed")
        except Exception as exc: self.sports2d_version.setText(f"未導入: {exc}")
        try:
            import PySide6
            self.pyside_version.setText(PySide6.__version__)
        except Exception: self.pyside_version.setText("unknown")
        self.env_label.setText(f"Sports2D: {'OK' if exe else 'PATH未検出'}")

    def closeEvent(self,event):
        if self.worker and self.worker.isRunning():
            self.worker.stop(); self.worker.wait(5000)
        event.accept()


def main() -> None:
    app=QApplication(sys.argv)
    app.setApplicationName("Sports2D GUI")
    win=MainWindow(); win.show()
    raise SystemExit(app.exec())


if __name__ == "__main__": main()
