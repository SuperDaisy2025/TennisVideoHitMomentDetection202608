import importlib.util
from pathlib import Path

import numpy as np


MODULE_PATH = Path(__file__).resolve().parents[1] / "tennis_analyzer.py"
SPEC = importlib.util.spec_from_file_location("tennis_analyzer", MODULE_PATH)
TA = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TA)


def feat(x, y, serve=False, stroke=False, angle=120.0):
    return {
        "rw": np.array([x, y], dtype=float),
        "re": np.array([0.6, 0.4], dtype=float),
        "rs": np.array([0.5, 0.35], dtype=float),
        "body_c": np.array([0.5, 0.55], dtype=float),
        "shoulder_w": 0.2,
        "torso": 0.3,
        "elbow_angle": angle,
        "serve_zone": serve,
        "stroke_zone": stroke,
    }


def classify(features):
    app = object.__new__(TA.TennisApp)
    return app._classify_hp_pose_triplet(
        [{"time": i * 0.1, "feat": value} for i, value in enumerate(features)]
    )


def test_serve_swing_is_kept():
    result = classify([
        feat(0.45, 0.28, serve=True, angle=105),
        feat(0.55, 0.12, serve=True, angle=145),
        feat(0.68, 0.25, serve=True, angle=125),
    ])
    assert result["keep"] is True
    assert result["shot"] == "serve"


def test_waist_height_stroke_is_kept():
    result = classify([
        feat(0.35, 0.58, stroke=True, angle=105),
        feat(0.52, 0.56, stroke=True, angle=130),
        feat(0.73, 0.55, stroke=True, angle=145),
    ])
    assert result["keep"] is True
    assert result["shot"] == "stroke"


def test_stationary_wall_sound_candidate_is_rejected():
    result = classify([
        feat(0.65, 0.56, stroke=True, angle=120),
        feat(0.655, 0.56, stroke=True, angle=121),
        feat(0.66, 0.56, stroke=True, angle=122),
    ])
    assert result["keep"] is False
    assert result["reason"] == "no_swing"


def test_missing_pose_is_kept_as_uncertain():
    result = classify([None, None, feat(0.5, 0.5, stroke=True)])
    assert result["keep"] is True
    assert result["reason"] == "pose_uncertain"


def test_frequency_filter_toggle_changes_peak_source():
    data = {
        "combined": np.array([0.0, 1.0, 0.0, 0.1, 0.0]),
        "broadband": np.array([0.0, 0.1, 0.0, 1.0, 0.0]),
        "times": np.arange(5, dtype=float),
        "sr": 512,
    }
    filtered, _ = TA.detect_peaks(data, sensitivity=0.2, min_gap=0.1,
                                  use_frequency_filter=True)
    broadband, _ = TA.detect_peaks(data, sensitivity=0.2, min_gap=0.1,
                                   use_frequency_filter=False)
    assert filtered.tolist() == [1]
    assert broadband.tolist() == [3]


def test_yolo_coco_keypoints_feed_common_swing_features():
    app = object.__new__(TA.TennisApp)
    kps = {
        "0": [0.50, 0.20, 0.9], "5": [0.42, 0.35, 0.9],
        "6": [0.58, 0.35, 0.9], "8": [0.62, 0.25, 0.9],
        "10": [0.60, 0.10, 0.9], "11": [0.44, 0.60, 0.9],
        "12": [0.56, 0.60, 0.9], "18": [0.64, 0.08, 0.8],
    }
    result = app._coco_pose_features(kps)
    assert result is not None
    assert result["serve_zone"] is True


def test_selected_sensitivity_is_direct_energy_threshold():
    data = {
        "combined": np.array([0.0, 0.35, 0.0, 0.65, 0.0]),
        "times": np.arange(5, dtype=float), "sr": 512,
    }
    peaks, _ = TA.detect_peaks(data, sensitivity=0.4, min_gap=0.1)
    assert peaks.tolist() == [3]


def test_pose_sampling_uses_five_requested_offsets():
    assert TA.HP_POSE_SAMPLE_OFFSETS == (-0.2, -0.1, 0.0, 0.1, 0.2)
