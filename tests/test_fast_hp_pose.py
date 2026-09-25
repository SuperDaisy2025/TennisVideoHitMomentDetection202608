import importlib.util
import sqlite3
import tempfile
from pathlib import Path

import numpy as np


MODULE_PATH = Path(__file__).resolve().parents[1] / "tennis_analyzer.py"
SPEC = importlib.util.spec_from_file_location("tennis_analyzer", MODULE_PATH)
TA = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TA)


def test_select_sound_top_candidates_keeps_three_strongest():
    data={"times":np.array([0.,1.,2.,3.]),"combined":np.array([.2,.9,.5,.7])}
    candidates=[{"idx":i,"time":float(i)} for i in range(4)]
    result=TA.select_sound_top_candidates(candidates,data,limit=3)
    assert [item["idx"] for item in result]==[1,3,2]
    assert [item["sound_energy"] for item in result]==[.9,.7,.5]


def test_motion_target_prefers_wrist_travel_over_sound():
    data={"times":np.array([0.,1.]),"combined":np.array([.95,.50])}
    candidates=[{"idx":0,"time":0.,"pose_travel":.2},
                {"idx":1,"time":1.,"pose_travel":.8}]
    assert TA.select_motion_validation_target(candidates,data)["idx"]==1


def test_candidate_marker_palette():
    assert TA.candidate_marker_color({"selected":None})=="#8a958e"
    assert TA.candidate_marker_color({"selected":False})=="#ff5252"
    assert TA.candidate_marker_color({"selected":True})=="#26c281"
    assert TA.candidate_marker_color({"selected":True,"full_frame_target":True})=="#1976d2"


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


def test_five_front_faces_and_bodies_override_lines_as_front_view():
    inspections=[{"body_directions":["正面（おへそ側）"],
                  "face_directions":["正面向き"]} for _ in range(5)]
    direction,confidence,_=TA.classify_camera_coarse(
        inspections,[],(100,200,3),("不明・複数",.25,"線不足"))
    assert direction=="正面" and confidence>.9


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


def test_all_edge_segments_are_drawn_as_thin_red_lines():
    frame=np.zeros((60,80,3),dtype=np.uint8)
    rendered=TA.draw_all_edge_segments(frame,[[5,10,70,10],[20,5,20,50]])
    assert rendered[10,30,2]>200 and rendered[10,30,0]<80
    assert rendered[30,20,2]>200 and rendered[30,20,0]<80


def test_segment_is_clipped_at_ankle_court_boundary():
    assert TA.clip_segment_below_y([10,10,30,50],30)==[20,30,30,50]
    assert TA.clip_segment_below_y([0,5,20,10],30) is None


def test_court_color_area_is_tinted_but_remains_visible():
    frame=np.full((60,80,3),(60,130,70),dtype=np.uint8)
    lab=TA.cv2.cvtColor(np.array([[[60,130,70]]],dtype=np.uint8),TA.cv2.COLOR_BGR2LAB)[0,0]
    sample={"lab":lab.tolist(),"sample_rect":[35,45,45,55]}
    rendered=TA.draw_court_color_area(frame,sample,(40,45),30)
    assert not np.array_equal(rendered[45,40],frame[45,40])
    assert np.all(rendered[45,40]>0)


def test_collinear_fragments_are_extended_into_one_supported_line():
    merged=TA.merge_collinear_fragments([[5,30,35,30],[50,31,90,31]],rho_tol=4,
                                        angle_tol=3,max_gap=20)
    assert len(merged)==1 and merged[0]["merged_count"]==2
    assert abs(merged[0]["line"][2]-merged[0]["line"][0])>=84


def test_person_occlusion_allows_a_wider_collinear_gap():
    lines=[[10,50,80,50],[220,51,290,51]]
    without=TA.merge_collinear_fragments(lines,rho_tol=4,angle_tol=3,max_gap=80)
    with_person=TA.merge_collinear_fragments(lines,rho_tol=4,angle_tol=3,max_gap=80,
                                             occlusion_boxes=[(90,20,210,100)],occlusion_gap=180)
    assert len(without)==2
    assert len(with_person)==1 and with_person[0]["merged_count"]==2


def test_merged_diagnostic_line_is_pink():
    frame=np.zeros((50,100,3),dtype=np.uint8)
    rendered=TA.draw_all_edge_segments(frame,[{"line":[5,25,95,25],"merged_count":2}])
    b,g,r=map(int,rendered[25,50])
    assert r>200 and b>150 and g<100


def test_strict_court_color_level_covers_less_area():
    frame=np.full((60,80,3),(65,135,75),dtype=np.uint8)
    frame[:,40:]=(80,145,90)
    lab=TA.cv2.cvtColor(np.array([[[65,135,75]]],dtype=np.uint8),TA.cv2.COLOR_BGR2LAB)[0,0]
    sample={"lab":lab.tolist(),"sample_rect":[10,45,20,55]}
    loose=TA.draw_court_color_area(frame,sample,(15,45),30,color_distance=42)
    strict=TA.draw_court_color_area(frame,sample,(15,45),30,color_distance=18)
    loose_changed=np.any(loose!=frame,axis=2).sum(); strict_changed=np.any(strict!=frame,axis=2).sum()
    assert strict_changed<=loose_changed


def test_yolo_face_direction_uses_nose_between_eyes():
    kps=np.zeros((17,3),dtype=float)
    kps[0]=[50,40,.9]; kps[1]=[45,35,.9]; kps[2]=[55,35,.9]
    assert TA.yolo_face_direction(kps)==(True,"正面向き")
    kps[0,0]=59
    assert TA.yolo_face_direction(kps)==(True,"画面右向き")


def test_rtmpose_output_is_normalized_to_coco17():
    points=np.zeros((1,17,2),dtype=float)
    scores=np.full((1,17),.8,dtype=float)
    points[0,10]=[320,180]
    result=TA.rtmpose_result_to_coco(points,scores,640,360)
    assert len(result)==17
    assert result["10"]==[.5,.5,.8]


def test_rtmpose_selects_largest_detected_person():
    points=np.zeros((2,17,2),dtype=float); scores=np.full((2,17),.9,dtype=float)
    points[0,:,0]=np.linspace(10,20,17); points[0,:,1]=np.linspace(10,30,17)
    points[1,:,0]=np.linspace(100,300,17); points[1,:,1]=np.linspace(50,330,17)
    result=TA.rtmpose_result_to_coco(points,scores,400,400)
    assert result["16"][0]==.75 and result["16"][1]==.825


def test_pose_backend_label_includes_rtmpose():
    assert TA.pose_backend_label("rtmpose")=="RTMPose"




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


def test_wall_mode_enforces_eight_tenths_peak_gap():
    energy=np.zeros(16,dtype=float); energy[[1,7,12]]=1.0
    data={"combined":energy,"times":np.arange(16,dtype=float)*.1,"sr":512}
    peaks,_,rejected=TA.detect_peaks(data,sensitivity=.4,min_gap=.1,wall_mode=True,
                                     return_rejected=True)
    assert TA.WALL_PEAK_MIN_GAP==.8
    assert peaks.tolist()==[1,12]
    assert rejected.tolist()==[7]


def test_three_meter_sound_delay_is_about_nine_milliseconds():
    assert abs(3.0/TA.SOUND_SPEED-0.00882)<0.0001


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
    # ±0.1秒の12cmと、±0.2秒を同じ時間幅へ直した10cmの平均。
    assert all(abs(values[key]-11.0)<1e-6 for key in ("rw_x","lw_x","re_x","le_x"))
    assert all(abs(values[key])<1e-6 for key in ("rw_y","lw_y","re_y","le_y"))
    assert values["rw_d"]==11.0 and values["lw_d"]==11.0


def test_motion_summary_treats_image_right_as_positive():
    def sample(x):
        kps={"0":[.5,.1,.9],"15":[.5,.9,.9],"16":[.5,.9,.9]}
        for index in (10,9,6,5,8,7):kps[str(index)]=[x,.4,.9]
        return {"kps":kps}
    values,_=TA.TennisApp._compute_hp_motion_cm(
        [sample(.5),sample(.7),sample(.6),sample(.4),sample(.5)],(100,100),160)
    assert all(abs(values[key]+30.0)<1e-6 for key in ("rw_x","lw_x","re_x","le_x"))
    assert all(abs(values[key])<1e-6 for key in ("rw_y","lw_y","re_y","le_y"))


def test_motion_summary_treats_image_down_as_positive_y():
    def sample(y):
        kps={"0":[.5,.1,.9],"15":[.5,.9,.9],"16":[.5,.9,.9]}
        for index in (10,9,8,7):kps[str(index)]=[.5,y,.9]
        return {"kps":kps}
    values,_=TA.TennisApp._compute_hp_motion_cm(
        [sample(.5),sample(.3),sample(.4),sample(.5),sample(.4)],(100,100),160)
    assert all(abs(values[key]-15.0)<1e-6 for key in ("rw_y","lw_y","re_y","le_y"))
    assert values["rw_d"]==15.0 and values["lw_d"]==15.0


def test_motion_summary_ignores_low_confidence_outer_outlier():
    def sample(x,confidence=.9):
        kps={"0":[.5,.1,.9],"15":[.5,.9,.9],"16":[.5,.9,.9]}
        for index in (10,9,8,7):kps[str(index)]=[x,.4,confidence]
        return {"kps":kps}
    values,_=TA.TennisApp._compute_hp_motion_cm(
        [sample(-.3,.3),sample(.4),sample(.5),sample(.6),sample(1.3,.3)],(100,100),160)
    # 外側ペアは大きく低信頼なので、±0.1秒の値を採用する。
    assert all(abs(values[key]-40.0)<1e-6 for key in ("rw_x","lw_x","re_x","le_x"))


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


def test_crop_badges_use_clear_time_ordered_numbers():
    app=object.__new__(TA.TennisApp)
    app._crops=[{"rank":8,"time":3.0},{"rank":4,"time":1.0},
                {"rank":0,"time":0.5}]
    assert app._crop_badges()=={4:"C1",8:"C2"}


def test_video_selection_opens_info_without_direction_estimation():
    class Value:
        def get(self): return __file__
    app=object.__new__(TA.TennisApp)
    app.video_path=Value(); app._cached_video_path=""
    opened=[]
    app._show_video_info_popup=lambda path:opened.append(path)
    app._on_video_selected()
    assert opened==[__file__]


def test_global_crop_applies_at_rejected_candidate_times():
    app=object.__new__(TA.TennisApp)
    rect=(.1,.2,.8,.9)
    app._crops=[{"rank":0,"time":3.0,"rect":rect}]
    app.peaks=[]
    assert app._crop_rect_for_time(12.5)==rect


def test_legacy_uniform_all_crop_is_treated_as_global():
    app=object.__new__(TA.TennisApp)
    rect=(.1,.2,.8,.9)
    app._crops=[{"rank":1,"time":3.0,"rect":rect},{"rank":2,"time":7.0,"rect":rect}]
    app.peaks=[{"rank":1,"time":3.0},{"rank":2,"time":7.0}]
    assert app._crop_rect_for_time(5.0)==rect


def test_display_number_is_separate_from_database_rank():
    assert TA.TennisApp._display_no({"rank":4,"_display_no":5})==5
    assert TA.TennisApp._display_no({"rank":4})==4


def test_rejected_candidate_has_dedicated_main_frame_path():
    class Value:
        def get(self):return "sample.mp4"
    app=object.__new__(TA.TennisApp)
    app.video_path=Value(); app.camera_dist=type("V",(),{"get":lambda self:3.0})()
    app._active_crop_rect=lambda time:(.1,.1,.9,.9)
    logs=[]; shown=[]
    app._log_hp_debug=logs.append
    app._display_frame=lambda frame,time,info=None:shown.append((time,info))
    old=TA.grab_frame
    try:
        TA.grab_frame=lambda path,time:np.zeros((10,10,3),dtype=np.uint8)
        app._show_rejected_main({"rank":5,"time":11.0,"pose_center_time":10.99,
                                 "reason":"wall_gap"})
    finally:TA.grab_frame=old
    assert shown==[(10.99,"除外候補 #5  11.00s")]
    assert "frame_ok=True" in logs[0] and "crop=(0.1, 0.1, 0.9, 0.9)" in logs[0]


def test_audio_band_modes_select_expected_energy_series():
    data={"combined":np.array([.1,.2]),"impact":np.array([.3,.4]),
          "wall":np.array([.5,.6]),"broadband":np.array([.7,.8])}
    assert np.array_equal(TA.audio_energy_series(data,"combined"),data["combined"])
    assert np.array_equal(TA.audio_energy_series(data,"racket"),data["impact"])
    assert np.array_equal(TA.audio_energy_series(data,"wall"),data["wall"])
    assert np.array_equal(TA.audio_energy_series(data,"broadband"),data["broadband"])


def test_audio_band_toggle_redraws_only_and_never_starts_pose():
    class Value:
        def __init__(self,value): self.value=value
        def get(self): return self.value
        def set(self,value): self.value=value
    class Button:
        def configure(self,**kwargs): self.kwargs=kwargs
    app=object.__new__(TA.TennisApp)
    app.audio_band_mode=Value("combined")
    app.audio_filter_enabled=Value(True)
    app.btn_audio_filter=Button()
    app.status_var=Value("")
    calls=[]
    app._update_shot_list=lambda:calls.append("list")
    app._draw_timeline=lambda:calls.append("timeline")
    app._refresh_hp_detail=lambda:calls.append("detail")
    app._start_fast_hp_pose_filter=lambda:(_ for _ in ()).throw(
        AssertionError("pose analysis must not run for a display-only toggle"))

    app._toggle_audio_filter()

    assert app.audio_band_mode.get()=="racket"
    assert calls==["list","timeline","detail"]
    assert "姿勢・採否は変更しません" in app.status_var.get()
    assert app.btn_audio_filter.kwargs["bg"]==TA.audio_band_color("racket")


def test_select_sound_rank_one_uses_surviving_candidates_only():
    data={"times":np.array([0.,1.,2.]),"combined":np.array([.2,.9,.7])}
    winner=TA.select_sound_rank_one([{"idx":0,"time":0.},{"idx":2,"time":2.}],data)
    assert winner["idx"]==2
    assert winner["sound_energy"]==.7


def test_full_frame_contact_score_exposes_components_and_choice():
    frames=[]
    for i,t in enumerate((.90,.95,1.00,1.05,1.10)):
        # Wrist accelerates into the center; ball changes direction there.
        ball_x=(.8,.5,.1,.45,.75)[i]
        frames.append({"time":t,"tracks":{"右手首":[i*.20,0.],
            "左手首":[0.,0.],"ボール":[ball_x,0.],"重心":[0.,-.5]}})
    scored,best=TA.score_full_frame_hit_candidates(frames,1.0)
    assert len(scored)==5 and best is not None
    assert sum(bool(row["selected"]) for row in scored)==1
    assert {"score","audio_prior","right_speed","hand_change","ball_change","proximity"}.issubset(scored[best])
    assert abs(scored[best]["time"]-1.0)<=.051


def test_relative_tracks_keep_visible_wrist_when_torso_reference_flickers():
    torso={"5":[.4,.3,.9],"6":[.6,.3,.9],"11":[.45,.6,.9],"12":[.55,.6,.9]}
    frames=[{"time":0.,"kps":{**torso,"10":[.7,.4,.9]}},
            {"time":.03,"kps":{"10":[.8,.4,.12]}},
            {"time":.06,"kps":{**torso,"10":[.9,.4,.9]}}]
    tracked=TA.build_person_relative_tracks(frames,min_conf=.05)
    assert "右手首" in tracked[1]["tracks"]
    assert tracked[1]["reference_borrowed"] is True
    assert tracked[1]["pose_points"]==1


def test_experiment_absolute_tracks_use_normalized_keypoint_values():
    app=object.__new__(TA.TennisApp)
    tracks=app._experiment_absolute_tracks({"kps":{"10":[.75,.25,.8],
        "5":[.4,.3,.9],"6":[.6,.3,.9],"11":[.45,.7,.9],"12":[.55,.7,.9]}})
    assert tracks["右手首"]==[.75,.25]
    assert np.allclose(tracks["重心"],[.5,.5])


def test_experiment_confidence_text_uses_pose_and_ball_scores():
    text=TA.experiment_confidence_text({"10":[.2,.3,.876],"9":[.1,.4,.654],
                                        "18":[.8,.2,.432]})
    assert text=="Confidence\nRW   88%\nLW   65%\nBall 43%"
    assert TA.experiment_confidence_text({})=="Confidence\nRW   --\nLW   --\nBall --"
