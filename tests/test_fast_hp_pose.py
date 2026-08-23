import importlib.util
import sqlite3
import tempfile
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


def test_camera_direction_does_not_treat_player_face_as_camera_front():
    direction,confidence,_=TA.classify_camera_direction_features(.7,.3,.5,.6)
    assert direction=="後ろ" and confidence>.7


def test_camera_direction_uses_center_vanishing_point_as_rear():
    direction,_,_=TA.classify_camera_direction_features(0,.4,.5,.6)
    assert direction=="後ろ"


def test_camera_direction_keeps_uncertain_evidence_unknown():
    direction,confidence,_=TA.classify_camera_direction_features(0,.02,None,.1)
    assert direction=="不明・複数" and confidence<.5


def test_hough_line_shapes_are_normalized_without_scalar_unpacking():
    nested=np.array([[[1,2,3,4]],[[5,6,7,8]]],dtype=np.int32)
    flat=np.array([[1,2,3,4],[5,6,7,8]],dtype=np.int32)
    assert TA.normalize_hough_lines(nested).shape==(2,4)
    assert np.array_equal(TA.normalize_hough_lines(nested),TA.normalize_hough_lines(flat))


def test_camera_samples_avoid_setup_and_stop_frames():
    times=TA.camera_sample_times(60,5)
    assert np.allclose(times,[6,18,30,42,54])
    assert TA.camera_sample_times(5,5)[0]==0


def test_missing_haar_cascade_is_resolved_without_opening_bad_path():
    assert TA.find_haar_cascade("definitely_missing_cascade.xml") is None


def test_duplicate_court_segments_are_consolidated():
    lines=[(100,100,100,400),(102,105,102,398),(300,100,500,100)]
    assert len(TA.dedupe_line_segments(lines))==2


def test_direction_explanation_states_that_face_is_not_decisive():
    text=TA.camera_direction_explanation({"direction":"不明・複数","confidence":.25,
        "convergence":0,"vp_x":None,"reason":"線不足","inspections":[]})
    assert "顔向きは撮影方向の決定には使っていません" in text


def test_court_line_confidence_rewards_long_bright_line():
    frame=np.zeros((100,200,3),dtype=np.uint8)
    frame[79:82,:]=255
    assert TA.court_line_confidence(frame,(0,80,199,80))>.7


def test_parallel_edges_merge_into_one_area_band_and_extend_fragments():
    lines=[(20,40,90,40),(22,50,95,50),(80,42,180,42)]
    bands=TA.merge_line_bands(lines,(100,200,3),rho_bin=28,angle_bin=7)
    assert len(bands)==1
    assert bands[0]["width"]>=10
    x_values=(bands[0]["line"][0],bands[0]["line"][2])
    assert min(x_values)<=22 and max(x_values)>=178


def test_yolo_body_direction_uses_anatomical_left_right_order():
    kps=np.zeros((17,3),dtype=float)
    for i,x,y in ((5,70,30),(6,30,30),(11,65,70),(12,35,70)):
        kps[i]=[x,y,.9]
    assert TA.yolo_body_direction(kps)=="正面（おへそ側）"
    kps[[5,6]]=kps[[6,5]]; kps[[11,12]]=kps[[12,11]]
    assert TA.yolo_body_direction(kps)=="背面"


def test_common_court_detection_returns_one_area_not_two_edges():
    frames=[]
    for _ in range(5):
        frame=np.zeros((120,200,3),dtype=np.uint8)
        cv2=TA.cv2
        cv2.rectangle(frame,(92,50),(108,119),(255,255,255),-1)
        frames.append(frame)
    regions=TA.detect_common_court_regions(frames)
    assert len(regions)==1
    assert regions[0]["area"]>900 and len(regions[0]["polygon"])>=4


def test_body_front_majority_makes_coarse_side_view():
    inspections=[{"body_directions":["正面（おへそ側）"]} for _ in range(4)]+[
                 {"body_directions":["背面"]}]
    direction,confidence,_=TA.classify_camera_coarse(
        inspections,[],(100,200,3),("不明・複数",.25,"線不足"))
    assert direction=="横(側不明)" and confidence>.7


def test_foot_color_sampling_ignores_white_paint():
    frame=np.full((120,200,3),(60,130,70),dtype=np.uint8)
    TA.cv2.line(frame,(100,80),(100,119),(255,255,255),5)
    sample=TA.sample_foot_court_color(frame,(100,85),100)
    assert sample is not None
    assert np.linalg.norm(np.asarray(sample["bgr"])-np.array([60,130,70]))<12


def test_line_is_kept_when_either_side_matches_foot_court_color():
    frame=np.full((120,200,3),(60,130,70),dtype=np.uint8)
    frame[:,105:]=(120,70,40)
    foot=TA.sample_foot_court_color(frame,(70,90),80)
    region={"line":[105,10,105,110],"width":4}
    matched,_,_=TA.court_region_color_match(frame,region,foot["lab"])
    assert matched


def test_line_is_rejected_only_when_both_sides_are_far_from_foot_color():
    frame=np.full((120,200,3),(20,20,170),dtype=np.uint8)
    target_bgr=np.array([70,130,60],dtype=np.uint8).reshape(1,1,3)
    target_lab=TA.cv2.cvtColor(target_bgr,TA.cv2.COLOR_BGR2LAB)[0,0]
    region={"line":[100,10,100,110],"width":4}
    matched,d1,d2=TA.court_region_color_match(frame,region,target_lab)
    assert not matched and d1>55 and d2>55


def test_yolo_face_direction_uses_nose_between_eyes():
    kps=np.zeros((17,3),dtype=float)
    kps[0]=[50,40,.9]; kps[1]=[45,35,.9]; kps[2]=[55,35,.9]
    assert TA.yolo_face_direction(kps)==(True,"正面向き")
    kps[0,0]=59
    assert TA.yolo_face_direction(kps)==(True,"画面右向き")




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


def test_first_minute_cache_is_separate_from_full_analysis():
    video=str(Path("sample.mp4"))
    assert TA.get_analysis_cache_path(video,True).endswith("sample_first60_analysis.npz")
    assert TA.get_analysis_cache_path(video,False).endswith("sample_analysis.npz")


def test_noise_metrics_report_dense_background_as_high():
    energy=np.full(120,.15,dtype=float)
    energy[::3]=.8
    metrics=TA.estimate_noise_metrics({"broadband":energy,"duration":60,"sr":1024})
    assert metrics["floor"]>=.15
    assert metrics["level"]=="高"


def test_pose_sampling_uses_five_requested_offsets():
    assert TA.HP_POSE_SAMPLE_OFFSETS == (-0.2, -0.1, 0.0, 0.1, 0.2)


def test_motion_summary_is_signed_horizontal_cm_delta_and_reports_ball():
    def sample(joint_x, ball=False):
        kps={"0":[0.5,0.1,0.9], "15":[0.45,0.9,0.9], "16":[0.55,0.9,0.9],
             "11":[0.45,0.5,0.9], "12":[0.55,0.5,0.9]}
        for index in (10,9,6,5,8,7):kps[str(index)]=[joint_x,0.5,0.9]
        if ball:kps["18"]=[0.75,0.5,0.9]
        return {"kps":kps}
    samples=[sample(0.6),sample(0.62),sample(0.65,True),sample(0.68),sample(0.7)]
    values,ball=TA.TennisApp._compute_hp_motion_cm(samples,(100,100),160)
    assert ball is True
    # Uses -0.1s (x=.62) and +0.1s (x=.68): 6px * 2cm/px = +12cm.
    assert all(abs(values[key]-12.0)<1e-6 for key in ("rw_x","lw_x","re_x","le_x"))
    assert all(abs(values[key])<1e-6 for key in ("rw_y","lw_y","re_y","le_y"))


def test_motion_summary_treats_image_right_as_positive():
    def sample(x):
        kps={"0":[.5,.1,.9],"15":[.5,.9,.9],"16":[.5,.9,.9]}
        for index in (10,9,6,5,8,7):kps[str(index)]=[x,.4,.9]
        return {"kps":kps}
    values,_=TA.TennisApp._compute_hp_motion_cm(
        [sample(.5),sample(.7),sample(.6),sample(.4),sample(.5)],(100,100),160)
    assert all(abs(values[key]+60.0)<1e-6 for key in ("rw_x","lw_x","re_x","le_x"))
    assert all(abs(values[key])<1e-6 for key in ("rw_y","lw_y","re_y","le_y"))


def test_motion_summary_treats_image_down_as_positive_y():
    def sample(y):
        kps={"0":[.5,.1,.9],"15":[.5,.9,.9],"16":[.5,.9,.9]}
        for index in (10,9,8,7):kps[str(index)]=[.5,y,.9]
        return {"kps":kps}
    values,_=TA.TennisApp._compute_hp_motion_cm(
        [sample(.5),sample(.3),sample(.4),sample(.5),sample(.4)],(100,100),160)
    assert all(abs(values[key]-40.0)<1e-6 for key in ("rw_y","lw_y","re_y","le_y"))


def test_motion_summary_uses_torso_scale_when_ankles_are_missing():
    def sample(x):
        kps={"5":[.4,.3,.9],"6":[.6,.3,.9],"11":[.45,.6,.9],"12":[.55,.6,.9]}
        for index in (10,9,8,7):kps[str(index)]=[x,.4,.9]
        return {"kps":kps}
    values,_=TA.TennisApp._compute_hp_motion_cm(
        [sample(.4),sample(.4),sample(.5),sample(.5),sample(.5)],(100,100),180)
    assert all(values[key] is not None for key in values)
    assert all(values[key]>0 for key in ("rw_x","lw_x","re_x","le_x"))


def test_verified_hit_point_database_persists_and_unchecks():
    with tempfile.TemporaryDirectory() as folder:
        db_path=str(Path(folder)/"truth.db")
        video=str(Path(folder)/"sample.mp4")
        row={"video_key":TA._ground_truth_video_key(video),"video_path":video,
             "video_file":"sample.mp4","peak_rank":2,"peak_time":1.234,
             "frame_time":1.235,"camera_dir":"正面","video_shots":"[\"バックハンド\"]",
             "content_type":"壁打ち","shot_type":"backhand","sensitivity":0.3,
             "rw_x":2.0,"rw_y":-1.0,"lw_x":1.0,
             "lw_y":0.0,"re_x":3.0,"re_y":2.0,"le_x":-2.0,"le_y":1.0,
             "ball_detected":1,"pose_backend":"yolo"}
        TA.save_ground_truth(row,True,db_path)
        assert (2,1.234,"yolo") in TA.load_ground_truth_keys(video,db_path)
        con=sqlite3.connect(db_path)
        saved=con.execute("SELECT camera_dir,content_type,shot_type,sensitivity "
                          "FROM verified_hit_points").fetchone()
        con.close()
        assert saved == ("正面","壁打ち","backhand",0.3)
        TA.save_ground_truth(row,False,db_path)
        assert TA.load_ground_truth_keys(video,db_path)==set()


def test_verified_yolo_and_mediapipe_are_stored_separately():
    with tempfile.TemporaryDirectory() as folder:
        db_path=str(Path(folder)/"truth.db"); video=str(Path(folder)/"sample.mp4")
        base={"video_key":TA._ground_truth_video_key(video),"video_path":video,
              "video_file":"sample.mp4","peak_rank":1,"peak_time":2.5,"frame_time":2.5,
              "camera_dir":"正面","content_type":"壁打ち","video_shots":"[]",
              "shot_type":"backhand","sensitivity":0.3,"ball_detected":0}
        for backend,value in (("yolo",4.0),("mediapipe",7.0)):
            row=dict(base,pose_backend=backend,rw_x=value)
            TA.save_ground_truth(row,True,db_path)
        keys=TA.load_ground_truth_keys(video,db_path)
        assert keys == {(1,2.5,"yolo"),(1,2.5,"mediapipe")}


def test_legacy_verified_peak_energy_is_backfilled_from_audio_cache():
    with tempfile.TemporaryDirectory() as folder:
        db_path=str(Path(folder)/"truth.db"); video=str(Path(folder)/"sample.mp4")
        row={"video_key":TA._ground_truth_video_key(video),"video_path":video,
             "video_file":"sample.mp4","peak_rank":1,"peak_time":1.0,"frame_time":1.0,
             "camera_dir":"正面","content_type":"壁打ち","video_shots":"[]",
             "shot_type":"forehand","sensitivity":0.3,"peak_energy":None,
             "audio_filter_enabled":1,"ball_detected":0,"pose_backend":"yolo"}
        TA.save_ground_truth(row,True,db_path)
        cache_path=TA.get_analysis_cache_path(video)
        np.savez_compressed(cache_path,times=np.array([0.,1.,2.]),
                            combined=np.array([.1,.65,.2]),broadband=np.array([.1,.4,.2]),sr=44100)
        assert TA.backfill_ground_truth_peak_energies(db_path)==1
        con=sqlite3.connect(db_path)
        energy=con.execute("SELECT peak_energy FROM verified_hit_points").fetchone()[0]
        con.close()
        assert abs(energy-.65)<1e-9


def test_verified_database_migrates_existing_schema_for_sensitivity():
    with tempfile.TemporaryDirectory() as folder:
        db_path=str(Path(folder)/"old_truth.db")
        con=sqlite3.connect(db_path)
        con.execute("""CREATE TABLE verified_hit_points (
            video_key TEXT,video_path TEXT,video_file TEXT,peak_rank INTEGER,peak_time REAL,
            frame_time REAL,camera_dir TEXT,content_type TEXT,video_shots TEXT,shot_type TEXT,
            sensitivity REAL,rw_x REAL,rw_y REAL,lw_x REAL,lw_y REAL,re_x REAL,re_y REAL,
            le_x REAL,le_y REAL,ball_detected INTEGER,pose_backend TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY(video_key,peak_rank,peak_time))""")
        con.commit(); con.close()
        TA.init_ground_truth_db(db_path)
        con=sqlite3.connect(db_path)
        columns={row[1] for row in con.execute("PRAGMA table_info(verified_hit_points)")}
        pk={row[1] for row in con.execute("PRAGMA table_info(verified_hit_points)") if row[5]>0}
        con.close()
        assert {"content_type","sensitivity","peak_energy","audio_filter_enabled"}.issubset(columns)
        assert "pose_backend" in pk
