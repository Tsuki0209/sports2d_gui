from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from tomlkit import dumps, load, parse

DEFAULT_CONFIG: dict[str, Any] = {
    "base": {
        "video_input": ["demo.mp4"],
        "nb_persons_to_detect": "all",
        "person_ordering_method": "on_click",
        "first_person_height": 1.65,
        "visible_side": ["auto", "front", "none"],
        "load_trc_px": "",
        "compare": False,
        "time_range": [],
        "video_dir": "",
        "webcam_id": 0,
        "input_size": [1280, 720],
        "show_realtime_results": True,
        "save_vid": True,
        "save_img": True,
        "save_pose": True,
        "calculate_angles": True,
        "save_angles": True,
        "result_dir": "",
    },
    "pose": {
        "slowmo_factor": 1.0,
        "pose_model": "body_with_feet",
        "mode": "balanced",
        "det_frequency": 4,
        "device": "auto",
        "backend": "auto",
        "tracking_mode": "sports2d",
        "predict_displacement": False,
        "match_by": "keypoints",
        "max_distance": 250,
        "min_iou": 0.2,
        "max_unseen_time": 1.0,
        "deepsort_params": "{'max_age':30, 'n_init':3, 'nms_max_overlap':0.8, 'max_cosine_distance':0.3, 'nn_budget':200, 'max_iou_distance':0.8, 'embedder_gpu': True, 'embedder':'torchreid'}",
        "keypoint_likelihood_threshold": 0.3,
        "average_likelihood_threshold": 0.5,
        "keypoint_number_threshold": 0.3,
        "CUSTOM": {
            "name": "Hip",
            "id": 19,
            "children": [],
        },
    },
    "px_to_meters_conversion": {
        "to_meters": True,
        "make_c3d": True,
        "save_calib": True,
        "perspective_value": 10.0,
        "perspective_unit": "distance_m",
        "distortions": [0.0, 0.0, 0.0, 0.0, 0.0],
        "floor_angle": "auto",
        "xy_origin": ["auto"],
        "calib_file": "",
    },
    "angles": {
        "display_angle_values_on": ["body", "list"],
        "fontSize": 0.3,
        "joint_angles": [
            "Right ankle", "Left ankle", "Right knee", "Left knee",
            "Right hip", "Left hip", "Right shoulder", "Left shoulder",
            "Right elbow", "Left elbow", "Right wrist", "Left wrist",
        ],
        "segment_angles": [
            "Right foot", "Left foot", "Right shank", "Left shank",
            "Right thigh", "Left thigh", "Pelvis", "Trunk", "Shoulders",
            "Head", "Right arm", "Left arm", "Right forearm", "Left forearm",
        ],
        "flip_left_right": True,
        "correct_segment_angles_with_floor_angle": True,
    },
    "post-processing": {
        "interpolate": True,
        "interp_gap_smaller_than": 100,
        "fill_large_gaps_with": "last_value",
        "sections_to_keep": "all",
        "min_chunk_size": 10,
        "reject_outliers": True,
        "filter": True,
        "show_graphs": True,
        "save_graphs": True,
        "filter_type": "butterworth",
        "butterworth": {"order": 4, "cut_off_frequency": 6.0},
        "kalman": {"trust_ratio": 500.0, "smooth": True},
        "one_euro": {"oneeuro_cut_off_frequency": 4.0, "oneeuro_beta": 1.5, "oneeuro_d_cut_off_frequency": 1.0},
        "gcv_spline": {"gcv_cut_off_frequency": "auto", "gcv_smoothing_factor": 1.0},
        "acc_minimizing": {"accminimizing_cut_off_frequency": 6.0},
        "gaussian": {"sigma_kernel": 1},
        "loess": {"nb_values_used": 5},
        "median": {"kernel_size": 3},
        "butterworth_on_speed": {"butterspeed_order": 4, "butterspeed_cut_off_frequency": 6.0},
    },
    "kinematics": {
        "do_augmentation": False,
        "do_ik": False,
        "filter_ik": False,
        "ik_filter_type": "acc_minimizing",
        "feet_on_floor": False,
        "use_simple_model": False,
        "participant_mass": [55.0, 67.0],
        "parallel_workers_kinematics": "auto",
        "right_left_symmetry": True,
        "default_height": 1.70,
        "large_hip_knee_angles": 135.0,
        "trimmed_extrema_percent": 50,
        "remove_individual_scaling_setup": True,
        "remove_individual_ik_setup": True,
        "osim_setup_path": "../OpenSim_setup",
    },
    "logging": {"use_custom_logging": False},
}


def merge_dicts(dst: dict[str, Any], src: dict[str, Any]) -> dict[str, Any]:
    for key, value in src.items():
        if isinstance(value, dict) and isinstance(dst.get(key), dict):
            merge_dicts(dst[key], value)
        else:
            dst[key] = deepcopy(value)
    return dst


PRESETS: dict[str, dict[str, Any]] = {
    "標準設定 (Standard)": deepcopy(DEFAULT_CONFIG),
    "高精度・詳細解析 (Performance & Filtered)": merge_dicts(
        deepcopy(DEFAULT_CONFIG),
        {
            "pose": {"mode": "performance", "det_frequency": 1},
            "post-processing": {"filter_type": "kalman"},
        },
    ),
    "高速スクリーニング (Fast Lightweight)": merge_dicts(
        deepcopy(DEFAULT_CONFIG),
        {
            "pose": {"mode": "lightweight", "det_frequency": 6},
            "base": {"save_img": False},
        },
    ),
    "OpenSim 連携 (Kinematics & IK)": merge_dicts(
        deepcopy(DEFAULT_CONFIG),
        {
            "kinematics": {"do_augmentation": True, "do_ik": True, "filter_ik": True},
            "px_to_meters_conversion": {"make_c3d": True},
        },
    ),
}


def default_config() -> dict[str, Any]:
    return deepcopy(DEFAULT_CONFIG)


def get_preset(name: str) -> dict[str, Any]:
    return deepcopy(PRESETS.get(name, DEFAULT_CONFIG))


def load_toml(path: str | Path) -> dict[str, Any]:
    with Path(path).open("rb") as f:
        data = dict(load(f))
    base = default_config()
    merge_dicts(base, data)
    return base


def dump_toml(config: dict[str, Any], path: str | Path) -> None:
    Path(path).write_text(dumps(config), encoding="utf-8")


def validate_config(config: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    base = config.get("base", {})
    vids = base.get("video_input")
    if not vids or (isinstance(vids, list) and len(vids) == 0) or (isinstance(vids, str) and not vids.strip()):
        issues.append("base.video_input が空です。動画ファイルまたは 'webcam' を指定してください。")
    if base.get("nb_persons_to_detect") not in ("all", None):
        try:
            if int(base["nb_persons_to_detect"]) < 1:
                issues.append("nb_persons_to_detect は 1 以上、または 'all' にしてください。")
        except (ValueError, TypeError):
            issues.append("nb_persons_to_detect の値が不正です。")

    pose = config.get("pose", {})
    try:
        if int(pose.get("det_frequency", 1)) < 1:
            issues.append("pose.det_frequency は 1 以上の整数にしてください。")
    except (ValueError, TypeError):
        issues.append("pose.det_frequency の値が不正です。")

    for key in ("keypoint_likelihood_threshold", "average_likelihood_threshold", "keypoint_number_threshold"):
        try:
            value = float(pose.get(key, 0))
            if not 0 <= value <= 1:
                issues.append(f"pose.{key} は 0.0 ～ 1.0 の範囲にしてください。")
        except (ValueError, TypeError):
            issues.append(f"pose.{key} の値が不正です。")

    px = config.get("px_to_meters_conversion", {})
    if px.get("perspective_unit") in {"distance_m", "f_px", "fov_deg", "fov_rad"}:
        try:
            if float(px.get("perspective_value", 0)) <= 0:
                issues.append("px_to_meters_conversion.perspective_value は 0 より大きい値にしてください。")
        except (ValueError, TypeError):
            issues.append("px_to_meters_conversion.perspective_value の値が不正です。")

    return issues


def parse_toml_text(text: str) -> dict[str, Any]:
    return dict(parse(text))


def toml_text(config: dict[str, Any]) -> str:
    return dumps(config)
