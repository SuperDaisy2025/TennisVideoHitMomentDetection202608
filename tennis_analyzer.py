"""
tennis_analyzer.py  v62
テニスフォーム分析アプリ
---------------------------------------------------------
v47 変更点:
  - 【修正】HPリストで2つ同時選択される問題 (bind_allをEnter/Leaveスコープに)
  - 【追加】KPマーカー形状: 左=○、右=□、中央=◇、ラケット/ボール/重心=★
  - 【変更】エディタ/連続写真/3D全タブで形状を統一適用
---------------------------------------------------------
v46 変更点:
  - 【削除】キーポイント検出タブ (Refiner統合済みのため非表示)
  - 【変更】Refiner topbar簡素化 (連動ラベル削除、⚙/学習DBをコンパクト配置)
  - 【追加】総合ビュー全体をスクロール可能に (マウスホイール対応)
  - 【修正】3D写真が表示されない問題 (時刻ベースでフレーム検索)
---------------------------------------------------------
v45 変更点:
  - 【修正】MediaPipe警告 (W0000... inference_feedback_manager 等) を抑制
     - 環境変数設定をネイティブライブラリimport前に移動 (効果の前提条件)
     - absl.logging を FATAL のみに引き上げ
     - google.protobuf / mediapipe のPythonログをERRORに
     - _suppress_stderr(): C++レベルのstderrをOSレベルで一時リダイレクト
       (FaceLandmarker/PoseLandmarker の初期化・detect呼び出しに適用)
---------------------------------------------------------
v44 変更点:
  - 【修正】プルダウン範囲を実データ範囲そのままに調整
     開始 = KPデータの実際のmin時刻 (-2.0秒等)
     終了 = KPデータの実際のmax時刻 (+1.0秒等)
  - 【変更】間隔デフォルトを 0.2秒 (実データ範囲>=1秒の場合)
     狭い範囲の場合は「最短」
---------------------------------------------------------
v43 変更点:
  - 【修正】二重 _refined_refined.json 生成の防止
  - 【修正】壊れたhit_timeの自動検出 (フレーム範囲外なら中央値で代替)
  - 【修正】3D再生でモデルが縮小する問題 (box_aspect固定)
  - 【修正】総合ビュー下の小さいグラフ(連続写真の残骸)を削除
  - 【変更】KP検出ボタンを1つに統合:
     「現在のヒットポイントを解析」(YOLO+Face Mesh補正)
---------------------------------------------------------
v42 変更点:
  - 【追加】MediaPipe Face Mesh 顔KP高精度化
     - 0.5秒間隔でFace Mesh実行 (処理コスト低)
     - 468点ランドマークから鼻/両目/両耳(5点)の座標を取得
     - 前後のFace Mesh結果から線形補間して全フレーム補正
     - 補正後の信頼度は0.95に設定 (YOLO誤検出を上書き)
     - モデル未検出時は自動ダウンロード (face_landmarker.task)
---------------------------------------------------------
v41 変更点:
  - 【追加】Refinerプルダウン (開始/終了/間隔) を実データ範囲に自動調整
     - 狭い(<0.5s)  → 0.05s刻み、実データの端まで
     - 中(<1.5s)   → 0.1s刻み、-1.0〜+1.0
     - 広い(>=1.5s) → 0.25s刻み、-2.0〜+2.0
  - 【追加】間隔プルダウンにフレーム間隔(dt)の倍数を自動列挙
     現在の値が範囲外なら「最短」に自動フォールバック
---------------------------------------------------------
v40 変更点:
  - 【追加】プロジェクトフォルダ集約管理: managed_videos/{動画名}/ に
     動画+解析データを自動コピー。元ファイルは維持。ポップアップで選択可
  - 【追加】MediaPipe vs YOLO 比較: 3Dタブ「MP比較(×)」チェックで
     2D写真にMediaPipeの対応17点を×マーカーで重ね表示
  - 【追加】MediaPipe検出時に2Dピクセル座標も保存 (landmarks_2d)
---------------------------------------------------------
v39 変更点:
  - 【追加】ヒットフレーム最適選択: 右手首の動きから真のHP時刻を推定
     サーブ/スマッシュ=最高点、ストローク=最高速度。JSONに記録
  - 【追加】3Dカメラ視点: 動画情報のカメラ方向を初期視点に反映
     (後ろ=-90°, 正面=90°, フォア側=0°, バック側=180°)
  - 【変更】KP再検出時、古い_refined.jsonを自動削除 (最新結果で置換)
---------------------------------------------------------
v38 変更点:
  - 【修正】RefinerのKPマーカーが写真とずれる問題 (根本修正)
     原因: v36のplaceholder方式 — fps不一致でフレーム膨張(61→71)、
     洗練処理がKPなしフレームに補間ゴーストKPを生成していた
     対策: placeholder方式を完全廃止、JSON既存フレームのみ使用
  - 【追加】KPデータ範囲が狭い場合 (±5フレーム等) はステータスバーで
     「キーポイント検出 (現在のHP)」での再検出を案内
  - 【防御】ロード時・保存時にplaceholderフレームを自動除去
     (v36-37で保存されたJSONも開けば自動クリーニング)
---------------------------------------------------------
v37 変更点:
  - 【修正】連続写真の間隔フィルタが効かない問題
     → 許容範囲を相対40%から絶対±0.02秒に変更
  - 【修正】_rf_intervalをStringVarに変更（「最短」選択時のエラー解消）
  - 【修正】placeholderフレームのKP描画をスキップ（ずれ防止）
  - 【修正】_draw_kps_pilに境界チェック追加
---------------------------------------------------------
v36 変更点:
  - 【修正】左上の「0秒 (解析中…)」白色表示を削除
  - 【修正】Refiner連続写真がstart/end/intervalに連動しない問題
     → フレーム抽出をJSON範囲から全時間範囲(-1.5s〜+0.5s)に拡張
  - 【修正】MediaPipeの処理範囲が短い問題 (同上、全範囲に拡張)
  - 【追加】間隔「最短」オプション (フレーム単位表示)
---------------------------------------------------------
v35 変更点:
  - 【修正】履歴から読み込み時、解析済みならポップアップをスキップ→直接ロード
  - 【追加】ポップアップの選択内容を_meta_extra.jsonに保存→次回復元
  - 【修正】2つポップアップが出る問題 (履歴→ポップアップスキップで解消)
---------------------------------------------------------
v34 変更点:
  - 【修正】グラフ2下の小さな重複グラフを削除
  - 【変更】グラフ2のデフォルト高さを90% (560→500px)
  - 【追加】間隔に「最短」オプション (フレーム単位表示)
  - 【変更】CP→HPにテキスト統一
  - 【変更】グラフ3凡例: フォント拡大+横一列配置
  - 【変更】進捗表示: メイン画像中央に大きく表示
  - 【追加】グラフ2: KPホバーで軌跡線を黄色ハイライト
---------------------------------------------------------
v33 変更点:
  - 【修正】グラフ2: 背景写真にcrop_rect適用、KP座標もオフセット調整
  - 【修正】シーン変化検出: HP切替時のfalse positiveを防止 (初回ロード時スキップ)
  - 【修正】HP切替: refined版を優先検索、HP JSON形式もフォールバック
  - 【修正】グラフ2: トグルoff→on時に背景写真が消える問題
  - 【修正】ホバー時の背景切替もクロップ対応
---------------------------------------------------------
v32 変更点:
  - 【修正】IndexError: refined_frames境界チェックを全箇所に追加
  - 【修正】グラフ2: 写真アスペクト比を保持 (aspect=equal)
  - 【修正】グラフ3: 角度データなし→動的計算にフォールバック
  - 【追加】グラフ3: 写真ホバーで黄色縦線を表示
  - 【修正】KP追加: 境界チェック強化、追加点は三角(見えない点)で表示
  - 【追加】複数ファイル選択: [+]ボタンで複数動画を一括選択
---------------------------------------------------------
v31 変更点:
  - 【変更】HPのみ検出: ±5フレーム(計11フレーム)に拡張、cp形式で保存
  - 【追加】グラフ3(角度): 顔水平角/仰角/体水平角の時系列グラフ
  - 【追加】Refiner洗練時にも角度データを自動計算
  - 【備考】ヒットフレーム最適選択(右手首最高点等)は次回実装予定
---------------------------------------------------------
v30 変更点:
  - 【追加】顔の向き検出: 水平角(yaw 0-359°)+仰角(pitch) をKP検出時に計算
  - 【追加】体の向き検出: 肩ラインから体幹水平角を算出
  - 【追加】見えないKP自動判定: 顔の向きから遮蔽KPの信頼度を自動低下
  - 【修正】壁打ち連続ピーク除去: 0.15-0.45秒内の2番目を自動除去
  - 【変更】壁打ちチェックをメイン画面から削除→ポップアップに統合
  - 【修正】スロー再生終了時のボタンリセット
  - 【追加】動画情報ポップアップ: サムネイル自動サイクル (10秒おき)
---------------------------------------------------------
v29 変更点:
  - 【追加】動画情報ポップアップ: 1秒おき10秒進みでサムネイル自動切替
  - 【修正】再生終了時にボタンが停止のまま残る問題
  - 【変更】グラフ2: 常に拡大サイズ、背景に写真を半透明表示
  - 【連携】グラフ2: 写真ホバーで背景写真切替 + KP点ハイライト
  - 【修正】KPパネルホバーでグラフが一瞬縮む問題
  - 【追加】Refiner凡例にハイライト色の説明 (黄=ホバー、オレンジ=追加)
---------------------------------------------------------
v28 変更点:
  - 【追加】Refiner総合ビュー: グラフ2 (XY軌跡) — x,y座標を2D平面に
    プロットし時系列順に白線で接続。打点フレームは金縁で強調
  - 【追加】グラフ2の表示トグル + 拡大モード (高さ2倍)
  - 【連携】写真ホバーでグラフ2の該当フレーム点を黄色リングでハイライト
---------------------------------------------------------
v27 変更点:
  - 【追加】動画情報: 日付時間表示、内容に球出し/練習を追加
  - 【追加】動画情報: キーポイント検出プルダウン (不要/HPのみ/HP前後±0.3s)
  - 【変更】コンパクト再生: 常に最初のHPから開始
  - 【修正】バージョン表記を一元化 (左パネルのv24表記を修正)
  - 【変更】Refiner編集: Frame表示の重複削除、文字を白に
  - 【変更】Refiner: ハイライト色整理 (黄=ホバー、オレンジ=追加モード)
  - 【統合】Refiner: グラフ・連続写真タブを総合ビューに統合
  - 【追加】Refiner: グラフ表示トグル + 拡大モード (高さ2倍)
---------------------------------------------------------
v26 変更点:
  - 【統合】YOLO Refiner (v2.9) をタブとして統合
  - 【連携】メインのHPリスト選択 → Refinerタブに自動連動
  - 【統合】Refiner 初回タブ選択時に遅延構築 (起動高速化)
---------------------------------------------------------
v25 変更点:
  - 【修正】クロップ後にHPが移動するバグ修正 (_sync_list_selection)
  - 【修正】手ぶれ閾値を厳格化 (2.0→1.0)
  - 【変更】評価デフォルトを毎回「普通」に (既存ラベルありでも)
  - 【変更】ファイル選択時にどのタブからでもメイン画面に遷移
  - 【変更】分類済チェックボックスでタイムライン即時再描画
  - 【変更】KPタブ: CPプルダウン廃止 → HPリスト連動 + HP1枚大表示
  - 【変更】同タイミング比較: スライダー → 間隔/範囲/オフセット プルダウン
  - 【修正】連続写真クロップ: 現在HPのrankクロップを全フレームに適用
  - 【変更】YOLO人物選択: 信頼度最大→面積最大 (他人誤検出防止)
---------------------------------------------------------
v24 変更点 (UX 改善 + 学習DB 統合 + クロップ仕様変更):
  - 動画解析中、抽出された各CPサムネを紙芝居のようにメイン画面で
    高速表示してビジュアルフィードバック
  - CPリストで1コマ進む時、選択行 (オレンジ) が常に見えるよう自動スクロール
  - コンパクト再生中にCPをクリックしたら、そのCPの位置からコンパクト再生継続
  - 履歴カード: タイトルが長すぎてアクションボタン (読込/展開/削除) が
    画面外に押し出されるレイアウトバグを修正 (action を先に pack)
  - ショット比較 A/B 動画選択を「履歴からサムネで選ぶ」UIに変更
  - 【クロップ仕様変更】
    クロップ追加バーに「範囲」プルダウン (個別 / 未実施全て) を追加
      ・個別 = 現在のCPのみ更新
      ・未実施全て (デフォルト) = 現在のCP + クロップ未設定のすべてのCPに適用
    「このCPのクロップ削除」ボタン廃止 (上書きで再設定可能なため)
    クロップ参照ロジックを時刻ベース → CP rank ベースに統一
      ・各タブで「そのCPのクロップ」を直接参照 (forward-only / Option B は廃止)
      ・コンパクト再生はフレーム時刻に最も近いCPのクロップでCP境界スナップ
  - 【新】ラケット先端アルゴリズム改良:
      従来: 信頼度のみで候補1を選び、4辺の中点で先端推定
      新規: 信頼度(0.35) + 手首近接度(0.30) + アスペクト(0.10)
            + 時間連続性(0.10) + 学習DB分布(0.15) で再ランク
            先端は腕(肘→手首)方向への射影で最遠2角の中点
  - 【新】学習DB統合 (learning_db.py):
      Refinerの手動編集を蓄積、kp_id × shot_type × camera_dir 別の
      手首基準/鼻基準の相対位置分布を集約
      検出時、ラケット先端候補のスコアにこの分布からの逸脱度を反映
v23: タイトル/単位/履歴強化
v22: state漏れ修正 / クロップアンカー / コンパクト再生1.5s
v21: タイトル機能
v20: 履歴タブ展開UI
v19: 壁打ちチェック左パネル / コンパクト再生独立行
v18: クロップバグ修正 / 壁打ち / ショット比較統合 / 4倍ズーム
v17: YOLO 解析時の顔キーポイント幾何補正
v16: ラケット候補3つ/refined.json優先読込
v15: 解析結果キャッシュ/履歴タブ/レジストリJSON
v14: YOLO解析タブ凡例廃止/CP相対時間軸
v13: 連続写真にKPオーバーレイ/ボール追加
v12: コンパクト再生・出力
v11: CP追加/再採番/YOLO分析タブ
v10: メイン画面プレビュー統合/複数クロップ
---------------------------------------------------------
使い方:  python tennis_analyzer.py

必要ライブラリ:
    pip install librosa numpy scipy pandas matplotlib opencv-python ffmpeg-python openpyxl Pillow
"""

import os
# v45: MediaPipe/TF警告抑制 — ネイティブライブラリのimport前に設定必須
os.environ.setdefault("GLOG_minloglevel", "3")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
os.environ.setdefault("MEDIAPIPE_DISABLE_GPU", "1")
import json, sqlite3, threading, time, math, copy, sys, warnings
warnings.filterwarnings("ignore")
import contextlib
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk, ImageDraw

import cv2, ffmpeg, librosa
import numpy as np
import pandas as pd
import scipy.signal as sp
# v45: absl (MediaPipe内部) ログをFATALのみに
try:
    import absl.logging
    absl.logging.set_verbosity(absl.logging.FATAL)
    absl.logging.set_stderrthreshold(absl.logging.FATAL)
except ImportError:
    pass
# v45: protobuf ログ抑制
try:
    import logging as _logging
    _logging.getLogger("google.protobuf").setLevel(_logging.ERROR)
    _logging.getLogger("mediapipe").setLevel(_logging.ERROR)
except Exception:
    pass

@contextlib.contextmanager
def _suppress_stderr():
    """v45: MediaPipe C++ 警告 (W0000...) を一時的に抑制。
    C++レベルのstderr出力をOSレベルでリダイレクトする。"""
    try:
        fd = sys.stderr.fileno()
        saved = os.dup(fd)
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, fd)
        os.close(devnull)
        try:
            yield
        finally:
            os.dup2(saved, fd)
            os.close(saved)
    except Exception:
        # fileno が使えない環境ではそのまま
        yield

try:
    import yolo_refiner as RFN
except ImportError:
    # 引継ぎZIPにはRefinerバックエンドが含まれていないため、HP専用UIでは
    # 読み込みを必須にしない。Refinerを再び有効化する際は実モジュールを配置する。
    class _RefinerUnavailable:
        KP_NAMES = ["鼻","左目","右目","左耳","右耳","左肩","右肩",
                    "左肘","右肘","左手首","右手首","左腰","右腰",
                    "左膝","右膝","左足首","右足首"]
        DEFAULT_KP_CONF_TH=0.3; DEFAULT_OBJ_CONF_TH=0.25
        VELOCITY_MAD_K=6.0; ACCEL_MAD_K=6.0; LINK_DEVIATION_FRAC=0.35
        SAVGOL_WINDOW=7; SAVGOL_ORDER=2; REFINED_CONF=0.8
    RFN = _RefinerUnavailable()
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ── 日本語フォント ─────────────────────────────
def _setup_jp_font():
    candidates = ["Meiryo","Meiryo UI","MS Gothic","Yu Gothic UI","Yu Gothic",
                  "Hiragino Sans","IPAGothic","Noto Sans CJK JP","TakaoPGothic"]
    available = {f.name for f in fm.fontManager.ttflist}
    chosen = "sans-serif"
    for name in candidates:
        if name in available:
            chosen = name; break
    matplotlib.rcParams["font.family"] = chosen
    return chosen

_JP_FONT = _setup_jp_font()
matplotlib.rcParams["axes.unicode_minus"] = False

# Tkinter用フォント (Meiryo系 → Yu Gothic → MS Gothic → 標準)
def _tk_font(size, bold=False):
    """日本語対応フォントを返す"""
    tk_candidates = ["Meiryo UI","Meiryo","Yu Gothic UI","MS Gothic","sans-serif"]
    weight = "bold" if bold else "normal"
    # 実際の利用可能チェックはOSに任せる (Tkinterが自動フォールバック)
    return (tk_candidates[0], size, weight)

# ── カラー ────────────────────────────────────
BG=     "#0f1117"; PANEL=  "#1a1d27"; PANEL2= "#141720"
ACCENT= "#e8593c"; ACCENT2="#3b8bd4"; GOLD=   "#ef9f27"
GREEN=  "#1d9e75"; TEXT=   "#d4d0c8"; SUBTEXT="#888780"
BORDER= "#2c2e3a"; DARK2=  "#12141e"; RED= "#ff5252"
APP_VERSION = "v63"; APP_VERSION_DESC = "高速MediaPipe HP検出"

# v63: 音声HP候補を姿勢で検証する高速パラメータ。
# 最初は候補時刻と前後0.1秒の3枚だけを解析し、打点探索は1フレームずつ行う。
HP_POSE_COARSE_SEC = 0.10
HP_POSE_MAX_REFINE_SEC = 0.18
HP_POSE_MIN_VIS = 0.35
HP_POSE_MIN_WRIST_TRAVEL = 0.12  # 肩幅で正規化した3点間の右手首移動量
HP_POSE_MIN_ARM_CHANGE_DEG = 10.0

# ── ラベル定義 ────────────────────────────────
SHOT_TYPES = [
    ("サーブ",  "serve"),
    ("フォアS", "forehand"),
    ("バックS", "backhand"),
    ("フォアV", "fore_volley"),
    ("バックV", "back_volley"),
    ("スマッシュ","smash"),
    ("その他",  "other"),
    ("ノイズ",  "noise"),
]
SPINS = [
    ("フラット","flat"),
    ("スピン",  "topspin"),
    ("スライス","slice"),
    ("キック",  "kick"),
    ("不明",    "unknown"),
]
RATINGS = [
    ("スーパー","super"),
    ("ナイス",  "nice"),
    ("普通",    "normal"),
    ("失敗",    "miss"),
    ("未評価",  "unrated"),
]
CAMERA_DIRS = [
    ("フロント(顔側)",   "front"),
    ("バック(背中側)",   "back"),
    ("デュース側(右横)", "deuce"),
    ("アド側(左横)",     "ad"),
]
COURT_TYPES  = [("オンコート","oncourt"),("壁打ち","wall")]
PLAYER_LEVELS= [("プロ","pro"),("上級","advanced"),("中級","intermediate"),
                ("初中級","beginner_plus"),("初級","beginner")]
SOUND_SPEED  = 340.0


# ══════════════════════════════════════════════
#  音声解析
# ══════════════════════════════════════════════
def extract_audio(video_path, audio_path):
    if not os.path.exists(audio_path):
        ffmpeg.input(video_path).output(
            audio_path, format="mp3", loglevel="quiet").run(overwrite_output=True)

def analyze_audio(audio_path):
    y, sr    = librosa.load(audio_path, sr=None, mono=True)
    duration = librosa.get_duration(y=y, sr=sr)
    y_perc   = librosa.effects.percussive(y, margin=3.0)
    sos_hi   = sp.butter(4, 2000/(sr/2), btype="high",  output="sos")
    sos_mid  = sp.butter(4, [200/(sr/2),1500/(sr/2)], btype="band", output="sos")
    impact   = librosa.onset.onset_strength(
        y=sp.sosfilt(sos_hi, y_perc), sr=sr, hop_length=512, aggregate=np.median)
    wall     = librosa.onset.onset_strength(
        y=sp.sosfilt(sos_mid, y), sr=sr, hop_length=512, aggregate=np.median)
    n = min(len(impact), len(wall))
    times = np.arange(n) * (512/sr)
    def norm(x): m=np.max(x); return x/m if m>0 else x
    impact_n=norm(impact[:n]); wall_n=norm(wall[:n])
    return {"y":y,"sr":sr,"duration":duration,"times":times,
            "impact":impact_n,"wall":wall_n,"combined":0.65*impact_n+0.35*wall_n}

def detect_peaks(data, sensitivity=0.5, min_gap=1.0, wall_mode=False):
    """ピーク検出。
       wall_mode=True なら壁打ちモード: min_gap を 0.5s 以上に強制し、
       0.05〜0.30秒間隔のペアピーク (壁エコー想定) を抑制"""
    if wall_mode:
        min_gap=max(min_gap,0.5)
    combined=data["combined"]; times=data["times"]; sr=data["sr"]
    raw,_=sp.find_peaks(combined, height=np.max(combined)*(1-sensitivity),
                        distance=max(1,int(min_gap*sr/512)) if not wall_mode else 1)
    filtered,last_t=[],- np.inf
    if wall_mode:
        # 壁打ち: 候補をまず時系列で並べる
        raw_sorted=sorted(raw, key=lambda i: times[i])
        suppressed=set()
        for j,idx in enumerate(raw_sorted):
            if idx in suppressed: continue
            tj=times[idx]
            # 0.05〜0.30秒後ろのピークは壁エコー扱いで抑制
            for idx2 in raw_sorted[j+1:]:
                if idx2 in suppressed: continue
                dt=times[idx2]-tj
                if dt>0.30: break
                if dt>=0.05:
                    suppressed.add(idx2)
        for idx in raw_sorted:
            if idx in suppressed: continue
            t=times[idx]
            if t-last_t>=min_gap: filtered.append(idx); last_t=t
        return np.array(filtered, dtype=int), len(suppressed)
    for idx in raw:
        t=times[idx]
        if t-last_t>=min_gap: filtered.append(idx); last_t=t
    return np.array(filtered, dtype=int), 0

def grab_frame(video_path, time_sec):
    cap=cv2.VideoCapture(video_path)
    if not cap.isOpened(): return None
    fps=cap.get(cv2.CAP_PROP_FPS) or 30
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(fps*time_sec))
    ret,frame=cap.read(); cap.release()
    return frame if ret else None

def extract_thumbnails(video_path, peak_times, output_dir, progress_cb=None):
    os.makedirs(output_dir, exist_ok=True)
    cap=cv2.VideoCapture(video_path)
    if not cap.isOpened(): return []
    fps=cap.get(cv2.CAP_PROP_FPS)
    base=os.path.splitext(os.path.basename(video_path))[0]
    saved=[]; total=max(1,len(peak_times))
    for rank,pt in enumerate(peak_times,1):
        last_path=None
        for offset,label in [(0.0,"hit"),(-0.3,"pre")]:
            t=max(0,pt+offset)
            cap.set(cv2.CAP_PROP_POS_FRAMES,int(fps*t))
            ret,frame=cap.read()
            if ret:
                name=f"{base}_rank{rank}_{label}_{round(t,2)}s.jpg"
                path=os.path.join(output_dir,name)
                cv2.imwrite(path,frame)
                saved.append({"rank":rank,"peak_time":pt,"label":label,"path":path})
                if label=="hit": last_path=path
        if progress_cb:
            # v24: 紙芝居プレビュー用にサムネのパスも渡す
            try: progress_cb(rank,total,last_path)
            except TypeError:
                # 旧形式のコールバック互換
                try: progress_cb(rank,total)
                except Exception: pass
            except Exception: pass
    cap.release(); return saved


# ══════════════════════════════════════════════
#  DB
# ══════════════════════════════════════════════
def get_db_path(video_path):
    return os.path.join(os.path.dirname(video_path),"tennis_labels.db")

def init_db(db_path):
    con=sqlite3.connect(db_path)
    con.execute("""CREATE TABLE IF NOT EXISTS video_meta (
        video_file TEXT PRIMARY KEY, camera_dirs TEXT, court_type TEXT,
        player_level TEXT, note TEXT, crop_rect TEXT,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")
    # 既存DBにcrop_rectカラムがない場合は追加
    try:
        con.execute("ALTER TABLE video_meta ADD COLUMN crop_rect TEXT")
    except Exception:
        pass
    con.execute("""CREATE TABLE IF NOT EXISTS labels (
        id INTEGER PRIMARY KEY AUTOINCREMENT, video_file TEXT, peak_time REAL,
        peak_rank INTEGER, frame_time REAL, thumb_path TEXT,
        shot_type TEXT, spin TEXT, rating TEXT, camera_dirs TEXT, note TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")
    # v10: 複数クロップ (時刻に紐づく) — peak_rank=0 は移行用のグローバルクロップ
    con.execute("""CREATE TABLE IF NOT EXISTS crops (
        video_file TEXT, peak_rank INTEGER, anchor_time REAL, rect TEXT,
        PRIMARY KEY(video_file, peak_rank))""")
    # v10: 削除済みチェックポイント (完全削除・再解析でも復活させない)
    con.execute("""CREATE TABLE IF NOT EXISTS deleted_peaks (
        video_file TEXT, peak_time REAL,
        PRIMARY KEY(video_file, peak_time))""")
    # v11: 手動追加CP + ランク上書き
    #   source='manual' → 手動追加。source='auto' → 再採番で上書きされた自動CP
    con.execute("""CREATE TABLE IF NOT EXISTS peak_meta (
        video_file TEXT, peak_time REAL, rank INTEGER, source TEXT,
        PRIMARY KEY(video_file, peak_time))""")
    con.commit(); con.close()

def save_video_meta(db_path, video_file, camera_dirs, court_type, player_level, note, crop_rect=None):
    con=sqlite3.connect(db_path)
    crop_json=json.dumps(list(crop_rect)) if crop_rect else None
    con.execute("""INSERT OR REPLACE INTO video_meta
        (video_file,camera_dirs,court_type,player_level,note,crop_rect) VALUES(?,?,?,?,?,?)""",
        (video_file,json.dumps(camera_dirs,ensure_ascii=False),court_type,player_level,note,crop_json))
    con.commit(); con.close()

def load_video_meta(db_path, video_file):
    if not os.path.exists(db_path): return {}
    con=sqlite3.connect(db_path)
    row=con.execute("SELECT camera_dirs,court_type,player_level,note,crop_rect FROM video_meta WHERE video_file=?",
                    (video_file,)).fetchone()
    con.close()
    if row:
        return {"camera_dirs":json.loads(row[0]) if row[0] else [],
                "court_type":row[1],"player_level":row[2],"note":row[3],
                "crop_rect":json.loads(row[4]) if row[4] else None}
    return {}

def upsert_label(db_path, video_file, peak_time, peak_rank, frame_time,
                 thumb_path, shot_type, spin, rating, camera_dirs, note=""):
    con=sqlite3.connect(db_path)
    row=con.execute("SELECT id FROM labels WHERE video_file=? AND peak_rank=?",
                    (video_file,peak_rank)).fetchone()
    cam=json.dumps(camera_dirs, ensure_ascii=False)
    if row:
        con.execute("""UPDATE labels SET peak_time=?,frame_time=?,thumb_path=?,
                       shot_type=?,spin=?,rating=?,camera_dirs=?,note=? WHERE id=?""",
                    (peak_time,frame_time,thumb_path,shot_type,spin,rating,cam,note,row[0]))
    else:
        con.execute("""INSERT INTO labels
            (video_file,peak_time,peak_rank,frame_time,thumb_path,shot_type,spin,rating,camera_dirs,note)
            VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (video_file,peak_time,peak_rank,frame_time,thumb_path,
             shot_type,spin,rating,cam,note))
    con.commit(); con.close()

def load_label(db_path, video_file, peak_rank):
    if not os.path.exists(db_path): return None
    con=sqlite3.connect(db_path)
    row=con.execute("""SELECT shot_type,spin,rating,camera_dirs,note,frame_time
                       FROM labels WHERE video_file=? AND peak_rank=?""",
                    (video_file,peak_rank)).fetchone()
    con.close()
    if row:
        return {"shot_type":row[0],"spin":row[1],"rating":row[2],
                "camera_dirs":json.loads(row[3]) if row[3] else [],
                "note":row[4],"frame_time":row[5]}
    return None

def load_all_labels(db_path, video_file):
    if not os.path.exists(db_path): return {}
    con=sqlite3.connect(db_path)
    rows=con.execute(
        "SELECT peak_rank,shot_type,spin,rating,frame_time FROM labels WHERE video_file=?",
        (video_file,)).fetchall()
    con.close()
    # {rank: (shot_type, spin, rating, frame_time)}
    return {r[0]:(r[1],r[2],r[3],r[4]) for r in rows}

def delete_label(db_path, video_file, peak_rank):
    if not os.path.exists(db_path): return
    con=sqlite3.connect(db_path)
    con.execute("DELETE FROM labels WHERE video_file=? AND peak_rank=?",
                (video_file,peak_rank))
    con.commit(); con.close()


# ── v10: 複数クロップ ───────────────────────────
def add_crop(db_path, video_file, peak_rank, anchor_time, rect):
    con=sqlite3.connect(db_path)
    con.execute("""INSERT OR REPLACE INTO crops (video_file,peak_rank,anchor_time,rect)
                   VALUES(?,?,?,?)""",
                (video_file,peak_rank,float(anchor_time),json.dumps(list(rect))))
    con.commit(); con.close()

def delete_crop(db_path, video_file, peak_rank):
    if not os.path.exists(db_path): return
    con=sqlite3.connect(db_path)
    con.execute("DELETE FROM crops WHERE video_file=? AND peak_rank=?",
                (video_file,peak_rank))
    con.commit(); con.close()

def clear_crops(db_path, video_file):
    if not os.path.exists(db_path): return
    con=sqlite3.connect(db_path)
    con.execute("DELETE FROM crops WHERE video_file=?", (video_file,))
    con.commit(); con.close()

def load_crops(db_path, video_file):
    """[{'rank':int,'time':float,'rect':(x1,y1,x2,y2)}, ...] を anchor_time 昇順で返す"""
    if not os.path.exists(db_path): return []
    con=sqlite3.connect(db_path)
    rows=con.execute(
        "SELECT peak_rank,anchor_time,rect FROM crops WHERE video_file=? ORDER BY anchor_time",
        (video_file,)).fetchall()
    con.close()
    out=[]
    for rank,t,rect in rows:
        try: r=tuple(json.loads(rect))
        except Exception: continue
        if len(r)==4: out.append({"rank":rank,"time":float(t),"rect":r})
    return out


# ── v10: 削除済みチェックポイント ───────────────
def add_deleted_peak(db_path, video_file, peak_time):
    con=sqlite3.connect(db_path)
    con.execute("INSERT OR REPLACE INTO deleted_peaks (video_file,peak_time) VALUES(?,?)",
                (video_file,float(peak_time)))
    con.commit(); con.close()

def load_deleted_peaks(db_path, video_file):
    if not os.path.exists(db_path): return []
    con=sqlite3.connect(db_path)
    rows=con.execute("SELECT peak_time FROM deleted_peaks WHERE video_file=?",
                     (video_file,)).fetchall()
    con.close()
    return [float(r[0]) for r in rows]


# ── v15: 解析結果キャッシュ ────────────────
def get_analysis_cache_path(video_path):
    audio_dir=os.path.join(os.path.dirname(video_path),"audio")
    os.makedirs(audio_dir,exist_ok=True)
    stem=os.path.splitext(os.path.basename(video_path))[0]
    return os.path.join(audio_dir,f"{stem}_analysis.npz")

def save_analysis_cache(cache_path,data):
    try:
        np.savez_compressed(cache_path,**data)
        return True
    except Exception as e:
        print("cache save failed:",e); return False

def load_analysis_cache(cache_path):
    """キャッシュが存在すれば dict を返す。なければ None。"""
    if not os.path.exists(cache_path): return None
    try:
        npz=np.load(cache_path,allow_pickle=False)
        out={}
        for k in npz.files:
            v=npz[k]
            out[k]=v.item() if v.shape==() else v
        return out
    except Exception as e:
        print("cache load failed:",e); return None


# ── v15: 解析済動画レジストリ (グローバルJSON) ──
def get_registry_path():
    try:
        d=os.path.dirname(os.path.abspath(__file__))
    except Exception:
        d=os.getcwd()
    return os.path.join(d,"analyzed_videos.json")

def load_registry():
    p=get_registry_path()
    if not os.path.exists(p): return {"videos":[]}
    try:
        with open(p,"r",encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"videos":[]}

def save_registry(reg):
    p=get_registry_path()
    try:
        with open(p,"w",encoding="utf-8") as f:
            json.dump(reg,f,ensure_ascii=False,indent=1)
    except Exception as e:
        print("registry save failed:",e)

def update_registry_entry(video_path,**fields):
    reg=load_registry()
    ap=os.path.abspath(video_path)
    entry=None
    for v in reg["videos"]:
        if v.get("path")==ap:
            entry=v; break
    now=time.strftime("%Y-%m-%d %H:%M:%S")
    if entry is None:
        entry={"path":ap,"filename":os.path.basename(video_path),
               "first_analyzed":now}
        reg["videos"].append(entry)
    entry["last_updated"]=now
    entry.update(fields)
    save_registry(reg)

# v20: 履歴タブ展開用ヘルパー
def find_cp_thumb_path(video_path, rank):
    """指定 rank のサムネファイルを探す (拡張子合致しているもの。hit を優先)"""
    base=os.path.splitext(os.path.basename(video_path))[0]
    thumb_dir=os.path.join(os.path.dirname(video_path),"1_thumbnails",base)
    if not os.path.isdir(thumb_dir): return None
    try: entries=os.listdir(thumb_dir)
    except Exception: return None
    for label in ("hit","pre"):
        pat=f"{base}_rank{rank}_{label}_"
        for fn in entries:
            if fn.startswith(pat) and fn.lower().endswith((".jpg",".jpeg",".png")):
                return os.path.join(thumb_dir,fn)
    return None

def find_any_thumb(video_path):
    """サムネディレクトリ内の任意のサムネを返す (フォールバック用)"""
    base=os.path.splitext(os.path.basename(video_path))[0]
    thumb_dir=os.path.join(os.path.dirname(video_path),"1_thumbnails",base)
    if not os.path.isdir(thumb_dir): return None
    try: entries=sorted(os.listdir(thumb_dir))
    except Exception: return None
    # hit を優先
    for fn in entries:
        if "_hit_" in fn and fn.lower().endswith((".jpg",".jpeg",".png")):
            return os.path.join(thumb_dir,fn)
    for fn in entries:
        if fn.lower().endswith((".jpg",".jpeg",".png")):
            return os.path.join(thumb_dir,fn)
    return None

def count_yolo_outputs(video_path):
    """yolo/ ディレクトリの解析済CP数を集計 → (n_yolo, n_refined)"""
    yolo_dir=os.path.join(os.path.dirname(video_path),"yolo")
    if not os.path.isdir(yolo_dir): return (0,0)
    stem=os.path.splitext(os.path.basename(video_path))[0]
    try: entries=os.listdir(yolo_dir)
    except Exception: return (0,0)
    n_yolo=0; n_refined=0
    for fn in entries:
        if not fn.startswith(f"{stem}_cp") or not fn.endswith(".json"): continue
        if fn.endswith("_refined.json"):
            n_refined+=1
        else:
            n_yolo+=1
    return (n_yolo, n_refined)

def check_cp_yolo_status(video_path, rank):
    """指定 rank の YOLO 状態 → (has_yolo, has_refined)"""
    yolo_dir=os.path.join(os.path.dirname(video_path),"yolo")
    if not os.path.isdir(yolo_dir): return (False,False)
    stem=os.path.splitext(os.path.basename(video_path))[0]
    has_yolo=os.path.exists(os.path.join(yolo_dir,f"{stem}_cp{rank:02d}.json"))
    has_refined=os.path.exists(os.path.join(yolo_dir,f"{stem}_cp{rank:02d}_refined.json"))
    return (has_yolo, has_refined)

# v21: エイリアス
def get_video_alias(video_path):
    """レジストリから動画のエイリアスを取得 (未設定なら空文字)"""
    if not video_path: return ""
    try: reg=load_registry()
    except Exception: return ""
    ap=os.path.abspath(video_path)
    for v in reg.get("videos",[]):
        if v.get("path")==ap:
            return v.get("alias","") or ""
    return ""

def set_video_alias(video_path, alias):
    """エイリアスをレジストリに保存 (動画ファイルは触らない)"""
    if not video_path: return
    update_registry_entry(video_path, alias=(alias or ""))

def display_label_for(video_path, fallback=None):
    """表示用ラベル: alias があれば alias、なければファイル名 (or fallback)"""
    if not video_path:
        return fallback or ""
    a=get_video_alias(video_path)
    if a: return a
    return fallback or os.path.basename(video_path)

# v23: プレイヤー身長 (cm 換算用)
DEFAULT_PLAYER_HEIGHT_CM = 177

def get_player_height(video_path):
    """レジストリから動画のプレイヤー身長 (cm) を取得 (未設定なら 177)"""
    if not video_path: return DEFAULT_PLAYER_HEIGHT_CM
    try: reg=load_registry()
    except Exception: return DEFAULT_PLAYER_HEIGHT_CM
    ap=os.path.abspath(video_path)
    for v in reg.get("videos",[]):
        if v.get("path")==ap:
            return int(v.get("player_height_cm",DEFAULT_PLAYER_HEIGHT_CM))
    return DEFAULT_PLAYER_HEIGHT_CM

def set_player_height(video_path, height_cm):
    """身長をレジストリに保存"""
    if not video_path: return
    update_registry_entry(video_path, player_height_cm=int(height_cm))

def get_shot_breakdown(db_path,video_file):
    if not os.path.exists(db_path): return {}
    con=sqlite3.connect(db_path)
    rows=con.execute(
        "SELECT shot_type,COUNT(*) FROM labels WHERE video_file=? GROUP BY shot_type",
        (video_file,)).fetchall()
    con.close()
    return {st:cnt for st,cnt in rows if st not in ("noise","")}


# ── v11: 手動CP + ランク上書き ───────────────
def upsert_peak_meta(db_path, video_file, peak_time, rank, source):
    con=sqlite3.connect(db_path)
    con.execute("""INSERT OR REPLACE INTO peak_meta
                   (video_file,peak_time,rank,source) VALUES(?,?,?,?)""",
                (video_file,float(peak_time),int(rank),source))
    con.commit(); con.close()

def load_peak_meta(db_path, video_file):
    """[{'time':float,'rank':int,'source':str}, ...]"""
    if not os.path.exists(db_path): return []
    con=sqlite3.connect(db_path)
    rows=con.execute(
        "SELECT peak_time,rank,source FROM peak_meta WHERE video_file=?",
        (video_file,)).fetchall()
    con.close()
    return [{"time":float(t),"rank":int(r),"source":s} for t,r,s in rows]

def clear_peak_meta(db_path, video_file):
    if not os.path.exists(db_path): return
    con=sqlite3.connect(db_path)
    con.execute("DELETE FROM peak_meta WHERE video_file=?", (video_file,))
    con.commit(); con.close()


# ══════════════════════════════════════════════
#  グラフ描画
# ══════════════════════════════════════════════
def build_mini_graph(data, peak_indices, selected_idx=None, camera_dist=3.0,
                     current_frame_time=None):
    sound_delay=camera_dist/SOUND_SPEED
    times=data["times"]; combined=data["combined"]
    impact=data["impact"]; wall=data["wall"]
    peak_t=times[peak_indices] if len(peak_indices) else np.array([])

    fig,axes=plt.subplots(2,1,figsize=(10,2.6),facecolor=BG,
                          gridspec_kw={"height_ratios":[1.4,1],"hspace":0.04})
    for ax,y_vals,color,ylabel in [
        (axes[0],combined,ACCENT,"合成"),
        (axes[1],impact,  ACCENT,"高周波"),
    ]:
        ax.set_facecolor(PANEL)
        ax.fill_between(times,y_vals,alpha=0.15,color=color)
        ax.plot(times,y_vals,color=color,lw=0.8,alpha=0.85)
        if ax is axes[1]:
            ax.fill_between(times,wall,alpha=0.1,color=ACCENT2)
            ax.plot(times,wall,color=ACCENT2,lw=0.7,alpha=0.6)

        for i,pt in enumerate(peak_t):
            c  = GOLD if (selected_idx is not None and i==selected_idx) else ACCENT
            lw = 2.0  if (selected_idx is not None and i==selected_idx) else 0.7
            ax.axvline(pt,color=c,lw=lw,alpha=0.85)
            if ax is axes[0]:
                ax.text(pt,np.max(combined)*1.02,f"{i+1}",color=c,
                        fontsize=6,ha="center",va="bottom")

        # 音速補正後の打球推定線 (緑破線)
        if selected_idx is not None and selected_idx<len(peak_t):
            corrected=max(0,peak_t[selected_idx]-sound_delay)
            ax.axvline(corrected,color=GREEN,lw=1.2,alpha=0.9,linestyle="--")

        # 現在フレーム位置 (黄色実線) ← コマ送り時に動く
        if current_frame_time is not None:
            ax.axvline(current_frame_time,color=GOLD,lw=2.0,alpha=1.0,linestyle="-")

        ax.set_xlim(0,data["duration"]); ax.set_ylim(0,np.max(combined)*1.15)
        ax.tick_params(colors=SUBTEXT,labelsize=7)
        ax.set_ylabel(ylabel,color=SUBTEXT,fontsize=7)
        for sp_ in ax.spines.values(): sp_.set_edgecolor(BORDER)

    axes[0].set_xticklabels([])
    axes[1].set_xlabel("Time (s)",color=SUBTEXT,fontsize=7)

    if selected_idx is not None and selected_idx<len(peak_t):
        pt=peak_t[selected_idx]
        corrected=max(0,pt-sound_delay)
        ft_str = f"{current_frame_time:.2f}s" if current_frame_time is not None else "---"
        axes[0].set_title(
            f"Peak #{selected_idx+1}  ピーク:{pt:.2f}s  打球推定:{corrected:.2f}s"
            f"  現在:{ft_str}  (距離{camera_dist:.1f}m)",
            color=TEXT,fontsize=8,loc="left",pad=3)

    fig.subplots_adjust(left=0.05,right=0.98,top=0.88,bottom=0.15)
    return fig


def get_video_info(video_path):
    """動画ファイルのメタ情報を取得"""
    info = {}
    try:
        cap = cv2.VideoCapture(video_path)
        info["fps"]    = cap.get(cv2.CAP_PROP_FPS)
        info["width"]  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        info["height"] = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames   = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        info["frames"] = total_frames
        info["duration_sec"] = total_frames / info["fps"] if info["fps"] > 0 else 0
        cap.release()
    except Exception as e:
        info["error"] = str(e)

    try:
        stat = os.stat(video_path)
        import datetime
        info["file_size_mb"] = round(stat.st_size / 1024 / 1024, 1)
        info["modified"] = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        # ファイル名から撮影日時を推定 (VID_YYYYMMDD_HHMMSS 形式)
        import re
        m = re.search(r"(\d{8})[_\-](\d{6})", os.path.basename(video_path))
        if m:
            d, t = m.group(1), m.group(2)
            info["shot_datetime"] = f"{d[:4]}-{d[4:6]}-{d[6:]} {t[:2]}:{t[2:4]}:{t[4:]}"
    except Exception:
        pass

    try:
        # EXIFからGPS情報を試みる (mp4のメタデータはffprobeで取得)
        import subprocess, json as _json
        result = subprocess.run(
            ["ffprobe","-v","quiet","-print_format","json","-show_format",video_path],
            capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            fmt = _json.loads(result.stdout).get("format", {})
            tags = fmt.get("tags", {})
            if "location" in tags:
                info["gps"] = tags["location"]
            elif "com.apple.quicktime.location.ISO6709" in tags:
                info["gps"] = tags["com.apple.quicktime.location.ISO6709"]
            if "creation_time" in tags:
                info["creation_time"] = tags["creation_time"]
    except Exception:
        pass

    return info


# ══════════════════════════════════════════════
#  メインアプリ
# ══════════════════════════════════════════════
class TennisApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"Tennis Form Analyzer  {APP_VERSION}")
        self.configure(bg=BG)
        self.geometry("1440x900"); self.minsize(1100,700)
        # v53: 起動時に最大化
        try: self.state("zoomed")
        except Exception: pass

        # 解析データ
        self.video_path   = tk.StringVar()
        self.sensitivity  = tk.DoubleVar(value=0.5)
        self.min_gap      = tk.DoubleVar(value=0.35)   # v18: 1.0 → 0.35s
        self.wall_mode    = tk.BooleanVar(value=False) # v18: 壁打ちモード
        self.camera_dist  = tk.DoubleVar(value=3.0)
        # v23: プレイヤー身長 (cm)
        self.player_height = tk.IntVar(value=DEFAULT_PLAYER_HEIGHT_CM)
        self.data         = None
        # v10: ピークは安定rank付きオブジェクトのリスト (表示=削除済みを除外したもの)
        #   各要素 {"rank":int(1始まり,検出順で固定), "idx":int, "time":float, "thumb":str}
        self.peaks        = []
        self.video_fps    = 30.0

        # 現在の選択状態
        self.peak_idx     = 0        # self.peaks 内のインデックス(表示位置)
        self.frame_offset = 0        # コマ送りオフセット(フレーム)
        self._current_frame_time = 0.0  # 現在表示中の実フレーム時刻

        # 前回ラベル記憶
        self._last_shot   = "serve"
        self._last_spin   = "unknown"
        self._last_rating = "unrated"
        self._last_cam    = []

        # 現在のラベル選択状態(即時記憶用)
        self._cur_shot    = tk.StringVar(value="serve")
        self._cur_spin    = tk.StringVar(value="unknown")
        self._cur_rating  = tk.StringVar(value="unrated")

        # v10: 複数クロップ (動画解像度に対する比率 0.0-1.0)
        #   各要素 {"rank":int, "time":float, "rect":(x1r,y1r,x2r,y2r)}  time昇順
        self._crops       = []
        self._crop_mode   = False  # クロップ追加ドラッグ中フラグ
        self._crop_drag_start = None
        self._crop_drag_end   = None
        self._crop_rect_id    = None
        self._video_wh        = (1920,1080)  # 実際の動画解像度(後で更新)

        # v10: インライン再生
        self._play_running = False
        self._play_paused  = False
        self._play_thread  = None
        self._play_seek_delta = 0
        self._play_seek_target = None  # v24: コンパクト再生中の絶対ジャンプ用
        self._play_cur_time   = [0.0]
        self._overlay_on   = True
        self._scrub_time   = None   # 停止中にタイムラインで掴んだ任意時刻
        self._deleted_peaks = []    # 削除済みチェックポイントの時刻
        self._play_highlight_idx = -1  # 再生中、通過ハイライトしている行
        self._force_uncropped = False  # クロップ解除直後の原画表示用

        # v22: 世代トークン (動画切替時にインクリメント、stale ワーカー UI 更新を無効化)
        self._gen = 0
        self._cached_video_path = None  # 最後にロードした動画パス (重複検知用)

        # ボタン参照
        self._shot_btns   = {}
        self._spin_btns   = {}
        self._rating_btns = {}

        self._build_ui()
        self.bind("<Key>", self._global_key)
        self.video_path.trace_add("write", lambda *_: self.after(50, self._on_video_selected))

    def _reset_video_state(self):
        """v22: 動画切替時に全 per-video state をクリア。世代トークンを進めて
        既存ワーカーの UI 更新を無効化する。"""
        # 世代を進める → 走行中のワーカーは UI 更新時にスキップされる
        self._gen += 1

        # 再生停止
        self._play_running = False
        self._play_highlight_idx = -1

        # データ系
        self.data = None
        self.peaks = []
        self.peak_idx = 0
        self.frame_offset = 0
        self._current_frame_time = 0.0
        self._scrub_time = None
        self._force_uncropped = False
        self._crops = []
        self._deleted_peaks = []
        self._video_wh = (1920, 1080)
        self._video_duration = 0
        self._pending_jump_rank = None

        # v24: 手ぶれ判定
        self._shake_scores = {}        # {rank: float} px/frame 平均移動量
        self._shake_threshold = 1.0    # これ以上 → 補正必要 (v24: 2.0→1.0 に厳格化)
        self._stab_cache = {}          # {rank: [(dx,dy), ...]} 補正オフセットキャッシュ
        self._stab_ref_rank = None     # 補正キャッシュの基準 rank

        # メタ情報
        self._last_cam = []
        self._meta_court = "oncourt"
        self._meta_level = "intermediate"
        self._meta_note = ""

        # UI ウィジェット内容のクリア (存在チェック付き)
        try:
            if hasattr(self,"peak_list") and self.peak_list.winfo_exists():
                self.peak_list.delete(0,"end")
        except Exception: pass
        try:
            if hasattr(self,"img_canvas") and self.img_canvas.winfo_exists():
                self.img_canvas.delete("all")
        except Exception: pass
        try:
            if hasattr(self,"_timeline_canvas") and self._timeline_canvas.winfo_exists():
                self._timeline_canvas.delete("all")
        except Exception: pass
        # 連続写真グリッド
        for attr in ("cs_grid","_yolo_grid","_cmp1_grid","_cmp2_grid"):
            try:
                w=getattr(self,attr,None)
                if w is not None and w.winfo_exists():
                    for c in list(w.winfo_children()):
                        try: c.destroy()
                        except Exception: pass
            except Exception: pass
        # サムネ参照クリア (PhotoImage GC)
        for attr in ("_cs_photo_refs","_yolo_photo_refs","_cmp1_photo_refs",
                     "_cmp2_photo_refs","_hist_thumb_refs"):
            try:
                lst=getattr(self,attr,None)
                if isinstance(lst,list): lst.clear()
            except Exception: pass

    # ══════════════════════════════════════════
    #  ピーク/クロップ ヘルパー (v10)
    # ══════════════════════════════════════════
    @property
    def peak_times(self):
        """表示中ピークの時刻リスト(削除済みを除外済み)"""
        return [p["time"] for p in self.peaks]

    def _rank(self, k=None):
        """表示位置kの安定rank (省略時は現在選択)"""
        if k is None: k=self.peak_idx
        if 0<=k<len(self.peaks): return self.peaks[k]["rank"]
        return k+1

    def _cur_thumb(self):
        if 0<=self.peak_idx<len(self.peaks):
            return self.peaks[self.peak_idx].get("thumb","") or ""
        return ""

    def _sync_list_selection(self):
        """peak_idx に対応する listbox 行を選択する (分類済フィルタ対応)。
           <<ListboxSelect>> イベントによる peak_idx 上書きを防ぐため
           一時フラグを使用。"""
        if not hasattr(self, "_list_to_peak_idx") or not self._list_to_peak_idx:
            list_idx = self.peak_idx
        else:
            try:
                list_idx = self._list_to_peak_idx.index(self.peak_idx)
            except ValueError:
                list_idx = 0  # フィルタで非表示の場合は先頭
        self._suppress_list_select = True
        self.peak_list.selection_clear(0, "end")
        self.peak_list.selection_set(list_idx)
        self.peak_list.see(list_idx)
        self.after(50, self._clear_suppress_flag)

    def _clear_suppress_flag(self):
        self._suppress_list_select = False

    def _crop_badges(self):
        """rank -> 'C1'/'C2'... (anchor_time順)。peak_rank=0(移行用)は番号付与しない"""
        badges={}
        n=0
        for c in sorted(self._crops,key=lambda c:c["time"]):
            if c["rank"]<=0:
                continue
            n+=1
            badges[c["rank"]]=f"C{n}"
        return badges

    def _crop_rect_for_rank(self, rank):
        """v24: 指定 CP rank に紐づくクロップ矩形を返す。なければ None"""
        if not self._crops: return None
        for c in self._crops:
            if c["rank"] == rank:
                return c["rect"]
        return None

    def _crop_rect_for_time(self, time_sec):
        """v24: 与えられた時刻に対応するCPのクロップ矩形を返す。
           時刻が最も近いCPを選び、そのCPのクロップを使用 (CP境界で切替)"""
        if not self.peaks or not self._crops: return None
        # 最も時刻が近い CP を選ぶ
        closest = min(self.peaks,
                      key=lambda p: abs((p.get("frame_time") or p["time"]) - time_sec))
        return self._crop_rect_for_rank(closest["rank"])

    def _active_crop_rect(self, time_sec, crops=None):
        """v24: 時刻ベースのクロップ取得 (旧 forward-only ロジックは廃止)。
           最近の CP のクロップを返す。 crops 引数は互換性のため残すが無視。"""
        return self._crop_rect_for_time(time_sec)

    def _crop_pil_at(self, pil_img, time_sec):
        """PIL画像に time_sec のクロップを適用"""
        rect=self._active_crop_rect(time_sec)
        if rect is None: return pil_img
        iw,ih=pil_img.size
        x1r,y1r,x2r,y2r=rect
        cx1=int(min(x1r,x2r)*iw); cy1=int(min(y1r,y2r)*ih)
        cx2=int(max(x1r,x2r)*iw); cy2=int(max(y1r,y2r)*ih)
        if cx2>cx1 and cy2>cy1:
            return pil_img.crop((cx1,cy1,cx2,cy2))
        return pil_img

    # ══════════════════════════════════════════
    #  UI構築
    # ══════════════════════════════════════════
    def _build_ui(self):
        # 左パネル (幅300)
        self.left=tk.Frame(self, bg=PANEL, width=300)
        self.left.pack(side="left", fill="y")
        self.left.pack_propagate(False)
        self._build_left()

        # メインエリア
        self.main=tk.Frame(self, bg=BG)
        self.main.pack(side="right", fill="both", expand=True)
        self._build_main()

    # ── 左パネル ──────────────────────────────
    def _build_left(self):
        p=self.left

        tk.Label(p,text="Tennis Analyzer",bg=PANEL,fg=ACCENT,
                 font=_tk_font(13,bold=True)).pack(pady=(14,2))
        tk.Label(p,text=f"{APP_VERSION}  {APP_VERSION_DESC}",bg=PANEL,fg=SUBTEXT,
                 font=_tk_font(10)).pack(pady=(0,6))
        self._hsep(p)

        # 動画選択 (v19: 同じ行に壁打ちチェックボックスを配置)
        head=tk.Frame(p,bg=PANEL); head.pack(fill="x",padx=12,pady=(6,2))
        tk.Label(head,text="動画ファイル",bg=PANEL,fg=TEXT,
                 font=_tk_font(11,bold=True)).pack(side="left",anchor="w")
        # v31: 壁打ちチェックはポップアップに統合（ここには非表示）
        fr=tk.Frame(p,bg=PANEL); fr.pack(fill="x",padx=12)
        tk.Entry(fr,textvariable=self.video_path,bg=DARK2,fg=TEXT,
                 insertbackground=TEXT,relief="flat",
                 font=_tk_font(9)).pack(side="left",fill="x",expand=True,ipady=4)
        tk.Button(fr,text="…",bg=ACCENT,fg="white",relief="flat",
                  font=_tk_font(10,bold=True),command=self._pick_file,width=2
                  ).pack(side="left",padx=(3,0))
        # v32: 複数ファイル選択ボタン
        tk.Button(fr,text="+",bg=DARK2,fg=SUBTEXT,relief="flat",
                  font=_tk_font(9),command=self._pick_files_multi,width=2,
                  cursor="hand2").pack(side="left",padx=(2,0))

        # v21: エイリアス表示 (動画情報ダイアログから設定可)
        self.alias_var=tk.StringVar(value="")
        self.alias_lbl=tk.Label(p,textvariable=self.alias_var,bg=PANEL,fg=GOLD,
                                font=_tk_font(10,bold=True),anchor="w")
        self.alias_lbl.pack(fill="x",padx=12,pady=(2,0))

        self.progress=ttk.Progressbar(p,mode="indeterminate",length=236)
        self.progress.pack(fill="x",padx=12,pady=(4,0))
        self.progress.pack_forget()

        self._hsep(p)

        # ポップアップボタン群
        btn_row=tk.Frame(p,bg=PANEL); btn_row.pack(fill="x",padx=12,pady=4)
        tk.Button(btn_row,text="動画情報",bg=DARK2,fg=TEXT,relief="flat",
                  font=_tk_font(8),command=self._open_meta_popup
                  ).pack(side="left",expand=True,fill="x",padx=(0,3),ipady=2)
        tk.Button(btn_row,text="検出設定",bg=DARK2,fg=TEXT,relief="flat",
                  font=_tk_font(8),command=self._open_param_popup
                  ).pack(side="left",expand=True,fill="x",padx=(3,0),ipady=2)

        self._hsep(p)

        # ヒットポイント一覧 + 分類済フィルタ
        hp_hdr=tk.Frame(p,bg=PANEL); hp_hdr.pack(fill="x",padx=12,pady=(2,2))
        # v61: ★凡例
        tk.Label(p,text="★=KP検出済  ◆=クロップ設定済  △=手ぶれ",
                 bg=PANEL,fg=SUBTEXT,font=_tk_font(7),anchor="w"
                 ).pack(fill="x",padx=12)
        tk.Label(hp_hdr,text="ヒットポイント",bg=PANEL,fg=ACCENT2,
                 font=_tk_font(11,bold=True)).pack(side="left")
        # v24: 「分類済」チェックボックス — 未分類 HP を非表示
        self._show_classified_only=tk.BooleanVar(value=False)
        tk.Checkbutton(hp_hdr,text="分類済",variable=self._show_classified_only,
                       bg=PANEL,fg=SUBTEXT,activebackground=PANEL,selectcolor=DARK2,
                       font=_tk_font(9),command=self._on_classified_filter_changed
                       ).pack(side="right")
        lf=tk.Frame(p,bg=PANEL)
        lf.pack(fill="both",expand=True,padx=12,pady=(0,4))
        sb=tk.Scrollbar(lf,bg=PANEL); sb.pack(side="right",fill="y")
        self.peak_list=tk.Listbox(lf,bg=DARK2,fg=TEXT,selectbackground=ACCENT,
                                   relief="flat",font=("Courier",10),
                                   yscrollcommand=sb.set,activestyle="none")
        self.peak_list.pack(side="left",fill="both",expand=True)
        sb.config(command=self.peak_list.yview)
        self.peak_list.bind("<<ListboxSelect>>",self._on_list_select)
        # 右クリック / Delキー で削除
        self.peak_list.bind("<Button-3>",self._on_list_right_click)
        self.peak_list.bind("<Delete>",
                             lambda e: (self._delete_current_checkpoint(), "break")[1])

        # v53: 検出情報（削除/再採番は削除、検出ステータスを表示）
        # v61: 検出情報 3行+ボタン形式
        self._di_vars = {}
        self._di_btns = {}
        di_frame = tk.Frame(p, bg=PANEL)
        di_frame.pack(fill="x", padx=12, pady=(2,4))
        for key, lbl, btn_txt, cmd in [
                ("img", "画像", "抽出", self._di_extract_images),
                ("mp",  "MP",  "検出", lambda: self._run_mp_detect_bg()),
                ("yolo","YOLO","検出", self._run_yolo_current_cp)]:
            row = tk.Frame(di_frame, bg=PANEL)
            row.pack(fill="x", pady=1)
            tk.Label(row, text=f"{lbl}:", bg=PANEL, fg=TEXT, width=5,
                     font=_tk_font(9, True), anchor="w").pack(side="left")
            v = tk.StringVar(value="─")
            self._di_vars[key] = v
            tk.Label(row, textvariable=v, bg=PANEL, fg=TEXT,
                     font=_tk_font(9), anchor="w").pack(side="left", fill="x", expand=True)
            b = tk.Button(row, text=btn_txt, bg=DARK2, fg=GOLD, relief="flat",
                          font=_tk_font(8), cursor="hand2", command=cmd, width=5)
            b.pack(side="right")
            self._di_btns[key] = b
        # 旧互換
        self._detect_info_var = tk.StringVar(value="")

        # v59: KP検出ボタン (MediaPipeデフォルト + YOLO別メニュー)
        tk.Button(p,text="🎯  現在のヒットポイントを解析",
                  bg=DARK2,fg=GOLD,relief="flat",font=_tk_font(10,bold=True),
                  command=self._run_yolo_current_cp,cursor="hand2"
                  ).pack(fill="x",padx=12,pady=(0,2),ipady=4)
        tk.Button(p,text="📥  YOLOで再検出",
                  bg=DARK2,fg=SUBTEXT,relief="flat",font=_tk_font(8),
                  command=self._run_yolo_current_cp,cursor="hand2"
                  ).pack(fill="x",padx=12,pady=(0,4),ipady=2)

        self.status_var=tk.StringVar(value="動画を選択してください")
        tk.Label(p,textvariable=self.status_var,bg=PANEL,fg=SUBTEXT,
                 font=_tk_font(9),wraplength=236,justify="left"
                 ).pack(padx=12,pady=(0,8),anchor="w")

    # ── メインエリア ──────────────────────────
    def _build_main(self):
        m=self.main

        # ── 全体ノートブック (メイン / 連続写真 / 比較1 / 比較2) ──
        style=ttk.Style(); style.theme_use("default")
        style.configure("Main.TNotebook",background=BG,borderwidth=0)
        style.configure("Main.TNotebook.Tab",background=PANEL,foreground=SUBTEXT,
                        padding=[16,6],font=_tk_font(10,bold=True))
        style.map("Main.TNotebook.Tab",
                  background=[("selected",ACCENT2)],foreground=[("selected","white")])

        self.tabs=ttk.Notebook(m,style="Main.TNotebook")
        self.tabs.pack(fill="both",expand=True)

        self.tab_main    = tk.Frame(self.tabs,bg=BG)
        self.tabs.add(self.tab_main,   text="ヒットポイント")
        self.tabs.bind("<<NotebookTabChanged>>",self._on_tab_changed)

        self._build_tab_main(self.tab_main)
        # v63: 今回の画面はヒットポイント検出に限定する。
        self.refiner = None

    def _build_tab_main(self,m):
        # フレーム表示 (上のコマ送りボタンは廃止 — 下のトランスポートへ統合)
        self.img_canvas=tk.Canvas(m,bg=DARK2,highlightthickness=0)
        self.img_canvas.pack(fill="both",expand=True,pady=4,padx=4)
        self.img_canvas.bind("<Configure>",self._on_canvas_resize)
        self.img_canvas.bind("<ButtonPress-1>",  self._crop_mouse_down)
        self.img_canvas.bind("<B1-Motion>",       self._crop_mouse_move)
        self.img_canvas.bind("<ButtonRelease-1>", self._crop_mouse_up)

        # ── タイムライン (波形+縦線+再生バー) ──
        self.timeline=tk.Canvas(m,bg="#111",height=60,highlightthickness=0)
        self.timeline.pack(fill="x",padx=4,pady=(0,0))
        self.timeline.bind("<Button-1>",self._on_timeline_click)
        self.timeline.bind("<Configure>",lambda e:self._draw_timeline())
        self.tl_placeholder=True

        # ── 再生コントロール (トランスポート) ──
        trans=tk.Frame(m,bg=PANEL2); trans.pack(fill="x")
        def _tb(text,cmd,bg=DARK2,fg=TEXT,w=7):
            return tk.Button(trans,text=text,bg=bg,fg=fg,relief="flat",
                             font=_tk_font(10),command=cmd,width=w,cursor="hand2")
        _tb("◀◀ -10s",lambda:self._seek(-10)).pack(side="left",padx=4,ipady=4,pady=3)
        _tb("◀ -3s",  lambda:self._seek(-3)).pack(side="left",padx=2,ipady=4,pady=3)
        _tb("◀ 1コマ",self._prev_frame).pack(side="left",padx=2,ipady=4,pady=3)
        self.btn_play=tk.Button(trans,text="▶ 再生",bg=GREEN,fg="white",relief="flat",
                                font=_tk_font(11,bold=True),width=8,
                                command=self._toggle_play,cursor="hand2")
        self.btn_play.pack(side="left",padx=6,ipady=4,pady=3)
        _tb("1コマ ▶",self._next_frame).pack(side="left",padx=2,ipady=4,pady=3)
        _tb("+3s ▶",  lambda:self._seek(+3)).pack(side="left",padx=2,ipady=4,pady=3)
        _tb("+10s ▶▶",lambda:self._seek(+10)).pack(side="left",padx=4,ipady=4,pady=3)
        self.btn_overlay=tk.Button(trans,text="字幕 ON",bg=GREEN,fg="white",relief="flat",
                                   font=_tk_font(9,bold=True),width=7,
                                   command=self._toggle_overlay,cursor="hand2")
        self.btn_overlay.pack(side="left",padx=6,ipady=4,pady=3)
        self.time_lbl=tk.Label(trans,text="00:00.00 / 00:00",bg=PANEL2,fg=GOLD,
                               font=("Courier",12,"bold"))
        self.time_lbl.pack(side="left",padx=12)

        # コンパクト再生コントロール (v22: 同じ PANEL2 上のサブ行として配置、
        #  トランスポートと視覚的に近接させ、デフォルト 1.5/1.5)
        cbar=tk.Frame(m,bg=PANEL2); cbar.pack(fill="x")
        self.cplay_pre =tk.StringVar(value="1.5")
        self.cplay_post=tk.StringVar(value="1.5")
        secs=[f"{x/2:.1f}" for x in range(1,21)]  # 0.5〜10.0 / 0.5
        tk.Label(cbar,text="▶ コンパクト再生範囲:",bg=PANEL2,fg=ACCENT2,
                 font=_tk_font(10,bold=True)).pack(side="left",padx=(8,4),pady=4)
        tk.Label(cbar,text="前",bg=PANEL2,fg=SUBTEXT,font=_tk_font(9)
                 ).pack(side="left",padx=(0,2))
        ttk.Combobox(cbar,textvariable=self.cplay_pre,values=secs,
                     width=4,state="readonly",font=_tk_font(9)
                     ).pack(side="left",padx=(0,2))
        tk.Label(cbar,text="s   後",bg=PANEL2,fg=SUBTEXT,font=_tk_font(9)
                 ).pack(side="left",padx=(0,2))
        ttk.Combobox(cbar,textvariable=self.cplay_post,values=secs,
                     width=4,state="readonly",font=_tk_font(9)
                     ).pack(side="left",padx=(0,2))
        tk.Label(cbar,text="s",bg=PANEL2,fg=SUBTEXT,font=_tk_font(9)
                 ).pack(side="left",padx=(0,10))
        self.btn_cplay=tk.Button(cbar,text="▶ コンパクト再生",bg=ACCENT2,fg="white",
                                 relief="flat",font=_tk_font(10,bold=True),
                                 command=self._toggle_compact_play,cursor="hand2")
        self.btn_cplay.pack(side="left",padx=4,ipady=4,pady=3)
        self.btn_cexp=tk.Button(cbar,text="💾 コンパクト出力",bg=GOLD,fg="#1a1000",
                                relief="flat",font=_tk_font(10,bold=True),
                                command=self._compact_export,cursor="hand2")
        self.btn_cexp.pack(side="left",padx=4,ipady=4,pady=3)

        # v24: スロー再生 (現在HPのみ、コンパクト再生と同じ前後範囲)
        self.slow_speed=tk.StringVar(value="2x")
        ttk.Combobox(cbar,textvariable=self.slow_speed,
                     values=["2x","3x","4x"],state="readonly",
                     width=3,font=_tk_font(9)).pack(side="left",padx=(12,2))
        self.btn_slow=tk.Button(cbar,text="▶ スロー",bg=ACCENT2,fg="white",
                  relief="flat",font=_tk_font(10,bold=True),cursor="hand2",
                  command=self._toggle_slow_play)
        self.btn_slow.pack(side="left",padx=(0,4),ipady=4,pady=3)

        # ── クロップツールバー (v24: 適用範囲モード追加) ──
        crop_bar=tk.Frame(m,bg=PANEL2); crop_bar.pack(fill="x")
        self.btn_crop=tk.Button(crop_bar,text="✂  クロップ追加",bg=DARK2,fg=TEXT,
                                relief="flat",font=_tk_font(9),
                                command=self._toggle_crop_mode,cursor="hand2")
        self.btn_crop.pack(side="left",padx=(8,4),ipady=3,pady=3)

        # v24: 適用範囲モード
        tk.Label(crop_bar,text="範囲:",bg=PANEL2,fg=SUBTEXT,
                 font=_tk_font(9)).pack(side="left",padx=(4,2))
        self._crop_apply_mode=tk.StringVar(value="個別")
        self.cb_crop_mode=ttk.Combobox(crop_bar,textvariable=self._crop_apply_mode,
                                        values=["未実施全て","個別"],
                                        state="readonly",width=10,font=_tk_font(9))
        self.cb_crop_mode.pack(side="left",padx=(0,8))

        self.btn_crop_clear=tk.Button(crop_bar,text="全クロップ解除",bg=DARK2,fg=SUBTEXT,
                                      relief="flat",font=_tk_font(9),
                                      command=self._crop_clear_all,cursor="hand2",
                                      state="disabled")
        self.btn_crop_clear.pack(side="left",padx=4,ipady=3,pady=3)
        self.lbl_crop_status=tk.Label(crop_bar,text="",bg=PANEL2,fg=GREEN,
                                      font=_tk_font(9))
        self.lbl_crop_status.pack(side="left",padx=8)

        # ラベルバー
        self._label_bar=tk.Frame(m,bg=PANEL2)
        self._label_bar.pack(fill="x")
        self._build_label_bar(self._label_bar)

    def _build_label_bar(self,parent):
        # ショット
        c1=tk.Frame(parent,bg=PANEL2); c1.pack(side="left",padx=(8,4),pady=5)
        tk.Label(c1,text="ショット",bg=PANEL2,fg=SUBTEXT,font=_tk_font(9)).pack(anchor="w")
        sg=tk.Frame(c1,bg=PANEL2); sg.pack()
        self._shot_btns={}
        for i,(ja,en) in enumerate(SHOT_TYPES):
            noise=(en=="noise")
            b=tk.Button(sg,text=ja,width=6,
                        bg="#2a0a0a" if noise else DARK2,
                        fg=ACCENT   if noise else TEXT,
                        relief="flat",font=_tk_font(10),
                        command=lambda e=en: self._select_shot(e,auto_save=True))
            b.grid(row=i//4,column=i%4,padx=2,pady=1)
            self._shot_btns[en]=b

        tk.Frame(parent,bg=BORDER,width=1).pack(side="left",fill="y",pady=4)

        # 回転
        c2=tk.Frame(parent,bg=PANEL2); c2.pack(side="left",padx=4,pady=5)
        tk.Label(c2,text="回転",bg=PANEL2,fg=SUBTEXT,font=_tk_font(9)).pack(anchor="w")
        spg=tk.Frame(c2,bg=PANEL2); spg.pack()
        self._spin_btns={}
        for i,(ja,en) in enumerate(SPINS):
            b=tk.Button(spg,text=ja,width=6,bg=DARK2,fg=TEXT,
                        relief="flat",font=_tk_font(10),
                        command=lambda e=en: self._select_spin(e,auto_save=True))
            b.grid(row=0,column=i,padx=2,pady=1)
            self._spin_btns[en]=b

        tk.Frame(parent,bg=BORDER,width=1).pack(side="left",fill="y",pady=4)

        # 評価
        c3=tk.Frame(parent,bg=PANEL2); c3.pack(side="left",padx=4,pady=5)
        tk.Label(c3,text="評価",bg=PANEL2,fg=SUBTEXT,font=_tk_font(9)).pack(anchor="w")
        rtg=tk.Frame(c3,bg=PANEL2); rtg.pack()
        self._rating_btns={}
        self._rating_selected={}
        for i,(ja,en) in enumerate(RATINGS):
            self._rating_selected[en]=False
            b=tk.Button(rtg,text=ja,width=6,bg=DARK2,fg=TEXT,
                        relief="flat",font=_tk_font(10),
                        command=lambda e=en: self._select_rating(e,auto_save=True))
            b.grid(row=0,column=i,padx=2,pady=1)
            self._rating_btns[en]=b

        tk.Frame(parent,bg=BORDER,width=1).pack(side="left",fill="y",pady=4)

        # CP追加ボタン (現在の表示コマを新規チェックポイントとして登録)
        c4=tk.Frame(parent,bg=PANEL2); c4.pack(side="left",padx=8,pady=5)
        tk.Label(c4,text="",bg=PANEL2,fg=SUBTEXT,font=_tk_font(9)).pack()
        tk.Button(c4,text="CP追加",bg=ACCENT2,fg="white",
                  relief="flat",font=_tk_font(12,bold=True),
                  command=self._add_checkpoint_at_current,cursor="hand2",width=7
                  ).pack(ipady=5,padx=4)

    # ── ヘルパー ────────────────────────────────
    def _hsep(self,parent):
        tk.Frame(parent,bg=BORDER,height=1).pack(fill="x",padx=12,pady=4)

    # ══════════════════════════════════════════
    #  ポップアップ: 動画情報
    # ══════════════════════════════════════════
    def _open_meta_popup(self):
        win=tk.Toplevel(self,bg=PANEL)
        win.title("動画情報"); win.geometry("460x680"); win.resizable(True,True)
        win.transient(self)
        # grab_setしない → モーダルにしない (即時保存するため)

        tk.Label(win,text="動画情報",bg=PANEL,fg=ACCENT,
                 font=_tk_font(13,bold=True)).pack(pady=(14,8))

        def _section(text):
            tk.Label(win,text=text,bg=PANEL,fg=TEXT,
                     font=_tk_font(11,bold=True)).pack(anchor="w",padx=16,pady=(10,2))

        # ── タイトル (旧: 別名/エイリアス) ──
        _section("タイトル (覚えやすい呼び名)")
        tk.Label(win,
                 text="動画ファイルとは別に、覚えやすいタイトルを付けられます。\n"
                      "左パネル・履歴・タイトルバーで表示されます。\n"
                      "ファイル自体はリネームされません。",
                 bg=PANEL,fg=SUBTEXT,font=_tk_font(8),justify="left",anchor="w"
                 ).pack(anchor="w",padx=16,pady=(0,4))
        alias_row=tk.Frame(win,bg=PANEL); alias_row.pack(fill="x",padx=16)
        # v24: 未設定なら撮影日 YYMMDD- をデフォルトとして入れる
        _cur_alias=get_video_alias(self.video_path.get())
        if not _cur_alias:
            _date_prefix=self._guess_shot_date_prefix(self.video_path.get())
            if _date_prefix:
                _cur_alias=_date_prefix
        alias_var=tk.StringVar(value=_cur_alias)
        alias_ent=tk.Entry(alias_row,textvariable=alias_var,bg=DARK2,fg=TEXT,
                           insertbackground=TEXT,relief="flat",font=_tk_font(10))
        alias_ent.pack(side="left",fill="x",expand=True,ipady=4)
        def _save_alias():
            p=self.video_path.get()
            if not p: return
            set_video_alias(p,alias_var.get().strip())
            self._refresh_alias_display()
            self.status_var.set("✓ タイトル保存済")
        tk.Button(alias_row,text="保存",bg=ACCENT,fg="white",relief="flat",
                  font=_tk_font(9,bold=True),command=_save_alias,cursor="hand2",
                  ).pack(side="left",padx=(4,0),ipady=3,ipadx=8)
        # フォーカスアウトでも自動保存
        alias_ent.bind("<FocusOut>",lambda e: _save_alias())

        # ── v23: プレイヤー身長 ──
        _section("プレイヤー身長")
        tk.Label(win,
                 text="グラフを cm 表示に切替える時の換算に使います。",
                 bg=PANEL,fg=SUBTEXT,font=_tk_font(8),justify="left",anchor="w"
                 ).pack(anchor="w",padx=16,pady=(0,4))
        ph_row=tk.Frame(win,bg=PANEL); ph_row.pack(fill="x",padx=16)
        ph_var=tk.StringVar(value=str(get_player_height(self.video_path.get())))
        ph_ent=tk.Entry(ph_row,textvariable=ph_var,bg=DARK2,fg=TEXT,
                        insertbackground=TEXT,relief="flat",font=_tk_font(10),width=6)
        ph_ent.pack(side="left",ipady=4)
        tk.Label(ph_row,text="cm",bg=PANEL,fg=SUBTEXT,font=_tk_font(10)
                 ).pack(side="left",padx=(4,8))
        def _save_height():
            p=self.video_path.get()
            if not p: return
            try: h=int(ph_var.get())
            except Exception: return
            if 100<=h<=250:
                set_player_height(p,h)
                self.player_height.set(h)
                self.status_var.set(f"✓ 身長 {h}cm 保存済")
        tk.Button(ph_row,text="保存",bg=ACCENT,fg="white",relief="flat",
                  font=_tk_font(9,bold=True),command=_save_height,cursor="hand2",
                  ).pack(side="left",ipady=3,ipadx=8)
        ph_ent.bind("<FocusOut>",lambda e: _save_height())

        def _do_save():
            cam=[en for en,v in cam_vars.items() if v.get()]
            self._last_cam=cam
            self._meta_court=court_var.get()
            self._meta_level=level_var.get()
            self._meta_note=note_box.get("1.0","end").strip()
            path=self.video_path.get()
            if path:
                db_path=get_db_path(path); init_db(db_path)
                save_video_meta(db_path,os.path.basename(path),
                                cam,self._meta_court,self._meta_level,
                                self._meta_note,None)
            self.status_var.set("✓ 動画情報保存済")

        # ── ファイル情報 (自動取得) ──────────────
        path=self.video_path.get()
        if path:
            _section("ファイル情報")
            info=get_video_info(path)
            info_frame=tk.Frame(win,bg=PANEL); info_frame.pack(fill="x",padx=16)
            def _info_row(label,value):
                row=tk.Frame(info_frame,bg=PANEL); row.pack(fill="x",pady=1)
                tk.Label(row,text=label,bg=PANEL,fg=SUBTEXT,
                         font=_tk_font(9),width=14,anchor="w").pack(side="left")
                tk.Label(row,text=str(value),bg=PANEL,fg=TEXT,
                         font=_tk_font(9),anchor="w").pack(side="left")
            _info_row("ファイル名",  os.path.basename(path))
            _info_row("解像度",      f"{info.get('width','?')} × {info.get('height','?')} px")
            _info_row("FPS",         f"{info.get('fps',0):.2f} fps")
            dur=info.get("duration_sec",0)
            _info_row("再生時間",    f"{int(dur//60)}:{int(dur%60):02d} ({dur:.1f}s)")
            _info_row("総フレーム数",f"{info.get('frames','?')} frames")
            _info_row("ファイルサイズ",f"{info.get('file_size_mb','?')} MB")
            if "shot_datetime" in info:
                _info_row("撮影日時(推定)", info["shot_datetime"])
            if "creation_time" in info:
                _info_row("作成日時",    info["creation_time"][:19])
            if "modified" in info:
                _info_row("更新日時",    info["modified"])
            if "gps" in info:
                _info_row("GPS情報",     info["gps"])

        # ── カメラ方向 ──────────────────────────
        _section("カメラ方向 (複数選択可)")
        cam_f=tk.Frame(win,bg=PANEL); cam_f.pack(padx=16,fill="x")
        cam_vars={}; cam_btns={}
        for i,(ja,en) in enumerate(CAMERA_DIRS):
            var=tk.BooleanVar(value=en in self._last_cam)
            cam_vars[en]=var
            b=tk.Button(cam_f,text=ja,width=16,
                        bg=GREEN if var.get() else DARK2,
                        fg="white" if var.get() else TEXT,
                        relief="flat",font=_tk_font(10))
            def _toggle(e=en,v=var,btn=b):
                v.set(not v.get())
                btn.config(bg=GREEN if v.get() else DARK2,fg="white" if v.get() else TEXT)
                _do_save()
            b.config(command=_toggle)
            b.grid(row=i//2,column=i%2,padx=3,pady=3,sticky="ew")
            cam_btns[en]=b
        cam_f.columnconfigure(0,weight=1); cam_f.columnconfigure(1,weight=1)

        # ── コートタイプ ─────────────────────────
        _section("コートタイプ")
        ct_f=tk.Frame(win,bg=PANEL); ct_f.pack(padx=16,fill="x")
        court_var=tk.StringVar(value=getattr(self,"_meta_court","oncourt"))
        ct_btns={}
        for ja,en in COURT_TYPES:
            b=tk.Button(ct_f,text=ja,
                        bg=ACCENT2 if court_var.get()==en else DARK2,
                        fg="white" if court_var.get()==en else TEXT,
                        relief="flat",font=_tk_font(10))
            def _sel_c(e=en,v=court_var):
                v.set(e)
                for k2,b2 in ct_btns.items():
                    b2.config(bg=ACCENT2 if k2==e else DARK2,fg="white" if k2==e else TEXT)
                _do_save()
            b.config(command=_sel_c)
            b.pack(side="left",expand=True,fill="x",padx=3)
            ct_btns[en]=b

        # ── プレイヤーレベル ─────────────────────
        _section("プレイヤーレベル")
        lv_f=tk.Frame(win,bg=PANEL); lv_f.pack(padx=16,fill="x")
        level_var=tk.StringVar(value=getattr(self,"_meta_level","intermediate"))
        lv_btns={}
        for ja,en in PLAYER_LEVELS:
            b=tk.Button(lv_f,text=ja,
                        bg=GREEN if level_var.get()==en else DARK2,
                        fg="white" if level_var.get()==en else TEXT,
                        relief="flat",font=_tk_font(10))
            def _sel_l(e=en,v=level_var):
                v.set(e)
                for k2,b2 in lv_btns.items():
                    b2.config(bg=GREEN if k2==e else DARK2,fg="white" if k2==e else TEXT)
                _do_save()
            b.config(command=_sel_l)
            b.pack(side="left",expand=True,fill="x",padx=2)
            lv_btns[en]=b

        # ── メモ (フォーカスアウト時に保存) ─────
        _section("動画メモ")
        note_box=tk.Text(win,bg=DARK2,fg=TEXT,insertbackground=TEXT,
                         relief="flat",font=_tk_font(10),height=3,wrap="word")
        note_box.pack(fill="x",padx=16)
        if hasattr(self,"_meta_note") and self._meta_note:
            note_box.insert("1.0",self._meta_note)
        note_box.bind("<FocusOut>",lambda e: _do_save())

        tk.Label(win,text="（メモは入力欄から離れると自動保存）",
                 bg=PANEL,fg=SUBTEXT,font=_tk_font(8)).pack(anchor="w",padx=16,pady=(2,12))

    def _on_wall_mode_changed(self):
        """v19: 壁打ちチェック切替時に既存データがあれば再検出"""
        if self.data is not None and self.peaks:
            try: self._refresh_peaks()
            except Exception: pass
            mode="ON" if self.wall_mode.get() else "OFF"
            self.status_var.set(f"壁打ちモード {mode}")

    def _refresh_alias_display(self):
        """v21: 左パネルのエイリアス表示とウィンドウタイトルを更新"""
        path=self.video_path.get()
        a=get_video_alias(path) if path else ""
        if a:
            self.alias_var.set(f"タイトル:  {a}")
            self.title(f"Tennis Form Analyzer  {APP_VERSION}  -  {a}")
        else:
            self.alias_var.set("")
            self.title(f"Tennis Form Analyzer  {APP_VERSION}")

    def _cs_pick_cp(self):
        """v24: 連続写真タブ用 CP サムネピッカー (オフセット0のサムネを一覧)"""
        if not self.peaks:
            messagebox.showinfo("CP選択","動画を読み込んでください"); return
        path=self.video_path.get()
        stem=os.path.splitext(os.path.basename(path))[0]
        thumb_dir=os.path.join(os.path.dirname(path),"1_thumbnails",stem)

        win=tk.Toplevel(self,bg=PANEL)
        win.title("ヒットポイントを選択"); win.geometry("760x520")
        win.transient(self); win.grab_set()
        tk.Label(win,text="ヒットポイントを選択 (打点フレーム)",
                 bg=PANEL,fg=GOLD,font=_tk_font(12,bold=True)).pack(pady=(10,4))
        tk.Label(win,text=f"{len(self.peaks)} CP",
                 bg=PANEL,fg=SUBTEXT,font=_tk_font(9)).pack(pady=(0,6))

        outer=tk.Frame(win,bg=PANEL); outer.pack(fill="both",expand=True,padx=8)
        canv=tk.Canvas(outer,bg=PANEL,highlightthickness=0)
        vsb=tk.Scrollbar(outer,orient="vertical",command=canv.yview)
        canv.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right",fill="y"); canv.pack(side="left",fill="both",expand=True)
        grid=tk.Frame(canv,bg=PANEL)
        canv.create_window((0,0),window=grid,anchor="nw")
        grid.bind("<Configure>",lambda e: canv.configure(scrollregion=canv.bbox("all")))

        def _on_mw(ev):
            try:
                if canv.winfo_exists(): canv.yview_scroll(int(-ev.delta/120),"units")
            except Exception: pass
        def _close_clean():
            try: canv.unbind_all("<MouseWheel>")
            except Exception: pass
            win.destroy()
        canv.bind("<Enter>",lambda e: canv.bind_all("<MouseWheel>",_on_mw))
        canv.bind("<Leave>",lambda e: [canv.unbind_all("<MouseWheel>")])
        win.protocol("WM_DELETE_WINDOW",_close_clean)

        photo_refs=[]; cols=5
        db_path=get_db_path(path); vf=os.path.basename(path)
        all_labels=load_all_labels(db_path,vf) if os.path.exists(db_path) else {}

        for i,p in enumerate(self.peaks):
            rank=p["rank"]
            row_i=i//cols; col_i=i%cols
            # hit サムネを探す
            tp=find_cp_thumb_path(path,rank)
            lbl_info=all_labels.get(rank,None)
            shot_ja=""
            if lbl_info: shot_ja=next((ja for ja,en in SHOT_TYPES if en==lbl_info[0]),"")
            cell=tk.Frame(grid,bg=DARK2,cursor="hand2",
                          highlightbackground=BORDER,highlightthickness=1)
            cell.grid(row=row_i,column=col_i,padx=3,pady=3,sticky="nsew")
            thumb_lbl=None
            if tp and os.path.exists(tp):
                try:
                    img=Image.open(tp); img.thumbnail((130,80),Image.LANCZOS)
                    photo=ImageTk.PhotoImage(img); photo_refs.append(photo)
                    thumb_lbl=tk.Label(cell,image=photo,bg=DARK2)
                except Exception: pass
            if thumb_lbl is None:
                thumb_lbl=tk.Label(cell,text="(no thumb)",bg=DARK2,fg=SUBTEXT,width=18,height=4)
            thumb_lbl.pack(padx=3,pady=3)
            t=p.get("frame_time") or p["time"]
            has_crop=any(c["rank"]==rank for c in self._crops)
            has_y,has_r=check_cp_yolo_status(path,rank)
            icons=("✂" if has_crop else " ")+("◆" if has_r else ("★" if has_y else " "))
            fg=GOLD if lbl_info else SUBTEXT
            tk.Label(cell,text=f"#{rank} {shot_ja} {icons}",
                     bg=DARK2,fg=fg,font=_tk_font(8,bold=bool(lbl_info))).pack()
            tk.Label(cell,text=f"{t:.2f}s",bg=DARK2,fg=SUBTEXT,font=_tk_font(8)).pack(pady=(0,2))

            def _pick(event,idx=i,rk=rank):
                try: canv.unbind_all("<MouseWheel>")
                except Exception: pass
                win.destroy()
                # 選択
                self.cs_peak_sel["values"]=[f"#{p['rank']}" for p in self.peaks]
                self.cs_peak_sel.current(idx)
                self._cs_cur_rank_var.set(f"#{rk}")
                if hasattr(self,"_cs_regen"): self._cs_regen()
            cell.bind("<Button-1>",_pick)
            thumb_lbl.bind("<Button-1>",_pick)
            for ch in cell.winfo_children(): ch.bind("<Button-1>",_pick)

        win._photo_refs=photo_refs
        tk.Button(win,text="キャンセル",bg=DARK2,fg=TEXT,relief="flat",
                  font=_tk_font(10),cursor="hand2",command=_close_clean
                  ).pack(pady=6,ipady=4,ipadx=12)

    def _guess_shot_date_prefix(self,path):
        """v24: 動画パスから撮影日を推測し "YYMMDD-" を返す。
        優先順: 1) ファイル名内の YYYYMMDD パターン
                2) ファイルの更新日時 (mtime)
        失敗時は空文字列を返す"""
        import re
        if not path: return ""
        # 1. ファイル名から
        basename=os.path.basename(path)
        m=re.search(r"(20\d{2})(\d{2})(\d{2})", basename)  # YYYYMMDD
        if m:
            yyyy,mm,dd=m.group(1),m.group(2),m.group(3)
            yy=yyyy[2:]
            return f"{yy}{mm}{dd}-"
        # 2. mtime
        try:
            import datetime
            mtime=os.path.getmtime(path)
            dt=datetime.datetime.fromtimestamp(mtime)
            return dt.strftime("%y%m%d-")
        except Exception:
            return ""

    # ══════════════════════════════════════════
    #  ポップアップ: 検出設定
    # ══════════════════════════════════════════
    def _open_param_popup(self):
        win=tk.Toplevel(self,bg=PANEL)
        win.title("検出パラメータ設定"); win.geometry("360x360")
        win.resizable(False,True); win.transient(self); win.grab_set()
        win.configure(bg=PANEL)

        tk.Label(win,text="検出パラメータ設定",bg=PANEL,fg=ACCENT,
                 font=_tk_font(13,bold=True)).pack(pady=(14,4))

        def _slider_row(label,var,from_,to_,resolution=0.05):
            tk.Label(win,text=label,bg=PANEL,fg=TEXT,
                     font=_tk_font(10,bold=True)).pack(anchor="w",padx=16,pady=(10,0))
            row=tk.Frame(win,bg=PANEL); row.pack(fill="x",padx=16)
            sld=tk.Scale(row,variable=var,from_=from_,to=to_,orient="horizontal",
                         resolution=resolution,bg=PANEL,fg=TEXT,troughcolor=DARK2,
                         highlightbackground=PANEL,activebackground=ACCENT,
                         relief="flat",length=240,sliderlength=16)
            sld.pack(side="left")
            tk.Label(row,textvariable=var,bg=PANEL,fg=ACCENT,
                     font=("Courier",10),width=5).pack(side="left",padx=4)

        _slider_row("検出感度  (高 → 多く検出)",self.sensitivity,0.1,0.95)
        _slider_row("最小間隔 (秒)",             self.min_gap,    0.1,3.0)
        _slider_row("カメラ距離 (m)",            self.camera_dist,1.0,5.0,resolution=0.5)

        # 壁打ちモードは左パネル上部 (動画ファイル行の隣) に移動 — v19
        tk.Label(win,
                 text="壁打ちモード ON 時:\n"
                      "  最小間隔を 0.5s 以上に固定\n"
                      "  0.05〜0.30秒のペアピーク (壁エコー) を抑制",
                 bg=PANEL,fg=SUBTEXT,font=_tk_font(8),justify="left"
                 ).pack(anchor="w",padx=16,pady=(14,8))

        def _apply():
            if self.data: self._refresh_peaks()
            self.status_var.set("✓ パラメータ適用済")
            win.destroy()

        tk.Button(win,text="適用して閉じる",bg=ACCENT,fg="white",relief="flat",
                  font=_tk_font(11,bold=True),command=_apply
                  ).pack(pady=16,ipadx=20,ipady=5)

    # ══════════════════════════════════════════
    #  動画選択 & 解析
    # ══════════════════════════════════════════
    def _pick_file(self):
        path=filedialog.askopenfilename(
            title="動画ファイルを選択",
            filetypes=[("動画ファイル","*.mp4 *.mov *.avi *.MP4 *.MOV")])
        if path: self.video_path.set(path)

    def _pick_files_multi(self):
        """v32: 複数ファイル選択モード"""
        paths = filedialog.askopenfilenames(
            title="動画ファイルを選択 (複数可)",
            filetypes=[("動画ファイル","*.mp4 *.mov *.avi *.MP4 *.MOV")])
        if not paths: return
        if len(paths) == 1:
            self.video_path.set(paths[0])
            return
        # 複数選択 → キュー表示
        self._multi_video_queue = list(paths)
        self._multi_video_idx = 0
        self.video_path.set(paths[0])

    def _pick_folder(self):
        folder=filedialog.askdirectory(title="動画フォルダを選択")
        if not folder: return
        exts=(".mp4",".mov",".avi")
        videos=[f for f in os.listdir(folder) if f.lower().endswith(exts)]
        if not videos:
            messagebox.showwarning("動画なし","動画ファイルが見つかりません"); return
        if len(videos)==1:
            self.video_path.set(os.path.join(folder,videos[0]))
        else:
            self._pick_from_list(folder,videos)

    def _pick_from_list(self,folder,videos):
        win=tk.Toplevel(self,bg=PANEL); win.title("動画を選択"); win.geometry("400x280")
        tk.Label(win,text="解析する動画を選択",bg=PANEL,fg=TEXT,
                 font=("Helvetica",10)).pack(pady=10)
        lb=tk.Listbox(win,bg=DARK2,fg=TEXT,selectbackground=ACCENT,
                      relief="flat",font=("Helvetica",9))
        lb.pack(fill="both",expand=True,padx=16,pady=4)
        for v in videos: lb.insert("end",v)
        lb.select_set(0)
        def _ok():
            sel=lb.curselection()
            if sel: self.video_path.set(os.path.join(folder,videos[sel[0]]))
            win.destroy()
        tk.Button(win,text="OK",bg=ACCENT,fg="white",relief="flat",
                  command=_ok,font=("Helvetica",10,"bold")).pack(pady=8,ipadx=16,ipady=4)

    def _on_video_selected(self):
        path=self.video_path.get().strip()
        if not path or not os.path.exists(path): return
        # v22: 同じ動画への再選択は無視 (state リセットでフリッカ防止)
        if path == self._cached_video_path:
            return
        # v25: 動画情報ポップアップを表示してから解析開始
        self._show_video_info_popup(path)

    def _show_video_info_popup(self, path):
        """v25: 動画選択時に動画情報を表示・設定するポップアップ"""
        cap = cv2.VideoCapture(path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fc = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        dur = fc / fps if fps > 0 else 0
        cap.set(cv2.CAP_PROP_POS_FRAMES, min(fc//2, 30))
        ret, frame = cap.read()
        cap.release()
        win = tk.Toplevel(self, bg=PANEL)
        win.title("動画情報")
        win.geometry("900x420")
        win.transient(self)
        win.grab_set()
        top = tk.Frame(win, bg=PANEL)
        top.pack(fill="both", expand=True, padx=12, pady=8)
        # 左: 動画プレビュー
        left = tk.Frame(top, bg=DARK2)
        left.pack(side="left", fill="both", padx=(0,8))
        self._popup_photo_ref = None
        if ret:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb)
            scale = min(360/img.width, 280/img.height)
            img = img.resize((int(img.width*scale), int(img.height*scale)), Image.LANCZOS)
            self._popup_photo_ref = ImageTk.PhotoImage(img)
        if self._popup_photo_ref:
            self._popup_thumb_lbl = tk.Label(left, image=self._popup_photo_ref, bg=DARK2)
            self._popup_thumb_lbl.pack(pady=4)
        else:
            self._popup_thumb_lbl = tk.Label(left, text="(プレビュー不可)", bg=DARK2, fg=SUBTEXT)
            self._popup_thumb_lbl.pack(pady=4)
        # v29: 10秒おきにサムネイルを自動切替
        self._popup_cycle_idx = 0
        self._popup_cycle_path = path
        self._popup_cycle_fc = fc
        self._popup_cycle_fps = fps
        self._popup_cycle_win = win
        self._popup_cycle_scale = min(360/(w or 640), 280/(h or 480))
        self._popup_cycle_id = win.after(1000, self._popup_cycle_thumb)
        info_text = (f"{os.path.basename(path)}\n"
                     f"{w}×{h}  {fps:.1f}fps  {dur:.1f}秒  ({fc}フレーム)")
        # v27: ファイルの日付時間を表示
        try:
            mtime = os.path.getmtime(path)
            dt_str = time.strftime("%Y/%m/%d %H:%M", time.localtime(mtime))
            info_text += f"\n撮影/更新: {dt_str}"
        except Exception: pass
        tk.Label(left, text=info_text, bg=DARK2, fg=TEXT,
                 font=_tk_font(9), justify="center").pack(pady=(0,4))
        # 右: 設定
        right = tk.Frame(top, bg=PANEL)
        right.pack(side="left", fill="both", expand=True)
        db_path = get_db_path(path); init_db(db_path)
        vf = os.path.basename(path)
        meta = load_video_meta(db_path, vf) or {}
        # v34: 追加メタデータの復元
        saved_extra = {}
        try:
            extra_path = os.path.splitext(path)[0] + "_meta_extra.json"
            if os.path.exists(extra_path):
                with open(extra_path, "r", encoding="utf-8") as f:
                    saved_extra = json.load(f)
        except Exception: pass
        # カメラ方向
        tk.Label(right, text="カメラ方向:", bg=PANEL, fg=TEXT,
                 font=_tk_font(10, True)).pack(anchor="w", pady=(4,2))
        cam_var = tk.StringVar(value=saved_extra.get("camera_dir",
                    (meta.get("camera_dirs",["不明・複数"])+["不明・複数"])[0]))
        cam_frame = tk.Frame(right, bg=PANEL); cam_frame.pack(anchor="w", padx=8)
        for cd in ["後ろ","横(フォア側)","横(バック側)","正面","不明・複数"]:
            tk.Radiobutton(cam_frame, text=cd, variable=cam_var, value=cd,
                           bg=PANEL, fg=TEXT, activebackground=PANEL,
                           selectcolor=DARK2, font=_tk_font(9)).pack(side="left", padx=2)
        # 主なショット (複数選択)
        tk.Label(right, text="主なショット:", bg=PANEL, fg=TEXT,
                 font=_tk_font(10, True)).pack(anchor="w", pady=(8,2))
        shot_frame = tk.Frame(right, bg=PANEL); shot_frame.pack(anchor="w", padx=8)
        saved_shots = saved_extra.get("main_shots", meta.get("main_shots", []))
        shot_vars = {}
        for st in ["サーブ","フォアハンド","バックハンド","ボレー","スマッシュ","リターン"]:
            v = tk.BooleanVar(value=(st in saved_shots))
            shot_vars[st] = v
            tk.Checkbutton(shot_frame, text=st, variable=v, bg=PANEL, fg=TEXT,
                           activebackground=PANEL, selectcolor=DARK2,
                           font=_tk_font(9)).pack(side="left", padx=2)
        # 内容
        tk.Label(right, text="内容:", bg=PANEL, fg=TEXT,
                 font=_tk_font(10, True)).pack(anchor="w", pady=(8,2))
        content_var = tk.StringVar(value=saved_extra.get("content_type",
                                   meta.get("content_type", "壁打ち")))
        ct_frame = tk.Frame(right, bg=PANEL); ct_frame.pack(anchor="w", padx=8)
        for ct in ["壁打ち","球出し","ラリー","練習","編集動画"]:
            tk.Radiobutton(ct_frame, text=ct, variable=content_var, value=ct,
                           bg=PANEL, fg=TEXT, activebackground=PANEL,
                           selectcolor=DARK2, font=_tk_font(9)).pack(side="left", padx=2)
        # v61: MediaPipe自動検出チェック (デフォルトON)
        tk.Label(right, text="キーポイント検出:", bg=PANEL, fg=TEXT,
                 font=_tk_font(10, True)).pack(anchor="w", pady=(8,2))
        kp_frame = tk.Frame(right, bg=PANEL); kp_frame.pack(anchor="w", padx=8)
        mp_auto_var = tk.BooleanVar(value=saved_extra.get("mp_auto", True))
        tk.Checkbutton(kp_frame, text="MediaPipe検出 (解析後に各HPを自動検出)",
                       variable=mp_auto_var, bg=PANEL, fg=TEXT,
                       activebackground=PANEL, selectcolor=DARK2,
                       font=_tk_font(9)).pack(side="left")
        # v40: プロジェクトフォルダ取込
        import_var = tk.BooleanVar(value=True)
        tk.Checkbutton(right, text="プロジェクトフォルダに取込 (動画+解析データを集約管理)",
                       variable=import_var, bg=PANEL, fg=TEXT,
                       activebackground=PANEL, selectcolor=DARK2,
                       font=_tk_font(9)).pack(anchor="w", pady=(8,2), padx=8)
        # メモ
        tk.Label(right, text="メモ:", bg=PANEL, fg=TEXT,
                 font=_tk_font(10, True)).pack(anchor="w", pady=(8,2))
        memo_entry = tk.Entry(right, bg=DARK2, fg=TEXT, font=_tk_font(9),
                              insertbackground=TEXT, width=40)
        memo_entry.pack(anchor="w", padx=8)
        memo_entry.insert(0, meta.get("note", ""))
        # ボタン
        btn_frame = tk.Frame(win, bg=PANEL)
        btn_frame.pack(fill="x", padx=12, pady=(0,8))
        def _on_ok():
            try:
                save_video_meta(db_path, vf,
                    camera_dirs=[cam_var.get()],
                    court_type=meta.get("court_type","oncourt"),
                    player_level=meta.get("player_level","intermediate"),
                    note=memo_entry.get().strip())
            except Exception: pass
            self._video_meta_extra = {
                "camera_dir": cam_var.get(),
                "main_shots": [k for k,v in shot_vars.items() if v.get()],
                "content_type": content_var.get(),
                "mp_auto": mp_auto_var.get(),  # v61
            }
            win.destroy()
            # v30: 壁打ちフラグをポップアップの選択から設定
            self.wall_mode.set(content_var.get() == "壁打ち")
            self._video_meta_extra = {
                "camera_dir": cam_var.get(),
                "main_shots": [k for k,v in shot_vars.items() if v.get()],
                "content_type": content_var.get(),
                "mp_auto": mp_auto_var.get(),
            }
            # v34: 追加メタデータをJSON保存 (次回復元用)
            try:
                extra_path = os.path.splitext(path)[0] + "_meta_extra.json"
                with open(extra_path, "w", encoding="utf-8") as f:
                    json.dump(self._video_meta_extra, f, ensure_ascii=False)
            except Exception: pass
            # v40: プロジェクトフォルダに取込
            load_path = path
            if import_var.get():
                imported = self._import_to_project(path)
                if imported:
                    load_path = imported
                    self.video_path.set(imported)
            self._proceed_video_load(load_path)
        tk.Button(btn_frame, text="OK - 解析開始", bg=ACCENT2, fg="white",
                  font=_tk_font(11, True), cursor="hand2",
                  command=_on_ok).pack(side="right", padx=4, ipady=4, ipadx=16)
        tk.Button(btn_frame, text="キャンセル", bg=DARK2, fg=TEXT,
                  font=_tk_font(10), cursor="hand2",
                  command=win.destroy).pack(side="right", padx=4, ipady=4, ipadx=8)

    def _import_to_project(self, path):
        """v40: 動画をプロジェクトフォルダ (managed_videos/{stem}/) にコピー。
        既にプロジェクト内なら何もしない。元ファイルは残す。
        戻り値: コピー先パス or None (失敗時)"""
        try:
            import shutil
            app_dir = os.path.dirname(os.path.abspath(__file__))
            managed_root = os.path.join(app_dir, "managed_videos")
            # 既にmanaged内ならそのまま
            if os.path.abspath(path).startswith(os.path.abspath(managed_root)):
                return path
            stem = os.path.splitext(os.path.basename(path))[0]
            dest_dir = os.path.join(managed_root, stem)
            os.makedirs(dest_dir, exist_ok=True)
            dest = os.path.join(dest_dir, os.path.basename(path))
            if not os.path.exists(dest):
                self.status_var.set("プロジェクトに取込中…")
                self.update_idletasks()
                shutil.copy2(path, dest)
            # 既存の解析データ (同フォルダのyolo/, _meta_extra.json等) もコピー
            src_dir = os.path.dirname(path)
            for extra in [stem + "_meta_extra.json", stem + "_analysis.db"]:
                src_f = os.path.join(src_dir, extra)
                if os.path.exists(src_f):
                    dst_f = os.path.join(dest_dir, extra)
                    if not os.path.exists(dst_f):
                        shutil.copy2(src_f, dst_f)
            src_yolo = os.path.join(src_dir, "yolo")
            dst_yolo = os.path.join(dest_dir, "yolo")
            if os.path.isdir(src_yolo) and not os.path.isdir(dst_yolo):
                # 該当動画のJSONのみコピー
                os.makedirs(dst_yolo, exist_ok=True)
                for fn in os.listdir(src_yolo):
                    if fn.startswith(stem):
                        shutil.copy2(os.path.join(src_yolo, fn),
                                     os.path.join(dst_yolo, fn))
            self.status_var.set(f"プロジェクトに取込完了: {dest_dir}")
            return dest
        except Exception as e:
            self.status_var.set(f"取込失敗 (元の場所で処理継続): {e}")
            return None

    def _popup_cycle_thumb(self):
        """v29: ポップアップのサムネイルを10秒進めて表示を切替"""
        try:
            win = self._popup_cycle_win
            if not win.winfo_exists(): return
            self._popup_cycle_idx += 1
            frame_pos = int(self._popup_cycle_idx * 10 * self._popup_cycle_fps)
            if frame_pos >= self._popup_cycle_fc:
                self._popup_cycle_idx = 0
                frame_pos = 0
            cap = cv2.VideoCapture(self._popup_cycle_path)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
            ret, frame = cap.read()
            cap.release()
            if ret:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb)
                sc = self._popup_cycle_scale
                img = img.resize((int(img.width*sc), int(img.height*sc)), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self._popup_photo_ref = photo
                self._popup_thumb_lbl.config(image=photo)
            self._popup_cycle_id = win.after(1000, self._popup_cycle_thumb)
        except Exception: pass

    def _proceed_video_load(self, path):
        """v25: ポップアップ後の実際の動画読込処理"""
        self._cached_video_path = path
        # v25: どのタブからでもメイン画面に遷移
        try: self.tabs.select(self.tab_main)
        except Exception: pass
        # v22: 全 per-video state をリセット + 世代トークン進める
        self._reset_video_state()
        # v21: エイリアス表示更新
        self._refresh_alias_display()
        # v23: プレイヤー身長読込
        try: self.player_height.set(get_player_height(path))
        except Exception: self.player_height.set(DEFAULT_PLAYER_HEIGHT_CM)
        # 再生中なら停止
        self._stop_play()
        cap=cv2.VideoCapture(path)
        self.video_fps=cap.get(cv2.CAP_PROP_FPS) or 30
        w=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_count=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self._video_wh=(w,h)
        self._video_duration=frame_count/self.video_fps if self.video_fps>0 else 0
        cap.release()
        db_path=get_db_path(path); init_db(db_path)
        vf=os.path.basename(path)
        meta=load_video_meta(db_path,vf)
        if meta:
            self._last_cam=meta.get("camera_dirs",[])
            self._meta_court=meta.get("court_type","oncourt")
            self._meta_level=meta.get("player_level","intermediate")
            self._meta_note=meta.get("note","")

        # クロップ読込 + 旧形式(単一crop_rect)の移行
        self._crops=load_crops(db_path,vf)
        if not self._crops and meta and meta.get("crop_rect"):
            legacy=meta.get("crop_rect")
            try:
                rect=tuple(legacy)
                if len(rect)==4:
                    add_crop(db_path,vf,0,0.0,rect)   # rank0=移行用グローバル
                    self._crops=load_crops(db_path,vf)
            except Exception:
                pass
        self._update_crop_ui()

        # 削除済みチェックポイント
        self._deleted_peaks=load_deleted_peaks(db_path,vf)

        # まず0秒のコマを即表示 (解析を待たずに寂しくないように)
        self.peaks=[]; self.peak_idx=0; self.frame_offset=0
        self._show_static_frame(0.0)

        # 2ショット比較タブの動画パスもメインに合わせる (ユーザーは…ボタンで変更可)
        if hasattr(self,"c1_path_a"): self.c1_path_a.set(path)
        if hasattr(self,"c1_path_b"): self.c1_path_b.set(path)

        # 長さ表示
        d=self._video_duration
        dur_str=f"{int(d//60)}分{d%60:04.1f}秒" if d>=60 else f"{d:.1f}秒"
        self.status_var.set(f"{vf}  ({dur_str})  解析準備中…")

        self._run_analysis()

    def _show_static_frame(self,time_sec):
        """解析前など、指定時刻のコマだけを表示"""
        path=self.video_path.get()
        frame=grab_frame(path,time_sec) if path else None
        if frame is None: return
        self._current_frame_time=time_sec
        # v36: 左上テキスト廃止 → 中央にのみ表示
        self._display_frame(frame,time_sec,info="")

    def _set_progress(self,pct,label):
        """進捗バー (0-100) と状態テキストを更新。v34: メイン画像中央に表示"""
        try:
            self.progress.configure(mode="determinate",maximum=100,value=max(0,min(100,pct)))
            d=getattr(self,"_video_duration",0)
            dur_str=f"{int(d//60)}分{d%60:04.1f}秒" if d>=60 else f"{d:.1f}秒"
            msg = f"{label}   ({dur_str})"
            self.status_var.set(msg)
            # v34: メイン画像キャンバスの中央にも進捗表示
            try:
                c = self.img_canvas
                c.delete("progress_text")
                cw = c.winfo_width(); ch = c.winfo_height()
                c.create_text(cw//2, ch//2, text=msg,
                              fill=GOLD, font=_tk_font(16, True),
                              tags="progress_text")
            except Exception: pass
        except Exception: pass

    def _show_kamishibai(self,thumb_path,done,total):
        """v24: 抽出中のサムネをメイン画面に高速表示 (紙芝居)"""
        try:
            if not os.path.exists(thumb_path): return
            from PIL import Image as _Img, ImageTk as _ImgTk, ImageDraw as _ImgD
            img=_Img.open(thumb_path)
            self.img_canvas.update_idletasks()
            cw=max(self.img_canvas.winfo_width(),300)
            ch=max(self.img_canvas.winfo_height(),200)
            iw_,ih_=img.size
            if iw_>0 and ih_>0:
                sc=min(cw/iw_, ch/ih_)
                img=img.resize((max(1,int(iw_*sc)),max(1,int(ih_*sc))),
                               _Img.LANCZOS)
            # 紙芝居感を出すため画面の下に小さなラベルを追加
            draw=_ImgD.Draw(img)
            tag=f"CP {done}/{total} 抽出中…"
            draw.rectangle([4,img.height-22,4+len(tag)*9,img.height-4],
                          fill=(0,0,0,180))
            draw.text((8,img.height-20),tag,fill="#ffd35e")
            photo=_ImgTk.PhotoImage(img)
            self._kamishibai_ref=photo  # GC防止
            self.img_canvas.delete("all")
            self.img_canvas.create_image(cw//2,ch//2,anchor="center",image=photo)
        except Exception: pass

    def _run_analysis(self):
        path=self.video_path.get().strip()
        if not path or not os.path.exists(path): return
        self.progress.pack(fill="x",padx=12,pady=(4,0))
        try: self.progress.stop()
        except Exception: pass
        self.progress.configure(mode="determinate",maximum=100,value=0)
        self._set_progress(0,"解析開始…")

        # キャッシュ確認 (.npz が存在すれば再解析せず即ロード)
        cache_path=get_analysis_cache_path(path)
        cached=load_analysis_cache(cache_path)
        if cached is not None:
            self.data=cached
            self._set_progress(50,"キャッシュ読込完了")
            self.after(0,self._finish_analysis)
            return

        def _worker():
            try:
                base=os.path.dirname(path); stem=os.path.splitext(os.path.basename(path))[0]
                audio_dir=os.path.join(base,"audio"); os.makedirs(audio_dir,exist_ok=True)
                audio_path=os.path.join(audio_dir,f"{stem}.mp3")
                self.after(0,lambda: self._set_progress(5,"音声抽出中…"))
                extract_audio(path,audio_path)
                self.after(0,lambda: self._set_progress(15,"音声解析中…"))
                self.data=analyze_audio(audio_path)
                # キャッシュ保存 (次回はスキップ可能)
                try: save_analysis_cache(cache_path,self.data)
                except Exception: pass
                self.after(0,lambda: self._set_progress(60,"ピーク検出中…"))
                self.after(0,self._finish_analysis)
            except Exception as e:
                err=str(e)
                self.after(0,lambda err=err: self._on_error(err))
        threading.Thread(target=_worker,daemon=True).start()

    def _finish_analysis(self):
        # v63: 音声候補をMediaPipeの3点解析で検証してから一覧を作る。
        # 姿勢解析はワーカーで行い、GUIスレッドを停止させない。
        self._start_fast_hp_pose_filter()

    @staticmethod
    def _hp_point(lms, index, min_vis=HP_POSE_MIN_VIS):
        """MediaPipeランドマークから可視点(x,y)を返す。座標は0..1。"""
        if not lms or index >= len(lms): return None
        lm = lms[index]
        vis = float(getattr(lm, "visibility", 1.0))
        if vis < min_vis: return None
        return np.array([float(lm.x), float(lm.y)], dtype=float)

    @staticmethod
    def _hp_angle(a, b, c):
        """bを頂点とする角度。点不足時はNone。"""
        if a is None or b is None or c is None: return None
        u=a-b; v=c-b
        den=float(np.linalg.norm(u)*np.linalg.norm(v))
        if den < 1e-9: return None
        return float(np.degrees(np.arccos(np.clip(np.dot(u,v)/den,-1.0,1.0))))

    def _hp_pose_features(self, lms):
        """右利きのサーブ/ストローク判定に必要な最小特徴量を作る。"""
        nose=self._hp_point(lms,0)
        ls=self._hp_point(lms,11); rs=self._hp_point(lms,12)
        re=self._hp_point(lms,14); rw=self._hp_point(lms,16)
        lh=self._hp_point(lms,23); rh=self._hp_point(lms,24)
        if any(x is None for x in (ls,rs,re,rw,lh,rh)):
            return None
        shoulder_c=(ls+rs)/2.0; hip_c=(lh+rh)/2.0
        shoulder_w=max(float(np.linalg.norm(ls-rs)),0.03)
        torso=max(float(np.linalg.norm(shoulder_c-hip_c)),shoulder_w)
        body_c=(shoulder_c+hip_c)/2.0
        elbow_angle=self._hp_angle(rs,re,rw)
        # 右手首が頭頂付近より上。鼻が取れない時は肩幅から頭頂を近似する。
        head_y=(float(nose[1])-0.12*torso) if nose is not None else \
               (float(shoulder_c[1])-0.65*torso)
        serve_zone=float(rw[1]) <= head_y + 0.18*torso
        # ストロークは肩から腰の帯を少し広めに許容する。
        top=float(shoulder_c[1])-0.20*torso
        bottom=float(hip_c[1])+0.35*torso
        stroke_zone=top <= float(rw[1]) <= bottom
        return {"rw":rw,"re":re,"rs":rs,"body_c":body_c,
                "shoulder_w":shoulder_w,"torso":torso,
                "elbow_angle":elbow_angle,"serve_zone":serve_zone,
                "stroke_zone":stroke_zone}

    def _classify_hp_pose_triplet(self, samples):
        """t-0.1,t,t+0.1の姿勢から明白な非スイング候補を落とす。"""
        valid=[s for s in samples if s.get("feat") is not None]
        if len(valid) < 2:
            return {"keep":True,"shot":"unknown","confidence":0.0,
                    "reason":"pose_uncertain"}
        feats=[s["feat"] for s in valid]
        scale=float(np.median([f["shoulder_w"] for f in feats]))
        travel=sum(float(np.linalg.norm(feats[i]["rw"]-feats[i-1]["rw"]))
                   for i in range(1,len(feats))) / max(scale,0.03)
        angles=[f["elbow_angle"] for f in feats if f["elbow_angle"] is not None]
        arm_change=(max(angles)-min(angles)) if len(angles)>=2 else 0.0
        has_serve=any(f["serve_zone"] for f in feats)
        has_stroke=any(f["stroke_zone"] for f in feats)
        moving=(travel >= HP_POSE_MIN_WRIST_TRAVEL or
                arm_change >= HP_POSE_MIN_ARM_CHANGE_DEG)
        if not moving or not (has_serve or has_stroke):
            return {"keep":False,"shot":"noise","confidence":0.85,
                    "reason":"no_swing","travel":travel,"arm_change":arm_change}
        # 頭上条件を満たす候補はサーブを優先する。
        shot="serve" if has_serve else "stroke"
        confidence=min(0.99,0.55+min(travel,1.0)*0.30+min(arm_change/60.0,1.0)*0.14)
        return {"keep":True,"shot":shot,"confidence":confidence,
                "reason":"swing","travel":travel,"arm_change":arm_change}

    def _hp_objective(self, feat, shot, camera_dir):
        if feat is None: return None
        if shot == "serve":
            return -float(feat["rw"][1])  # 画面上で最も高い点を最大化
        dist=abs(float(feat["rw"][0]-feat["body_c"][0]))/max(feat["shoulder_w"],0.03)
        side=("横" in camera_dir or camera_dir in ("deuce","ad"))
        return -dist if side else dist

    def _start_fast_hp_pose_filter(self):
        """音声候補を3枚のMediaPipe Poseで絞り、打点だけ局所探索する。"""
        if self.data is None: return
        # 壁打ちはラケット音と壁音を両方候補に残し、姿勢一致で後者を落とす。
        # find_peaksのdistanceで先に片方を消さないよう、この段階だけ間隔を短くする。
        candidate_gap=0.12 if bool(self.wall_mode.get()) else self.min_gap.get()
        indices,_=detect_peaks(self.data,self.sensitivity.get(),candidate_gap,
                               wall_mode=False)
        candidates=[{"idx":int(i),"time":float(self.data["times"][i])} for i in indices]
        if not candidates:
            self._refresh_peaks(refined_candidates=[])
            return
        path=self.video_path.get(); gen=self._gen
        camera_dir=str(getattr(self,"_video_meta_extra",{}).get("camera_dir",""))
        self._set_progress(62,f"姿勢で候補確認中… 0/{len(candidates)}")

        def _worker():
            cap=None
            try:
                model_path=self._mp_model_path_or_download()
                if not model_path: raise RuntimeError("MediaPipeモデルを準備できません")
                import mediapipe as mp
                from mediapipe.tasks.python import BaseOptions, vision
                cap=cv2.VideoCapture(path)
                fps=cap.get(cv2.CAP_PROP_FPS) or 30.0
                duration=(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)/fps
                opts=vision.PoseLandmarkerOptions(
                    base_options=BaseOptions(model_asset_path=model_path),
                    running_mode=vision.RunningMode.IMAGE,num_poses=1,
                    min_pose_detection_confidence=0.30,
                    min_pose_presence_confidence=0.30)
                frame_cache={}
                def detect_at(det,t):
                    frame_no=max(0,int(round(max(0.0,t)*fps)))
                    if frame_no in frame_cache: return frame_cache[frame_no]
                    cap.set(cv2.CAP_PROP_POS_FRAMES,frame_no)
                    ok,bgr=cap.read()
                    if not ok:
                        result={"time":frame_no/fps,"feat":None}; frame_cache[frame_no]=result; return result
                    rgb=cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
                    img=mp.Image(image_format=mp.ImageFormat.SRGB,data=np.ascontiguousarray(rgb))
                    with _suppress_stderr(): res=det.detect(img)
                    lms=res.pose_landmarks[0] if res.pose_landmarks else None
                    result={"time":frame_no/fps,"feat":self._hp_pose_features(lms)}
                    frame_cache[frame_no]=result
                    return result

                accepted=[]; rejected=0
                with _suppress_stderr(): detector_cm=vision.PoseLandmarker.create_from_options(opts)
                with detector_cm as det:
                    for n,cand in enumerate(candidates,1):
                        if self._gen != gen: return
                        t=cand["time"]
                        coarse=[detect_at(det,max(0.0,min(duration,t+d)))
                                for d in (-HP_POSE_COARSE_SEC,0.0,HP_POSE_COARSE_SEC)]
                        verdict=self._classify_hp_pose_triplet(coarse)
                        if not verdict["keep"]:
                            rejected+=1
                        else:
                            shot=verdict["shot"]
                            best=max((s for s in coarse if self._hp_objective(
                                s.get("feat"),shot,camera_dir) is not None),
                                key=lambda s:self._hp_objective(s["feat"],shot,camera_dir),
                                default=None)
                            best_t=t if best is None else best["time"]
                            # 中央から、粗判定で良かった方向へ1フレームずつ進む。
                            before=self._hp_objective(coarse[0].get("feat"),shot,camera_dir)
                            after=self._hp_objective(coarse[2].get("feat"),shot,camera_dir)
                            direction=-1 if before is not None and (after is None or before>after) else 1
                            best_score=self._hp_objective(best.get("feat"),shot,camera_dir) if best else None
                            stale=0; max_steps=max(1,int(round(HP_POSE_MAX_REFINE_SEC*fps)))
                            for step in range(1,max_steps+1):
                                s=detect_at(det,t+direction*step/fps)
                                score=self._hp_objective(s.get("feat"),shot,camera_dir)
                                if score is not None and (best_score is None or score>best_score+1e-4):
                                    best_score=score; best_t=s["time"]; stale=0
                                else:
                                    stale+=1
                                    if stale>=2: break
                            item=dict(cand); item.update({"frame_time":float(best_t),
                                "pose_shot":shot,"pose_confidence":verdict["confidence"],
                                "pose_reason":verdict["reason"]})
                            accepted.append(item)
                        self.after(0,lambda d=n,total=len(candidates),r=rejected:
                            self._set_progress(62+7*d/max(1,total),
                                f"姿勢で候補確認中… {d}/{total}  除外 {r}"))
                if self._gen==gen:
                    self.after(0,lambda a=accepted,r=rejected:
                        self._refresh_peaks(refined_candidates=a,pose_rejected=r))
            except Exception as e:
                print(f"[高速HP姿勢判定エラー] {e}")
                # モデルや環境の問題では音声候補を失わない。
                if self._gen==gen:
                    self.after(0,lambda:self._refresh_peaks())
            finally:
                if cap is not None: cap.release()
        threading.Thread(target=_worker,daemon=True).start()

    def _on_error(self,msg):
        try: self.progress.stop()
        except Exception: pass
        self.progress.pack_forget()
        messagebox.showerror("解析エラー",msg)
        self.status_var.set("エラーが発生しました")

    def _refresh_peaks(self, refined_candidates=None, pose_rejected=0):
        if self.data is None: return
        pose_filtered = refined_candidates is not None
        path=self.video_path.get(); vf=os.path.basename(path)
        db_path=get_db_path(path)
        self._deleted_peaks=load_deleted_peaks(db_path,vf)

        if refined_candidates is None:
            indices,n_echo=detect_peaks(self.data,self.sensitivity.get(),
                                         self.min_gap.get(),
                                         wall_mode=bool(self.wall_mode.get()))
            all_times=[float(self.data["times"][i]) for i in indices]
            refined_candidates=[{"idx":int(i),"time":t} for i,t in zip(indices,all_times)]
        else:
            n_echo=0
            indices=np.array([c["idx"] for c in refined_candidates],dtype=int)
            all_times=[float(c["time"]) for c in refined_candidates]
        if n_echo>0:
            self.status_var.set(f"壁エコー抑制 {n_echo} 件")

        # サムネイル抽出 (検出順=rank順) — 進捗付き
        # v24 後修正: 紙芝居は廃止 (画面バタつき・0%固まり問題の原因)
        #            シンプルな進捗テキストのみ
        base=os.path.dirname(path)
        thumb_dir=os.path.join(base,"1_thumbnails",
                               os.path.splitext(os.path.basename(path))[0])
        def _cb(done,total,thumb_path=None):
            pct=70 + 28*done/max(1,total)
            self.after(0,lambda: self._set_progress(
                pct,f"サムネイル抽出 {done}/{total}"))
        saved=extract_thumbnails(path,all_times,thumb_dir,progress_cb=_cb)
        thumbs=[s["path"] for s in saved if s["label"]=="pre"]

        # 既存ラベルとピークメタ (再採番済みのランク・手動CP)
        all_labels=load_all_labels(db_path,vf)
        metas=load_peak_meta(db_path,vf)
        tol=max(0.12,self.min_gap.get()*0.25)

        def _meta_for_time(t):
            for m in metas:
                if abs(m["time"]-t)<=tol: return m
            return None

        # まず自動検出ピーク (削除済みを除外、メタ優先)
        self.peaks=[]
        for i,(idx,t) in enumerate(zip(indices,all_times)):
            if any(abs(t-dt)<=tol for dt in self._deleted_peaks):
                continue
            m=_meta_for_time(t)
            if m and m["source"]=="manual":
                # 同じ時刻に手動 CP がある場合は自動側はスキップ (重複防止)
                continue
            rank = m["rank"] if m else (i+1)
            lbl=all_labels.get(rank)
            ft=float(lbl[3]) if (lbl and lbl[3] is not None and lbl[3]>0) else None
            pose_meta=refined_candidates[i] if i<len(refined_candidates) else {}
            self.peaks.append({"rank":rank,"idx":int(idx),"time":t,
                               "thumb":thumbs[i] if i<len(thumbs) else "",
                               "frame_time":ft if ft is not None else pose_meta.get("frame_time"),
                               "pose_shot":pose_meta.get("pose_shot"),
                               "pose_confidence":pose_meta.get("pose_confidence"),
                               "pose_reason":pose_meta.get("pose_reason"),
                               "source":"auto"})

        # 手動CP
        for m in metas:
            if m["source"]!="manual": continue
            t=m["time"]
            if any(abs(t-dt)<=tol for dt in self._deleted_peaks): continue
            lbl=all_labels.get(m["rank"])
            ft=float(lbl[3]) if (lbl and lbl[3] is not None and lbl[3]>0) else t
            self.peaks.append({"rank":m["rank"],"idx":-1,"time":t,
                               "thumb":"","frame_time":ft,"source":"manual"})

        # 時系列に並べる
        self.peaks.sort(key=lambda p: p["time"])

        # v30: 壁打ちモード時、0.2〜0.4秒以内の連続ピークの2番目を除去
        #      （サーブ音→壁音の2重検出を防止）
        if self.wall_mode.get() and not pose_filtered and len(self.peaks) > 1:
            filtered = [self.peaks[0]]
            for p in self.peaks[1:]:
                gap = p["time"] - filtered[-1]["time"]
                if 0.15 <= gap <= 0.45:
                    continue  # 2番目のピーク (壁音) をスキップ
                filtered.append(p)
            self.peaks = filtered

        self.peak_idx=0; self.frame_offset=0
        self._update_shot_list()
        self._update_view()
        self._set_progress(100,"完了")
        self.status_var.set(
            f"ヒットポイント: {len(self.peaks)} 件"
            + (f"  (姿勢で除外 {pose_rejected})" if pose_rejected else "")
            + (f"  (削除済 {len(self._deleted_peaks)})" if self._deleted_peaks else ""))
        try: self._refresh_active_tab()
        except Exception: pass
        try: self._update_registry()
        except Exception: pass
        # v24: 手ぶれ判定を自動実行 (バックグラウンド、2-6秒)
        try: self._detect_all_shake()
        except Exception: pass
        # v63: 全HPの±1.5秒MediaPipe自動検出は行わない。
        # HP抽出では上の高速3点判定と局所探索だけを使い、必要な解析量に限定する。
        self._first_analysis = False
        # v59: 検出情報を更新
        try: self._update_detect_info()
        except Exception: pass
        # v20: 履歴タブからのジャンプ要求があれば処理
        pj=getattr(self,"_pending_jump_rank",None)
        if pj is not None:
            self._pending_jump_rank=None
            try: self._jump_to_rank(pj)
            except Exception: pass

    def _update_registry(self):
        """解析済動画レジストリを更新"""
        path=self.video_path.get()
        if not path: return
        vf=os.path.basename(path)
        db_path=get_db_path(path)
        shot_counts=get_shot_breakdown(db_path,vf)
        first_thumb=""
        if self.peaks:
            first_thumb=self.peaks[0].get("thumb","") or ""
            # v20: フォールバック - first_thumb が無効/欠落ならラベル済CPから探す
            if not first_thumb or not os.path.exists(first_thumb):
                for p in self.peaks:
                    t=p.get("thumb","")
                    if t and os.path.exists(t):
                        first_thumb=t; break
        # v20: YOLO 解析数を集計
        n_yolo, n_refined = count_yolo_outputs(path)
        update_registry_entry(
            path,
            duration_sec=round(getattr(self,"_video_duration",0),2),
            num_cps=len(self.peaks),
            num_labeled=sum(shot_counts.values()),
            shot_counts=shot_counts,
            first_thumb=first_thumb,
            num_yolo=n_yolo,
            num_refined=n_refined,
        )

    # ══════════════════════════════════════════
    #  ショット一覧更新
    # ══════════════════════════════════════════
    def _on_classified_filter_changed(self):
        """分類済チェックボックス変更時: リスト + タイムライン即時再描画"""
        self._update_shot_list()
        self._sync_list_selection()
        self._draw_timeline()

    def _update_shot_list(self):
        path=self.video_path.get()
        db_path=get_db_path(path)
        all_labels=load_all_labels(db_path,os.path.basename(path))
        badges=self._crop_badges()
        crop_ranks={c["rank"] for c in self._crops}
        self.peak_list.delete(0,"end")
        # v24: 分類済フィルタ用の index マッピング (listbox idx → peaks idx)
        self._list_to_peak_idx=[]
        classified_only=(self._show_classified_only.get()
                         if hasattr(self,"_show_classified_only") else False)
        for i,p in enumerate(self.peaks):
            rank=p["rank"]; t=p["time"]
            lbl=all_labels.get(rank,None)
            # v24: 分類済フィルタ — ラベルがない HP は非表示
            if classified_only and lbl is None:
                continue
            cb=badges.get(rank,"")
            cb=f" [{cb}]" if cb else ""
            # v23: アイコン (クロップ + 検出済 + refined)
            has_y,has_r=check_cp_yolo_status(path,rank) if path else (False,False)
            icons=""
            if rank in crop_ranks: icons+="✂"
            if has_r: icons+="◆"
            elif has_y: icons+="★"
            # v24: 手ぶれ判定結果
            if self._is_shaky(rank): icons+="⚠"
            icons=f" {icons:<3}" if icons else "    "
            # v24: 評価アイコン (nice/super→👍、miss→👎、それ以外はスペース)
            if lbl:
                rating=lbl[2]
                rating_icon=" 👍" if rating in ("nice","super") else \
                            " 👎" if rating=="miss" else "   "
                shot_ja=next((ja for ja,en in SHOT_TYPES if en==lbl[0]),"?")
                spin_ja=next((ja for ja,en in SPINS      if en==lbl[1]),"")
                ft=lbl[3]
                ft_str=f"{ft:.2f}s" if (ft is not None and ft>0) else f"{t:.2f}s"
                tag=f"#{rank:2d}{icons}{rating_icon} {ft_str:>7} {shot_ja}/{spin_ja}{cb}"
            else:
                tag=f"#{rank:2d}{icons}    {t:6.2f}s   未{cb}"
            self.peak_list.insert("end",tag)
            self._list_to_peak_idx.append(i)

    # ══════════════════════════════════════════
    #  フレーム表示
    # ══════════════════════════════════════════
    def _update_detect_info(self):
        """v61: 検出情報 (画像/MP/YOLO) 3行を更新"""
        if not hasattr(self, "_di_vars"): return
        if not self.peaks or self.peak_idx >= len(self.peaks):
            for v in self._di_vars.values(): v.set("─")
            return
        p = self.peaks[self.peak_idx]
        rank = p["rank"]; path = self.video_path.get()
        stem = os.path.splitext(os.path.basename(path))[0]
        out_dir = self._yolo_out_dir(path)
        # 画像 (Refinerのframes_cache)
        if self.refiner and self.refiner.frames_cache:
            nc = len(self.refiner.frames_cache)
            nr = len(self.refiner.raw_frames) if self.refiner.raw_frames else 0
            if getattr(self.refiner, "_extracting", False):
                self._di_vars["img"].set(f"⏳ 抽出中 ({nc}/{nr})")
                self._di_btns["img"].config(state="disabled")
            else:
                self._di_vars["img"].set(f"✅ {nc}枚")
                self._di_btns["img"].config(state="disabled")
        else:
            self._di_vars["img"].set("❌ 未抽出")
            self._di_btns["img"].config(state="normal")
        # v62: MP/YOLO独立判定
        mp_path = os.path.join(out_dir, f"{stem}_cp{rank:02d}_mp.json")
        yolo_path = os.path.join(out_dir, f"{stem}_cp{rank:02d}_yolo.json")
        legacy_path = os.path.join(out_dir, f"{stem}_cp{rank:02d}.json")
        # legacyを判別 (modelフィールドで振り分け)
        legacy_is_mp = False; legacy_frames = 0
        if os.path.exists(legacy_path) and not os.path.exists(mp_path) and not os.path.exists(yolo_path):
            try:
                with open(legacy_path, "r", encoding="utf-8") as f:
                    d = json.load(f)
                legacy_is_mp = d.get("model", "") == "mediapipe"
                legacy_frames = len(d.get("frames", []))
            except Exception: pass
        # MP行
        cur_mp = self._di_vars["mp"].get()
        mp_frames = 0
        if os.path.exists(mp_path):
            try:
                with open(mp_path, "r", encoding="utf-8") as f:
                    mp_frames = len(json.load(f).get("frames", []))
            except Exception: pass
        elif legacy_is_mp:
            mp_frames = legacy_frames
        if mp_frames > 0:
            if not cur_mp.startswith("⏳"):
                self._di_vars["mp"].set(f"✅ 検出済 ({mp_frames}フレーム)")
                self._di_btns["mp"].config(state="disabled")
        else:
            if not cur_mp.startswith("⏳"):
                self._di_vars["mp"].set("❌ 未検出")
                self._di_btns["mp"].config(state="normal")
        # YOLO行
        cur_yolo = self._di_vars["yolo"].get()
        yolo_frames = 0
        if os.path.exists(yolo_path):
            try:
                with open(yolo_path, "r", encoding="utf-8") as f:
                    yolo_frames = len(json.load(f).get("frames", []))
            except Exception: pass
        elif os.path.exists(legacy_path) and not legacy_is_mp:
            yolo_frames = legacy_frames
        if yolo_frames > 0:
            if not cur_yolo.startswith("⏳"):
                self._di_vars["yolo"].set(f"✅ 検出済 ({yolo_frames}フレーム)")
                self._di_btns["yolo"].config(state="disabled")
        else:
            if not cur_yolo.startswith("⏳"):
                self._di_vars["yolo"].set("❌ 未検出")
                self._di_btns["yolo"].config(state="normal")

    def _di_extract_images(self):
        """v61: 画像抽出ボタン → RefinerにHPロードして抽出開始"""
        try:
            self._sync_refiner_hp()
            self._set_di_status("img", "⏳ 抽出中…")
        except Exception as e:
            print(f"[画像抽出] {e}")

    def _update_view(self,preview_frame=None,preview_time=None):
        if self.data is None and not self.peaks:
            return
        # v53: 検出情報を更新
        try: self._update_detect_info()
        except Exception: pass
        if preview_frame is not None:
            self._display_frame(preview_frame, preview_time or 0.0, preview=True)
            return
        # 再生中はプレイヤーがキャンバスを占有
        if self._play_running:
            self._draw_timeline()
            return

        # 通常モード
        if self.peaks and self.peak_idx<len(self.peaks):
            pt=self.peaks[self.peak_idx]["time"]
            sound_delay=self.camera_dist.get()/SOUND_SPEED
            base_time=max(0.0,pt-sound_delay)
            frame_time=max(0.0,base_time+self.frame_offset/self.video_fps)
        else:
            frame_time=0.0

        self._current_frame_time=frame_time
        self._scrub_time=None
        path=self.video_path.get()
        frame=grab_frame(path,frame_time) if path else None
        if frame is not None:
            self._display_frame(frame,frame_time)
        else:
            self.img_canvas.delete("all")
            self.img_canvas.create_text(
                max(self.img_canvas.winfo_width()//2,200),
                max(self.img_canvas.winfo_height()//2,150),
                text="読み込み中…",fill=SUBTEXT,font=_tk_font(12))

        self._restore_label_for_current()
        self._draw_timeline()

    def _display_frame(self,frame,frame_time,preview=False,info=None):
        rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        img=Image.fromarray(rgb)

        # v24: クロップ適用は「現在選択中のCP」のものを使用
        # (frame_offset でずれた時にも、ユーザーの認識通りそのCPのクロップを保つ)
        crop_active=False
        if not self._crop_mode and not self._force_uncropped:
            cur_rank=None
            if self.peaks and 0<=self.peak_idx<len(self.peaks):
                cur_rank=self.peaks[self.peak_idx]["rank"]
            rect=self._crop_rect_for_rank(cur_rank) if cur_rank is not None else None
            if rect is not None:
                iw,ih=img.size
                x1r,y1r,x2r,y2r=rect
                cx1=int(min(x1r,x2r)*iw); cy1=int(min(y1r,y2r)*ih)
                cx2=int(max(x1r,x2r)*iw); cy2=int(max(y1r,y2r)*ih)
                if cx2>cx1 and cy2>cy1:
                    img=img.crop((cx1,cy1,cx2,cy2)); crop_active=True

        self.img_canvas.update_idletasks()
        cw=max(self.img_canvas.winfo_width(),200)
        ch=max(self.img_canvas.winfo_height(),150)
        # v18 fix: thumbnail() は縮小しかしないので、640×360 のような
        # 小さい動画ではキャンバスにフィットせず、クロップ計算が狂う
        # resize() でアスペクト比保持しつつ拡大も許可
        iw_,ih_=img.size
        if iw_>0 and ih_>0:
            sc=min(cw/iw_, ch/ih_)
            new_w=max(1,int(iw_*sc)); new_h=max(1,int(ih_*sc))
            method=Image.LANCZOS if not preview else Image.NEAREST
            img=img.resize((new_w,new_h), method)
        photo=ImageTk.PhotoImage(img)
        self.img_canvas.delete("all")
        self.img_canvas.create_image(cw//2,ch//2,anchor="center",image=photo)

        if preview:
            # 再生中: 中央下に大きな字幕
            self._draw_play_overlay(frame_time,cw,ch)
        elif info is not None:
            self.img_canvas.create_rectangle(4,4,260,30,fill="#000000",stipple="gray50",outline="")
            self.img_canvas.create_text(10,16,anchor="w",text=info,
                fill=TEXT,font=("Helvetica",13,"bold"))
        else:
            rank     = self._rank()
            n_peaks  = len(self.peaks)
            pos      = self.peak_idx+1
            pt       = self.peaks[self.peak_idx]["time"] if self.peaks else 0.0
            offset_f = self.frame_offset
            line1 = f"#{rank}  ({pos}/{n_peaks})"
            line2 = f"表示: {frame_time:.2f}s"
            line3 = f"ピーク: {pt:.2f}s  (offset {offset_f:+d}f)"
            self.img_canvas.create_rectangle(4,4,290,76,fill="#000000",stipple="gray50",outline="")
            self.img_canvas.create_text(10,16,anchor="nw",text=line1,
                fill="white",font=("Helvetica",16,"bold"))
            self.img_canvas.create_text(10,38,anchor="nw",text=line2,
                fill=TEXT,font=("Helvetica",14))
            self.img_canvas.create_text(10,58,anchor="nw",text=line3,
                fill=SUBTEXT,font=("Helvetica",12))
        # クロップ中バッジ
        if crop_active:
            self.img_canvas.create_rectangle(cw-86,4,cw-4,24,fill="#1d9e75",outline="")
            self.img_canvas.create_text(cw-45,14,anchor="center",text="✂ クロップ中",
                fill="white",font=("Helvetica",9))

        self._img_ref=photo

    def _draw_play_overlay(self,current_time,cw,ch):
        """再生中: ピーク±1秒以内のラベルを中央下に大きく表示"""
        if not self._overlay_on or not self.peaks: return
        path=self.video_path.get(); db_path=get_db_path(path); vf=os.path.basename(path)
        for p in self.peaks:
            disp_t=p.get("frame_time") or p["time"]
            if abs(current_time-disp_t)<=1.0:
                lbl=load_label(db_path,vf,p["rank"])
                if lbl and lbl.get("shot_type") not in ("noise",""):
                    shot_ja=next((ja for ja,en in SHOT_TYPES if en==lbl["shot_type"]),"")
                    spin_ja=next((ja for ja,en in SPINS    if en==lbl.get("spin","")),"")
                    rating_ja=next((ja for ja,en in RATINGS if en==lbl.get("rating","")),"")
                    txt=f"#{p['rank']} {shot_ja} / {spin_ja} / {rating_ja}"
                    tw=len(txt)*22; x=cw//2; y=ch-60
                    # チェックポイント瞬間 (frame_time の ±1フレーム以内): 白フラッシュ
                    near_exact=abs(current_time-disp_t)<=max(1.5/self.video_fps,0.04)
                    if near_exact:
                        # 画面端にも白枠
                        self.img_canvas.create_rectangle(2,2,cw-2,ch-2,
                            outline="#ffffff",width=6)
                        # 字幕背景を白に
                        self.img_canvas.create_rectangle(x-tw//2-12,y-28,x+tw//2+12,y+28,
                            fill="#ffffff",outline="")
                        self.img_canvas.create_text(x,y,anchor="center",text=txt,
                            fill="#a00000",font=_tk_font(34,bold=True))
                    else:
                        self.img_canvas.create_rectangle(x-tw//2-10,y-26,x+tw//2+10,y+26,
                            fill="#000000",stipple="gray50",outline="")
                        self.img_canvas.create_text(x,y,anchor="center",text=txt,
                            fill=GOLD,font=_tk_font(34,bold=True))
                break

    def _on_canvas_resize(self,event):
        self.after(50,self._update_view)

    def _step_frame(self,delta_frames):
        """現在の表示コマから ±delta_frames コマ進める"""
        if self.video_fps<=0: return
        if self._play_running:
            self._seek(delta_frames/self.video_fps); return
        new_t=max(0.0,self._current_frame_time+delta_frames/self.video_fps)
        # peak が選択されているなら frame_offset を更新 (保存と整合)
        if self.peaks and 0<=self.peak_idx<len(self.peaks):
            sd=self.camera_dist.get()/SOUND_SPEED
            base=max(0.0,self.peaks[self.peak_idx]["time"]-sd)
            self.frame_offset=int(round((new_t-base)*self.video_fps))
            self._scrub_time=None
            self._update_view()
            self._auto_save()
        else:
            self._scrub_to(new_t)

    def _prev_frame(self):
        self._step_frame(-1)

    def _next_frame(self):
        self._step_frame(+1)

    def _prev_frame5(self):
        self._step_frame(-5)

    def _next_frame5(self):
        self._step_frame(+5)

    # ══════════════════════════════════════════
    #  タイムライン (波形 + 縦線 + 再生位置)
    # ══════════════════════════════════════════
    # ══════════════════════════════════════════
    #  手ぶれ判定 + 補正 (v24)
    # ══════════════════════════════════════════
    def _detect_all_shake(self):
        """全HPの手ぶれスコアをバックグラウンドで計算。
        解析完了後に自動呼出し。"""
        path=self.video_path.get()
        if not path or not self.peaks: return
        gen=self._gen
        def _worker():
            try:
                cap=cv2.VideoCapture(path)
                if not cap.isOpened(): return
                fps=cap.get(cv2.CAP_PROP_FPS) or 30
                scores={}
                for p in self.peaks:
                    if self._gen!=gen: break  # 動画切替が起きたら中止
                    rank=p["rank"]
                    hit_t=p.get("frame_time") or p["time"]
                    score=self._shake_score_range(cap,hit_t,fps,duration=1.0,
                                                  n_samples=15)
                    scores[rank]=score
                cap.release()
                if self._gen==gen:
                    self._shake_scores=scores
                    self.after(0,self._update_shot_list)
                    n_shaky=sum(1 for s in scores.values() if s>=self._shake_threshold)
                    self.after(0,lambda: self.status_var.set(
                        f"手ぶれ判定完了: {n_shaky}/{len(scores)} HP が補正対象"))
            except Exception: pass
        threading.Thread(target=_worker,daemon=True).start()

    def _shake_score_range(self,cap,center_t,fps,duration=1.0,n_samples=15):
        """指定時刻±duration の範囲で n_samples フレームペアを解析し、
        背景特徴点のフレーム間平均移動量 (px) を返す。
        0 → 完全に固定  2+ → 手持ち  10+ → 激しい手ぶれ"""
        total=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fstart=max(0,int((center_t-duration)*fps))
        fend=min(total-1,int((center_t+duration)*fps))
        if fend-fstart<4: return 0.0
        step=max(1,(fend-fstart)//(n_samples+1))
        indices=list(range(fstart,fend,step))[:n_samples+1]
        if len(indices)<2: return 0.0

        displacements=[]
        prev_gray=None
        prev_pts=None
        for fi in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES,fi)
            ret,frame=cap.read()
            if not ret: continue
            gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            if prev_gray is not None and prev_pts is not None and len(prev_pts)>=4:
                pts1,status,_=cv2.calcOpticalFlowPyrLK(prev_gray,gray,prev_pts,None)
                if pts1 is not None and status is not None:
                    good=status.ravel()==1
                    if good.sum()>=4:
                        dx=pts1[good,0,0]-prev_pts[good,0,0]
                        dy=pts1[good,0,1]-prev_pts[good,0,1]
                        # 人物領域を除外: 中央 1/3 の特徴点はスキップ
                        h,w=gray.shape[:2]
                        cx_lo,cx_hi=w*0.33,w*0.67
                        bg_mask=np.ones(good.sum(),dtype=bool)
                        pts_g=prev_pts[good]
                        for ki in range(len(pts_g)):
                            px=pts_g[ki,0,0]
                            if cx_lo<=px<=cx_hi: bg_mask[ki]=False
                        if bg_mask.sum()>=3:
                            med_d=np.sqrt(np.median(dx[bg_mask])**2+
                                          np.median(dy[bg_mask])**2)
                            displacements.append(med_d)
            # 次のフレーム用に特徴点を検出
            pts=cv2.goodFeaturesToTrack(gray,maxCorners=200,
                                        qualityLevel=0.01,minDistance=10)
            prev_gray=gray; prev_pts=pts

        if not displacements: return 0.0
        return float(np.median(displacements))

    def _compute_stab_offsets(self,cap,hit_t,fps,pre=1.5,post=1.5,rank=None):
        """指定HP周辺のフレームごとの補正オフセット (dx,dy) を計算。
        基準フレーム = 打点フレーム。各フレームの背景移動量を累積して返す。
        戻り値: {frame_number: (dx, dy)}"""
        if rank is not None and rank==self._stab_ref_rank and self._stab_cache:
            return self._stab_cache  # キャッシュヒット
        ref_fn=int(hit_t*fps)
        fn_start=max(0,int((hit_t-pre)*fps))
        fn_end=int((hit_t+post)*fps)
        # 基準フレーム
        cap.set(cv2.CAP_PROP_POS_FRAMES,ref_fn)
        ret,ref_frame=cap.read()
        if not ret: return {}
        ref_gray=cv2.cvtColor(ref_frame,cv2.COLOR_BGR2GRAY)
        ref_pts=cv2.goodFeaturesToTrack(ref_gray,maxCorners=300,
                                         qualityLevel=0.01,minDistance=8)
        if ref_pts is None or len(ref_pts)<5: return {}
        offsets={}
        offsets[ref_fn]=(0.0,0.0)
        # 基準から前後に走査
        for direction in [-1,1]:
            prev_gray=ref_gray
            prev_pts=ref_pts.copy()
            cum_dx,cum_dy=0.0,0.0
            fn=ref_fn
            while True:
                fn+=direction
                if direction<0 and fn<fn_start: break
                if direction>0 and fn>fn_end: break
                cap.set(cv2.CAP_PROP_POS_FRAMES,fn)
                ret,frame=cap.read()
                if not ret: break
                gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                if prev_pts is None or len(prev_pts)<4:
                    prev_pts=cv2.goodFeaturesToTrack(gray,maxCorners=300,
                                                     qualityLevel=0.01,minDistance=8)
                    prev_gray=gray; continue
                pts1,status,_=cv2.calcOpticalFlowPyrLK(prev_gray,gray,prev_pts,None)
                if pts1 is not None and status is not None:
                    good=status.ravel()==1
                    if good.sum()>=4:
                        dx_arr=pts1[good,0,0]-prev_pts[good,0,0]
                        dy_arr=pts1[good,0,1]-prev_pts[good,0,1]
                        # 中央 1/3 (人物) を除外
                        h,w=gray.shape[:2]
                        pts_g=prev_pts[good]
                        bg=np.array([(pts_g[k,0,0]<w*0.3 or pts_g[k,0,0]>w*0.7)
                                     for k in range(len(pts_g))])
                        if bg.sum()>=3:
                            cum_dx+=float(np.median(dx_arr[bg]))
                            cum_dy+=float(np.median(dy_arr[bg]))
                offsets[fn]=(-cum_dx,-cum_dy)  # 逆方向にずらして補正
                new_pts=cv2.goodFeaturesToTrack(gray,maxCorners=300,
                                                qualityLevel=0.01,minDistance=8)
                prev_gray=gray; prev_pts=new_pts
        # キャッシュ
        if rank is not None:
            self._stab_ref_rank=rank
            self._stab_cache=offsets
        return offsets

    def _apply_stabilization(self,frame,frame_number,offsets):
        """フレームに手ぶれ補正を適用 (並進シフト)"""
        if not offsets or frame_number not in offsets:
            return frame
        dx,dy=offsets[frame_number]
        if abs(dx)<0.5 and abs(dy)<0.5:
            return frame  # ほぼゼロなら何もしない
        h,w=frame.shape[:2]
        M=np.float32([[1,0,dx],[0,1,dy]])
        return cv2.warpAffine(frame,M,(w,h),borderMode=cv2.BORDER_REPLICATE)

    def _is_shaky(self,rank):
        """指定HPが手ぶれ補正対象かどうか"""
        return self._shake_scores.get(rank,0.0)>=self._shake_threshold

    def _draw_timeline(self,cur_t=None):
        tl=self.timeline
        tl.delete("all")
        tl.update_idletasks()
        cw=tl.winfo_width(); ch=tl.winfo_height()
        if cw<10: return
        if self.data is None:
            tl.create_text(cw//2,ch//2,text="動画を選択すると解析が始まります",
                           fill=SUBTEXT,font=_tk_font(10)); return
        duration=self.data["duration"]
        if duration<=0: return
        times=self.data["times"]; combined=self.data["combined"]
        n=len(times)

        # 波形
        pts=[]
        stepn=max(1,n//max(1,cw))
        for j in range(0,n,stepn):
            x=int(times[j]/duration*cw)
            y=int(ch-combined[j]*(ch-14)-4)
            pts.extend([x,max(4,y)])
        if len(pts)>=4:
            tl.create_line(pts,fill="#555",width=1)

        # 再生位置
        if cur_t is None:
            cur_t=self._play_cur_time[0] if self._play_running else \
                  (self._scrub_time if self._scrub_time is not None else self._current_frame_time)

        # ピーク縦線 (削除済みは self.peaks に含まれないので自動的に消える)
        badges=self._crop_badges()
        # v24: 分類済フィルタ
        classified_only=(self._show_classified_only.get()
                         if hasattr(self,"_show_classified_only") else False)
        if classified_only:
            path=self.video_path.get()
            _db_path=get_db_path(path)
            _all_labels=load_all_labels(_db_path,os.path.basename(path))
        for i,p in enumerate(self.peaks):
            if classified_only and p["rank"] not in _all_labels:
                continue
            # ラベル保存済みなら frame_time (人手で合わせた位置) を使う
            disp_t=p.get("frame_time") or p["time"]
            x=int(disp_t/duration*cw)
            is_sel=(i==self.peak_idx)
            color=GOLD if is_sel else ACCENT2
            lw=3 if is_sel else 1
            tl.create_line(x,12,x,ch,fill=color,width=lw)
            tl.create_text(x,4,anchor="n",text=str(p["rank"]),fill=color,
                           font=("Helvetica",8,"bold" if is_sel else "normal"))
            if p["rank"] in badges:
                tl.create_text(x,ch-2,anchor="s",text=badges[p["rank"]],
                               fill=GREEN,font=("Helvetica",7,"bold"))

        # 再生位置マーカー
        cx=int(min(max(cur_t,0),duration)/duration*cw)
        tl.create_line(cx,0,cx,ch,fill="#ffd24a",width=2)

    def _on_timeline_click(self,event):
        if self.data is None: return
        duration=self.data["duration"]
        cw=self.timeline.winfo_width()
        if cw<=0 or duration<=0: return
        t=event.x/cw*duration
        if self._play_running:
            # 再生中: その位置へシーク
            self._play_seek_delta += (t-self._play_cur_time[0])
            return
        # 停止中: 近いチェックポイントへスナップ、なければ任意位置をプレビュー
        if self.peaks:
            dists=[abs(p["time"]-t) for p in self.peaks]
            k=int(np.argmin(dists))
            if dists[k]<duration*0.03:
                self.peak_idx=k; self.frame_offset=0
                self.peak_list.selection_clear(0,"end")
                self.peak_list.selection_set(k); self.peak_list.see(k)
                self._update_view(); return
        # 任意位置スクラブ
        self._scrub_to(t)

    def _scrub_to(self,t):
        path=self.video_path.get()
        frame=grab_frame(path,t) if path else None
        if frame is None: return
        self._scrub_time=t; self._current_frame_time=t
        self._display_frame(frame,t)
        self._draw_timeline(t)

    # ══════════════════════════════════════════
    #  ラベル操作
    # ══════════════════════════════════════════
    def _restore_label_for_current(self):
        path=self.video_path.get()
        if not path or not self.peaks: return
        db_path=get_db_path(path)
        existing=load_label(db_path,os.path.basename(path),self._rank())
        if existing:
            # v24: 既存ラベルがあっても評価は常に「普通」をデフォルトに
            # (保存済みの評価は表示するが、次の保存まで変更は普通扱い)
            self._apply_label_ui(existing["shot_type"],existing["spin"],
                                 "normal")
        else:
            # 未ラベル: ショット/スピンは前回を引継ぎ、評価は「普通」にリセット
            self._apply_label_ui(self._last_shot,self._last_spin,"normal")

    def _apply_label_ui(self,shot,spin,rating):
        # ボタンの色を更新 (save不要)
        for k,b in self._shot_btns.items():
            noise=(k=="noise")
            b.config(bg=ACCENT if k==shot else ("#2a0a0a" if noise else DARK2),
                     fg="white" if k==shot else (ACCENT if noise else TEXT))
        for k,b in self._spin_btns.items():
            b.config(bg=ACCENT2 if k==spin else DARK2,fg="white" if k==spin else TEXT)
        rating_bg={"super":GOLD,"nice":GREEN,"normal":ACCENT2,"miss":ACCENT,"unrated":DARK2}
        for k,b in self._rating_btns.items():
            sel=(k==rating)
            self._rating_selected[k]=sel
            b.config(bg=rating_bg.get(k,DARK2) if sel else DARK2,
                     fg="white" if sel else TEXT)

    def _get_current_label(self):
        shot=next((en for en,b in self._shot_btns.items()
                   if b.cget("bg")==ACCENT),"other")
        spin=next((en for en,b in self._spin_btns.items()
                   if b.cget("bg")==ACCENT2),"unknown")
        rating=next((en for en,sel in self._rating_selected.items() if sel),"unrated")
        return shot,spin,rating

    def _select_shot(self,en,auto_save=False):
        self._last_shot=en
        for k,b in self._shot_btns.items():
            noise=(k=="noise")
            b.config(bg=ACCENT if k==en else ("#2a0a0a" if noise else DARK2),
                     fg="white" if k==en else (ACCENT if noise else TEXT))
        if auto_save: self._auto_save()

    def _select_spin(self,en,auto_save=False):
        self._last_spin=en
        for k,b in self._spin_btns.items():
            b.config(bg=ACCENT2 if k==en else DARK2,fg="white" if k==en else TEXT)
        if auto_save: self._auto_save()

    def _select_rating(self,en,auto_save=False):
        self._last_rating=en
        rating_bg={"super":GOLD,"nice":GREEN,"normal":ACCENT2,"miss":ACCENT,"unrated":DARK2}
        for k,b in self._rating_btns.items():
            sel=(k==en)
            self._rating_selected[k]=sel
            b.config(bg=rating_bg.get(k,DARK2) if sel else DARK2,
                     fg="white" if sel else TEXT)
        if auto_save: self._auto_save()

    def _auto_save(self):
        """ラベル変更・コマ送りのたびに自動でDBに保存"""
        path=self.video_path.get()
        if not path or self.peak_idx>=len(self.peaks): return
        shot,spin,rating=self._get_current_label()
        db_path=get_db_path(path); init_db(db_path)
        p=self.peaks[self.peak_idx]
        upsert_label(db_path,os.path.basename(path),
                     p["time"],p["rank"],
                     self._current_frame_time,
                     p.get("thumb",""),shot,spin,rating,self._last_cam)
        # タイムライン位置に反映
        p["frame_time"]=self._current_frame_time
        self._update_shot_list()
        self.peak_list.selection_clear(0,"end")
        self.peak_list.selection_set(self.peak_idx)
        self.peak_list.see(self.peak_idx)  # v24: 選択行を常に表示
        self._draw_timeline()
        try: self._update_registry()
        except Exception: pass

    def _next_peak(self):
        if self.peak_idx<len(self.peaks)-1:
            self.peak_idx+=1; self.frame_offset=0
            self.peak_list.selection_clear(0,"end")
            self.peak_list.selection_set(self.peak_idx)
            self.peak_list.see(self.peak_idx)
            self._update_view()

    def _on_list_select(self,event):
        if getattr(self, "_suppress_list_select", False): return
        sel=self.peak_list.curselection()
        if not sel: return
        list_idx=sel[0]
        # v24: 分類済フィルタで listbox→peaks のマッピングを使用
        if hasattr(self,"_list_to_peak_idx") and self._list_to_peak_idx:
            if list_idx>=len(self._list_to_peak_idx): return
            idx=self._list_to_peak_idx[list_idx]
        else:
            idx=list_idx
        if idx>=len(self.peaks): return
        p=self.peaks[idx]
        target=p.get("frame_time") or p["time"]
        if self._play_running:
            self._stop_play()
        self.peak_idx=idx; self.frame_offset=0
        # DBから保存済みframe_timeを取得
        path=self.video_path.get()
        db_path=get_db_path(path)
        lbl=load_label(db_path,os.path.basename(path),self._rank())
        if lbl and lbl.get("frame_time"):
            sound_delay=self.camera_dist.get()/SOUND_SPEED
            base_time=max(0.0,self.peaks[self.peak_idx]["time"]-sound_delay)
            offset_sec=lbl["frame_time"]-base_time
            self.frame_offset=int(round(offset_sec*self.video_fps))
        else:
            self.frame_offset=0
        self._update_view()
        # v24: 連続写真タブの CP セレクタを同期 + そのタブ表示中なら再描画
        try:
            if hasattr(self,"cs_peak_sel") and self.cs_peak_sel.winfo_exists():
                vals=self.cs_peak_sel["values"]
                if vals and idx<len(vals):
                    self.cs_peak_sel.current(idx)
                    # cur rank label も更新
                    if hasattr(self,"_cs_cur_rank_var") and idx<len(self.peaks):
                        self._cs_cur_rank_var.set(f"#{self.peaks[idx]['rank']}")
                    # 連続写真タブが現在表示されているなら再描画
                    cur_tab=self.tabs.select() if hasattr(self,"tabs") else ""
                    if cur_tab and str(self.tab_contact)==cur_tab:
                        if hasattr(self,"_cs_regen"): self._cs_regen()
        except Exception: pass
        # v25: キーポイント検出タブが表示中ならHP連動更新
        try:
            cur_tab=self.tabs.select() if hasattr(self,"tabs") else ""
            if cur_tab and str(self.tab_yolo)==cur_tab:
                self._update_yolo_dropdowns()
            # v26: Refinerタブが表示中ならHP連動更新
            if cur_tab and str(self.tab_refiner)==cur_tab:
                self._sync_refiner_hp()
        except Exception: pass
        # v59: 検出情報を更新
        try: self._update_detect_info()
        except Exception: pass

    # ══════════════════════════════════════════
    #  インライン再生 (v10) — メイン画像内で再生
    # ══════════════════════════════════════════
    def _toggle_play(self):
        if self._play_running:
            self._stop_play()
        else:
            self._start_play()

    def _toggle_overlay(self):
        self._overlay_on=not self._overlay_on
        self.btn_overlay.config(
            text="字幕 ON" if self._overlay_on else "字幕 OFF",
            bg=GREEN if self._overlay_on else DARK2)

    def _seek(self,delta_sec):
        if self._play_running:
            self._play_seek_delta += delta_sec
        else:
            # 停止中: 現在の表示時刻から相対ジャンプしてスクラブ表示
            base=self._scrub_time if self._scrub_time is not None else self._current_frame_time
            self._scrub_to(max(0.0,base+delta_sec))

    def _start_play(self):
        path=self.video_path.get()
        if not path or self.data is None:
            messagebox.showwarning("再生","動画を解析してから再生してください"); return
        # 開始位置: 現在の表示時刻
        start_t=self._scrub_time if self._scrub_time is not None else self._current_frame_time
        self._play_running=True
        self._play_paused =False
        self._play_seek_delta=0
        self._play_cur_time[0]=start_t
        # 再生中はリストの選択は出さず、通過時のみハイライト
        try:
            # v62: 選択は常に維持（再生中もハイライト）
            pass
        except Exception: pass
        self._play_highlight_idx=-1
        self.btn_play.config(text="■ 停止",bg=ACCENT)
        self._play_thread=threading.Thread(target=self._play_loop,args=(path,start_t),daemon=True)
        self._play_thread.start()

    def _reset_play_buttons(self):
        """v29: 再生終了時に全関連ボタンをリセット"""
        try: self.btn_play.config(text="▶ 再生", bg=GREEN)
        except Exception: pass
        try: self.btn_cplay.config(text="▶ コンパクト再生", bg=ACCENT2)
        except Exception: pass
        # v30: スローボタンもリセット
        try: self.btn_slow.config(text="▶ スロー再生", bg=ACCENT2)
        except Exception: pass

    def _stop_play(self):
        self._play_running=False
        try: self.btn_play.config(text="▶ 再生",bg=GREEN)
        except Exception: pass
        # v24: コンパクト再生・スロー再生ボタンもリセット
        if hasattr(self,"btn_cplay"):
            try: self.btn_cplay.config(text="▶ コンパクト再生",bg=ACCENT2)
            except Exception: pass
        if hasattr(self,"btn_slow"):
            try: self.btn_slow.config(text="▶ スロー",bg=ACCENT2)
            except Exception: pass
        try: self._clear_list_highlight()
        except Exception: pass
        self._play_highlight_idx=-1

    def _clear_list_highlight(self):
        """通過ハイライトをリセット"""
        for i in range(self.peak_list.size()):
            self.peak_list.itemconfig(i,background=DARK2,foreground=TEXT)

    def _set_list_highlight(self,peak_idx):
        """指定ピークインデックスの行だけオレンジ背景に。それ以外はリセット。
        v24: 分類済フィルタ時はリスト→ピーク idx マッピングを使って正しい行を特定"""
        # peak_idx → listbox idx に変換
        list_idx = peak_idx
        if hasattr(self,"_list_to_peak_idx") and self._list_to_peak_idx:
            try:
                list_idx = self._list_to_peak_idx.index(peak_idx)
            except ValueError:
                return  # フィルタで非表示の HP
        if not (0<=list_idx<self.peak_list.size()): return
        if list_idx==self._play_highlight_idx: return
        self._clear_list_highlight()
        self.peak_list.itemconfig(list_idx,background=ACCENT,foreground="white")
        self.peak_list.see(list_idx)
        self._play_highlight_idx=list_idx

    def _play_loop(self,path,start_t,segments=None,start_seg_idx=0,override_fps=None):
        """segments=[(s,e),...] が指定されたら、その区間のみを順に再生 (コンパクト再生)
        v24: start_seg_idx と start_t で任意セグメントの任意位置から開始可能
        v24: override_fps を指定すると表示フレームレートを上書き (スロー再生用)"""
        cap=cv2.VideoCapture(path)
        if not cap.isOpened():
            self._play_running=False; return
        fps  =cap.get(cv2.CAP_PROP_FPS) or 30
        total=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration=self.data["duration"] if self.data else (total/fps if fps>0 else 0)
        # v24: スロー再生の場合はフレーム間隔を延ばす (表示は実際の FPS より低く)
        display_fps = override_fps if override_fps is not None else fps
        frame_ms=1000.0/max(1.0, display_fps)

        # 再生ヘッダ
        seg_idx=start_seg_idx
        if segments:
            # v24: 指定セグメント内の start_t (またはセグメント先頭) から開始
            seg_s,seg_e=segments[seg_idx] if 0<=seg_idx<len(segments) else segments[0]
            init_t=max(seg_s,min(seg_e,start_t)) if start_t else seg_s
            fn=int(init_t*fps)
        else:
            fn=int(start_t*fps)
        fn=max(0,min(total-1,fn))
        cap.set(cv2.CAP_PROP_POS_FRAMES,fn)

        while self._play_running and fn<total:
            # v24: 絶対時刻ジャンプ (CP クリックでの呼出。コンパクト再生でも有効)
            if self._play_seek_target is not None:
                tgt=self._play_seek_target
                self._play_seek_target=None
                fn=max(0,min(total-1,int(tgt*fps)))
                cap.set(cv2.CAP_PROP_POS_FRAMES,fn)
                if segments:
                    # 対応するセグメント (含むもの) を探す。なければ最寄り (target 以下で最大)
                    found=False
                    for si,(s_,e_) in enumerate(segments):
                        if s_<=tgt<=e_+0.05:
                            seg_idx=si; found=True; break
                    if not found:
                        seg_idx=0
                        for si,(s_,_e) in enumerate(segments):
                            if s_<=tgt: seg_idx=si
                continue

            # シーク (通常再生時のみ)
            if self._play_seek_delta!=0 and not segments:
                fn=max(0,min(total-1,fn+int(self._play_seek_delta*fps)))
                self._play_seek_delta=0
                cap.set(cv2.CAP_PROP_POS_FRAMES,fn)

            # セグメント終端チェック → 次のセグメントへスキップ
            if segments:
                cur_t_check=fn/fps
                seg_s,seg_e=segments[seg_idx]
                if cur_t_check>seg_e:
                    seg_idx+=1
                    if seg_idx>=len(segments): break
                    fn=int(segments[seg_idx][0]*fps)
                    fn=max(0,min(total-1,fn))
                    cap.set(cv2.CAP_PROP_POS_FRAMES,fn)
                    continue

            t0=time.time()
            ret,frame=cap.read()
            if not ret: break
            cur_t=fn/fps
            self._play_cur_time[0]=cur_t
            self._current_frame_time=cur_t

            # v24: 手ぶれ補正 (shaky HP のフレームにだけ適用)
            if segments and hasattr(self,"_shake_scores"):
                near_peak=min(self.peaks,
                              key=lambda p: abs((p.get("frame_time") or p["time"])-cur_t),
                              default=None)
                if near_peak and self._is_shaky(near_peak["rank"]):
                    hp_t=near_peak.get("frame_time") or near_peak["time"]
                    # キャッシュにあればそのまま使う (cap を移動させない)
                    if (self._stab_ref_rank==near_peak["rank"]
                            and fn in self._stab_cache):
                        frame=self._apply_stabilization(frame,fn,self._stab_cache)
                    elif self._stab_ref_rank!=near_peak["rank"]:
                        # 新しい HP → オフセットを事前計算 (cap を一時的に使う)
                        saved_fn=fn+1  # read() した後なので +1
                        stab=self._compute_stab_offsets(cap,hp_t,fps,
                                pre=3.0,post=3.0,rank=near_peak["rank"])
                        cap.set(cv2.CAP_PROP_POS_FRAMES,saved_fn)
                        frame=self._apply_stabilization(frame,fn,stab)

            rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
            pil_img=self._crop_pil_at(Image.fromarray(rgb),cur_t)
            self.img_canvas.update_idletasks()
            cw=max(self.img_canvas.winfo_width(),320)
            ch=max(self.img_canvas.winfo_height(),200)
            # v18: resize でアスペクト比保持しつつ拡大も許可
            iw_,ih_=pil_img.size
            if iw_>0 and ih_>0:
                sc=min(cw/iw_, ch/ih_)
                pil_img=pil_img.resize((max(1,int(iw_*sc)),max(1,int(ih_*sc))),Image.NEAREST)
            photo=ImageTk.PhotoImage(pil_img)

            seg_info=None
            if segments:
                seg_info=f"  [{seg_idx+1}/{len(segments)}]"

            def _render(ph=photo,t=cur_t,cw=cw,ch=ch,seg_info=seg_info):
                if not self._play_running: return
                self.img_canvas.delete("all")
                self.img_canvas.create_image(cw//2,ch//2,anchor="center",image=ph)
                self._draw_play_overlay(t,cw,ch)
                if self._active_crop_rect(t) is not None:
                    self.img_canvas.create_rectangle(cw-86,4,cw-4,24,fill="#1d9e75",outline="")
                    self.img_canvas.create_text(cw-45,14,anchor="center",text="✂ クロップ中",
                        fill="white",font=("Helvetica",9))
                ts=f"{int(t//60):02d}:{t%60:05.2f}"
                ds=f"{int(duration//60):02d}:{duration%60:05.2f}"
                extra=seg_info or ""
                try: self.time_lbl.config(text=f"{ts} / {ds}{extra}")
                except Exception: pass
                near=-1
                for j,p in enumerate(self.peaks):
                    pt=p.get("frame_time") or p["time"]
                    if abs(t-pt)<=1.0: near=j; break
                if near>=0:
                    self._set_list_highlight(near)
                elif self._play_highlight_idx>=0:
                    self._clear_list_highlight()
                    self._play_highlight_idx=-1
                self._img_ref=ph
            self.after(0,_render)

            if fn%5==0:
                self.after(0,lambda t=cur_t: self._draw_timeline(t))

            fn+=1
            elapsed=time.time()-t0
            time.sleep(max(0,frame_ms/1000.0-elapsed))

        cap.release()
        self._play_running=False
        self.after(0,self._reset_play_buttons)
        if hasattr(self,"btn_cplay"):
            self.after(0,lambda: self.btn_cplay.config(text="▶ コンパクト再生",bg=ACCENT2))
        self.after(0,lambda: self._scrub_to(self._play_cur_time[0]))

    # ══════════════════════════════════════════
    #  コンパクト再生 / コンパクト出力 (v12)
    # ══════════════════════════════════════════
    def _compute_compact_segments(self,pre=None,post=None):
        """各CPの (t-pre, t+post) を計算、重複は結合。
           v18: pre/post 未指定なら UI のドロップダウン値を使用
           v24: 分類済フィルタが ON なら未分類 HP はスキップ"""
        if pre is None:
            try: pre=float(self.cplay_pre.get())
            except Exception: pre=3.0
        if post is None:
            try: post=float(self.cplay_post.get())
            except Exception: post=2.0
        if not self.peaks: return []
        # v24: 分類済フィルタ
        classified_only=(self._show_classified_only.get()
                         if hasattr(self,"_show_classified_only") else False)
        if classified_only:
            path=self.video_path.get()
            db_path=get_db_path(path)
            all_labels=load_all_labels(db_path,os.path.basename(path))
        segs=[]
        for p in self.peaks:
            if classified_only:
                if p["rank"] not in all_labels: continue
            t=p.get("frame_time") or p["time"]
            segs.append((max(0.0,t-pre),t+post))
        if not segs: return []
        segs.sort()
        merged=[segs[0]]
        for s,e in segs[1:]:
            if s<=merged[-1][1]:
                merged[-1]=(merged[-1][0],max(merged[-1][1],e))
            else:
                merged.append((s,e))
        return merged

    def _toggle_slow_play(self):
        """v24: スロー再生のトグル (停止中→開始、再生中→停止)"""
        if self._play_running:
            self._stop_play()
            return
        self._start_slow_play()

    def _start_slow_play(self):
        """v24: 現在HPのみをスロー再生 (コンパクト再生と同じ前後範囲、速度 1/N)"""
        path=self.video_path.get()
        if not path or self.data is None:
            messagebox.showwarning("スロー再生","動画を解析してから実行してください"); return
        if not self.peaks:
            messagebox.showinfo("スロー再生","ヒットポイントがありません"); return
        if self._play_running: self._stop_play()
        # 現在HPの前後範囲だけのセグメント
        p=self.peaks[self.peak_idx]
        hit_t=p.get("frame_time") or p["time"]
        try: pre=float(self.cplay_pre.get())
        except Exception: pre=1.5
        try: post=float(self.cplay_post.get())
        except Exception: post=1.5
        seg_s=max(0.0,hit_t-pre)
        seg_e=hit_t+post
        segs=[(seg_s,seg_e)]
        # スロー倍率から fps を計算
        try: mult=float(self.slow_speed.get().rstrip("x"))
        except Exception: mult=2.0
        real_fps=self.video_fps if self.video_fps>0 else 30.0
        slow_fps=max(1.0, real_fps/mult)
        self._play_running=True
        self._play_paused=False
        self._play_seek_delta=0
        self._play_cur_time[0]=seg_s
        try:
            self.peak_list.selection_clear(0,"end")
        except Exception: pass
        self.btn_play.config(text="■ 停止",bg=ACCENT)
        if hasattr(self,"btn_cplay"):
            self.btn_cplay.config(text="■ 停止",bg=ACCENT)
        if hasattr(self,"btn_slow"):
            self.btn_slow.config(text="■ 停止",bg=ACCENT)
        self._play_thread=threading.Thread(
            target=self._play_loop,
            args=(path,seg_s),
            kwargs={"segments":segs,"start_seg_idx":0,"override_fps":slow_fps},
            daemon=True)
        self._play_thread.start()

    def _start_compact_play(self):
        path=self.video_path.get()
        if not path or self.data is None:
            messagebox.showwarning("コンパクト再生","動画を解析してから実行してください"); return
        if not self.peaks:
            messagebox.showinfo("コンパクト再生","ヒットポイントがありません"); return
        if self._play_running: self._stop_play()
        segs=self._compute_compact_segments()
        if not segs: return
        # v27: 常に最初のHPのセグメント先頭 (HP数秒前) から再生開始
        start_time=segs[0][0]
        start_seg_idx=0
        self._play_running=True
        self._play_paused=False
        self._play_seek_delta=0
        self._play_cur_time[0]=start_time
        try:
            # v62: 選択は常に維持（再生中もハイライト）
            pass
        except Exception: pass
        self._play_highlight_idx=-1
        self.btn_play.config(text="■ 停止",bg=ACCENT)
        if hasattr(self,"btn_cplay"):
            self.btn_cplay.config(text="■ 停止",bg=ACCENT)
        # v24: 開始セグメントのインデックスをワーカーに渡す
        self._play_thread=threading.Thread(target=self._play_loop,
                                           args=(path,start_time),
                                           kwargs={"segments":segs,
                                                   "start_seg_idx":start_seg_idx},
                                           daemon=True)
        self._play_thread.start()

    def _toggle_compact_play(self):
        if self._play_running:
            self._stop_play()
        else:
            self._start_compact_play()

    def _compact_export(self):
        path=self.video_path.get()
        if not path or self.data is None:
            messagebox.showwarning("コンパクト出力","動画を解析してから実行してください"); return
        if not self.peaks:
            messagebox.showinfo("コンパクト出力","ヒットポイントがありません"); return
        segs=self._compute_compact_segments()
        if not segs: return
        # 出力先パス
        base,ext=os.path.splitext(os.path.basename(path))
        out_dir=os.path.dirname(path)
        out_path=os.path.join(out_dir,f"{base}_compact.mp4")
        # バックグラウンドで出力
        threading.Thread(target=self._compact_export_worker,
                         args=(path,out_path,segs),daemon=True).start()

    def _find_jp_font(self,size=28):
        """日本語が出るフォントを探す。なければデフォルト"""
        from PIL import ImageFont
        candidates=[
            r"C:\Windows\Fonts\meiryo.ttc",
            r"C:\Windows\Fonts\YuGothB.ttc",
            r"C:\Windows\Fonts\YuGothM.ttc",
            r"C:\Windows\Fonts\msgothic.ttc",
            "/System/Library/Fonts/HiraginoSans-W6.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        ]
        for fp in candidates:
            try: return ImageFont.truetype(fp,size)
            except Exception: pass
        return ImageFont.load_default()

    def _compact_export_worker(self,path,out_path,segs):
        from PIL import Image as PILImage, ImageDraw, ImageFont
        try:
            cap=cv2.VideoCapture(path)
            if not cap.isOpened():
                self.after(0,lambda: messagebox.showerror("コンパクト出力","動画を開けません"))
                return
            fps=cap.get(cv2.CAP_PROP_FPS) or 30
            in_w=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            in_h=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # 出力解像度を決める: クロップ後の最大幅 × 高さ (アスペクト保持)
            # 各CPのクロップを試算
            out_w,out_h=in_w,in_h
            if self._crops:
                # クロップ後寸法の最大を採用
                max_w=max_h=0
                for c in self._crops:
                    x1,y1,x2,y2=c["rect"]
                    cw=int(abs(x2-x1)*in_w); ch=int(abs(y2-y1)*in_h)
                    if cw>max_w: max_w=cw
                    if ch>max_h: max_h=ch
                if max_w>0 and max_h>0:
                    out_w,out_h=max_w,max_h
            # 偶数化 (一部コーデックの制約)
            out_w-=out_w%2; out_h-=out_h%2

            fourcc=cv2.VideoWriter_fourcc(*'mp4v')
            writer=cv2.VideoWriter(out_path,fourcc,fps,(out_w,out_h))
            if not writer.isOpened():
                cap.release()
                self.after(0,lambda: messagebox.showerror("コンパクト出力",
                    "出力ファイルを作成できません (コーデック対応を確認してください)"))
                return

            # 必要な総フレーム数
            total_frames=sum(int((e-s)*fps) for s,e in segs)
            written=0
            font_main=self._find_jp_font(int(out_h*0.04))
            font_flash=self._find_jp_font(int(out_h*0.06))

            db_path=get_db_path(path); vf=os.path.basename(path)

            self.after(0,lambda: self.status_var.set(f"コンパクト出力開始… {len(segs)}区間"))

            for s,e in segs:
                fn_start=int(s*fps); fn_end=int(e*fps)
                cap.set(cv2.CAP_PROP_POS_FRAMES,fn_start)
                for fn in range(fn_start,fn_end+1):
                    ok,frame=cap.read()
                    if not ok: break
                    t=fn/fps
                    # クロップ適用
                    cropped=self._apply_crop_to_frame(frame,time_sec=t)
                    # 出力サイズに合わせて (アスペクト保持してレターボックス)
                    ih,iw=cropped.shape[:2]
                    scale=min(out_w/iw,out_h/ih)
                    nw,nh=int(iw*scale),int(ih*scale)
                    resized=cv2.resize(cropped,(nw,nh),interpolation=cv2.INTER_AREA)
                    canvas=np.zeros((out_h,out_w,3),dtype=np.uint8)
                    ox,oy=(out_w-nw)//2,(out_h-nh)//2
                    canvas[oy:oy+nh,ox:ox+nw]=resized

                    # 字幕: CP情報 (該当する場合)
                    hit_cp=None
                    for p in self.peaks:
                        pt=p.get("frame_time") or p["time"]
                        if abs(t-pt)<=1.0:
                            hit_cp=p; break
                    if hit_cp is not None:
                        lbl=load_label(db_path,vf,hit_cp["rank"])
                        if lbl:
                            shot_ja=next((ja for ja,en in SHOT_TYPES if en==lbl["shot_type"]),"")
                            spin_ja=next((ja for ja,en in SPINS    if en==lbl.get("spin","")),"")
                            rating_ja=next((ja for ja,en in RATINGS if en==lbl.get("rating","")),"")
                            txt=f"#{hit_cp['rank']} {shot_ja} / {spin_ja} / {rating_ja}"
                            disp_t=hit_cp.get("frame_time") or hit_cp["time"]
                            near_exact=abs(t-disp_t)<=max(1.5/fps,0.04)
                            # PIL で文字描画
                            rgb=cv2.cvtColor(canvas,cv2.COLOR_BGR2RGB)
                            pil=PILImage.fromarray(rgb)
                            draw=ImageDraw.Draw(pil)
                            font=font_flash if near_exact else font_main
                            try:
                                bb=draw.textbbox((0,0),txt,font=font)
                                tw=bb[2]-bb[0]; th=bb[3]-bb[1]
                            except Exception:
                                tw=len(txt)*int(out_h*0.04); th=int(out_h*0.05)
                            x=(out_w-tw)//2; y=out_h-th-20
                            if near_exact:
                                # 白背景・赤文字 + 白枠
                                draw.rectangle([0,0,out_w-1,out_h-1],outline=(255,255,255),width=6)
                                draw.rectangle([x-14,y-10,x+tw+14,y+th+10],fill=(255,255,255))
                                draw.text((x,y),txt,fill=(180,20,20),font=font)
                            else:
                                draw.rectangle([x-10,y-8,x+tw+10,y+th+8],fill=(0,0,0))
                                draw.text((x,y),txt,fill=(255,210,40),font=font)
                            canvas=cv2.cvtColor(np.array(pil),cv2.COLOR_RGB2BGR)

                    writer.write(canvas)
                    written+=1
                    if written%20==0:
                        pct=int(written*100/max(1,total_frames))
                        self.after(0,lambda pct=pct,w=written,t=total_frames:
                                   self.status_var.set(f"コンパクト出力 {pct}%  ({w}/{t})"))

            cap.release(); writer.release()
            self.after(0,lambda: self.status_var.set(f"出力完了: {os.path.basename(out_path)}"))
            self.after(0,lambda: messagebox.showinfo("コンパクト出力",
                f"出力完了:\n{out_path}\n\nフレーム数: {written}\n区間数: {len(segs)}"))
        except Exception as ex:
            err=str(ex)
            self.after(0,lambda err=err: messagebox.showerror("コンパクト出力",
                f"出力中にエラー: {err}"))

    # ══════════════════════════════════════════
    #  チェックポイント削除 (v10) — 完全削除
    # ══════════════════════════════════════════
    def _on_list_right_click(self,event):
        idx=self.peak_list.nearest(event.y)
        if 0<=idx<len(self.peaks):
            self.peak_list.selection_clear(0,"end")
            self.peak_list.selection_set(idx)
            self.peak_list.see(idx)  # v24
            self.peak_idx=idx
            self._delete_current_checkpoint()

    def _delete_current_checkpoint(self):
        if not self.peaks or self.peak_idx>=len(self.peaks): return
        p=self.peaks[self.peak_idx]
        rank=p["rank"]; t=p["time"]
        path=self.video_path.get(); vf=os.path.basename(path)
        db_path=get_db_path(path); init_db(db_path)
        add_deleted_peak(db_path,vf,t)
        delete_label(db_path,vf,rank)
        delete_crop(db_path,vf,rank)
        self._deleted_peaks=load_deleted_peaks(db_path,vf)
        self._crops=load_crops(db_path,vf)
        del self.peaks[self.peak_idx]
        if self.peak_idx>=len(self.peaks):
            self.peak_idx=max(0,len(self.peaks)-1)
        self.frame_offset=0
        self._update_crop_ui()
        self._update_shot_list()
        if self.peaks:
            self._sync_list_selection()
        self._update_view()
        self.status_var.set(f"#{rank} を削除しました")
    # ══════════════════════════════════════════
    #  クロップ機能 (v10) — 時刻に紐づく複数クロップ
    # ══════════════════════════════════════════
    def _toggle_crop_mode(self):
        if not self.peaks or self.peak_idx>=len(self.peaks):
            messagebox.showinfo("クロップ","クロップは選択中のヒットポイントに紐づきます。\n"
                                "先にヒットポイントを選んでください。"); return
        if self._play_running: self._stop_play()
        self._crop_mode=not self._crop_mode
        if self._crop_mode:
            self.btn_crop.config(text="✂  ドラッグで範囲指定",bg=ACCENT,fg="white")
            self.img_canvas.config(cursor="crosshair")
            rank=self._rank()
            self.lbl_crop_status.config(
                text=f"  #{rank} 用のクロップを全体画像からドラッグで指定",fg=GOLD)
            self._update_view()   # フル画像を表示 (crop_mode中はクロップ非適用)
        else:
            self.btn_crop.config(text="✂  クロップ追加",bg=DARK2,fg=TEXT)
            self.img_canvas.config(cursor="")
            if self._crop_rect_id:
                self.img_canvas.delete(self._crop_rect_id); self._crop_rect_id=None
            self._crop_drag_start=None; self._crop_drag_end=None
            self._update_crop_ui()
            self._update_view()

    def _crop_mouse_down(self,event):
        if not self._crop_mode: return
        self._crop_drag_start=(event.x,event.y)
        self._crop_drag_end  =(event.x,event.y)
        if self._crop_rect_id:
            self.img_canvas.delete(self._crop_rect_id); self._crop_rect_id=None

    def _crop_mouse_move(self,event):
        if not self._crop_mode or self._crop_drag_start is None: return
        self._crop_drag_end=(event.x,event.y)
        if self._crop_rect_id:
            self.img_canvas.delete(self._crop_rect_id)
        x1,y1=self._crop_drag_start; x2,y2=self._crop_drag_end
        self._crop_rect_id=self.img_canvas.create_rectangle(
            x1,y1,x2,y2, outline=ACCENT, width=2, dash=(6,3))
        # v18: 画像表示サイズ基準で % を計算 (キャンバス基準だと小動画でズレる)
        cw=self.img_canvas.winfo_width(); ch=self.img_canvas.winfo_height()
        vw,vh=self._video_wh
        sc=min(cw/vw, ch/vh) if vw>0 and vh>0 else 1.0
        dw=max(vw*sc,1); dh=max(vh*sc,1)
        pw=abs(x2-x1)/dw*100; ph=abs(y2-y1)/dh*100
        self.lbl_crop_status.config(text=f"  {pw:.0f}% × {ph:.0f}%  ← 離して確定",fg=GOLD)

    def _crop_mouse_up(self,event):
        if not self._crop_mode or self._crop_drag_start is None: return
        self._crop_drag_end=(event.x,event.y)
        x1c,y1c=self._crop_drag_start; x2c,y2c=self._crop_drag_end
        if abs(x2c-x1c)<20 or abs(y2c-y1c)<20:
            self.lbl_crop_status.config(text="範囲が小さすぎます。もう一度ドラッグ",fg=ACCENT)
            return

        # crop_mode中はフル画像を表示しているので、フルフレーム基準で比率を計算
        cw=self.img_canvas.winfo_width(); ch=self.img_canvas.winfo_height()
        vw,vh=self._video_wh
        scale=min(cw/vw, ch/vh)
        disp_w=int(vw*scale); disp_h=int(vh*scale)
        off_x=(cw-disp_w)//2; off_y=(ch-disp_h)//2
        ix1=(x1c-off_x)/disp_w; iy1=(y1c-off_y)/disp_h
        ix2=(x2c-off_x)/disp_w; iy2=(y2c-off_y)/disp_h
        ix1=max(0.0,min(1.0,ix1)); iy1=max(0.0,min(1.0,iy1))
        ix2=max(0.0,min(1.0,ix2)); iy2=max(0.0,min(1.0,iy2))
        ix1,ix2=min(ix1,ix2),max(ix1,ix2)
        iy1,iy2=min(iy1,iy2),max(iy1,iy2)
        rect=(ix1,iy1,ix2,iy2)

        # v24: 適用範囲モードに応じて1つ以上のCPにクロップを保存
        path=self.video_path.get(); vf=os.path.basename(path)
        db_path=get_db_path(path); init_db(db_path)

        mode=self._crop_apply_mode.get() if hasattr(self,"_crop_apply_mode") else "個別"
        existing_ranks={c["rank"] for c in self._crops}
        targets=[]  # 適用先 rank のリスト
        if mode=="未実施全て":
            # 現CP + クロップを持たないすべてのCP
            cur_rank=self.peaks[self.peak_idx]["rank"]
            for p in self.peaks:
                r=p["rank"]
                if r==cur_rank or r not in existing_ranks:
                    targets.append(p)
        else:  # 個別
            targets=[self.peaks[self.peak_idx]]

        for p in targets:
            # anchor_time は CP の frame_time を保存 (互換性維持、参照は rank ベース)
            anchor_t=float(p.get("frame_time") or p["time"])
            add_crop(db_path,vf,p["rank"],anchor_t,rect)
        self._crops=load_crops(db_path,vf)

        self._crop_mode=False
        self.btn_crop.config(text="✂  クロップ追加",bg=DARK2,fg=TEXT)
        self.img_canvas.config(cursor="")
        if self._crop_rect_id:
            self.img_canvas.delete(self._crop_rect_id); self._crop_rect_id=None

        # ステータスメッセージで何件適用したか表示
        n=len(targets)
        if mode=="未実施全て" and n>1:
            self.lbl_crop_status.config(text=f"クロップを {n} CP に適用",fg=GREEN)

        self._update_crop_ui()
        self._update_shot_list()
        self._sync_list_selection()
        self._update_view()

    def _delete_current_crop(self):
        """選択中チェックポイントに紐づくクロップを削除"""
        if not self.peaks or self.peak_idx>=len(self.peaks): return
        rank=self._rank()
        if not any(c["rank"]==rank for c in self._crops):
            self.status_var.set("このヒットポイントにクロップはありません"); return
        path=self.video_path.get(); vf=os.path.basename(path)
        db_path=get_db_path(path)
        delete_crop(db_path,vf,rank)
        self._crops=load_crops(db_path,vf)
        self._update_crop_ui()
        self._update_shot_list()
        self._sync_list_selection()
        # 解除直後は一旦オリジナル表示
        self._force_uncropped=True
        self._update_view()
        self._force_uncropped=False

    def _crop_clear_all(self):
        if not self._crops: return
        path=self.video_path.get(); vf=os.path.basename(path)
        db_path=get_db_path(path)
        clear_crops(db_path,vf)
        self._crops=[]
        self._crop_mode=False
        self.btn_crop.config(text="✂  クロップ追加",bg=DARK2,fg=TEXT)
        self.img_canvas.config(cursor="")
        self._update_crop_ui()
        self._update_shot_list()
        self._force_uncropped=True
        self._update_view()
        self._force_uncropped=False

    def _update_crop_ui(self):
        n=len(self._crops)
        has_any=n>0
        if has_any:
            self.lbl_crop_status.config(text=f"✂ クロップ {n}件",fg=GREEN)
            self.btn_crop_clear.config(state="normal")
        else:
            self.lbl_crop_status.config(text="",fg=GREEN)
            self.btn_crop_clear.config(state="disabled")

    def _apply_crop_to_frame(self,frame,time_sec=0.0,crops=None):
        """numpy配列フレームに time_sec のクロップを適用して返す"""
        rect=self._active_crop_rect(time_sec,crops=crops)
        if rect is None: return frame
        h,w=frame.shape[:2]
        x1r,y1r,x2r,y2r=rect
        cx1=int(min(x1r,x2r)*w); cy1=int(min(y1r,y2r)*h)
        cx2=int(max(x1r,x2r)*w); cy2=int(max(y1r,y2r)*h)
        cx1=max(0,cx1); cy1=max(0,cy1); cx2=min(w,cx2); cy2=min(h,cy2)
        if cx2>cx1 and cy2>cy1:
            return frame[cy1:cy2,cx1:cx2]
        return frame

    def _load_crops_for_video(self,video_path):
        """別動画(比較モード用)のクロップを読み込む"""
        db=get_db_path(video_path)
        return load_crops(db,os.path.basename(video_path))

    # ══════════════════════════════════════════
    #  タブ切替時のハンドラ
    # ══════════════════════════════════════════
    def _on_tab_changed(self,event=None):
        self._refresh_active_tab()

    def _refresh_active_tab(self):
        try: idx=self.tabs.index(self.tabs.select())
        except Exception: return
        if idx==1:
            if not self.peaks: return
            self._update_cs_dropdowns()
            if hasattr(self,"_cs_regen"): self._cs_regen()
        elif idx==2:
            if not self.peaks: return
            self._update_c1_dropdowns()
            if hasattr(self,"_c1_regen"): self._c1_regen()
        elif idx==3:
            # v18: クロス比較を統合したので同タイミング比較は idx 3 に繰上
            if not self.peaks: return
            self._update_c2_dropdowns()
            if hasattr(self,"_c2_regen"): self._c2_regen()
        elif idx==4:
            # v46: Refiner
            self._activate_refiner_tab()
        elif idx==5:
            if self.refiner:
                try: self.refiner._3d_render_frame(self.refiner._mp3d_cur_idx)
                except Exception: pass
        elif idx==6:
            # v62: MP-YOLO比較タブ
            try: self._refresh_compare_tab()
            except Exception: pass
        elif idx==7:
            self._refresh_history_tab()

    def _update_cs_dropdowns(self):
        if not hasattr(self,"cs_peak_sel"): return
        vals=[f"#{p['rank']}" for p in self.peaks]
        self.cs_peak_sel["values"]=vals
        if vals: self.cs_peak_sel.current(min(self.peak_idx,len(vals)-1))

    def _update_c1_dropdowns(self):
        if not hasattr(self,"c1_peak_a"): return
        # 動画パスが空なら main の動画と同期
        cur=self.video_path.get()
        if hasattr(self,"c1_path_a") and not self.c1_path_a.get():
            self.c1_path_a.set(cur)
        if hasattr(self,"c1_path_b") and not self.c1_path_b.get():
            self.c1_path_b.set(cur)
        vals=[f"#{p['rank']}" for p in self.peaks]
        self.c1_peak_a["values"]=vals
        if vals: self.c1_peak_a.current(min(self.peak_idx,len(vals)-1))
        # peak_b: 同じ動画のときは self.peaks、別動画はラベルから
        pb=self.c1_path_b.get() if hasattr(self,"c1_path_b") else ""
        if pb and pb!=self.video_path.get() and os.path.exists(pb):
            lbs=load_all_labels(get_db_path(pb),os.path.basename(pb))
            ranks=sorted(lbs.keys()) if lbs else []
            self.c1_peak_b["values"]=[f"#{r}" for r in ranks] if ranks else [""]
            if ranks: self.c1_peak_b.current(0)
            else: self.c1_peak_b_var.set("")
        else:
            self.c1_peak_b["values"]=vals
            if vals: self.c1_peak_b.current(min(self.peak_idx+1,len(vals)-1))

    def _update_c2_dropdowns(self):
        pass   # mode2 はピーク数に依存しない (filter のみ)

    # ══════════════════════════════════════════
    #  連続写真タブ (v10)
    # ══════════════════════════════════════════
    def _build_tab_contact(self,parent):
        ctrl=tk.Frame(parent,bg=PANEL2); ctrl.pack(fill="x",pady=4,padx=8)

        # v24: チェックポイント選択をサムネピッカーボタンに変更
        tk.Label(ctrl,text="ヒットポイント:",bg=PANEL2,fg=TEXT,font=_tk_font(9)).pack(side="left",padx=(6,2))
        self._cs_cur_rank_var=tk.StringVar(value="(未選択)")
        tk.Label(ctrl,textvariable=self._cs_cur_rank_var,bg=PANEL2,fg=GOLD,
                 font=_tk_font(9,bold=True),width=6).pack(side="left")
        tk.Button(ctrl,text="CP選択",bg=ACCENT,fg="white",relief="flat",
                  font=_tk_font(8,bold=True),cursor="hand2",
                  command=lambda: self._cs_pick_cp()
                  ).pack(side="left",padx=(2,12),ipady=2)
        # 非表示の Combobox (内部互換用)
        self.cs_peak_sel=ttk.Combobox(ctrl,width=4,state="readonly",font=_tk_font(9))

        # 開始/終了 (個別スライダー)
        tk.Label(ctrl,text="開始:",bg=PANEL2,fg=TEXT,font=_tk_font(9)).pack(side="left",padx=(0,2))
        self.cs_start=tk.DoubleVar(value=-1.0)
        self.cs_start_scale=tk.Scale(ctrl,variable=self.cs_start,from_=-3.0,to=0.0,
            orient="horizontal",resolution=0.1,bg=PANEL2,fg=TEXT,troughcolor=DARK2,
            highlightbackground=PANEL2,relief="flat",length=100,sliderlength=12)
        self.cs_start_scale.pack(side="left")
        tk.Label(ctrl,textvariable=self.cs_start,bg=PANEL2,fg=ACCENT,
                 font=("Courier",9),width=5).pack(side="left",padx=(0,8))

        tk.Label(ctrl,text="終了:",bg=PANEL2,fg=TEXT,font=_tk_font(9)).pack(side="left",padx=(0,2))
        self.cs_end=tk.DoubleVar(value=1.0)
        self.cs_end_scale=tk.Scale(ctrl,variable=self.cs_end,from_=0.0,to=3.0,
            orient="horizontal",resolution=0.1,bg=PANEL2,fg=TEXT,troughcolor=DARK2,
            highlightbackground=PANEL2,relief="flat",length=100,sliderlength=12)
        self.cs_end_scale.pack(side="left")
        tk.Label(ctrl,textvariable=self.cs_end,bg=PANEL2,fg=ACCENT,
                 font=("Courier",9),width=5).pack(side="left",padx=(0,12))

        # 間隔
        tk.Label(ctrl,text="間隔(秒):",bg=PANEL2,fg=TEXT,font=_tk_font(9)).pack(side="left",padx=(0,2))
        self.cs_interval=tk.DoubleVar(value=0.1)
        tk.Scale(ctrl,variable=self.cs_interval,from_=0.05,to=0.5,orient="horizontal",
                 resolution=0.05,bg=PANEL2,fg=TEXT,troughcolor=DARK2,
                 highlightbackground=PANEL2,relief="flat",length=100,sliderlength=12
                 ).pack(side="left")
        tk.Label(ctrl,textvariable=self.cs_interval,bg=PANEL2,fg=ACCENT,
                 font=("Courier",9),width=4).pack(side="left",padx=(0,12))

        # 倍率 1.0〜4.0 / 0.1 (v18: 4倍まで拡大)
        tk.Label(ctrl,text="表示倍率:",bg=PANEL2,fg=TEXT,font=_tk_font(9)).pack(side="left",padx=(0,2))
        self.cs_scale=ttk.Combobox(ctrl,width=5,state="readonly",font=_tk_font(9),
            values=[f"{x/10:.1f}x" for x in range(10,41)])
        self.cs_scale.current(0)
        self.cs_scale.pack(side="left",padx=(0,12))

        self.cs_prog=tk.StringVar(value="動画を読み込むと自動描画します")
        tk.Label(ctrl,textvariable=self.cs_prog,bg=PANEL2,fg=SUBTEXT,font=_tk_font(9)
                 ).pack(side="left",padx=8)
        btn_gen=tk.Button(ctrl,text="▶ 再描画",bg=ACCENT,fg="white",relief="flat",
                          font=_tk_font(10,bold=True),cursor="hand2")
        btn_gen.pack(side="left",padx=4,ipady=3)

        # スクロール領域
        outer=tk.Frame(parent,bg=BG); outer.pack(fill="both",expand=True)
        canvas_scroll=tk.Canvas(outer,bg=BG,highlightthickness=0)
        vsb=tk.Scrollbar(outer,orient="vertical",command=canvas_scroll.yview)
        canvas_scroll.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right",fill="y")
        canvas_scroll.pack(side="left",fill="both",expand=True)
        cs_grid=tk.Frame(canvas_scroll,bg=BG)
        grid_win=canvas_scroll.create_window((0,0),window=cs_grid,anchor="nw")
        cs_grid.bind("<Configure>",lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all")))
        canvas_scroll.bind("<Configure>",lambda e: canvas_scroll.itemconfig(grid_win,width=e.width))
        self._cs_photo_refs=[]

        def _on_interval_changed(*_):
            iv=self.cs_interval.get()
            if iv<=0: return
            # start/end の resolution を interval に合わせて、値を倍数にスナップ
            try:
                self.cs_start_scale.config(resolution=iv,from_=-max(iv*30,3.0),to=0.0)
                self.cs_end_scale  .config(resolution=iv,from_=0.0,to=max(iv*30,3.0))
            except Exception: pass
            for v in (self.cs_start,self.cs_end):
                cur=v.get()
                sn=round(cur/iv)*iv
                if abs(sn-cur)>1e-6: v.set(round(sn,3))
        self.cs_interval.trace_add("write",_on_interval_changed)
        _on_interval_changed()

        def _generate():
            # v22: 世代チェック
            my_gen=self._gen
            def _alive():
                try:
                    return (my_gen==self._gen and cs_grid.winfo_exists())
                except Exception: return False
            if not _alive(): return
            if not self.peaks: 
                if _alive(): self.cs_prog.set("動画を読み込んでください")
                return
            interval=self.cs_interval.get()
            start=self.cs_start.get(); end=self.cs_end.get()
            if end-start<interval/2:
                self.cs_prog.set("開始 < 終了 で指定してください"); return
            pidx=self.cs_peak_sel.current()
            if pidx<0 or pidx>=len(self.peaks):
                self.cs_prog.set("ヒットポイントを選択してください"); return
            try: scale=float(self.cs_scale.get().rstrip("x"))
            except Exception: scale=1.0

            rank_g=self.peaks[pidx]["rank"]
            path=self.video_path.get()
            db_path_g=get_db_path(path)
            lbl_g=load_label(db_path_g,os.path.basename(path),rank_g)
            if lbl_g and lbl_g.get("frame_time") and lbl_g["frame_time"]>0:
                hit_t=lbl_g["frame_time"]
            else:
                sd=self.camera_dist.get()/SOUND_SPEED
                hit_t=max(0.0,self.peaks[pidx]["time"]-sd)

            # 開始から終了まで interval ずつ
            n=int(round((end-start)/interval))
            offsets=[round(start+k*interval,4) for k in range(n+1)]
            frame_times=[max(0.0,round(hit_t+o,4)) for o in offsets]

            self.cs_prog.set(f"フレーム抽出中… 0/{len(frame_times)}")
            self.after(0, lambda: None)  # v24: スレッド安全

            cap=cv2.VideoCapture(path)
            fps_v=cap.get(cv2.CAP_PROP_FPS) or 30
            frames=[]
            for i,ft in enumerate(frame_times):
                cap.set(cv2.CAP_PROP_POS_FRAMES,int(fps_v*ft))
                ret,frame=cap.read()
                if ret:
                    # v25: 現在HPのrankのクロップを全フレームに適用
                    crop_rect=self._crop_rect_for_rank(rank_g)
                    if crop_rect is not None:
                        fh_,fw_=frame.shape[:2]
                        x1r,y1r,x2r,y2r=crop_rect
                        cx1=max(0,int(min(x1r,x2r)*fw_))
                        cy1=max(0,int(min(y1r,y2r)*fh_))
                        cx2=min(fw_,int(max(x1r,x2r)*fw_))
                        cy2=min(fh_,int(max(y1r,y2r)*fh_))
                        if cx2>cx1 and cy2>cy1:
                            frame=frame[cy1:cy2,cx1:cx2]
                    frames.append((ft,frame,offsets[i]))
                if i%5==0:
                    self.cs_prog.set(f"フレーム抽出中… {i+1}/{len(frame_times)}")
                    self.after(0, lambda: None)  # v24: スレッド安全
            cap.release()

            if not _alive(): return
            try:
                for w in cs_grid.winfo_children(): w.destroy()
            except Exception: return
            self._cs_photo_refs.clear()
            if not frames:
                if _alive(): self.cs_prog.set("フレームを取得できませんでした")
                return

            # 倍率に応じたサムネサイズ、アスペクトは実フレームから
            parent.update_idletasks()
            avail_w=max(canvas_scroll.winfo_width()-20,400)
            base_w=max(140,avail_w//8)
            thumb_w=int(base_w*scale)
            aspect=16/9
            fh,fw=frames[0][1].shape[:2]
            if fh>0: aspect=fw/fh
            thumb_h=int(thumb_w/aspect)
            cols=max(1,avail_w//(thumb_w+10))

            self.cs_prog.set(f"描画中… {cols}列 × {math.ceil(len(frames)/cols)}行")
            self.after(0, lambda: None)  # v24: スレッド安全

            for i,(ft,frame,off) in enumerate(frames):
                # v22 fix: 各イテレーション開始時に世代/widget生存チェック
                if not _alive(): return
                try:
                    row_i=i//cols; col_i=i%cols
                    cell=tk.Frame(cs_grid,bg=BG); cell.grid(row=row_i,column=col_i,padx=3,pady=3)
                    rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
                    img=Image.fromarray(rgb)
                    iw_,ih_=img.size
                    if iw_>0 and ih_>0:
                        sc=min(thumb_w/iw_, thumb_h/ih_)
                        img=img.resize((max(1,int(iw_*sc)),max(1,int(ih_*sc))),Image.LANCZOS)
                    photo=ImageTk.PhotoImage(img); self._cs_photo_refs.append(photo)
                    is_hit=abs(off)<interval/2
                    border_color=GOLD if is_hit else BORDER
                    lbl=tk.Label(cell,image=photo,bg=BG,
                                 highlightbackground=border_color,
                                 highlightthickness=3 if is_hit else 1,cursor="hand2")
                    lbl.pack()
                    if abs(off)<0.001: ds="0.00s"
                    elif off<0: ds=f"{off:.2f}s"
                    else: ds=f"+{off:.2f}s"
                    tk.Label(cell,text=ds,bg=BG,
                             fg=GOLD if is_hit else SUBTEXT,
                             font=_tk_font(10,bold=is_hit)).pack()
                    def _on_click(event,t=ft,pi=pidx):
                        if pi>=len(self.peaks): return
                        self.peak_idx=pi
                        sd=self.camera_dist.get()/SOUND_SPEED
                        base=max(0.0,self.peaks[pi]["time"]-sd)
                        self.frame_offset=int(round((t-base)*self.video_fps))
                        self._scrub_time=None
                        self._update_view()
                        self.tabs.select(self.tab_main)
                    lbl.bind("<Button-1>",_on_click)
                except tk.TclError:
                    return
                except Exception:
                    continue

            self.cs_prog.set(f"完了: {len(frames)}枚  (#{rank_g}  ヒット {hit_t:.2f}s, {scale}x)")

        def _regen(*_): threading.Thread(target=_generate,daemon=True).start()
        btn_gen.config(command=_regen)
        self.cs_peak_sel.bind("<<ComboboxSelected>>",_regen)
        self.cs_scale.bind("<<ComboboxSelected>>",_regen)
        self.cs_start.trace_add("write",lambda *_: _regen())
        self.cs_end  .trace_add("write",lambda *_: _regen())
        self.cs_interval.trace_add("write",lambda *_: _regen())
        self._cs_regen=_regen

    # ══════════════════════════════════════════
    #  比較モード１ タブ
    # ══════════════════════════════════════════
    def _build_tab_cmp1(self,parent):
        # コンパクトな2段コントロール
        ctrl=tk.Frame(parent,bg=PANEL2); ctrl.pack(fill="x",padx=8,pady=4)
        # 段1: A & B (動画 / チェックポイント) - v24: 履歴サムネ選択
        row1=tk.Frame(ctrl,bg=PANEL2); row1.pack(fill="x")
        tk.Label(row1,text="A 動画:",bg=PANEL2,fg=ACCENT,font=_tk_font(9,bold=True)).pack(side="left",padx=(4,2))
        self.c1_path_a=tk.StringVar(value=self.video_path.get())
        self.c1_label_a=tk.Label(row1,textvariable=tk.StringVar(),width=20,
                                  bg=DARK2,fg=ACCENT,relief="flat",font=_tk_font(9),
                                  anchor="w",padx=4)
        self.c1_label_a.pack(side="left",ipady=2)
        # 表示更新ヘルパ
        def _update_label_a(*_):
            p=self.c1_path_a.get()
            txt=display_label_for(p) if p else "(未選択)"
            self.c1_label_a.config(text=txt[:24])
        self.c1_path_a.trace_add("write",_update_label_a)
        _update_label_a()
        tk.Button(row1,text="📂選択",bg=ACCENT,fg="white",relief="flat",
                  font=_tk_font(8,bold=True),
                  command=lambda: self._pick_video_from_history(self.c1_path_a)
                  ).pack(side="left",padx=2,ipadx=2)
        tk.Label(row1,text="CP:",bg=PANEL2,fg=TEXT,font=_tk_font(9)).pack(side="left",padx=(8,2))
        self.c1_peak_a=ttk.Combobox(row1,width=5,state="readonly",font=_tk_font(9))
        self.c1_peak_a.pack(side="left",padx=(0,16))

        tk.Label(row1,text="B 動画:",bg=PANEL2,fg=GREEN,font=_tk_font(9,bold=True)).pack(side="left",padx=(4,2))
        self.c1_path_b=tk.StringVar(value=self.video_path.get())
        self.c1_label_b=tk.Label(row1,textvariable=tk.StringVar(),width=20,
                                  bg=DARK2,fg=GREEN,relief="flat",font=_tk_font(9),
                                  anchor="w",padx=4)
        self.c1_label_b.pack(side="left",ipady=2)
        def _update_label_b(*_):
            p=self.c1_path_b.get()
            txt=display_label_for(p) if p else "(未選択)"
            self.c1_label_b.config(text=txt[:24])
        self.c1_path_b.trace_add("write",_update_label_b)
        _update_label_b()
        tk.Button(row1,text="📂選択",bg=GREEN,fg="white",relief="flat",
                  font=_tk_font(8,bold=True),
                  command=lambda: self._pick_video_from_history(self.c1_path_b)
                  ).pack(side="left",padx=2,ipadx=2)
        tk.Label(row1,text="CP:",bg=PANEL2,fg=TEXT,font=_tk_font(9)).pack(side="left",padx=(8,2))
        self.c1_peak_b_var=tk.StringVar()
        self.c1_peak_b=ttk.Combobox(row1,width=5,state="readonly",
            textvariable=self.c1_peak_b_var,font=_tk_font(9))
        self.c1_peak_b.pack(side="left")

        # 段2: 範囲 / 間隔 / 倍率 / 進捗 / 再描画
        row2=tk.Frame(ctrl,bg=PANEL2); row2.pack(fill="x",pady=(4,0))
        tk.Label(row2,text="範囲±:",bg=PANEL2,fg=TEXT,font=_tk_font(9)).pack(side="left",padx=(4,2))
        self.c1_range=tk.DoubleVar(value=1.0)
        self.c1_range_scale=tk.Scale(row2,variable=self.c1_range,from_=0.1,to=3.0,
            orient="horizontal",resolution=0.1,bg=PANEL2,fg=TEXT,troughcolor=DARK2,
            highlightbackground=PANEL2,relief="flat",length=110,sliderlength=12)
        self.c1_range_scale.pack(side="left")
        tk.Label(row2,textvariable=self.c1_range,bg=PANEL2,fg=ACCENT,
                 font=("Courier",9),width=4).pack(side="left",padx=(0,10))

        tk.Label(row2,text="間隔:",bg=PANEL2,fg=TEXT,font=_tk_font(9)).pack(side="left",padx=(0,2))
        self.c1_interval=tk.DoubleVar(value=0.10)
        # v18: スライダ → ドロップダウン
        c1_iv_vals=["0.05","0.10","0.15","0.20","0.30","0.50"]
        self.c1_iv_cb=ttk.Combobox(row2,values=c1_iv_vals,width=5,
                                   state="readonly",font=_tk_font(9))
        self.c1_iv_cb.set("0.10")
        self.c1_iv_cb.pack(side="left",padx=(0,10))
        def _c1_iv_set(*_):
            try: self.c1_interval.set(float(self.c1_iv_cb.get()))
            except Exception: pass
        self.c1_iv_cb.bind("<<ComboboxSelected>>",_c1_iv_set)

        tk.Label(row2,text="倍率:",bg=PANEL2,fg=TEXT,font=_tk_font(9)).pack(side="left",padx=(0,2))
        self.c1_scale=ttk.Combobox(row2,width=5,state="readonly",font=_tk_font(9),
            values=[f"{x/10:.1f}x" for x in range(10,21)])
        self.c1_scale.current(0)
        self.c1_scale.pack(side="left",padx=(0,10))

        self.c1_prog=tk.StringVar(value="プルダウン変更で自動更新します")
        tk.Label(row2,textvariable=self.c1_prog,bg=PANEL2,fg=SUBTEXT,font=_tk_font(9)
                 ).pack(side="left",padx=8)
        btn1=tk.Button(row2,text="▶ 再描画",bg=ACCENT,fg="white",relief="flat",
                       font=_tk_font(10,bold=True),cursor="hand2")
        btn1.pack(side="left",padx=4,ipady=3)

        # 表示エリア
        outer=tk.Frame(parent,bg=BG); outer.pack(fill="both",expand=True)
        cscroll=tk.Canvas(outer,bg=BG,highlightthickness=0)
        vsb=tk.Scrollbar(outer,orient="vertical",command=cscroll.yview)
        hsb=tk.Scrollbar(outer,orient="horizontal",command=cscroll.xview)
        cscroll.configure(yscrollcommand=vsb.set,xscrollcommand=hsb.set)
        vsb.pack(side="right",fill="y"); hsb.pack(side="bottom",fill="x")
        cscroll.pack(side="left",fill="both",expand=True)
        grid_f=tk.Frame(cscroll,bg=BG)
        cscroll.create_window((0,0),window=grid_f,anchor="nw")
        grid_f.bind("<Configure>",lambda e: cscroll.configure(scrollregion=cscroll.bbox("all")))
        _refs1=[]

        def _on_interval_changed_c1(*_):
            iv=self.c1_interval.get()
            if iv<=0: return
            try: self.c1_range_scale.config(resolution=iv,from_=iv,to=max(iv*30,3.0))
            except Exception: pass
            cur=self.c1_range.get()
            sn=round(cur/iv)*iv
            if abs(sn-cur)>1e-6: self.c1_range.set(round(sn,3))
        self.c1_interval.trace_add("write",_on_interval_changed_c1)
        _on_interval_changed_c1()

        def _update_peak_b_list(*_):
            pb=self.c1_path_b.get()
            if pb and os.path.exists(pb) and pb!=self.video_path.get():
                db2=get_db_path(pb)
                if os.path.exists(db2):
                    lbs=load_all_labels(db2,os.path.basename(pb))
                    ranks=sorted(lbs.keys()) if lbs else []
                    self.c1_peak_b["values"]=[f"#{r}" for r in ranks] if ranks else [""]
                    if ranks: self.c1_peak_b.current(0)
                    else: self.c1_peak_b_var.set("")
        self.c1_path_b.trace_add("write",_update_peak_b_list)

        def _gen1():
            # v22: 世代チェック
            my_gen=self._gen
            def _alive():
                try:
                    return (my_gen==self._gen
                            and grid_f.winfo_exists())
                except Exception: return False
            if not _alive(): return
            try:
                for w in grid_f.winfo_children(): w.destroy()
            except Exception: return
            _refs1.clear()
            if not self.peaks:
                if _alive(): self.c1_prog.set("動画を読み込んでください")
                return
            interval=self.c1_interval.get(); rng=self.c1_range.get()
            pa=self.c1_path_a.get(); pb_=self.c1_path_b.get()
            try: scale=float(self.c1_scale.get().rstrip("x"))
            except Exception: scale=1.0

            def _rank_for(video_path,pidx):
                if video_path==self.video_path.get() and 0<=pidx<len(self.peaks):
                    return self.peaks[pidx]["rank"]
                return pidx+1
            def _get_hit_t(video_path,pidx):
                db2=get_db_path(video_path); rank=_rank_for(video_path,pidx)
                if os.path.exists(db2):
                    lbl2=load_label(db2,os.path.basename(video_path),rank)
                    if lbl2 and lbl2.get("frame_time") and lbl2["frame_time"]>0:
                        return lbl2["frame_time"]
                if video_path==self.video_path.get() and 0<=pidx<len(self.peaks):
                    sd=self.camera_dist.get()/SOUND_SPEED
                    return max(0.0,self.peaks[pidx]["time"]-sd)
                return 0.0

            pidx_a=self.c1_peak_a.current(); pidx_b=self.c1_peak_b.current()
            vals_a=list(self.c1_peak_a["values"]); vals_b=list(self.c1_peak_b["values"])
            valid_a=(0<=pidx_a<len(vals_a) and vals_a[pidx_a].startswith("#") and vals_a[pidx_a]!="#0")
            valid_b=(0<=pidx_b<len(vals_b) and vals_b[pidx_b].startswith("#") and vals_b[pidx_b]!="#0")

            def _lbl_str(video_path,pidx):
                db2=get_db_path(video_path); rank=_rank_for(video_path,pidx)
                # v21: alias 優先
                disp=display_label_for(video_path)
                if os.path.exists(db2):
                    lbl2=load_label(db2,os.path.basename(video_path),rank)
                    if lbl2:
                        sj=next((ja for ja,en in SHOT_TYPES if en==lbl2.get("shot_type","")),"")
                        rj=next((ja for ja,en in RATINGS   if en==lbl2.get("rating","")),"")
                        return f"{disp} #{rank} {sj} {rj}"
                return f"{disp} #{rank}"

            # 間隔の倍数で対称オフセット
            n_each=int(round(rng/interval))
            offsets=[round(k*interval,4) for k in range(-n_each,n_each+1)]
            hit_a=_get_hit_t(pa,pidx_a) if valid_a else 0.0
            hit_b=_get_hit_t(pb_,pidx_b) if valid_b else 0.0
            self.c1_prog.set(f"抽出中… A:{hit_a:.2f}s  B:{hit_b:.2f}s")
            self.after(0, lambda: None)  # v24: スレッド安全

            def _extract(video_path,hit_t,offs,rank,_cap_cache=None):
                """v18: cap_cache を渡せば同じ動画では1度しか開かない
                v24: rank ベースで該当動画のクロップを取得し、全フレームに適用"""
                if _cap_cache is not None and video_path in _cap_cache:
                    cap=_cap_cache[video_path]
                    fps_=_cap_cache.get(video_path+"::fps",30)
                else:
                    cap=cv2.VideoCapture(video_path)
                    fps_=cap.get(cv2.CAP_PROP_FPS) or 30
                    if _cap_cache is not None:
                        _cap_cache[video_path]=cap
                        _cap_cache[video_path+"::fps"]=fps_
                # 該当動画のクロップ
                if video_path==self.video_path.get():
                    crops=self._crops
                else:
                    crops=self._load_crops_for_video(video_path)
                # その CP rank のクロップ矩形 (なければ None)
                crop_rect=None
                for c in crops:
                    if c.get("rank")==rank:
                        crop_rect=c.get("rect"); break
                frames=[]
                for off in offs:
                    ft=max(0,hit_t+off)
                    cap.set(cv2.CAP_PROP_POS_FRAMES,int(fps_*ft))
                    ret,fr=cap.read()
                    if ret and crop_rect is not None:
                        h_,w_=fr.shape[:2]
                        x1r,y1r,x2r,y2r=crop_rect
                        cx1=int(min(x1r,x2r)*w_); cy1=int(min(y1r,y2r)*h_)
                        cx2=int(max(x1r,x2r)*w_); cy2=int(max(y1r,y2r)*h_)
                        cx1=max(0,cx1); cy1=max(0,cy1)
                        cx2=min(w_,cx2); cy2=min(h_,cy2)
                        if cx2>cx1 and cy2>cy1:
                            fr=fr[cy1:cy2,cx1:cx2]
                    frames.append(fr if ret else None)
                if _cap_cache is None: cap.release()
                return frames

            # v18: A==B のケースで cap を共有
            rank_a=_rank_for(pa,pidx_a)
            rank_b=_rank_for(pb_,pidx_b)
            _caps={}
            frames_a=_extract(pa,hit_a,offsets,rank_a,_cap_cache=_caps) if valid_a else [None]*len(offsets)
            frames_b=_extract(pb_,hit_b,offsets,rank_b,_cap_cache=_caps) if valid_b else [None]*len(offsets)
            for k,v in list(_caps.items()):
                if k.endswith("::fps"): continue
                try: v.release()
                except Exception: pass

            base_w=120
            thumb_w=int(base_w*scale)
            aspect=16/9
            for fr in frames_a+frames_b:
                if fr is not None:
                    ah,aw=fr.shape[:2]
                    if ah>0: aspect=aw/ah; break
            thumb_h=int(thumb_w/aspect)

            # ヘッダ行
            row_top=0
            try:
                if valid_a:
                    tk.Label(grid_f,text=_lbl_str(pa,pidx_a),bg=BG,fg=ACCENT,
                             font=_tk_font(11,bold=True)).grid(row=0,column=0,
                             columnspan=len(offsets),pady=4,sticky="w")
                if valid_b:
                    tk.Label(grid_f,text=_lbl_str(pb_,pidx_b),bg=BG,fg=GREEN,
                             font=_tk_font(11,bold=True)).grid(row=3,column=0,
                             columnspan=len(offsets),pady=4,sticky="w")
            except tk.TclError: return

            for col,(fa_f,fb_f,off) in enumerate(zip(frames_a,frames_b,offsets)):
                # v22 fix: 各イテレーション開始時に世代/widget生存チェック
                if not _alive(): return
                try:
                    for fr,row_base,color in [(fa_f,1,ACCENT),(fb_f,4,GREEN)]:
                        cell=tk.Frame(grid_f,bg=BG)
                        cell.grid(row=row_base,column=col,padx=2,pady=1)
                        if fr is None:
                            tk.Label(cell,text="—",bg=BG,fg=SUBTEXT,
                                     font=_tk_font(9),width=8,height=2).pack(); continue
                        rgb=cv2.cvtColor(fr,cv2.COLOR_BGR2RGB)
                        img=Image.fromarray(rgb)
                        iw_,ih_=img.size
                        if iw_>0 and ih_>0:
                            sc=min(thumb_w/iw_, thumb_h/ih_)
                            img=img.resize((max(1,int(iw_*sc)),max(1,int(ih_*sc))),Image.LANCZOS)
                        photo=ImageTk.PhotoImage(img); _refs1.append(photo)
                        is_hit=abs(off)<interval/2
                        bcol=GOLD if is_hit else color
                        tk.Label(cell,image=photo,bg=BG,
                                 highlightbackground=bcol,
                                 highlightthickness=3 if is_hit else 1).pack()
                    # 秒数ラベルは画像の下
                    if abs(off)<0.001: ds="0.00s"
                    elif off<0: ds=f"{off:.2f}s"
                    else: ds=f"+{off:.2f}s"
                    is_hit=abs(off)<interval/2
                    if valid_a:
                        tk.Label(grid_f,text=ds,bg=BG,
                                 fg=GOLD if is_hit else SUBTEXT,
                                 font=_tk_font(9,bold=is_hit)).grid(row=2,column=col,pady=(0,4))
                    if valid_b:
                        tk.Label(grid_f,text=ds,bg=BG,
                                 fg=GOLD if is_hit else SUBTEXT,
                                 font=_tk_font(9,bold=is_hit)).grid(row=5,column=col,pady=(0,4))
                except tk.TclError:
                    return
                except Exception:
                    continue

            who=("A" if valid_a else "")+("B" if valid_b else "")
            self.c1_prog.set(f"完了: {len(offsets)}コマ × {who}  ({scale}x)")

        def _refresh(*_): threading.Thread(target=_gen1,daemon=True).start()

        def _refresh_a(*_):
            """A 側だけ差分更新 (B 行を消さずに A 行だけ再描画)"""
            def _worker():
                my_gen=self._gen
                try:
                    if not grid_f.winfo_exists(): return
                except Exception: return
                interval=self.c1_interval.get(); rng=self.c1_range.get()
                n_each=int(round(rng/interval)); offsets=sorted(set(
                    round(interval*k,4) for k in range(-n_each,n_each+1)))
                pa=self.c1_path_a.get()
                pidx_a=self.c1_peak_a.current()
                vals_a=list(self.c1_peak_a["values"])
                valid_a=(0<=pidx_a<len(vals_a) and vals_a[pidx_a].startswith("#")
                         and vals_a[pidx_a]!="#0")
                hit_a=_get_hit_t(pa,pidx_a) if valid_a else 0.0
                rank_a=_rank_for(pa,pidx_a)
                frames_a=_extract(pa,hit_a,offsets,rank_a) if valid_a else [None]*len(offsets)
                # アスペクト比
                aspect=16/9
                for fr in frames_a:
                    if fr is not None:
                        ah,aw=fr.shape[:2]
                        if ah>0: aspect=aw/ah; break
                try: scale=float(self.c1_scale.get().rstrip("x"))
                except Exception: scale=1.0
                thumb_w=int(120*scale); thumb_h=int(thumb_w/aspect)
                # A 行だけ削除して再描画
                def _redraw_a():
                    try:
                        if not grid_f.winfo_exists(): return
                        # row 0,1,2 のウィジェットを削除
                        for ch in list(grid_f.winfo_children()):
                            try:
                                info=ch.grid_info()
                                if info.get("row",99) in (0,1,2): ch.destroy()
                            except Exception: pass
                        _refs1.clear()  # A/B 共用なので全クリア → B はその後再描画しないが ref は残る
                        if valid_a:
                            tk.Label(grid_f,text=_lbl_str(pa,pidx_a),bg=BG,fg=ACCENT,
                                     font=_tk_font(11,bold=True)).grid(row=0,column=0,
                                     columnspan=len(offsets),pady=4,sticky="w")
                        for col,(fa_f,off) in enumerate(zip(frames_a,offsets)):
                            cell=tk.Frame(grid_f,bg=BG); cell.grid(row=1,column=col,padx=2,pady=1)
                            if fa_f is None:
                                tk.Label(cell,text="—",bg=BG,fg=SUBTEXT,
                                         font=_tk_font(9),width=8,height=2).pack(); continue
                            rgb=cv2.cvtColor(fa_f,cv2.COLOR_BGR2RGB)
                            img=Image.fromarray(rgb)
                            iw_,ih_=img.size
                            if iw_>0 and ih_>0:
                                sc=min(thumb_w/iw_, thumb_h/ih_)
                                img=img.resize((max(1,int(iw_*sc)),max(1,int(ih_*sc))),Image.LANCZOS)
                            photo=ImageTk.PhotoImage(img); _refs1.append(photo)
                            is_hit=abs(off)<interval/2
                            tk.Label(cell,image=photo,bg=BG,
                                     highlightbackground=GOLD if is_hit else ACCENT,
                                     highlightthickness=3 if is_hit else 1).pack()
                            if valid_a:
                                ds="0.00s" if abs(off)<0.001 else (f"{off:.2f}s" if off<0 else f"+{off:.2f}s")
                                tk.Label(grid_f,text=ds,bg=BG,
                                         fg=GOLD if is_hit else SUBTEXT,
                                         font=_tk_font(9,bold=is_hit)).grid(row=2,column=col,pady=(0,4))
                    except Exception: pass
                self.after(0,_redraw_a)
            threading.Thread(target=_worker,daemon=True).start()

        def _refresh_b(*_):
            """B 側だけ差分更新"""
            def _worker():
                my_gen=self._gen
                try:
                    if not grid_f.winfo_exists(): return
                except Exception: return
                interval=self.c1_interval.get(); rng=self.c1_range.get()
                n_each=int(round(rng/interval)); offsets=sorted(set(
                    round(interval*k,4) for k in range(-n_each,n_each+1)))
                pb_=self.c1_path_b.get()
                pidx_b=self.c1_peak_b.current()
                vals_b=list(self.c1_peak_b["values"])
                valid_b=(0<=pidx_b<len(vals_b) and vals_b[pidx_b].startswith("#")
                         and vals_b[pidx_b]!="#0")
                hit_b=_get_hit_t(pb_,pidx_b) if valid_b else 0.0
                rank_b=_rank_for(pb_,pidx_b)
                frames_b=_extract(pb_,hit_b,offsets,rank_b) if valid_b else [None]*len(offsets)
                aspect=16/9
                for fr in frames_b:
                    if fr is not None:
                        ah,aw=fr.shape[:2]
                        if ah>0: aspect=aw/ah; break
                try: scale=float(self.c1_scale.get().rstrip("x"))
                except Exception: scale=1.0
                thumb_w=int(120*scale); thumb_h=int(thumb_w/aspect)
                def _redraw_b():
                    try:
                        if not grid_f.winfo_exists(): return
                        for ch in list(grid_f.winfo_children()):
                            try:
                                info=ch.grid_info()
                                if info.get("row",99) in (3,4,5): ch.destroy()
                            except Exception: pass
                        if valid_b:
                            tk.Label(grid_f,text=_lbl_str(pb_,pidx_b),bg=BG,fg=GREEN,
                                     font=_tk_font(11,bold=True)).grid(row=3,column=0,
                                     columnspan=len(offsets),pady=4,sticky="w")
                        for col,(fb_f,off) in enumerate(zip(frames_b,offsets)):
                            cell=tk.Frame(grid_f,bg=BG); cell.grid(row=4,column=col,padx=2,pady=1)
                            if fb_f is None:
                                tk.Label(cell,text="—",bg=BG,fg=SUBTEXT,
                                         font=_tk_font(9),width=8,height=2).pack(); continue
                            rgb=cv2.cvtColor(fb_f,cv2.COLOR_BGR2RGB)
                            img=Image.fromarray(rgb)
                            iw_,ih_=img.size
                            if iw_>0 and ih_>0:
                                sc=min(thumb_w/iw_, thumb_h/ih_)
                                img=img.resize((max(1,int(iw_*sc)),max(1,int(ih_*sc))),Image.LANCZOS)
                            photo=ImageTk.PhotoImage(img); _refs1.append(photo)
                            is_hit=abs(off)<interval/2
                            tk.Label(cell,image=photo,bg=BG,
                                     highlightbackground=GOLD if is_hit else GREEN,
                                     highlightthickness=3 if is_hit else 1).pack()
                            if valid_b:
                                ds="0.00s" if abs(off)<0.001 else (f"{off:.2f}s" if off<0 else f"+{off:.2f}s")
                                tk.Label(grid_f,text=ds,bg=BG,
                                         fg=GOLD if is_hit else SUBTEXT,
                                         font=_tk_font(9,bold=is_hit)).grid(row=5,column=col,pady=(0,4))
                    except Exception: pass
                self.after(0,_redraw_b)
            threading.Thread(target=_worker,daemon=True).start()

        btn1.config(command=_refresh)
        self.c1_peak_a.bind("<<ComboboxSelected>>",_refresh_a)  # A変更 → A行だけ
        self.c1_peak_b.bind("<<ComboboxSelected>>",_refresh_b)  # B変更 → B行だけ
        # パスや表示倍率が変わった時は全体再描画
        self.c1_path_a.trace_add("write",lambda *_: _refresh())
        self.c1_path_b.trace_add("write",lambda *_: _refresh())
        self.c1_scale.bind("<<ComboboxSelected>>",_refresh)
        self.c1_range.trace_add("write",lambda *_:_refresh())
        self.c1_interval.trace_add("write",lambda *_:_refresh())
        self._c1_regen=_refresh

    # ══════════════════════════════════════════
    #  比較モード２ タブ (全ショット一覧)
    # ══════════════════════════════════════════
    def _build_tab_cmp2(self,parent):
        ctrl=tk.Frame(parent,bg=PANEL2); ctrl.pack(fill="x",padx=8,pady=4)

        # v25: 間隔プルダウン
        tk.Label(ctrl,text="間隔:",bg=PANEL2,fg=TEXT,font=_tk_font(9)
                 ).pack(side="left",padx=(6,2))
        self._c2_step=tk.DoubleVar(value=0.1)
        self._c2_step_cb=ttk.Combobox(ctrl,width=5,state="readonly",font=_tk_font(9),
            values=["0.05","0.10","0.15","0.20","0.25","0.50"])
        self._c2_step_cb.set("0.10")
        self._c2_step_cb.pack(side="left",padx=(0,6))

        # v25: 範囲プルダウン
        tk.Label(ctrl,text="範囲:",bg=PANEL2,fg=TEXT,font=_tk_font(9)
                 ).pack(side="left",padx=(4,2))
        self._c2_range=tk.DoubleVar(value=1.0)
        self._c2_range_cb=ttk.Combobox(ctrl,width=5,state="readonly",font=_tk_font(9),
            values=["0.5","1.0","1.5","2.0","3.0"])
        self._c2_range_cb.set("1.0")
        self._c2_range_cb.pack(side="left",padx=(0,6))

        # v25: オフセットプルダウン (間隔・範囲変更で自動更新)
        tk.Label(ctrl,text="オフセット(秒):",bg=PANEL2,fg=TEXT,font=_tk_font(9)
                 ).pack(side="left",padx=(4,2))
        self.c2_offset=tk.DoubleVar(value=-0.5)
        self._c2_offset_cb=ttk.Combobox(ctrl,width=6,state="readonly",font=_tk_font(9))
        self._c2_offset_cb.pack(side="left",padx=(0,8))

        def _rebuild_offset_values(*_):
            try: step=float(self._c2_step_cb.get())
            except Exception: step=0.1
            try: rng=float(self._c2_range_cb.get())
            except Exception: rng=1.0
            self._c2_step.set(step)
            self._c2_range.set(rng)
            if step<=0: step=0.1
            vals=[]
            v=-rng
            while v<=rng+1e-9:
                vals.append(f"{v:.2f}")
                v+=step
            self._c2_offset_cb["values"]=vals
            # 現在の値を維持できなければデフォルトに
            cur=f"{self.c2_offset.get():.2f}"
            if cur in vals:
                self._c2_offset_cb.set(cur)
            else:
                mid=vals[len(vals)//2] if vals else "0.00"
                self._c2_offset_cb.set(mid)
                self.c2_offset.set(float(mid))

        self._c2_step_cb.bind("<<ComboboxSelected>>",_rebuild_offset_values)
        self._c2_range_cb.bind("<<ComboboxSelected>>",_rebuild_offset_values)
        _rebuild_offset_values()  # 初期値生成

        def _on_offset_sel(*_):
            try: self.c2_offset.set(float(self._c2_offset_cb.get()))
            except Exception: pass
        self._c2_offset_cb.bind("<<ComboboxSelected>>",_on_offset_sel)

        tk.Label(ctrl,text="ショット:",bg=PANEL2,fg=TEXT,font=_tk_font(9)).pack(side="left",padx=4)
        self.c2_filter=ttk.Combobox(ctrl,width=8,state="readonly",font=_tk_font(9))
        self.c2_filter["values"]=["すべて"]+[ja for ja,_ in SHOT_TYPES]
        self.c2_filter.current(0); self.c2_filter.pack(side="left",padx=(0,8))

        # mode2 の倍率は 1〜5 整数
        tk.Label(ctrl,text="表示倍率:",bg=PANEL2,fg=TEXT,font=_tk_font(9)).pack(side="left",padx=4)
        self.c2_scale=ttk.Combobox(ctrl,width=4,state="readonly",font=_tk_font(9),
            values=["1x","2x","3x","4x","5x"])
        self.c2_scale.current(2); self.c2_scale.pack(side="left",padx=(0,8))

        self.c2_prog=tk.StringVar(value="プルダウン変更で自動更新します")
        tk.Label(ctrl,textvariable=self.c2_prog,bg=PANEL2,fg=SUBTEXT,font=_tk_font(9)
                 ).pack(side="left",padx=8)
        btn2=tk.Button(ctrl,text="▶ 再描画",bg=ACCENT,fg="white",relief="flat",
                       font=_tk_font(10,bold=True),cursor="hand2")
        btn2.pack(side="left",padx=4,ipady=3)

        outer=tk.Frame(parent,bg=BG); outer.pack(fill="both",expand=True)
        cscroll=tk.Canvas(outer,bg=BG,highlightthickness=0)
        vsb=tk.Scrollbar(outer,orient="vertical",command=cscroll.yview)
        cscroll.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right",fill="y")
        cscroll.pack(side="left",fill="both",expand=True)
        grid_f=tk.Frame(cscroll,bg=BG)
        gwin=cscroll.create_window((0,0),window=grid_f,anchor="nw")
        grid_f.bind("<Configure>",lambda e: cscroll.configure(scrollregion=cscroll.bbox("all")))
        cscroll.bind("<Configure>",lambda e: cscroll.itemconfig(gwin,width=max(e.width,1)))
        _refs2=[]

        def _gen2():
            # v22: 世代チェック - 動画切替後の stale 実行を防ぐ
            my_gen=self._gen
            def _alive():
                try:
                    return (my_gen==self._gen
                            and grid_f.winfo_exists())
                except Exception: return False
            if not _alive(): return
            try:
                for w in grid_f.winfo_children(): w.destroy()
            except Exception: return
            _refs2.clear()
            if not self.peaks:
                if _alive(): self.c2_prog.set("動画を読み込んでください")
                return
            offset=self.c2_offset.get(); sel_shot=self.c2_filter.get()
            try: scale=int(self.c2_scale.get().rstrip("x"))
            except Exception: scale=3
            path=self.video_path.get()
            db_path2=get_db_path(path)
            all_lbl2=load_all_labels(db_path2,os.path.basename(path))

            targets=[]
            for i,p in enumerate(self.peaks):
                pt=p["time"]; rank=p["rank"]
                lbl2=all_lbl2.get(rank,None)
                if lbl2 is None: continue
                if lbl2[0] in ("noise",""): continue
                if sel_shot!="すべて":
                    shot_ja=next((ja for ja,en in SHOT_TYPES if en==lbl2[0]),"")
                    if shot_ja!=sel_shot: continue
                lbl_full=load_label(db_path2,os.path.basename(path),rank)
                if lbl_full and lbl_full.get("frame_time") and lbl_full["frame_time"]>0:
                    hit_t=lbl_full["frame_time"]
                else:
                    sd=self.camera_dist.get()/SOUND_SPEED
                    hit_t=max(0.0,pt-sd)
                targets.append((i,pt,hit_t,lbl2))

            if not targets:
                self.c2_prog.set("該当ラベル済みショットがありません"); return

            self.after(0, lambda t=len(targets):
                       self.c2_prog.set(f"抽出中… {t}ショット"))

            # v24: 各CPは「そのCP自身のクロップ」を使う (Option Bは廃止)
            def _crop_for_pidx(frame, pidx_):
                """指定 CP インデックスに紐づくクロップを適用"""
                if frame is None or not (0<=pidx_<len(self.peaks)): return frame
                rank=self.peaks[pidx_]["rank"]
                rect=self._crop_rect_for_rank(rank)
                if rect is None: return frame
                ih,iw=frame.shape[:2]
                x1r,y1r,x2r,y2r=rect
                cx1=int(min(x1r,x2r)*iw); cy1=int(min(y1r,y2r)*ih)
                cx2=int(max(x1r,x2r)*iw); cy2=int(max(y1r,y2r)*ih)
                if cx2>cx1 and cy2>cy1:
                    return frame[cy1:cy2,cx1:cx2]
                return frame

            cap=cv2.VideoCapture(path)
            fps_=cap.get(cv2.CAP_PROP_FPS) or 30
            # v24 fix: winfo_width はメインスレッドで取得が安全
            avail_w=self.after_idle(lambda:None) or 400
            try: avail_w=max(cscroll.winfo_width()-20,400)
            except Exception: avail_w=400
            thumb_w=120*scale
            cols=max(1,avail_w//(thumb_w+10))
            aspect=16/9
            cap.set(cv2.CAP_PROP_POS_FRAMES,int(fps_*max(0,targets[0][2]+offset)))
            ok0,fr0=cap.read()
            if ok0:
                fr0=_crop_for_pidx(fr0,targets[0][0])
                h0,w0=fr0.shape[:2]
                if h0>0: aspect=w0/h0
            thumb_h=int(thumb_w/max(0.01,aspect))

            if abs(offset)<0.001: ds="0.00s"
            elif offset<0: ds=f"{offset:.2f}s"
            else: ds=f"+{offset:.2f}s"

            for i2,(pidx,pt,hit_t,lbl2) in enumerate(targets):
                # v22 fix: 各イテレーション開始時に世代/widget生存チェック
                if not _alive():
                    try: cap.release()
                    except Exception: pass
                    return
                ft=max(0,hit_t+offset)
                cap.set(cv2.CAP_PROP_POS_FRAMES,int(fps_*ft))
                ret,frame=cap.read()
                # widget作成は try で囲み、競合で破棄されていたら静かに撤退
                try:
                    row_i=i2//cols; col_i=i2%cols
                    cell=tk.Frame(grid_f,bg=BG); cell.grid(row=row_i,column=col_i,padx=3,pady=3)
                    if not ret:
                        tk.Label(cell,text="—",bg=BG,fg=SUBTEXT,
                                 font=_tk_font(9),width=8,height=4).pack(); continue
                    frame=_crop_for_pidx(frame,pidx)
                    rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
                    img=Image.fromarray(rgb)
                    iw_,ih_=img.size
                    if iw_>0 and ih_>0:
                        sc=min(thumb_w/iw_, thumb_h/ih_)
                        img=img.resize((max(1,int(iw_*sc)),max(1,int(ih_*sc))),Image.LANCZOS)
                    photo=ImageTk.PhotoImage(img); _refs2.append(photo)
                    lbl_w=tk.Label(cell,image=photo,bg=BG,
                                   highlightbackground=ACCENT2,highlightthickness=1,cursor="hand2")
                    lbl_w.pack()
                    shot_ja=next((ja for ja,en in SHOT_TYPES if en==lbl2[0]),"")
                    spin_ja=next((ja for ja,en in SPINS      if en==lbl2[1]),"")
                    rtg_ja =next((ja for ja,en in RATINGS    if en==lbl2[2]),"")
                    rank_disp=self.peaks[pidx]["rank"] if pidx<len(self.peaks) else pidx+1
                    info=f"#{rank_disp} {shot_ja}/{spin_ja}\n{rtg_ja}  {hit_t:.2f}s  ({ds})"
                    tk.Label(cell,text=info,bg=BG,fg=TEXT,
                             font=_tk_font(8),justify="center").pack(pady=(2,2))
                    def _on_click(event,pi=pidx,_hit=hit_t,_off=offset):
                        # v22 fix: frame_offset を直接設定して target_t に到達させる
                        if not self.peaks or pi>=len(self.peaks):
                            return
                        self.peak_idx=pi
                        target_t=max(0.0,_hit+_off)
                        pt=self.peaks[pi]["time"]
                        sd=self.camera_dist.get()/SOUND_SPEED
                        base_in_view=max(0.0,pt-sd)
                        try:
                            self.frame_offset=int(round((target_t-base_in_view)*self.video_fps))
                        except Exception:
                            self.frame_offset=0
                        try:
                            self.peak_list.selection_clear(0,"end")
                            self.peak_list.selection_set(pi)
                            self.peak_list.see(pi)
                        except Exception: pass
                        self.tabs.select(self.tab_main)
                        self._update_view()
                    lbl_w.bind("<Button-1>",_on_click)
                    if i2%5==0:
                        if not _alive():
                            try: cap.release()
                            except Exception: pass
                            return
                        # v24 fix: UI 更新はメインスレッドへ after() で投げる
                        self.after(0, lambda n=i2+1, t=len(targets):
                                   self.c2_prog.set(f"描画中… {n}/{t}"))
                except tk.TclError:
                    # widget が破棄された (動画切替など) → 静かに終了
                    try: cap.release()
                    except Exception: pass
                    return
                except Exception:
                    # その他例外は1セルだけスキップして続行
                    continue
            cap.release()
            self.after(0, lambda t=len(targets), d=ds, s=scale:
                       self.c2_prog.set(f"完了: {t}ショット  (オフセット {d},  {s}x)"))

        def _refresh2(*_): threading.Thread(target=_gen2,daemon=True).start()
        btn2.config(command=_refresh2)
        self.c2_filter.bind("<<ComboboxSelected>>",_refresh2)
        self.c2_scale.bind("<<ComboboxSelected>>",_refresh2)
        self.c2_offset.trace_add("write",lambda *_:_refresh2())
        self._c2_regen=_refresh2

    # ══════════════════════════════════════════
    #  CP追加 / 再採番 (v11)
    # ══════════════════════════════════════════
    def _add_checkpoint_at_current(self):
        path=self.video_path.get()
        if not path or self.data is None:
            messagebox.showinfo("CP追加","動画を解析してから実行してください"); return
        t=float(self._current_frame_time)
        # 既存と近すぎないかチェック
        tol=max(0.12,self.min_gap.get()*0.25)
        for p in self.peaks:
            if abs(p["time"]-t)<=tol:
                self.status_var.set(f"既に近接するCP (#{p['rank']}) があります"); return
        vf=os.path.basename(path); db_path=get_db_path(path); init_db(db_path)
        new_rank = max((p["rank"] for p in self.peaks),default=0)+1
        upsert_peak_meta(db_path,vf,t,new_rank,"manual")
        # ピーク一覧に即追加して時系列ソート
        self.peaks.append({"rank":new_rank,"idx":-1,"time":t,
                           "thumb":"","frame_time":t,"source":"manual"})
        self.peaks.sort(key=lambda p: p["time"])
        # 新しいCPを選択
        for i,p in enumerate(self.peaks):
            if abs(p["time"]-t)<1e-6: self.peak_idx=i; break
        self.frame_offset=0
        self._update_shot_list()
        self.peak_list.selection_clear(0,"end")
        self.peak_list.selection_set(self.peak_idx)
        self.peak_list.see(self.peak_idx)
        self._update_view()
        self.status_var.set(f"CP #{new_rank} を追加しました ({t:.2f}s)")

    def _renumber_checkpoints(self):
        if not self.peaks:
            self.status_var.set("CPがありません"); return
        path=self.video_path.get(); vf=os.path.basename(path)
        db_path=get_db_path(path); init_db(db_path)

        # 既存ラベル・クロップを取得 → ランク→旧データ
        old_labels=load_all_labels(db_path,vf)   # rank -> (shot,spin,rating,ft)
        old_crops =load_crops(db_path,vf)        # [{rank,time,rect}]

        # 時系列に並べて新ランク決定
        sorted_peaks=sorted(self.peaks,key=lambda p: p["time"])
        mapping=[]  # (old_rank,new_rank,peak)
        for i,p in enumerate(sorted_peaks,start=1):
            mapping.append((p["rank"],i,p))

        # DBを書き直し
        con=sqlite3.connect(db_path)
        con.execute("DELETE FROM labels WHERE video_file=?",(vf,))
        con.execute("DELETE FROM crops  WHERE video_file=?",(vf,))
        con.execute("DELETE FROM peak_meta WHERE video_file=?",(vf,))
        con.commit(); con.close()

        for old_rank,new_rank,p in mapping:
            # 元データを新ランクで再書き込み
            lbl=old_labels.get(old_rank)
            if lbl:
                upsert_label(db_path,vf,p["time"],new_rank,
                             lbl[3] if (lbl[3] is not None) else p.get("frame_time") or p["time"],
                             p.get("thumb",""),lbl[0],lbl[1],lbl[2],self._last_cam)
            for c in old_crops:
                if c["rank"]==old_rank:
                    add_crop(db_path,vf,new_rank,c["time"],c["rect"])
            # ランク上書きを peak_meta に記録 (auto も manual も)
            upsert_peak_meta(db_path,vf,p["time"],new_rank,p.get("source","auto"))
            p["rank"]=new_rank

        self.peaks=sorted_peaks
        self.peak_idx=min(self.peak_idx,len(self.peaks)-1)
        self._update_shot_list()
        self.peak_list.selection_clear(0,"end")
        self.peak_list.selection_set(self.peak_idx)
        self.peak_list.see(self.peak_idx)  # v24
        self._update_view()
        self.status_var.set(f"再採番完了: 1〜{len(self.peaks)}")

    # ══════════════════════════════════════════
    #  YOLO 解析 (v11)
    # ══════════════════════════════════════════
    YOLO_KP_NAMES=[
        "鼻","左目","右目","左耳","右耳",
        "左肩","右肩","左肘","右肘","左手首","右手首",
        "左腰","右腰","左膝","右膝","左足首","右足首",
    ]
    # キーポイント拡張: 17=ラケット先端, 18=ボール, 19=重心(COG)
    YOLO_EXT_NAMES = YOLO_KP_NAMES + ["ラケット先端","ボール","重心"]
    # 各キーポイントの表示色 (連続写真オーバーレイ + 折れ線色)
    YOLO_KP_COLORS=[
        "#ff4d4d",  # 0  鼻       赤
        "#ff9933",  # 1  左目     橙
        "#ffcc00",  # 2  右目     黄橙
        "#cc6600",  # 3  左耳     茶橙
        "#996633",  # 4  右耳     茶
        "#66b3ff",  # 5  左肩     水色
        "#0066cc",  # 6  右肩     青
        "#66cc66",  # 7  左肘     緑
        "#006633",  # 8  右肘     深緑
        "#ffff66",  # 9  左手首   薄黄
        "#ff66ff",  # 10 右手首   マゼンタ
        "#cc99ff",  # 11 左腰     淡紫
        "#6600cc",  # 12 右腰     深紫
        "#ff99cc",  # 13 左膝     桃
        "#cc0066",  # 14 右膝     深桃
        "#cccccc",  # 15 左足首   灰
        "#666666",  # 16 右足首   深灰
        "#00ffff",  # 17 ラケ先   シアン
        "#aaff00",  # 18 ボール   蛍光黄緑
        "#ffd700",  # 19 重心     金 (★)
    ]
    # 信頼度しきい値プリセット {表示名: (keypoint, object)}
    YOLO_TH_PRESETS={
        "低精度":(0.20,0.10),
        "中精度":(0.40,0.30),
        "高精度":(0.70,0.60),
    }

    def _yolo_out_dir(self,video_path):
        return os.path.join(os.path.dirname(video_path),"yolo")

    def _yolo_data_file(self,video_path,rank,prefer_refined=False):
        """v62: 互換維持。source指定なしはMP優先→YOLO fallback"""
        return self._kp_data_file(video_path, rank, source="auto", prefer_refined=prefer_refined)

    def _kp_data_file(self, video_path, rank, source="auto", prefer_refined=False):
        """v62: KP JSONのパスを取得。
        source: 'mp' | 'yolo' | 'auto' (MP優先→YOLO fallback→legacy)"""
        d = self._yolo_out_dir(video_path)
        os.makedirs(d, exist_ok=True)
        stem = os.path.splitext(os.path.basename(video_path))[0]
        mp_raw = os.path.join(d, f"{stem}_cp{rank:02d}_mp.json")
        yolo_raw = os.path.join(d, f"{stem}_cp{rank:02d}_yolo.json")
        legacy = os.path.join(d, f"{stem}_cp{rank:02d}.json")
        def _with_refined(p):
            if prefer_refined:
                r = p[:-5] + "_refined.json"
                if os.path.exists(r): return r
            return p
        if source == "mp": return _with_refined(mp_raw)
        if source == "yolo": return _with_refined(yolo_raw)
        # auto: 存在するものを優先
        if os.path.exists(mp_raw): return _with_refined(mp_raw)
        if os.path.exists(yolo_raw): return _with_refined(yolo_raw)
        if os.path.exists(legacy): return _with_refined(legacy)
        return mp_raw  # 未検出時のデフォルト作成先

    @staticmethod
    def _calc_face_body_angles(row):
        """v30: KPデータから顔と体の向き角度を計算。
        顔水平角: 0°=正面, 90°=左耳が正面, 180°=背面, 270°=右耳が正面
        顔仰角: 0°=水平, 正=上向き (サーブ時60°程度)
        体水平角: 左右肩の中点と左右腰の中点から体幹の向きを推定
        戻り値: dict(face_yaw, face_pitch, body_yaw) or None"""
        def _get(ki):
            x = row.get(f"kp{ki:02d}_x"); y = row.get(f"kp{ki:02d}_y")
            c = row.get(f"kp{ki:02d}_c", 0) or 0
            if x is None or y is None or c < 0.3: return None
            return (x, y, c)
        nose = _get(0); l_eye = _get(1); r_eye = _get(2)
        l_ear = _get(3); r_ear = _get(4)
        l_sho = _get(5); r_sho = _get(6)
        l_hip = _get(11); r_hip = _get(12)
        result = {}
        # ── 顔水平角 (yaw) ──
        if l_ear and r_ear and nose:
            ear_mid_x = (l_ear[0] + r_ear[0]) / 2
            ear_mid_y = (l_ear[1] + r_ear[1]) / 2
            dx = nose[0] - ear_mid_x; dy = nose[1] - ear_mid_y
            yaw = math.degrees(math.atan2(-dx, -dy)) % 360
            # 左右耳の距離比で補正
            ear_dist = ((l_ear[0]-r_ear[0])**2 + (l_ear[1]-r_ear[1])**2)**0.5
            if l_sho and r_sho:
                sho_dist = ((l_sho[0]-r_sho[0])**2 + (l_sho[1]-r_sho[1])**2)**0.5
                if sho_dist > 0:
                    ratio = ear_dist / sho_dist
                    # ratio小=横向き, ratio大=正面
                    if ratio < 0.3:  # ほぼ横向き
                        if l_ear[2] > r_ear[2]: yaw = 90.0  # 左耳が見える=右向き
                        else: yaw = 270.0
            result["face_yaw"] = round(yaw, 1)
        elif l_eye and r_eye and nose:
            eye_mid_x = (l_eye[0] + r_eye[0]) / 2
            dx = nose[0] - eye_mid_x
            eye_dist = ((l_eye[0]-r_eye[0])**2 + (l_eye[1]-r_eye[1])**2)**0.5
            if eye_dist > 1:
                yaw = math.degrees(math.atan2(dx, eye_dist)) * 2
                result["face_yaw"] = round(yaw % 360, 1)
        # ── 顔仰角 (pitch) ──
        if nose and l_sho and r_sho:
            sho_mid_y = (l_sho[1] + r_sho[1]) / 2
            sho_mid_x = (l_sho[0] + r_sho[0]) / 2
            sho_dist = ((l_sho[0]-r_sho[0])**2 + (l_sho[1]-r_sho[1])**2)**0.5
            if sho_dist > 1:
                dy = sho_mid_y - nose[1]  # 肩より上=正
                pitch = math.degrees(math.atan2(dy, sho_dist * 0.8))
                result["face_pitch"] = round(max(-90, min(90, pitch)), 1)
        # ── 体水平角 (body yaw) ──
        if l_sho and r_sho:
            dx = r_sho[0] - l_sho[0]; dy = r_sho[1] - l_sho[1]
            body_yaw = (math.degrees(math.atan2(dy, dx)) + 90) % 360
            result["body_yaw"] = round(body_yaw, 1)
        # ── 見えないKPの判定 ──
        invisible = set()
        if "face_yaw" in result:
            fy = result["face_yaw"]
            if 60 < fy < 180:  # 右向き → 左目・左耳は見えない
                invisible.update([1, 3])
            elif 180 < fy < 300:  # 左向き → 右目・右耳は見えない
                invisible.update([2, 4])
            if 120 < fy < 240:  # 背面 → 両目見えない
                invisible.update([1, 2])
        result["invisible_kps"] = invisible
        return result if result else None

    @staticmethod
    def _find_optimal_hit_frame(rows, hit_time, shot_type=""):
        """v39: KPデータからヒットに最も近いフレームを推定。
        右手首 (kp10) の動きを分析:
        - サーブ/スマッシュ: 右手首y座標が最小 (最高点) のフレーム
        - その他 (ストローク): 右手首の速度が最大のフレーム付近
        戻り値: (optimal_time, reason) or (None, None)"""
        wrist_data = []  # (time, x, y)
        for r in rows:
            wx = r.get("kp10_x"); wy = r.get("kp10_y")
            wc = r.get("kp10_c", 0) or 0
            if wx is not None and wy is not None and wc >= 0.3:
                wrist_data.append((r["time"], wx, wy))
        if len(wrist_data) < 3:
            return None, None
        is_overhead = any(s in (shot_type or "") for s in ["サーブ", "スマッシュ"])
        if is_overhead:
            # y最小 = 画面最上部 = 最高点
            best = min(wrist_data, key=lambda w: w[2])
            return best[0], "右手首最高点"
        else:
            # 速度最大 (隣接フレーム間の移動距離/時間)
            best_v = 0; best_t = None
            for i in range(1, len(wrist_data)):
                t0, x0, y0 = wrist_data[i-1]
                t1, x1, y1 = wrist_data[i]
                dt = t1 - t0
                if dt <= 0: continue
                v = ((x1-x0)**2 + (y1-y0)**2)**0.5 / dt
                if v > best_v:
                    best_v = v
                    best_t = (t0 + t1) / 2
            if best_t is not None:
                return best_t, "右手首最高速度"
        return None, None

    @staticmethod
    def _apply_face_mesh_correction(rows, video_path, hit_t, sample_interval=0.5):
        """v42: MediaPipe Face Meshで顔KP (鼻/両目/両耳) を高精度化。
        sample_interval 秒間隔でFace Mesh実行 → 前後の結果から線形補間して全フレーム補正。
        戻り値: 補正されたフレーム数"""
        if not rows: return 0
        try:
            import mediapipe as mp
            from mediapipe.tasks.python import BaseOptions, vision as mp_vision
        except ImportError:
            return 0
        # モデル探索
        app_dir = os.path.dirname(os.path.abspath(__file__))
        model_candidates = [
            os.path.join(app_dir, "face_landmarker.task"),
            os.path.join(os.path.dirname(video_path), "face_landmarker.task"),
        ]
        model_path = next((p for p in model_candidates if os.path.exists(p)), None)
        if model_path is None:
            # 自動ダウンロード
            try:
                import urllib.request
                url = ("https://storage.googleapis.com/mediapipe-models/face_landmarker/"
                       "face_landmarker/float16/latest/face_landmarker.task")
                target = model_candidates[0]
                urllib.request.urlretrieve(url, target)
                model_path = target
            except Exception:
                return 0
        # サンプリング対象時刻の決定
        times = sorted({r["time"] for r in rows})
        if not times: return 0
        t_start, t_end = times[0], times[-1]
        # hit_t を基準に sample_interval 秒間隔
        sample_times = []
        t = hit_t
        while t >= t_start - 1e-6:
            sample_times.append(t); t -= sample_interval
        t = hit_t + sample_interval
        while t <= t_end + 1e-6:
            sample_times.append(t); t += sample_interval
        sample_times.sort()
        # 実データに最も近い時刻を選択
        sample_rows_idx = []
        for st in sample_times:
            best_i = min(range(len(rows)), key=lambda i: abs(rows[i]["time"] - st))
            if best_i not in sample_rows_idx:
                sample_rows_idx.append(best_i)
        # Face Mesh 実行
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        opts = mp_vision.FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=mp_vision.RunningMode.IMAGE,
            num_faces=1)
        # MediaPipe Face Mesh のランドマーク index → COCO KP
        # 1=鼻先, 33=右目外角, 133=左目外角 (MPは鏡像なので反転), 234=右頬(耳), 454=左頬(耳)
        # COCO 0=鼻, 1=左目, 2=右目, 3=左耳, 4=右耳
        MP_TO_COCO = {
            1:   0,   # 鼻先 → 鼻
            473: 1,   # 左瞳孔 → 左目
            468: 2,   # 右瞳孔 → 右目
            234: 4,   # 右頬 → 右耳
            454: 3,   # 左頬 → 左耳
        }
        face_results = {}  # rows_idx → {coco_ki: (x, y, conf)}
        try:
            with _suppress_stderr():
                detector_cm = mp_vision.FaceLandmarker.create_from_options(opts)
            with detector_cm as detector:
                for ri in sample_rows_idx:
                    r = rows[ri]
                    cap.set(cv2.CAP_PROP_POS_FRAMES, int(r["time"] * fps))
                    ok, frame = cap.read()
                    if not ok: continue
                    # person_bboxがあればクロップ
                    bbox = r.get("person_bbox")
                    off_x, off_y = 0, 0
                    if bbox:
                        h, w = frame.shape[:2]
                        x1, y1, x2, y2 = [int(v) for v in bbox]
                        margin = int((x2-x1) * 0.2)
                        x1 = max(0, x1-margin); y1 = max(0, y1-margin)
                        x2 = min(w, x2+margin); y2 = min(h, y2+margin)
                        if x2 > x1 and y2 > y1:
                            frame = frame[y1:y2, x1:x2]
                            off_x, off_y = x1, y1
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    fh, fw = rgb.shape[:2]
                    mp_img = mp.Image(image_format=mp.ImageFormat.SRGB,
                                       data=np.ascontiguousarray(rgb))
                    with _suppress_stderr():
                        det = detector.detect(mp_img)
                    if not det.face_landmarks: continue
                    lms = det.face_landmarks[0]
                    frame_result = {}
                    for mp_i, coco_i in MP_TO_COCO.items():
                        if mp_i >= len(lms): continue
                        lm = lms[mp_i]
                        fx = lm.x * fw + off_x
                        fy = lm.y * fh + off_y
                        frame_result[coco_i] = (fx, fy, 0.95)
                    if frame_result:
                        face_results[ri] = frame_result
        except Exception:
            cap.release()
            return 0
        cap.release()
        if not face_results: return 0
        # 全フレームを線形補間で補正
        sorted_ri = sorted(face_results.keys())
        corrected = 0
        for i, row in enumerate(rows):
            # 前後の Face Mesh サンプル
            before_ri = None; after_ri = None
            for ri in sorted_ri:
                if ri <= i: before_ri = ri
                if ri >= i and after_ri is None: after_ri = ri
            for coco_i in [0, 1, 2, 3, 4]:
                fx = fy = None
                if before_ri is not None and after_ri is not None:
                    if before_ri == after_ri:
                        if coco_i in face_results[before_ri]:
                            fx, fy, _ = face_results[before_ri][coco_i]
                    else:
                        b = face_results.get(before_ri, {}).get(coco_i)
                        a = face_results.get(after_ri, {}).get(coco_i)
                        if b and a:
                            t_b = rows[before_ri]["time"]
                            t_a = rows[after_ri]["time"]
                            t_c = row["time"]
                            if t_a > t_b:
                                w = (t_c - t_b) / (t_a - t_b)
                                fx = b[0] * (1-w) + a[0] * w
                                fy = b[1] * (1-w) + a[1] * w
                        elif b:
                            fx, fy = b[0], b[1]
                        elif a:
                            fx, fy = a[0], a[1]
                elif before_ri is not None:
                    b = face_results[before_ri].get(coco_i)
                    if b: fx, fy = b[0], b[1]
                elif after_ri is not None:
                    a = face_results[after_ri].get(coco_i)
                    if a: fx, fy = a[0], a[1]
                if fx is not None:
                    row[f"kp{coco_i:02d}_x"] = float(fx)
                    row[f"kp{coco_i:02d}_y"] = float(fy)
                    row[f"kp{coco_i:02d}_c"] = 0.95
                    corrected += 1
        return corrected


    # ══════════════════════════════════════════
    #  v61: MediaPipe 独立検出 (YOLO非依存)
    # ══════════════════════════════════════════
    MP_TO_COCO = {0:0, 2:1, 5:2, 7:3, 8:4, 11:5, 12:6, 13:7, 14:8,
                  15:9, 16:10, 23:11, 24:12, 25:13, 26:14, 27:15, 28:16}

    def _mp_model_path_or_download(self):
        """pose_landmarker モデルのパスを返す (無ければDL)"""
        app_dir = os.path.dirname(os.path.abspath(__file__))
        target = os.path.join(app_dir, "pose_landmarker_lite.task")
        if os.path.exists(target): return target
        try:
            import urllib.request
            url = ("https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
                   "pose_landmarker_lite/float16/latest/pose_landmarker_lite.task")
            self.status_var.set("MediaPipeモデルをダウンロード中…")
            urllib.request.urlretrieve(url, target)
            return target
        except Exception as e:
            print(f"[MPモデルDL失敗] {e}")
            return None

    def _run_mp_detect_bg(self, rank=None, on_done=None):
        """v61: 指定HPをMediaPipeで検出 (バックグラウンド)。
        2D座標をYOLO互換形式で _cp{rank}.json に保存 + 3Dを _mp3d.json に保存"""
        if rank is None:
            if not self.peaks or self.peak_idx >= len(self.peaks): return
            rank = self.peaks[self.peak_idx]["rank"]
        path = self.video_path.get()
        if not path: return
        p = next((x for x in self.peaks if x["rank"] == rank), None)
        if p is None: return
        hit_t = p.get("frame_time") or p["time"]
        gen = self._gen
        def _worker():
            try:
                self.after(0, lambda: self._set_di_status("mp", "⏳ 準備中…"))
                model_path = self._mp_model_path_or_download()
                if not model_path:
                    self.after(0, lambda: self._set_di_status("mp", "❌ モデルなし"))
                    return
                import mediapipe as mp
                from mediapipe.tasks.python import BaseOptions, vision
                cap = cv2.VideoCapture(path)
                fps_ = cap.get(cv2.CAP_PROP_FPS) or 30.0
                dt = 1.0 / fps_
                t0 = max(0, hit_t - 1.5); t1 = hit_t + 1.0
                times = []
                t = t0
                while t <= t1 + 1e-9:
                    times.append(t); t += dt
                opts = vision.PoseLandmarkerOptions(
                    base_options=BaseOptions(model_asset_path=model_path),
                    running_mode=vision.RunningMode.IMAGE, num_poses=1,
                    min_pose_detection_confidence=0.3)
                rows = []; mp3d = []
                with _suppress_stderr():
                    detector_cm = vision.PoseLandmarker.create_from_options(opts)
                with detector_cm as det:
                    for i, t in enumerate(times):
                        if self._gen != gen: break
                        cap.set(cv2.CAP_PROP_POS_FRAMES, int(t * fps_))
                        ok, bgr = cap.read()
                        if not ok: continue
                        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                        h, w = rgb.shape[:2]
                        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB,
                                          data=np.ascontiguousarray(rgb))
                        with _suppress_stderr():
                            res = det.detect(mp_img)
                        row = {"frame_idx": i, "time": float(t), "obj_conf": 0.0}
                        lm3d = []
                        if res.pose_landmarks:
                            lms = res.pose_landmarks[0]
                            xs = []; ys = []
                            for mp_i, coco_i in self.MP_TO_COCO.items():
                                if mp_i >= len(lms): continue
                                lm = lms[mp_i]
                                px = lm.x * w; py = lm.y * h
                                vis = getattr(lm, "visibility", 0.5)
                                row[f"kp{coco_i:02d}_x"] = float(px)
                                row[f"kp{coco_i:02d}_y"] = float(py)
                                row[f"kp{coco_i:02d}_c"] = float(max(0.35, vis))
                                xs.append(px); ys.append(py)
                            if xs:
                                mx = (max(xs)-min(xs))*0.15
                                my = (max(ys)-min(ys))*0.15
                                row["person_bbox"] = [min(xs)-mx, min(ys)-my,
                                                       max(xs)+mx, max(ys)+my]
                                row["obj_conf"] = 0.9
                        if res.pose_world_landmarks:
                            for lm in res.pose_world_landmarks[0]:
                                lm3d.append({"x": lm.x, "y": lm.y, "z": lm.z,
                                             "vis": getattr(lm, "visibility", 0.0)})
                        lm2d = []
                        if res.pose_landmarks:
                            for lm in res.pose_landmarks[0]:
                                lm2d.append({"x": lm.x * w, "y": lm.y * h,
                                             "vis": getattr(lm, "visibility", 0.0)})
                        mp3d.append({"frame_idx": i, "time": float(t),
                                     "landmarks": lm3d, "landmarks_2d": lm2d})
                        rows.append(row)
                        if i % 5 == 0:
                            self.after(0, lambda d=i, n=len(times):
                                self._set_di_status("mp", f"⏳ 検出中 ({d}/{n})"))
                cap.release()
                if not rows or self._gen != gen: return
                # 角度計算
                for r in rows:
                    try:
                        ang = self._calc_face_body_angles(r)
                        if ang:
                            for k, v in ang.items():
                                if k != "invisible_kps": r[k] = v
                    except Exception: pass
                # 保存: YOLO互換 _cp{rank}.json
                out_dir = self._yolo_out_dir(path)
                os.makedirs(out_dir, exist_ok=True)
                stem = os.path.splitext(os.path.basename(path))[0]
                out_path = os.path.join(out_dir, f"{stem}_cp{rank:02d}_mp.json")
                opt_t, opt_r = self._find_optimal_hit_frame(rows, hit_t, "")
                meta = {"video": os.path.basename(path), "cp_rank": rank,
                        "hit_time": float(hit_t), "model": "mediapipe",
                        "frames": rows}
                if opt_t is not None:
                    meta["optimal_hit_time"] = float(opt_t)
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(meta, f, ensure_ascii=False)
                # refined削除
                rp = out_path[:-5] + "_refined.json"
                if os.path.exists(rp):
                    try: os.remove(rp)
                    except Exception: pass
                # 3D保存
                mp3d_path = os.path.join(out_dir, f"{stem}_cp{rank:02d}_mp3d.json")
                with open(mp3d_path, "w", encoding="utf-8") as f:
                    json.dump({"version": "61", "ground_shift": 0.0,
                               "frames": mp3d}, f, ensure_ascii=False)
                self.after(0, lambda: self._set_di_status("mp", "✅ 完了"))
                self.after(0, self._update_detect_info)
                self.after(0, self._update_shot_list)
                if on_done: self.after(0, on_done)
            except Exception as e:
                print(f"[MP検出エラー] {e}")
                import traceback; traceback.print_exc()
                self.after(0, lambda: self._set_di_status("mp", f"❌ エラー"))
        threading.Thread(target=_worker, daemon=True).start()

    def _auto_mp_detect_all(self):
        """v61: 全HPをMediaPipeで順次検出 (mp_autoがONの場合)"""
        if not getattr(self, "_video_meta_extra", {}).get("mp_auto", True): return
        if not self.peaks: return
        ranks = [p["rank"] for p in self.peaks]
        self._mp_queue = list(ranks)
        def _next():
            if not self._mp_queue: 
                self.status_var.set("MediaPipe全HP検出完了")
                return
            r = self._mp_queue.pop(0)
            n_total = len(ranks); n_done = n_total - len(self._mp_queue)
            self.status_var.set(f"MediaPipe検出中… HP#{r} ({n_done}/{n_total})")
            self._run_mp_detect_bg(rank=r, on_done=_next)
        _next()

    def _set_di_status(self, key, text):
        """v61: 検出情報の特定行を更新"""
        try:
            if hasattr(self, "_di_vars") and key in self._di_vars:
                self._di_vars[key].set(text)
        except Exception: pass

    def _auto_kp_detect_by_mode(self):
        """v27: 動画情報ポップアップで選択したKP検出モードを自動実行。
           - ヒットポイントのみ: 全HPの打点1フレームをKP検出
           - ヒットポイント前後: 全HPの±0.3秒の全フレームをKP検出"""
        mode = getattr(self, "_video_meta_extra", {}).get("kp_mode", "不要")
        if mode == "不要" or not self.peaks: return
        try:
            from ultralytics import YOLO  # noqa
        except ImportError:
            self.status_var.set("KP自動検出スキップ (ultralytics未インストール)")
            return
        path = self.video_path.get()
        peaks_snapshot = list(self.peaks)
        gen = self._gen
        def _worker():
            try:
                from ultralytics import YOLO
                model_pose = YOLO("yolov8n-pose.pt")
                cap = cv2.VideoCapture(path)
                fps_ = cap.get(cv2.CAP_PROP_FPS) or 30
                stem = os.path.splitext(os.path.basename(path))[0]
                out_dir = self._yolo_out_dir(path)
                os.makedirs(out_dir, exist_ok=True)
                n_total = len(peaks_snapshot)
                for pi, p in enumerate(peaks_snapshot):
                    if self._gen != gen: break
                    rank = p["rank"]
                    hit_t = p.get("frame_time") or p["time"]
                    self.after(0, lambda r=rank, i=pi, n=n_total:
                        self.status_var.set(f"KP自動検出中… HP#{r} ({i+1}/{n})"))
                    if mode == "ヒットポイントのみ":
                        # v31: ±5フレーム (計11フレーム) を解析
                        dt = 1.0 / fps_
                        times = [hit_t + i * dt for i in range(-5, 6)]
                        out_path = os.path.join(out_dir, f"{stem}_cp{rank:02d}.json")
                    else:  # ヒットポイント前後 ±0.3s
                        dt = 1.0 / fps_
                        times = []
                        t = hit_t - 0.3
                        while t <= hit_t + 0.3 + 1e-9:
                            times.append(t); t += dt
                        out_path = os.path.join(out_dir, f"{stem}_cp{rank:02d}.json")
                    rows = []
                    for fi_, t in enumerate(times):
                        if self._gen != gen: break
                        cap.set(cv2.CAP_PROP_POS_FRAMES, int(t * fps_))
                        ret, frame = cap.read()
                        if not ret: continue
                        res = model_pose(frame, verbose=False, conf=0.25)
                        row = {"frame_idx": fi_, "time": float(t), "obj_conf": 0.0}
                        if res and res[0].keypoints is not None and len(res[0].keypoints.data) > 0:
                            boxes = res[0].boxes
                            if boxes is not None and len(boxes.xyxy) > 1:
                                bxyxy = boxes.xyxy.cpu().numpy()
                                areas = [(bxyxy[k][2]-bxyxy[k][0])*(bxyxy[k][3]-bxyxy[k][1])
                                         for k in range(len(bxyxy))]
                                best_j = int(np.argmax(areas))
                            else:
                                best_j = 0
                            kps = res[0].keypoints.data[best_j].cpu().numpy()
                            if boxes is not None and len(boxes.conf) > best_j:
                                row["obj_conf"] = float(boxes.conf[best_j])
                                bb = boxes.xyxy.cpu().numpy()[best_j]
                                row["person_bbox"] = [float(v) for v in bb]
                            for ki in range(min(17, len(kps))):
                                row[f"kp{ki:02d}_x"] = float(kps[ki, 0])
                                row[f"kp{ki:02d}_y"] = float(kps[ki, 1])
                                row[f"kp{ki:02d}_c"] = float(kps[ki, 2])
                        # v30: 顔・体の向き角度を計算
                        angles = self._calc_face_body_angles(row)
                        if angles:
                            for ak, av in angles.items():
                                if ak != "invisible_kps":
                                    row[ak] = av
                            # 見えないKPの信頼度を下げる
                            for ik in angles.get("invisible_kps", set()):
                                if row.get(f"kp{ik:02d}_c", 0) > 0:
                                    row[f"kp{ik:02d}_c"] = min(row.get(f"kp{ik:02d}_c", 0), 0.25)
                        rows.append(row)
                    if rows and self._gen == gen:
                        # v42: Face Mesh で顔KP高精度化 (0.5秒間隔)
                        try:
                            n_fm = self._apply_face_mesh_correction(rows, path, hit_t, 0.5)
                            if n_fm > 0:
                                self.after(0, lambda n=n_fm, r=rank: self.status_var.set(
                                    f"HP#{r} Face Mesh補正: {n}件"))
                        except Exception as fme:
                            print(f"Face Mesh補正スキップ: {fme}")
                        # v39: ヒットフレーム最適選択
                        shot_type = ""
                        try:
                            shot_type = (p.get("shot_type") or
                                         ",".join(getattr(self, "_video_meta_extra", {}).get("main_shots", [])))
                        except Exception: pass
                        opt_t, opt_reason = self._find_optimal_hit_frame(rows, hit_t, shot_type)
                        save_data = {"hit_time": float(hit_t), "rank": rank,
                                     "frames": rows}
                        if opt_t is not None:
                            save_data["optimal_hit_time"] = float(opt_t)
                            save_data["optimal_hit_reason"] = opt_reason
                        with open(out_path, "w", encoding="utf-8") as f:
                            json.dump(save_data, f, ensure_ascii=False)
                        # v39: 古いrefined版は無効化 (再検出で置換)
                        refined_path = out_path[:-5] + "_refined.json"
                        if os.path.exists(refined_path):
                            try: os.remove(refined_path)
                            except Exception: pass
                cap.release()
                if self._gen == gen:
                    self.after(0, lambda: self.status_var.set(
                        f"KP自動検出完了: {n_total} HP ({mode})"))
            except Exception as e:
                self.after(0, lambda err=e: self.status_var.set(f"KP自動検出エラー: {err}"))
        threading.Thread(target=_worker, daemon=True).start()

    def _run_yolo_current_cp(self):
        if not self.peaks or self.peak_idx>=len(self.peaks):
            messagebox.showinfo("キーポイント検出","ヒットポイントを選択してください"); return
        # ultralytics 依存チェック
        try:
            from ultralytics import YOLO  # noqa
        except ImportError:
            messagebox.showerror("キーポイント検出",
                "ultralytics がインストールされていません。\n"
                "  pip install ultralytics\n"
                "を実行してから再試行してください。\n\n"
                "推奨モデル: yolov8n-pose.pt (姿勢) + yolov8n.pt (ボール/ラケット)")
            return
        threading.Thread(target=self._yolo_worker,daemon=True).start()

    def _run_yolo_hit_frame(self):
        """v24: 現在HPの打点フレーム1枚だけキーポイント検出"""
        if not self.peaks or self.peak_idx>=len(self.peaks):
            messagebox.showinfo("キーポイント検出","ヒットポイントを選択してください"); return
        try:
            from ultralytics import YOLO
        except ImportError:
            messagebox.showerror("キーポイント検出",
                "ultralytics がインストールされていません。\n  pip install ultralytics"); return
        path=self.video_path.get()
        p=self.peaks[self.peak_idx]
        rank=p["rank"]
        hit_t=p.get("frame_time") or p["time"]
        self.status_var.set(f"HP#{rank} ヒットポイント検出中…")
        def _worker():
            try:
                model_pose=YOLO("yolov8n-pose.pt")
                cap=cv2.VideoCapture(path)
                fps_=cap.get(cv2.CAP_PROP_FPS) or 30
                cap.set(cv2.CAP_PROP_POS_FRAMES,int(hit_t*fps_))
                ret,frame=cap.read()
                cap.release()
                if not ret:
                    self.after(0,lambda: self.status_var.set("フレーム取得失敗")); return
                res=model_pose(frame,verbose=False,conf=0.25)
                row={"frame_idx":0,"time":hit_t,"obj_conf":0.0}
                if res and res[0].keypoints is not None and len(res[0].keypoints.data)>0:
                    # v25: 最大バウンディングボックスの人物を選択
                    boxes=res[0].boxes
                    if boxes is not None and len(boxes.xyxy)>1:
                        bxyxy=boxes.xyxy.cpu().numpy()
                        areas=[(bxyxy[k][2]-bxyxy[k][0])*(bxyxy[k][3]-bxyxy[k][1])
                               for k in range(len(bxyxy))]
                        best_j=int(np.argmax(areas))
                    else:
                        best_j=0
                    kps=res[0].keypoints.data[best_j].cpu().numpy()
                    if boxes is not None and len(boxes.conf)>best_j:
                        row["obj_conf"]=float(boxes.conf[best_j])
                    for ki in range(min(17,len(kps))):
                        row[f"kp{ki:02d}_x"]=float(kps[ki,0])
                        row[f"kp{ki:02d}_y"]=float(kps[ki,1])
                        row[f"kp{ki:02d}_c"]=float(kps[ki,2]) if kps.shape[1]>2 else 0.0
                # 保存 (yolo/ ディレクトリに _hp<rank>.json)
                out_dir=self._yolo_out_dir(path)
                os.makedirs(out_dir,exist_ok=True)
                stem=os.path.splitext(os.path.basename(path))[0]
                out_path=os.path.join(out_dir,f"{stem}_hp{rank:02d}.json")
                import json
                out_data={"video":os.path.basename(path),"hp_rank":rank,
                          "hit_time":hit_t,"single_frame":True,
                          "frames":[row]}
                with open(out_path,"w",encoding="utf-8") as f:
                    json.dump(out_data,f,ensure_ascii=False,indent=1)
                self.after(0,lambda: self.status_var.set(
                    f"HP#{rank} 検出完了 → {os.path.basename(out_path)}"))
            except Exception as e:
                self.after(0,lambda err=e: self.status_var.set(f"検出エラー: {err}"))
        threading.Thread(target=_worker,daemon=True).start()

    def _display_hp_single_frame(self,hp_path,video_path,rank):
        """v25: HP 単一フレーム検出データを大きく表示 + KPマーカー"""
        import json
        try:
            with open(hp_path,"r",encoding="utf-8") as f:
                hp_data=json.load(f)
        except Exception as e:
            self.yolo_status.set(f"HP データ読込失敗: {e}"); return
        frames=hp_data.get("frames",[])
        if not frames:
            self.yolo_status.set("HP フレームが空"); return
        row=frames[0]
        hit_t=hp_data.get("hit_time",0.0)
        obj_conf=row.get("obj_conf",0.0)
        # フレームを動画から取得
        cap=cv2.VideoCapture(video_path)
        fps_=cap.get(cv2.CAP_PROP_FPS) or 30
        cap.set(cv2.CAP_PROP_POS_FRAMES,int(hit_t*fps_))
        ret,frame=cap.read()
        cap.release()
        if not ret:
            self.yolo_status.set("フレーム取得失敗"); return
        # KP マーカー描画
        rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        img=Image.fromarray(rgb)
        draw=ImageDraw.Draw(img,"RGBA")
        kp_colors=self.YOLO_KP_COLORS
        selected_kps={i for i,v in enumerate(self._yolo_kp_vars) if v.get()}
        for ki in range(20):
            if ki not in selected_kps: continue
            kx=row.get(f"kp{ki:02d}_x"); ky=row.get(f"kp{ki:02d}_y")
            kc=row.get(f"kp{ki:02d}_c",0)
            if kx is None or ky is None or (kc or 0)<0.3: continue
            color=kp_colors[ki] if ki<len(kp_colors) else "#fff"
            r=8
            if ki==19:  # 重心は★
                self._draw_star_pil(draw,kx,ky,r,color)
            else:
                draw.ellipse([kx-r,ky-r,kx+r,ky+r],fill=color,outline="white",width=2)
            # ラベル表示
            name=self.YOLO_EXT_NAMES[ki] if ki<len(self.YOLO_EXT_NAMES) else ""
            if name:
                try:
                    draw.text((kx+r+2,ky-r),name,fill=color)
                except Exception: pass
        # 前の描画を消す (連続写真エリア + チャートエリア)
        if self._yolo_canvas:
            self._yolo_canvas.get_tk_widget().destroy()
            self._yolo_canvas=None
        for ch in self.yolo_plot_frame.winfo_children():
            try: ch.destroy()
            except Exception: pass
        for ch in self.yolo_cs_grid.winfo_children():
            try: ch.destroy()
            except Exception: pass
        self._yolo_photo_refs.clear()
        # v25: 連続写真エリアに大きく表示
        self._yolo_cs_canvas.update_idletasks()
        avail_w=max(self._yolo_cs_canvas.winfo_width()-20, 400)
        avail_h=max(self._yolo_cs_canvas.winfo_height()-20, 300)
        scale=min(avail_w/img.width, avail_h/img.height, 1.0)
        disp_w=int(img.width*scale); disp_h=int(img.height*scale)
        img_disp=img.resize((disp_w,disp_h),Image.LANCZOS)
        photo=ImageTk.PhotoImage(img_disp)
        self._yolo_photo_refs.append(photo)
        lbl=tk.Label(self.yolo_cs_grid,image=photo,bg=BG)
        lbl.pack(pady=8)
        self.yolo_status.set(
            f"HP#{rank} ヒットポイント検出済: 人物信頼度 {obj_conf:.0%}  "
            f"(打点 t={hit_t:.2f}s)")

    def _estimate_racket_tip(self, bbox, wx, wy, arm_dx=0.0, arm_dy=0.0):
        """v24: ラケット先端推定。
        手首と肘→手首方向 (arm_dx, arm_dy) を用いて、bbox の4角を腕方向に射影、
        最遠2角の中点を返す (斜めに振った時も追従)。
        wx,wy が None なら bbox の中心から最も離れた角を返す。"""
        x1,y1,x2,y2=bbox
        corners=[(x1,y1),(x2,y1),(x1,y2),(x2,y2)]
        if wx is None or wy is None:
            cx,cy=(x1+x2)/2,(y1+y2)/2
            best=max(corners,key=lambda c:(c[0]-cx)**2+(c[1]-cy)**2)
            return (best[0],best[1])
        # 腕方向ベクトルがあれば、手首から各角への射影
        if abs(arm_dx)+abs(arm_dy)>0.01:
            projections=[]
            for cx,cy in corners:
                p=(cx-wx)*arm_dx+(cy-wy)*arm_dy
                projections.append(p)
            order=sorted(range(4),key=lambda i:-projections[i])
            c1=corners[order[0]]; c2=corners[order[1]]
            return ((c1[0]+c2[0])/2,(c1[1]+c2[1])/2)
        # 腕方向不明 → 手首から最遠の角
        best=max(corners,key=lambda c:(c[0]-wx)**2+(c[1]-wy)**2)
        return (best[0],best[1])

    def _load_learning_stats(self):
        """v24: 学習DBから ショット種別/カメラ向き別の統計を取得し
        self._learning_stats にキャッシュ"""
        try:
            import learning_db as LDB
        except Exception:
            self._learning_stats={}
            return
        shot=getattr(self,"_meta_current_shot",None)
        cam=(self._last_cam[0] if self._last_cam else None)
        try:
            self._learning_stats=LDB.get_stats(
                shot_type=shot,camera_dir=cam,min_samples=3)
        except Exception:
            self._learning_stats={}

    def _apply_face_correction(self,row,kp_th=0.30):
        """v17: YOLO出力の顔KPに幾何整合性チェック。
           規則1: 耳の体からの距離が肩幅×2.5を超えたら除去。
           規則2: 両耳とも残っていれば、鼻/目が耳のX範囲+20%を外れたら除去。
           除去された点は元値を kpNN_yolo_raw に退避してから None に。"""
        def _g(k):
            return (row.get(f"kp{k:02d}_x"),
                    row.get(f"kp{k:02d}_y"),
                    row.get(f"kp{k:02d}_c",0) or 0)
        def _suppress(k):
            ox,oy,oc=_g(k)
            if ox is None: return
            row[f"kp{k:02d}_yolo_raw"]=[float(ox),float(oy),float(oc)]
            row[f"kp{k:02d}_x"]=None
            row[f"kp{k:02d}_y"]=None
            row[f"kp{k:02d}_c"]=0.0
        s5x,s5y,s5c=_g(5); s6x,s6y,s6c=_g(6)
        if s5x is None or s6x is None or s5c<kp_th or s6c<kp_th:
            return
        sh_mid_x=(s5x+s6x)/2.0
        sh_mid_y=(s5y+s6y)/2.0
        sh_w=math.hypot(s5x-s6x,s5y-s6y)
        if sh_w<1.0: return
        # 規則1: 耳の体からの距離
        for ek in (3,4):
            ex,ey,_=_g(ek)
            if ex is None: continue
            if math.hypot(ex-sh_mid_x,ey-sh_mid_y) > sh_w*2.5:
                _suppress(ek)
        # 規則2: 顔点 (両耳とも残っていれば)
        lex,ley,_=_g(3); rex,rey,_=_g(4)
        if lex is not None and rex is not None:
            ear_xmin=min(lex,rex); ear_xmax=max(lex,rex)
            ear_d=abs(lex-rex); ear_ym=(ley+rey)/2.0
            margin_x=max(ear_d*0.20,8.0)
            margin_y=max(ear_d*1.0,30.0)
            for fk in (0,1,2):
                fx,fy,_=_g(fk)
                if fx is None: continue
                if (fx<ear_xmin-margin_x or fx>ear_xmax+margin_x or
                    abs(fy-ear_ym)>margin_y):
                    _suppress(fk)

    def _yolo_worker(self):
        from ultralytics import YOLO
        path=self.video_path.get()
        p=self.peaks[self.peak_idx]
        rank=p["rank"]
        hit_t=p.get("frame_time") or p["time"]

        # v24: 現在のHPのショット種別を取得 (学習DB照会用)
        try:
            db_path=get_db_path(path)
            lbl=load_label(db_path,os.path.basename(path),rank)
            self._meta_current_shot=lbl.get("shot_type") if lbl else None
        except Exception:
            self._meta_current_shot=None
        # v24: 学習DB統計をロード (この CP の解析中、参照に使う)
        self._load_learning_stats()

        # 古い出力 (json/refined/xlsx) を削除して上書き
        out_dir=self._yolo_out_dir(path)
        os.makedirs(out_dir,exist_ok=True)
        stem=os.path.splitext(os.path.basename(path))[0]
        prefix=f"{stem}_cp{rank:02d}"
        wiped=0
        for fn in os.listdir(out_dir):
            if fn.startswith(prefix):
                try:
                    os.remove(os.path.join(out_dir,fn)); wiped+=1
                except Exception: pass
        if wiped:
            self.after(0,lambda w=wiped: self.status_var.set(f"古いキーポイント検出出力 {w} 件を削除"))

        self.status_var.set("キーポイント検出モデル読込中…")
        # モデルはキャッシュ
        if not hasattr(self,"_yolo_pose"):
            try:
                self._yolo_pose=YOLO("yolov8n-pose.pt")
                self._yolo_obj =YOLO("yolov8n.pt")
            except Exception as e:
                err=str(e)
                self.after(0,lambda err=err: messagebox.showerror("キーポイント検出",
                    f"モデル読込に失敗しました:\n{err}\n\n"
                    "初回はモデル (yolov8n-pose.pt, yolov8n.pt) を自動ダウンロードします。\n"
                    "ネットワーク・ファイアウォール設定を確認するか、\n"
                    "事前に https://github.com/ultralytics/assets/releases から\n"
                    "上記2ファイルをダウンロードして同フォルダに置いてください。"))
                return
        # 時刻リスト: hit-2s 〜 hit+1s, 0.05s
        ts=[round(hit_t+k*0.05,3) for k in range(-40,21) if hit_t+k*0.05>=0]
        results=[]
        cap=cv2.VideoCapture(path)
        fps_=cap.get(cv2.CAP_PROP_FPS) or 30
        for i,t in enumerate(ts):
            cap.set(cv2.CAP_PROP_POS_FRAMES,int(fps_*t))
            ok,frame=cap.read()
            if not ok: continue
            # クロップ領域に限定 (関係ない人を拾わない)
            cx_off=cy_off=0
            rect=self._active_crop_rect(t)
            if rect is not None:
                fh,fw=frame.shape[:2]
                x1r,y1r,x2r,y2r=rect
                cx1=int(min(x1r,x2r)*fw); cy1=int(min(y1r,y2r)*fh)
                cx2=int(max(x1r,x2r)*fw); cy2=int(max(y1r,y2r)*fh)
                if cx2>cx1 and cy2>cy1:
                    frame=frame[cy1:cy2,cx1:cx2]
                    cx_off,cy_off=cx1,cy1
            row={"time":t,"crop_offset":[cx_off,cy_off]}
            # 姿勢
            r_pose=self._yolo_pose(frame,verbose=False)[0]
            person=None
            if len(r_pose.boxes)>0:
                # v25: 最大バウンディングボックス (面積) の人物を選択
                boxes_xyxy=r_pose.boxes.xyxy.cpu().numpy()
                areas=[(boxes_xyxy[k][2]-boxes_xyxy[k][0])*(boxes_xyxy[k][3]-boxes_xyxy[k][1])
                       for k in range(len(boxes_xyxy))]
                j=int(np.argmax(areas))
                box=r_pose.boxes.xyxy[j].cpu().numpy().tolist()
                # 元動画座標系に戻す
                box=[box[0]+cx_off,box[1]+cy_off,box[2]+cx_off,box[3]+cy_off]
                kps =r_pose.keypoints.data[j].cpu().numpy()
                row["person_bbox"]=box
                row["person_conf"]=float(r_pose.boxes.conf[j])
                for k in range(17):
                    x=float(kps[k,0])+cx_off
                    y=float(kps[k,1])+cy_off
                    c=float(kps[k,2])
                    row[f"kp{k:02d}_x"]=x; row[f"kp{k:02d}_y"]=y; row[f"kp{k:02d}_c"]=c
                person=(box,kps)
                # 顔KPの幾何整合性チェック (V17)
                self._apply_face_correction(row, kp_th=0.30)
            # 物体検出 (ball=32, racket=38)
            r_obj=self._yolo_obj(frame,verbose=False,conf=0.1)[0]
            cls=r_obj.boxes.cls.cpu().numpy() if len(r_obj.boxes)>0 else np.array([])
            cnf=r_obj.boxes.conf.cpu().numpy() if len(r_obj.boxes)>0 else np.array([])
            xy =r_obj.boxes.xyxy.cpu().numpy() if len(r_obj.boxes)>0 else np.zeros((0,4))
            # ラケット候補 (cls=38) — 上位3つ
            ridx=sorted([k for k,c in enumerate(cls) if int(c)==38],
                        key=lambda k: -cnf[k])[:3]
            cand_list=[]  # v24: 候補を蓄積して再ランク付け
            for n_r,k in enumerate(ridx,1):
                bb=xy[k].tolist()
                bb=[bb[0]+cx_off,bb[1]+cy_off,bb[2]+cx_off,bb[3]+cy_off]
                row[f"racket{n_r}_bbox"]=bb
                row[f"racket{n_r}_conf"]=float(cnf[k])
                cand_list.append({"bbox":bb,"conf":float(cnf[k])})
            if cand_list:
                # v24: 改良アルゴリズム — 信頼度のみではなく、手首近接度・
                # アスペクト・時間連続性・学習DB分布の4軸でスコアし最良を選択
                # 先端推定も「腕の延長線への射影で最遠2角の中点」に変更
                wx,wy=None,None
                arm_dx,arm_dy=0.0,0.0
                shot_type=getattr(self,"_meta_current_shot",None)
                cam_dir=(self._last_cam[0] if self._last_cam else None)
                if person is not None:
                    box,kps=person
                    lw,rw=kps[9],kps[10]
                    le,re=kps[7],kps[8]
                    if rw[2]>=lw[2]:
                        wx,wy=rw[0]+cx_off,rw[1]+cy_off
                        ex,ey=re[0]+cx_off,re[1]+cy_off
                    else:
                        wx,wy=lw[0]+cx_off,lw[1]+cy_off
                        ex,ey=le[0]+cx_off,le[1]+cy_off
                    nrm=math.hypot(wx-ex,wy-ey)
                    if nrm>1:
                        arm_dx=(wx-ex)/nrm; arm_dy=(wy-ey)/nrm
                # 前フレームの先端 (時間連続性用)
                prev_tip=None
                if results and "racket_tip_x" in results[-1]:
                    prev_tip=(results[-1]["racket_tip_x"],results[-1]["racket_tip_y"])
                # 学習DB統計
                rstats=self._learning_stats.get(17) if hasattr(self,"_learning_stats") else None
                nose_pos=None; pixel_h=None
                if person is not None:
                    box,kps=person
                    if kps[0,2]>=0.3:
                        nose_pos=(kps[0,0]+cx_off,kps[0,1]+cy_off)
                    la,ra=kps[15],kps[16]
                    if kps[0,2]>=0.3 and (la[2]>=0.3 or ra[2]>=0.3):
                        ay=la[1] if la[2]>ra[2] else ra[1]
                        pixel_h=abs((ay+cy_off)-(kps[0,1]+cy_off))
                        if pixel_h<10: pixel_h=None

                best_score=-1e9; best_tip=None; best_cand_idx=-1
                for ci,c in enumerate(cand_list):
                    x1,y1,x2,y2=c["bbox"]
                    cx_b,cy_b=(x1+x2)/2,(y1+y2)/2
                    w_=x2-x1; h_=y2-y1
                    # 1. YOLO信頼度
                    s_conf=c["conf"]
                    # 2. 手首近接度 (距離が近いほど高スコア)
                    if wx is not None:
                        d_w=math.hypot(cx_b-wx,cy_b-wy)
                        # 体高があれば正規化、なければ400px基準
                        ref=max(200.0, pixel_h or 0)
                        s_wrist=max(0.0,1.0 - d_w/(ref*0.9))
                    else:
                        s_wrist=0.4
                    # 3. アスペクト (ラケットは縦長)
                    aspect=max(w_,h_)/max(1.0,min(w_,h_))
                    s_aspect=1.0 if 1.2<=aspect<=4.5 else 0.4
                    # 4. 時間連続性 (前フレームの先端に近い候補を優遇)
                    s_time=0.5
                    if prev_tip is not None:
                        d_t=math.hypot(cx_b-prev_tip[0],cy_b-prev_tip[1])
                        ref=max(200.0, pixel_h or 0)
                        s_time=max(0.0,1.0 - d_t/(ref*0.7))
                    # 候補の先端を腕方向で推定
                    tip_xy=self._estimate_racket_tip(c["bbox"],wx,wy,arm_dx,arm_dy)
                    # 5. 学習DB分布スコア (低いほど典型 → 高スコア化)
                    s_learn=0.5
                    if rstats and tip_xy:
                        try:
                            from learning_db import score_position
                            dev=score_position(rstats,tip_xy[0],tip_xy[1],
                                               nose_x=nose_pos[0] if nose_pos else None,
                                               nose_y=nose_pos[1] if nose_pos else None,
                                               wrist_x=wx,wrist_y=wy,pixel_h=pixel_h)
                            # 0 → 1.0, 2 → 0.5, 5+ → ~0
                            s_learn=max(0.0,1.0/(1.0+dev*0.5))
                        except Exception: pass
                    # 合計スコア
                    score=(0.35*s_conf + 0.30*s_wrist + 0.10*s_aspect
                           + 0.10*s_time + 0.15*s_learn)
                    if score>best_score:
                        best_score=score; best_tip=tip_xy; best_cand_idx=ci

                # 採用された候補の bbox を racket_bbox としても保存
                row["racket_bbox"]=cand_list[best_cand_idx]["bbox"]
                row["racket_conf"]=cand_list[best_cand_idx]["conf"]
                row["racket_tip_score"]=float(best_score)
                row["racket_picked_idx"]=best_cand_idx  # デバッグ用
                if best_tip is not None:
                    row["racket_tip_x"]=best_tip[0]
                    row["racket_tip_y"]=best_tip[1]
            # ボール (cls=32) — 上位3つ
            bidx=sorted([k for k,c in enumerate(cls) if int(c)==32],
                        key=lambda k: -cnf[k])[:3]
            for n,k in enumerate(bidx,1):
                bb=xy[k].tolist()
                bb=[bb[0]+cx_off,bb[1]+cy_off,bb[2]+cx_off,bb[3]+cy_off]
                row[f"ball{n}_bbox"]=bb
                row[f"ball{n}_conf"]=float(cnf[k])
            results.append(row)
            if i%5==0:
                self.after(0,lambda i=i: self.status_var.set(
                    f"キーポイント検出中… {i+1}/{len(ts)}"))
        cap.release()
        # v42: Face Mesh で顔KP高精度化 (0.5秒間隔)
        try:
            n_fm = self._apply_face_mesh_correction(results, path, hit_t, 0.5)
            if n_fm > 0:
                self.after(0, lambda n=n_fm: self.status_var.set(
                    f"Face Mesh補正: {n}件"))
        except Exception as fme:
            print(f"Face Mesh補正スキップ: {fme}")
        # JSON 出力
        meta={"video":os.path.basename(path),"cp_rank":rank,
              "hit_time":hit_t,"model":"yolov8n-pose + yolov8n",
              "kp_names":self.YOLO_KP_NAMES,"frames":results}
        # v39: ヒットフレーム最適選択
        try:
            shot_type = ",".join(getattr(self, "_video_meta_extra", {}).get("main_shots", []))
            opt_t, opt_reason = self._find_optimal_hit_frame(results, hit_t, shot_type)
            if opt_t is not None:
                meta["optimal_hit_time"] = float(opt_t)
                meta["optimal_hit_reason"] = opt_reason
                self.after(0, lambda t=opt_t, r=opt_reason: self.status_var.set(
                    f"最適HP推定: {t:.3f}s ({r}, 音声HP: {hit_t:.3f}s)"))
        except Exception: pass
        # v62: YOLO専用ファイル
        outf = self._kp_data_file(path, rank, source="yolo")
        with open(outf,"w",encoding="utf-8") as f:
            json.dump(meta,f,ensure_ascii=False,indent=1)
        # v39: 古いrefined版を削除
        refined_path = outf[:-5] + "_refined.json"
        if os.path.exists(refined_path):
            try: os.remove(refined_path)
            except Exception: pass
        # v56: 検出情報を更新
        self.after(0, lambda: self._update_detect_info())
        # Excel 出力 (pandas)
        try:
            import pandas as pd
            df=pd.DataFrame(results)
            xlsx=outf.replace(".json",".xlsx")
            df.to_excel(xlsx,index=False)
        except Exception as e:
            print("xlsx export failed:",e)
        self.after(0,lambda: self.status_var.set(
            f"キーポイント検出完了: {len(results)}フレーム → {os.path.basename(outf)}"))
        self.after(0,self._update_yolo_dropdowns)
        # v23: アイコン更新 + レジストリ更新
        self.after(0,self._update_shot_list)
        self.after(0,self._update_registry)

    # ══════════════════════════════════════════
    #  YOLO 解析タブ (v14 — ホバー & 重心 & しきい値)
    # ══════════════════════════════════════════
    def _build_tab_yolo(self,parent):
        # ホバー状態
        self._yolo_hover_kp = -1
        self._yolo_hover_clear_id = None
        self._yolo_cs_extract_key = None
        self._yolo_cs_extracted = []
        self._yolo_hover_vline = None

        # ── 右パネル: キーポイント選択 ──
        right=tk.Frame(parent,bg=PANEL,width=210)
        right.pack(side="right",fill="y",padx=(2,4),pady=4)
        right.pack_propagate(False)
        tk.Label(right,text="キーポイント",bg=PANEL,fg=ACCENT2,
                 font=_tk_font(11,bold=True)).pack(pady=(8,2),anchor="w",padx=8)
        tk.Label(right,text="(複数選択可・ホバーで強調)",bg=PANEL,fg=SUBTEXT,
                 font=_tk_font(8)).pack(pady=(0,4),anchor="w",padx=8)

        kp_outer=tk.Frame(right,bg=PANEL)
        kp_outer.pack(fill="both",expand=True,padx=4,pady=2)
        canvas_kp=tk.Canvas(kp_outer,bg=PANEL,highlightthickness=0)
        sb=tk.Scrollbar(kp_outer,orient="vertical",command=canvas_kp.yview)
        canvas_kp.configure(yscrollcommand=sb.set)
        sb.pack(side="right",fill="y")
        canvas_kp.pack(side="left",fill="both",expand=True)
        kp_inner=tk.Frame(canvas_kp,bg=PANEL)
        canvas_kp.create_window((0,0),window=kp_inner,anchor="nw")
        kp_inner.bind("<Configure>",
            lambda e: canvas_kp.configure(scrollregion=canvas_kp.bbox("all")))

        self._yolo_kp_vars=[]
        defaults={10,17,18,19}   # 右手首, ラケ先, ボール, 重心
        for i,name in enumerate(self.YOLO_EXT_NAMES):
            row=tk.Frame(kp_inner,bg=PANEL)
            row.pack(fill="x",padx=2,pady=1)
            var=tk.BooleanVar(value=(i in defaults))
            self._yolo_kp_vars.append(var)
            cb=tk.Checkbutton(row,variable=var,bg=PANEL,fg=TEXT,
                              activebackground=PANEL,selectcolor=DARK2,
                              command=self._yolo_redraw_overlays)
            cb.pack(side="left")
            color=self.YOLO_KP_COLORS[i] if i<len(self.YOLO_KP_COLORS) else "#888"
            c=tk.Canvas(row,width=16,height=16,bg=PANEL,highlightthickness=0)
            # v58: KP形状対応
            kp_sh = KP_SHAPES[i] if i < len(KP_SHAPES) else "circle"
            _draw_kp_shape_canvas(c, kp_sh, 8, 8, 6, fill=color, outline="white", width=1)
            c.pack(side="left",padx=(2,4))
            lbl=tk.Label(row,text=name,bg=PANEL,fg=TEXT,font=_tk_font(9),anchor="w")
            lbl.pack(side="left",fill="x",expand=True)
            # ホバー検出: 行内の全ウィジェットでEnter/Leaveをトリガ
            for w in (row,cb,c,lbl):
                w.bind("<Enter>",lambda e,idx=i: self._yolo_set_kp_hover(idx))
                w.bind("<Leave>",lambda e,idx=i: self._yolo_clear_kp_hover(idx))

        bf=tk.Frame(right,bg=PANEL); bf.pack(fill="x",padx=4,pady=4)
        tk.Button(bf,text="全選択",bg=DARK2,fg=TEXT,relief="flat",font=_tk_font(8),
                  command=self._yolo_select_all,cursor="hand2"
                  ).pack(side="left",padx=2,fill="x",expand=True)
        tk.Button(bf,text="全解除",bg=DARK2,fg=TEXT,relief="flat",font=_tk_font(8),
                  command=self._yolo_clear_all,cursor="hand2"
                  ).pack(side="left",padx=2,fill="x",expand=True)

        # ── メインエリア ──
        main_area=tk.Frame(parent,bg=BG)
        main_area.pack(side="left",fill="both",expand=True)

        # コントロール
        ctrl=tk.Frame(main_area,bg=PANEL2); ctrl.pack(fill="x",padx=8,pady=4)
        # v25: CPプルダウン廃止 → メインHPリスト連動 (現在HP表示ラベル)
        tk.Label(ctrl,text="HP:",bg=PANEL2,fg=TEXT,font=_tk_font(9)
                 ).pack(side="left",padx=(6,2))
        self.yolo_hp_lbl=tk.Label(ctrl,text="-",bg=PANEL2,fg=ACCENT2,
                                   font=_tk_font(9,bold=True))
        self.yolo_hp_lbl.pack(side="left",padx=(0,8))

        # v22: スライダー → プルダウン (操作性向上)
        start_vals=[f"{-x/10:.1f}" for x in range(0,21)]    # 0.0 〜 -2.0
        end_vals  =[f"{x/10:.1f}" for x in range(0,21)]     # 0.0 〜 2.0
        iv_vals   =["0.05","0.10","0.15","0.20","0.25","0.30","0.40","0.50"]

        tk.Label(ctrl,text="開始:",bg=PANEL2,fg=TEXT,font=_tk_font(9)).pack(side="left")
        self.yolo_start=tk.DoubleVar(value=-1.0)
        self.yolo_start_cb=ttk.Combobox(ctrl,values=start_vals,width=5,
                                        state="readonly",font=_tk_font(9))
        self.yolo_start_cb.set("-1.0")
        self.yolo_start_cb.pack(side="left",padx=(2,6))
        def _on_yolo_start(*_):
            try: self.yolo_start.set(float(self.yolo_start_cb.get()))
            except Exception: pass
        self.yolo_start_cb.bind("<<ComboboxSelected>>",_on_yolo_start)

        tk.Label(ctrl,text="終了:",bg=PANEL2,fg=TEXT,font=_tk_font(9)).pack(side="left")
        self.yolo_end=tk.DoubleVar(value=1.0)
        self.yolo_end_cb=ttk.Combobox(ctrl,values=end_vals,width=5,
                                      state="readonly",font=_tk_font(9))
        self.yolo_end_cb.set("1.0")
        self.yolo_end_cb.pack(side="left",padx=(2,6))
        def _on_yolo_end(*_):
            try: self.yolo_end.set(float(self.yolo_end_cb.get()))
            except Exception: pass
        self.yolo_end_cb.bind("<<ComboboxSelected>>",_on_yolo_end)

        tk.Label(ctrl,text="間隔:",bg=PANEL2,fg=TEXT,font=_tk_font(9)).pack(side="left")
        self.yolo_interval=tk.DoubleVar(value=0.1)
        self.yolo_iv_cb=ttk.Combobox(ctrl,values=iv_vals,width=5,
                                     state="readonly",font=_tk_font(9))
        self.yolo_iv_cb.set("0.10")
        self.yolo_iv_cb.pack(side="left",padx=(2,6))
        def _on_yolo_iv(*_):
            try: self.yolo_interval.set(float(self.yolo_iv_cb.get()))
            except Exception: pass
        self.yolo_iv_cb.bind("<<ComboboxSelected>>",_on_yolo_iv)

        tk.Label(ctrl,text="倍率:",bg=PANEL2,fg=TEXT,font=_tk_font(9)).pack(side="left")
        self.yolo_scale=ttk.Combobox(ctrl,width=4,state="readonly",font=_tk_font(9),
                                     values=[f"{x/10:.1f}x" for x in range(10,21)])
        self.yolo_scale.current(3)   # 1.3x
        self.yolo_scale.pack(side="left",padx=(0,6))

        tk.Label(ctrl,text="軸:",bg=PANEL2,fg=TEXT,font=_tk_font(9)).pack(side="left",padx=(6,2))
        self.yolo_axis=ttk.Combobox(ctrl,width=3,state="readonly",font=_tk_font(9),
                                    values=["y","x"])
        self.yolo_axis.current(0); self.yolo_axis.pack(side="left",padx=(0,6))

        # v23: px/cm 切替
        self.yolo_use_cm=tk.BooleanVar(value=False)
        tk.Checkbutton(ctrl,text="cm表示",variable=self.yolo_use_cm,
                       bg=PANEL2,fg=GOLD,activebackground=PANEL2,selectcolor=DARK2,
                       font=_tk_font(9,bold=True),
                       command=lambda: self._yolo_plot()
                       ).pack(side="left",padx=(4,6))

        tk.Label(ctrl,text="精度:",bg=PANEL2,fg=TEXT,font=_tk_font(9)).pack(side="left",padx=(6,2))
        self.yolo_thresh=ttk.Combobox(ctrl,width=5,state="readonly",font=_tk_font(9),
                                       values=list(self.YOLO_TH_PRESETS.keys()))
        self.yolo_thresh.current(1)   # 中精度 がデフォルト
        self.yolo_thresh.pack(side="left",padx=(0,6))

        btn_plot=tk.Button(ctrl,text="▶ 再描画",bg=ACCENT,fg="white",relief="flat",
                           font=_tk_font(10,bold=True),cursor="hand2",
                           command=self._yolo_plot)
        btn_plot.pack(side="left",padx=4,ipady=3)

        self.yolo_status=tk.StringVar(value="左パネル「キーポイント検出」で現在のHPを解析します")
        tk.Label(ctrl,textvariable=self.yolo_status,bg=PANEL2,fg=SUBTEXT,
                 font=_tk_font(9)).pack(side="left",padx=8)

        # 連続写真エリア (上)
        cs_outer=tk.Frame(main_area,bg=BG)
        cs_outer.pack(side="top",fill="both",expand=True,padx=8,pady=(4,2))
        cs_scroll=tk.Canvas(cs_outer,bg=BG,highlightthickness=0)
        cs_vsb=tk.Scrollbar(cs_outer,orient="vertical",command=cs_scroll.yview)
        cs_scroll.configure(yscrollcommand=cs_vsb.set)
        cs_vsb.pack(side="right",fill="y")
        cs_scroll.pack(side="left",fill="both",expand=True)
        self.yolo_cs_grid=tk.Frame(cs_scroll,bg=BG)
        cs_win=cs_scroll.create_window((0,0),window=self.yolo_cs_grid,anchor="nw")
        self.yolo_cs_grid.bind("<Configure>",
            lambda e: cs_scroll.configure(scrollregion=cs_scroll.bbox("all")))
        cs_scroll.bind("<Configure>",
            lambda e: cs_scroll.itemconfig(cs_win,width=e.width))
        self._yolo_cs_canvas=cs_scroll
        self._yolo_photo_refs=[]

        # チャートエリア (下)
        chart_frame=tk.Frame(main_area,bg=BG,height=280)
        chart_frame.pack(side="bottom",fill="x",padx=8,pady=(2,4))
        chart_frame.pack_propagate(False)
        self.yolo_plot_frame=chart_frame
        self._yolo_canvas=None
        self._yolo_fig=None

        # バインド
        self.yolo_axis.bind("<<ComboboxSelected>>",lambda e: self._yolo_plot())
        self.yolo_scale.bind("<<ComboboxSelected>>",lambda e: self._yolo_plot())
        self.yolo_thresh.bind("<<ComboboxSelected>>",lambda e: self._yolo_plot())
        self.yolo_start.trace_add("write",lambda *_: self._yolo_plot())
        self.yolo_end.trace_add("write",lambda *_: self._yolo_plot())
        self.yolo_interval.trace_add("write",lambda *_: self._yolo_plot())

    # ── ヘルパー: 星の描画 ─────────────────────
    def _star_points(self,cx,cy,r):
        """5点星の頂点リスト (アウター5 + インナー5)"""
        pts=[]
        for k in range(10):
            ang=-math.pi/2 + k*math.pi/5
            rad = r if k%2==0 else r*0.42
            pts.append((cx+rad*math.cos(ang), cy+rad*math.sin(ang)))
        return pts

    def _draw_star_tk(self,canvas,cx,cy,r,color):
        pts=self._star_points(cx,cy,r)
        flat=[v for xy in pts for v in xy]
        canvas.create_polygon(flat,fill=color,outline="white")

    def _draw_star_pil(self,draw,cx,cy,r,fill,outline="white"):
        pts=self._star_points(cx,cy,r)
        draw.polygon(pts,fill=fill,outline=outline)

    def _yolo_select_all(self):
        for v in self._yolo_kp_vars: v.set(True)
        self._yolo_redraw_overlays()
    def _yolo_clear_all(self):
        for v in self._yolo_kp_vars: v.set(False)
        self._yolo_redraw_overlays()

    # ── ホバー処理 ─────────────────────────
    def _yolo_set_kp_hover(self,idx):
        if self._yolo_hover_clear_id:
            try: self.after_cancel(self._yolo_hover_clear_id)
            except Exception: pass
            self._yolo_hover_clear_id=None
        if self._yolo_hover_kp!=idx:
            self._yolo_hover_kp=idx
            self._yolo_redraw_overlays()

    def _yolo_clear_kp_hover(self,idx):
        def _do_clear():
            self._yolo_hover_clear_id=None
            if self._yolo_hover_kp!=-1:
                self._yolo_hover_kp=-1
                self._yolo_redraw_overlays()
        if self._yolo_hover_clear_id:
            try: self.after_cancel(self._yolo_hover_clear_id)
            except Exception: pass
        self._yolo_hover_clear_id=self.after(60,_do_clear)

    # ── 信頼度しきい値 ────────────────────
    def _yolo_thresholds(self):
        """現在のしきい値 (kp_th, obj_th) を返す"""
        name=self.yolo_thresh.get() if hasattr(self,"yolo_thresh") else "中精度"
        return self.YOLO_TH_PRESETS.get(name,(0.4,0.3))

    # ── キーポイント座標解決 ────────────────
    def _yolo_kp_position(self,ydata,ki,kp_th=0.2,obj_th=0.1):
        """しきい値以下は None"""
        if ki<17:
            kx=ydata.get(f"kp{ki:02d}_x"); ky=ydata.get(f"kp{ki:02d}_y")
            kc=ydata.get(f"kp{ki:02d}_c",0) or 0
            if kx is None or ky is None or kc<kp_th: return None
            return (float(kx),float(ky))
        if ki==17:
            tx=ydata.get("racket_tip_x"); ty=ydata.get("racket_tip_y")
            rc=ydata.get("racket_conf",0) or 0
            if tx is None or ty is None or rc<obj_th: return None
            return (float(tx),float(ty))
        if ki==18:
            # refined.json なら ball_refined を優先
            brx=ydata.get("ball_refined_x"); bry=ydata.get("ball_refined_y")
            if brx is not None and bry is not None:
                return (float(brx),float(bry))
            bb=ydata.get("ball1_bbox"); bc=ydata.get("ball1_conf",0) or 0
            if not bb or bc<obj_th: return None
            return ((bb[0]+bb[2])/2.0,(bb[1]+bb[3])/2.0)
        if ki==19:
            # refined.json なら cog を優先
            cx=ydata.get("cog_x"); cy=ydata.get("cog_y")
            if cx is not None and cy is not None:
                return (float(cx),float(cy))
            # 重心 = Dempsterの人体セグメント質量比による加重平均
            # 検出できているセグメントの重心を、その質量比で平均する
            def kp(k):
                kx=ydata.get(f"kp{k:02d}_x"); ky=ydata.get(f"kp{k:02d}_y")
                kc=ydata.get(f"kp{k:02d}_c",0) or 0
                if kx is None or ky is None or kc<kp_th: return None
                return (float(kx),float(ky))
            # 必須: 両肩+両腰 (胴体 50%)
            l_sh,r_sh=kp(5),kp(6)
            l_hp,r_hp=kp(11),kp(12)
            if not (l_sh and r_sh and l_hp and r_hp): return None
            sh_mid=((l_sh[0]+r_sh[0])/2,(l_sh[1]+r_sh[1])/2)
            hp_mid=((l_hp[0]+r_hp[0])/2,(l_hp[1]+r_hp[1])/2)
            pts=[]; ws=[]
            # 頭 (鼻があれば使う、なければ肩中点)
            head=kp(0) or sh_mid
            pts.append(head); ws.append(0.083)
            # 胴体重心: 肩中点と腰中点の間で、腰寄り60%地点
            # (おへそ高さ ≈ 腸骨稜 = COCOの腰キーポイントよりやや下に重心が来るよう調整)
            trunk=(sh_mid[0]+0.6*(hp_mid[0]-sh_mid[0]),
                   sh_mid[1]+0.6*(hp_mid[1]-sh_mid[1]))
            pts.append(trunk); ws.append(0.497)
            # 上腕 (肩-肘) ×2
            for sh,el_k in [(l_sh,7),(r_sh,8)]:
                el=kp(el_k)
                if el:
                    pts.append(((sh[0]+el[0])/2,(sh[1]+el[1])/2)); ws.append(0.028)
            # 前腕+手 (肘-手首) ×2
            for el_k,wr_k in [(7,9),(8,10)]:
                el=kp(el_k); wr=kp(wr_k)
                if el and wr:
                    pts.append(((el[0]+wr[0])/2,(el[1]+wr[1])/2)); ws.append(0.022)
            # 大腿 (腰-膝) ×2
            for hp,kn_k in [(l_hp,13),(r_hp,14)]:
                kn=kp(kn_k)
                if kn:
                    pts.append(((hp[0]+kn[0])/2,(hp[1]+kn[1])/2)); ws.append(0.10)
            # 下腿+足 (膝-足首) ×2
            for kn_k,an_k in [(13,15),(14,16)]:
                kn=kp(kn_k); an=kp(an_k)
                if kn and an:
                    pts.append(((kn[0]+an[0])/2,(kn[1]+an[1])/2)); ws.append(0.061)
            total_w=sum(ws)
            if total_w<0.5: return None   # セグメント不足
            cx=sum(p[0]*w for p,w in zip(pts,ws))/total_w
            cy=sum(p[1]*w for p,w in zip(pts,ws))/total_w
            return (cx,cy)
        return None

    def _update_yolo_dropdowns(self):
        """v25: CPプルダウン廃止 — メインHPリストと連動。
           現在の peak_idx の rank でラベル更新 + 自動プロット。"""
        if not hasattr(self,"yolo_hp_lbl"): return
        if not self.peaks or self.peak_idx>=len(self.peaks):
            self.yolo_hp_lbl.config(text="-"); return
        rank=self.peaks[self.peak_idx]["rank"]
        self.yolo_hp_lbl.config(text=f"#{rank}")
        self._yolo_plot()

    def _yolo_plot(self):
        """フルプロット: フレーム抽出 + 描画"""
        if not self.peaks or self.peak_idx>=len(self.peaks): return
        rank=self.peaks[self.peak_idx]["rank"]
        path=self.video_path.get()
        outf=self._yolo_data_file(path,rank,prefer_refined=True)
        if not os.path.exists(outf):
            # v24: HP 単一フレーム検出データがあるかチェック
            stem=os.path.splitext(os.path.basename(path))[0]
            hp_path=os.path.join(self._yolo_out_dir(path),f"{stem}_hp{rank:02d}.json")
            if os.path.exists(hp_path):
                self._display_hp_single_frame(hp_path,path,rank)
                return
            self.yolo_status.set("キーポイント検出データがありません"); return
        with open(outf,"r",encoding="utf-8") as f:
            data=json.load(f)
        frames=data.get("frames",[])
        if not frames:
            self.yolo_status.set("フレームデータが空です"); return
        self._yolo_data=data
        self._yolo_frames=frames
        self._yolo_rank=rank

        # 連続写真フレーム抽出 (パラメータが変わったら再抽出)
        try: scale=float(self.yolo_scale.get().rstrip("x"))
        except Exception: scale=1.3
        start=self.yolo_start.get(); end=self.yolo_end.get()
        interval=self.yolo_interval.get()
        hit_t=data.get("hit_time",frames[len(frames)//2]["time"])
        crops_sig=tuple((c["rank"],round(c["time"],2),tuple(round(x,3) for x in c["rect"]))
                        for c in self._crops)
        key=(path,rank,round(start,3),round(end,3),round(interval,3),round(scale,3),crops_sig)
        if key!=self._yolo_cs_extract_key:
            self._yolo_extract_cs_frames(path,hit_t,start,end,interval)
            self._yolo_cs_extract_key=key

        self._yolo_redraw_overlays()
        kp_th,obj_th=self._yolo_thresholds()
        self.yolo_status.set(
            f"#{rank}  ({len(frames)}フレーム,  {scale}x,  "
            f"精度={self.yolo_thresh.get()} kp≥{kp_th} obj≥{obj_th})")

    def _yolo_extract_cs_frames(self,path,hit_t,start,end,interval):
        self._yolo_cs_extracted=[]
        if end-start<interval/2: return
        n=int(round((end-start)/interval))
        offsets=[round(start+k*interval,4) for k in range(n+1)]
        frame_times=[max(0.0,round(hit_t+o,4)) for o in offsets]
        cap=cv2.VideoCapture(path)
        if not cap.isOpened(): return
        fps_v=cap.get(cv2.CAP_PROP_FPS) or 30
        for ft,off in zip(frame_times,offsets):
            cap.set(cv2.CAP_PROP_POS_FRAMES,int(fps_v*ft))
            ret,frame=cap.read()
            if ret: self._yolo_cs_extracted.append((ft,frame,off))
        cap.release()

    def _yolo_redraw_overlays(self):
        """キャッシュ済みフレームを使って 連続写真+グラフ を再描画"""
        if not hasattr(self,"yolo_cs_grid"): return
        # v22: 世代チェック
        try:
            if not self.yolo_cs_grid.winfo_exists(): return
        except Exception: return
        from PIL import ImageDraw
        try:
            for w in self.yolo_cs_grid.winfo_children(): w.destroy()
        except Exception: return
        self._yolo_photo_refs.clear()
        extracted=self._yolo_cs_extracted
        if not extracted:
            self._yolo_render_chart()
            return

        yolo_frames=getattr(self,"_yolo_frames",[])
        selected=[i for i,v in enumerate(self._yolo_kp_vars) if v.get()]
        kp_th,obj_th=self._yolo_thresholds()
        hover=self._yolo_hover_kp
        try: scale=float(self.yolo_scale.get().rstrip("x"))
        except Exception: scale=1.3
        interval=self.yolo_interval.get()

        # サイズ
        self._yolo_cs_canvas.update_idletasks()
        avail_w=max(self._yolo_cs_canvas.winfo_width()-20,400)
        base_w=max(140,avail_w//8)
        thumb_w=int(base_w*scale)
        fh,fw=extracted[0][1].shape[:2]
        rect=self._active_crop_rect(extracted[0][0])
        if rect is not None:
            x1r,y1r,x2r,y2r=rect
            crop_w=int(abs(x2r-x1r)*fw); crop_h=int(abs(y2r-y1r)*fh)
            aspect=crop_w/crop_h if crop_h>0 else fw/fh
        else:
            aspect=fw/fh if fh>0 else 16/9
        thumb_h=int(thumb_w/aspect)
        cols=max(1,avail_w//(thumb_w+10))

        for i,(ft,frame,off) in enumerate(extracted):
            row_i=i//cols; col_i=i%cols
            cell=tk.Frame(self.yolo_cs_grid,bg=BG)
            cell.grid(row=row_i,column=col_i,padx=3,pady=3)

            rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
            img=Image.fromarray(rgb)
            iw,ih=img.size
            cx_off=cy_off=0
            r2=self._active_crop_rect(ft)
            if r2 is not None:
                x1r,y1r,x2r,y2r=r2
                cx1=int(min(x1r,x2r)*iw); cy1=int(min(y1r,y2r)*ih)
                cx2=int(max(x1r,x2r)*iw); cy2=int(max(y1r,y2r)*ih)
                if cx2>cx1 and cy2>cy1:
                    img=img.crop((cx1,cy1,cx2,cy2))
                    cx_off,cy_off=cx1,cy1

            ydata=None
            if yolo_frames:
                # v25: まず時刻でマッチ、ダメならオフセットでマッチ
                ydata=min(yolo_frames,key=lambda r: abs(r["time"]-ft))
                if abs(ydata["time"]-ft)>=0.08:
                    # フォールバック: hit_tからのオフセットで再試行
                    hit_t=getattr(self,"_yolo_data",{}).get("hit_time",0)
                    if hit_t>0:
                        ydata=min(yolo_frames,key=lambda r: abs((r["time"]-hit_t)-off))
                        if abs((ydata["time"]-hit_t)-off)>=0.08:
                            ydata=None
                    else:
                        ydata=None
            if ydata:
                draw=ImageDraw.Draw(img)
                base_r=max(4,int(min(img.size)*0.012))
                for ki in selected:
                    pos=self._yolo_kp_position(ydata,ki,kp_th,obj_th)
                    if pos is None: continue
                    px,py=pos[0]-cx_off,pos[1]-cy_off
                    if px<0 or py<0 or px>img.size[0] or py>img.size[1]: continue
                    color=self.YOLO_KP_COLORS[ki] if ki<len(self.YOLO_KP_COLORS) else "#fff"
                    # ホバー時は2倍
                    r=base_r*2 if ki==hover else base_r
                    if ki==19:   # 重心は★
                        self._draw_star_pil(draw,px,py,r*1.4,color,"white")
                    else:
                        draw.ellipse([px-r-1,py-r-1,px+r+1,py+r+1],
                                    outline="white",width=2)
                        draw.ellipse([px-r,py-r,px+r,py+r],fill=color,outline="black")

            # v18: resize でアスペクト比保持しつつ拡大も
            iw_,ih_=img.size
            if iw_>0 and ih_>0:
                sc=min(thumb_w/iw_, thumb_h/ih_)
                img=img.resize((max(1,int(iw_*sc)),max(1,int(ih_*sc))),Image.LANCZOS)
            photo=ImageTk.PhotoImage(img); self._yolo_photo_refs.append(photo)
            is_hit=abs(off)<interval/2
            lbl=tk.Label(cell,image=photo,bg=BG,
                         highlightbackground=GOLD if is_hit else BORDER,
                         highlightthickness=3 if is_hit else 1)
            lbl.pack()
            # サムネホバー → グラフ縦線
            lbl.bind("<Enter>",lambda e,o=off: self._yolo_show_hover_line(o))
            lbl.bind("<Leave>",lambda e: self._yolo_hide_hover_line())
            # 秒数表示
            if abs(off)<0.001: ds="0.00s"
            elif off<0: ds=f"{off:.2f}s"
            else: ds=f"+{off:.2f}s"
            tk.Label(cell,text=ds,bg=BG,
                     fg=GOLD if is_hit else SUBTEXT,
                     font=_tk_font(9,bold=is_hit)).pack()

        # チャート
        self._yolo_render_chart()

    def _yolo_render_chart(self):
        if not hasattr(self,"_yolo_frames"): return
        frames=self._yolo_frames; rank=getattr(self,"_yolo_rank",0)
        hit_t=self._yolo_data.get("hit_time",frames[len(frames)//2]["time"])
        selected=[i for i,v in enumerate(self._yolo_kp_vars) if v.get()]
        axis=self.yolo_axis.get() or "y"
        kp_th,obj_th=self._yolo_thresholds()
        hover=self._yolo_hover_kp

        if self._yolo_canvas:
            self._yolo_canvas.get_tk_widget().destroy()
            self._yolo_canvas=None
        if self._yolo_fig:
            try: plt.close(self._yolo_fig)
            except Exception: pass

        fig=plt.Figure(figsize=(10,2.8),dpi=88,facecolor=BG)
        ax=fig.add_subplot(111,facecolor=DARK2)
        ax.tick_params(colors=TEXT,labelsize=11)
        for sp in ax.spines.values(): sp.set_color(SUBTEXT)

        # CP相対時間に変換
        rel_times=[r["time"]-hit_t for r in frames]

        # v23: cm 換算スケールを計算
        # 各フレームで「鼻〜足首中点」の縦ピクセル距離を計算、最大値を使用
        use_cm=False
        cm_per_px=1.0
        try: use_cm=bool(self.yolo_use_cm.get())
        except Exception: pass
        if use_cm:
            pixel_heights=[]
            for r in frames:
                nose=self._yolo_kp_position(r,0,kp_th,obj_th)  # 鼻
                la=self._yolo_kp_position(r,15,kp_th,obj_th)   # 左足首
                ra=self._yolo_kp_position(r,16,kp_th,obj_th)   # 右足首
                ankle_y=None
                if la and ra: ankle_y=(la[1]+ra[1])/2
                elif la: ankle_y=la[1]
                elif ra: ankle_y=ra[1]
                if nose and ankle_y is not None:
                    ph=abs(ankle_y-nose[1])
                    if ph>10: pixel_heights.append(ph)
            if pixel_heights:
                ref_h=max(pixel_heights)   # 最も伸びている姿勢を基準
                try: real_cm=float(self.player_height.get())
                except Exception: real_cm=DEFAULT_PLAYER_HEIGHT_CM
                cm_per_px=real_cm/ref_h
            else:
                use_cm=False  # 換算不可

        for ki in selected:
            ys=[]
            for r in frames:
                pos=self._yolo_kp_position(r,ki,kp_th,obj_th)
                if pos is None: ys.append(np.nan)
                else:
                    v=pos[1] if axis=="y" else pos[0]
                    ys.append(v*cm_per_px if use_cm else v)
            if all(np.isnan(ys)): continue
            color=self.YOLO_KP_COLORS[ki] if ki<len(self.YOLO_KP_COLORS) else "#fff"
            # ホバー: 該当はそのまま、他はライトグレー薄め
            if hover>=0 and ki!=hover:
                line_c="#888"; alpha=0.35; lw=1.0; z=2; ms=3
            else:
                line_c=color; alpha=1.0
                lw=2.2 if ki==hover else 1.3
                z=10 if ki==hover else 5
                ms=7 if ki==hover else 4
            marker="*" if ki==19 else "."
            ms_scale = (ms*1.6) if ki==19 else ms
            ax.plot(rel_times,ys,marker=marker,color=line_c,
                    linewidth=lw,markersize=ms_scale,alpha=alpha,zorder=z)

        ax.axvline(0,color=GOLD,linestyle="--",alpha=0.7,linewidth=1.5)
        self._yolo_hover_vline=None
        if axis=="y": ax.invert_yaxis()
        ax.set_xlabel("CPからの時刻 (秒)",color=TEXT,fontsize=12)
        unit_label="cm" if use_cm else "px"
        ax.set_ylabel(f"{axis} 座標 ({unit_label})",color=TEXT,fontsize=12)
        ax.grid(True,alpha=0.2)
        # 凡例は出さない (右パネルで識別)
        fig.tight_layout(pad=0.5)
        self._yolo_fig=fig
        self._yolo_canvas=FigureCanvasTkAgg(fig,master=self.yolo_plot_frame)
        self._yolo_canvas.draw()
        self._yolo_canvas.get_tk_widget().pack(fill="both",expand=True)

    def _yolo_show_hover_line(self,offset_t):
        if not self._yolo_fig: return
        ax=self._yolo_fig.axes[0]
        if self._yolo_hover_vline is None:
            self._yolo_hover_vline=ax.axvline(offset_t,color="#ffff00",
                                              linewidth=2,alpha=0.95,zorder=20)
        else:
            self._yolo_hover_vline.set_xdata([offset_t,offset_t])
            self._yolo_hover_vline.set_visible(True)
        try: self._yolo_canvas.draw_idle()
        except Exception: pass

    def _yolo_hide_hover_line(self):
        if self._yolo_hover_vline is not None:
            self._yolo_hover_vline.set_visible(False)
            try: self._yolo_canvas.draw_idle()
            except Exception: pass

    # ══════════════════════════════════════════
    #  履歴タブ (v15) — 過去解析動画の一覧+読込
    # ══════════════════════════════════════════
    def _build_tab_hist(self,parent):
        toolbar=tk.Frame(parent,bg=PANEL2); toolbar.pack(fill="x",padx=8,pady=4)
        tk.Button(toolbar,text="🔄 更新",bg=DARK2,fg=TEXT,relief="flat",
                  font=_tk_font(10),command=self._refresh_history_tab,cursor="hand2"
                  ).pack(side="left",padx=4,ipady=3)
        tk.Button(toolbar,text="📊 Excelエクスポート",bg=GOLD,fg="#1a1000",
                  relief="flat",font=_tk_font(10,bold=True),
                  command=self._export_registry_xlsx,cursor="hand2"
                  ).pack(side="left",padx=4,ipady=3)
        self.hist_status=tk.StringVar(value="")
        tk.Label(toolbar,textvariable=self.hist_status,bg=PANEL2,fg=SUBTEXT,
                 font=_tk_font(9)).pack(side="left",padx=8)

        outer=tk.Frame(parent,bg=BG); outer.pack(fill="both",expand=True)
        canvas=tk.Canvas(outer,bg=BG,highlightthickness=0)
        sb=tk.Scrollbar(outer,orient="vertical",command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right",fill="y")
        canvas.pack(side="left",fill="both",expand=True)
        self.hist_grid=tk.Frame(canvas,bg=BG)
        win=canvas.create_window((0,0),window=self.hist_grid,anchor="nw")
        self.hist_grid.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
            lambda e: canvas.itemconfig(win,width=e.width))
        self._hist_thumb_refs=[]
        self._refresh_history_tab()

    # ══════════════════════════════════════════
    #  v26: Refiner タブ (統合)
    # ══════════════════════════════════════════
    def _activate_refiner_tab(self):
        """Refinerタブ初回表示時に構築、HP選択時にデータを自動ロード"""
        if self.refiner is None:
            try:
                self.refiner = RefinerFrame(self.tab_refiner, analyzer=self)
                self.refiner.pack(fill="both", expand=True)
                # v59: 3D構築（デバッグ付き）
                try:
                    if hasattr(self, "_3d_placeholder") and self._3d_placeholder:
                        self._3d_placeholder.destroy()
                        self._3d_placeholder = None
                    self.refiner.tab_3d = self.tab_3d_main
                    self.refiner._build_3d_tab()
                    print("[3D構築] 成功")
                except Exception as e:
                    print(f"[3D構築] 失敗: {e}")
                    import traceback; traceback.print_exc()
                    tk.Label(self.tab_3d_main, text=f"3D初期化失敗: {e}",
                             bg=BG, fg="red").pack(pady=20)
            except Exception as e:
                tk.Label(self.tab_refiner, text=f"Refiner 初期化失敗:\n{e}",
                         bg=BG, fg="red", font=_tk_font(12)).pack(pady=40)
                return
        # HP連動: 現在のHPのYOLOデータをRefinerにロード
        self._sync_refiner_hp()

    def _sync_refiner_hp(self):
        """現在選択中のHPのデータをRefinerにロード"""
        if self.refiner is None: return
        if not self.peaks or self.peak_idx >= len(self.peaks): return
        path = self.video_path.get()
        if not path: return
        rank = self.peaks[self.peak_idx]["rank"]
        # v33: refined版を優先、なければ通常版
        outf = self._yolo_data_file(path, rank, prefer_refined=True)
        if not os.path.exists(outf):
            outf = self._yolo_data_file(path, rank, prefer_refined=False)
        if not os.path.exists(outf):
            # HP JSONも試行
            stem = os.path.splitext(os.path.basename(path))[0]
            hp_path = os.path.join(self._yolo_out_dir(path), f"{stem}_hp{rank:02d}.json")
            if os.path.exists(hp_path):
                outf = hp_path
            else:
                self.status_var.set(f"HP#{rank} のKPデータがありません")
                return
        # 既に同じファイルをロード済みなら再ロードしない
        if getattr(self.refiner, "json_path", None) == outf:
            return
        # Refiner にデータをロード
        try:
            self.refiner.video_path = path
            self.refiner._current_video_path = path
            self.refiner.cp_files = [outf]
            if hasattr(self.refiner, "cp_sel"):
                self.refiner.cp_sel["values"] = [os.path.basename(outf)]
                self.refiner.cp_sel.current(0)
            self.refiner._load_one(outf)
        except Exception as e:
            self.status_var.set(f"Refiner データロード失敗: {e}")


    # ══════════════════════════════════════════
    #  v62: MP-YOLO 比較タブ
    # ══════════════════════════════════════════
    def _build_tab_compare(self, parent):
        top = tk.Frame(parent, bg=PANEL); top.pack(fill="x", padx=4, pady=4)
        self._cmp_hp_var = tk.StringVar(value="HP未選択")
        tk.Label(top, textvariable=self._cmp_hp_var, bg=PANEL, fg=GOLD,
                 font=_tk_font(13, True)).pack(side="left", padx=8)
        tk.Label(top, text="  ○=MediaPipe  ×=YOLO", bg=PANEL, fg=SUBTEXT,
                 font=_tk_font(10)).pack(side="left", padx=8)
        # フレームスライダー
        self._cmp_frame_var = tk.IntVar(value=0)
        self._cmp_slider = tk.Scale(top, variable=self._cmp_frame_var,
            from_=0, to=1, orient="horizontal", bg=PANEL, fg=TEXT,
            troughcolor=DARK2, length=400, showvalue=True,
            command=lambda v: self._render_compare_frame(int(float(v))))
        self._cmp_slider.pack(side="left", padx=8)
        # 画像表示
        self._cmp_img_frame = tk.Frame(parent, bg=DARK2)
        self._cmp_img_frame.pack(fill="both", expand=True, padx=4, pady=4)
        self._cmp_img_lbl = tk.Label(self._cmp_img_frame, bg=DARK2)
        self._cmp_img_lbl.pack(fill="both", expand=True)
        self._cmp_photo_ref = None

    def _refresh_compare_tab(self):
        if not self.peaks or self.peak_idx >= len(self.peaks):
            self._cmp_hp_var.set("HPを選択してください"); return
        p = self.peaks[self.peak_idx]
        rank = p["rank"]; path = self.video_path.get()
        stem = os.path.splitext(os.path.basename(path))[0]
        out_dir = self._yolo_out_dir(path)
        mp_path = os.path.join(out_dir, f"{stem}_cp{rank:02d}_mp.json")
        yolo_path = os.path.join(out_dir, f"{stem}_cp{rank:02d}_yolo.json")
        self._cmp_mp = None; self._cmp_yolo = None
        if os.path.exists(mp_path):
            try:
                with open(mp_path, "r", encoding="utf-8") as f:
                    self._cmp_mp = json.load(f)
            except Exception: pass
        if os.path.exists(yolo_path):
            try:
                with open(yolo_path, "r", encoding="utf-8") as f:
                    self._cmp_yolo = json.load(f)
            except Exception: pass
        n = 0
        if self._cmp_mp: n = max(n, len(self._cmp_mp.get("frames", [])))
        if self._cmp_yolo: n = max(n, len(self._cmp_yolo.get("frames", [])))
        shot = p.get("shot_type", "") or ""
        status = []
        if self._cmp_mp: status.append(f"MP:{len(self._cmp_mp.get('frames',[]))}")
        else: status.append("MP:未")
        if self._cmp_yolo: status.append(f"YOLO:{len(self._cmp_yolo.get('frames',[]))}")
        else: status.append("YOLO:未")
        self._cmp_hp_var.set(f"HP#{rank}  t={p['time']:.2f}s  {shot}  [{' / '.join(status)}]")
        if n > 0:
            self._cmp_slider.config(to=n-1)
            # 打点フレームに移動
            mid = n // 2
            if self._cmp_mp:
                hit_t = self._cmp_mp.get("hit_time", 0)
                frames = self._cmp_mp.get("frames", [])
                if frames:
                    mid = min(range(len(frames)), key=lambda i: abs(frames[i]["time"]-hit_t))
            self._cmp_frame_var.set(mid)
            self._render_compare_frame(mid)

    def _render_compare_frame(self, idx):
        if not (self._cmp_mp or self._cmp_yolo): return
        # 時刻を決定
        t = None
        if self._cmp_mp and idx < len(self._cmp_mp.get("frames", [])):
            t = self._cmp_mp["frames"][idx]["time"]
        elif self._cmp_yolo and idx < len(self._cmp_yolo.get("frames", [])):
            t = self._cmp_yolo["frames"][idx]["time"]
        if t is None: return
        # 動画から画像取得
        path = self.video_path.get()
        cap = cv2.VideoCapture(path)
        fps_ = cap.get(cv2.CAP_PROP_FPS) or 30
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(t * fps_))
        ok, bgr = cap.read(); cap.release()
        if not ok: return
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)
        draw = ImageDraw.Draw(img, "RGBA")
        # MP: ○
        if self._cmp_mp:
            frames = self._cmp_mp.get("frames", [])
            row = min(frames, key=lambda r: abs(r["time"]-t)) if frames else None
            if row:
                for ki in range(17):
                    kx = row.get(f"kp{ki:02d}_x"); ky = row.get(f"kp{ki:02d}_y")
                    kc = row.get(f"kp{ki:02d}_c", 0) or 0
                    if kx is None or kc < 0.3: continue
                    color = self.YOLO_KP_COLORS[ki] if ki < len(self.YOLO_KP_COLORS) else "#fff"
                    r = 12
                    draw.ellipse([kx-r, ky-r, kx+r, ky+r], outline=color, width=4)
        # YOLO: ×
        if self._cmp_yolo:
            frames = self._cmp_yolo.get("frames", [])
            row = min(frames, key=lambda r: abs(r["time"]-t)) if frames else None
            if row:
                for ki in range(17):
                    kx = row.get(f"kp{ki:02d}_x"); ky = row.get(f"kp{ki:02d}_y")
                    kc = row.get(f"kp{ki:02d}_c", 0) or 0
                    if kx is None or kc < 0.3: continue
                    color = self.YOLO_KP_COLORS[ki] if ki < len(self.YOLO_KP_COLORS) else "#fff"
                    s = 12
                    draw.line([kx-s, ky-s, kx+s, ky+s], fill=color, width=5)
                    draw.line([kx-s, ky+s, kx+s, ky-s], fill=color, width=5)
        # リサイズ
        self._cmp_img_frame.update_idletasks()
        pw = max(self._cmp_img_frame.winfo_width()-8, 400)
        ph = max(self._cmp_img_frame.winfo_height()-8, 300)
        sc = min(pw/img.width, ph/img.height, 1.0)
        dw = int(img.width*sc); dh = int(img.height*sc)
        img_d = img.resize((dw, dh), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img_d)
        self._cmp_photo_ref = photo
        self._cmp_img_lbl.config(image=photo)

    def _refresh_history_tab(self):
        if not hasattr(self,"hist_grid"): return
        reg=load_registry()
        videos=reg.get("videos",[])
        videos.sort(key=lambda v: v.get("last_updated",""),reverse=True)
        for w in self.hist_grid.winfo_children(): w.destroy()
        self._hist_thumb_refs.clear()
        if not videos:
            tk.Label(self.hist_grid,text="解析済の動画はまだありません",
                     bg=BG,fg=SUBTEXT,font=_tk_font(11)).pack(pady=20)
            self.hist_status.set("0件"); return
        for v in videos: self._add_history_card(v)
        self.hist_status.set(f"解析済: {len(videos)} 件")

    def _add_history_card(self,v):
        """v20: 展開機能付き履歴カード"""
        card=tk.Frame(self.hist_grid,bg=PANEL)
        card.pack(fill="x",padx=8,pady=4)

        # ── ヘッダ行 (常時表示) ──
        head=tk.Frame(card,bg=PANEL); head.pack(fill="x")

        thumb_lbl=tk.Label(head,bg=PANEL,width=22,height=7)
        # v20: サムネのフォールバック
        tp=v.get("first_thumb","")
        if not tp or not os.path.exists(tp):
            tp=find_any_thumb(v.get("path","")) or ""
        if tp and os.path.exists(tp):
            try:
                img=Image.open(tp); img.thumbnail((160,100),Image.LANCZOS)
                photo=ImageTk.PhotoImage(img); self._hist_thumb_refs.append(photo)
                thumb_lbl.config(image=photo,width=0,height=0)
            except Exception: pass
        thumb_lbl.pack(side="left",padx=6,pady=4)

        # v24 fix: action を info より先に pack することで、長いタイトルでも
        # 必ず読み込み/展開/削除ボタンが画面内に表示される
        action=tk.Frame(head,bg=PANEL); action.pack(side="right",padx=4)
        tk.Button(action,text="読み込み",bg=ACCENT2,fg="white",relief="flat",
                  font=_tk_font(10,bold=True),cursor="hand2",
                  command=lambda p=v["path"]: self._load_history_video(p)
                  ).pack(pady=2,ipady=4,ipadx=8)
        exp_btn=tk.Button(action,text="▼ 詳細",bg=DARK2,fg=GOLD,relief="flat",
                          font=_tk_font(9,bold=True),cursor="hand2")
        exp_btn.pack(pady=2,ipady=2,ipadx=4)
        tk.Button(action,text="✏ タイトル",bg=DARK2,fg=GOLD,relief="flat",
                  font=_tk_font(9),cursor="hand2",
                  command=lambda p=v["path"]: self._edit_title_from_history(p)
                  ).pack(pady=2,ipady=2,ipadx=4)
        tk.Button(action,text="削除",bg=DARK2,fg=ACCENT,relief="flat",
                  font=_tk_font(9),cursor="hand2",
                  command=lambda p=v["path"]: self._remove_history_entry(p)
                  ).pack(pady=2,ipady=2)

        # info は最後に pack (残り領域を取る)
        info=tk.Frame(head,bg=PANEL); info.pack(side="left",fill="both",expand=True,padx=4)
        # 長いタイトル対応: wraplength 設定で複数行折返し
        alias=v.get("alias","") or ""
        fn=v.get("filename","")
        if alias:
            tk.Label(info,text=alias,bg=PANEL,fg=GOLD,
                     font=_tk_font(13,bold=True),anchor="w",
                     wraplength=900,justify="left").pack(fill="x")
            tk.Label(info,text=fn,bg=PANEL,fg=SUBTEXT,
                     font=_tk_font(9),anchor="w",
                     wraplength=900,justify="left").pack(fill="x")
        else:
            tk.Label(info,text=fn,bg=PANEL,fg=ACCENT,
                     font=_tk_font(12,bold=True),anchor="w",
                     wraplength=900,justify="left").pack(fill="x")
        n_cp=v.get("num_cps",0); n_lab=v.get("num_labeled",0)
        n_yolo=v.get("num_yolo",0); n_ref=v.get("num_refined",0)
        stats_text=f"CP: {n_cp}    ラベル済: {n_lab}    検出済: {n_yolo}"
        if n_ref>0: stats_text+=f"  (refined: {n_ref})"
        tk.Label(info,text=stats_text,
                 bg=PANEL,fg=TEXT,font=_tk_font(10),anchor="w").pack(fill="x")
        sc=v.get("shot_counts",{})
        if sc:
            parts=[f"{next((ja for ja,en in SHOT_TYPES if en==st),st)}:{cnt}"
                   for st,cnt in sc.items()]
            tk.Label(info,text="  /  ".join(parts),
                     bg=PANEL,fg=SUBTEXT,font=_tk_font(9),anchor="w").pack(fill="x")
        tk.Label(info,text=f"最終更新: {v.get('last_updated','')}",
                 bg=PANEL,fg=SUBTEXT,font=_tk_font(8),anchor="w").pack(fill="x")
        tk.Label(info,text=v.get("path",""),bg=PANEL,fg=SUBTEXT,
                 font=_tk_font(8),anchor="w",
                 wraplength=900,justify="left").pack(fill="x")

        # ── 展開エリア (初期は非表示) ──
        exp_frame=tk.Frame(card,bg=DARK2)
        state={"open":False,"built":False}
        def _toggle_exp():
            if state["open"]:
                exp_frame.pack_forget()
                exp_btn.config(text="▼ 詳細")
                state["open"]=False
            else:
                if not state["built"]:
                    self._build_history_expansion(exp_frame, v)
                    state["built"]=True
                exp_frame.pack(fill="x",padx=4,pady=(0,4))
                exp_btn.config(text="▲ 詳細")
                state["open"]=True
        exp_btn.config(command=_toggle_exp)

    def _build_history_expansion(self, parent, v):
        """v20: 履歴カード展開時のサブサムネグリッド"""
        path=v.get("path","")
        if not path:
            tk.Label(parent,text="パス情報なし",bg=DARK2,fg=SUBTEXT,
                     font=_tk_font(9)).pack(pady=8); return

        db_path=get_db_path(path)
        vf=os.path.basename(path)
        labels=load_all_labels(db_path,vf)  # {rank: (shot, spin, rating, frame_time)}
        # v23: クロップも読込
        try: crops=load_crops(db_path,vf)
        except Exception: crops=[]
        if not labels:
            tk.Label(parent,text="ラベル済CPがありません",bg=DARK2,fg=SUBTEXT,
                     font=_tk_font(10)).pack(pady=8); return

        def _apply_crop_to_pil_by_rank(pil_img, rank):
            """v24: 該当CPの rank のクロップを PIL 画像に適用 (rank ベース)"""
            if not crops: return pil_img
            rect=None
            for c in crops:
                if c.get("rank")==rank:
                    rect=c.get("rect"); break
            if not rect: return pil_img
            iw,ih=pil_img.size
            x1r,y1r,x2r,y2r=rect
            cx1=int(min(x1r,x2r)*iw); cy1=int(min(y1r,y2r)*ih)
            cx2=int(max(x1r,x2r)*iw); cy2=int(max(y1r,y2r)*ih)
            if cx2>cx1 and cy2>cy1:
                return pil_img.crop((cx1,cy1,cx2,cy2))
            return pil_img

        ranks=sorted(labels.keys())
        tk.Label(parent,
                 text=f"ラベル済CP一覧  ({len(ranks)}件)  "
                      "クリックでそのCPに読込ジャンプ",
                 bg=DARK2,fg=GOLD,font=_tk_font(10,bold=True),anchor="w"
                 ).pack(fill="x",padx=8,pady=(6,4))

        grid=tk.Frame(parent,bg=DARK2); grid.pack(fill="x",padx=8,pady=(0,8))
        cols=10
        for i,rk in enumerate(ranks):
            row_i=i//cols * 2; col_i=i%cols
            shot,spin,rating,ft=labels[rk]
            shot_ja=next((ja for ja,en in SHOT_TYPES if en==shot),shot or "")

            cell=tk.Frame(grid,bg=DARK2,cursor="hand2")
            cell.grid(row=row_i,column=col_i,padx=3,pady=2)

            tpath=find_cp_thumb_path(path,rk)
            has_y,has_r=check_cp_yolo_status(path,rk)

            sub_photo=None
            if tpath and os.path.exists(tpath):
                try:
                    img=Image.open(tpath)
                    # v24: rank ベースで該当CPのクロップを適用
                    img=_apply_crop_to_pil_by_rank(img,rk)
                    img.thumbnail((90,55),Image.LANCZOS)
                    sub_photo=ImageTk.PhotoImage(img)
                    self._hist_thumb_refs.append(sub_photo)
                except Exception: pass

            if sub_photo:
                border_color=GOLD if has_r else (ACCENT if has_y else BORDER)
                bw=2 if (has_y or has_r) else 1
                tlbl=tk.Label(cell,image=sub_photo,bg=DARK2,
                              highlightbackground=border_color,
                              highlightthickness=bw)
            else:
                tlbl=tk.Label(cell,text="(no thumb)",bg=DARK2,fg=SUBTEXT,
                              width=12,height=4,relief="solid",bd=1)
            tlbl.pack()

            # ステータスアイコン (★黄=YOLO  ★青=refined)
            status_txt=""
            if has_r: status_txt="★🔵"
            elif has_y: status_txt="★"
            stat=tk.Label(cell,
                          text=f"#{rk}  {shot_ja[:6]}  {status_txt}",
                          bg=DARK2,
                          fg=(GOLD if has_r else (ACCENT if has_y else TEXT)),
                          font=_tk_font(8,bold=bool(has_y or has_r)))
            stat.pack()

            # クリックハンドラ
            def _on_click(e=None, p=path, r=rk):
                self._load_history_video_and_jump(p,r)
            for w in (cell,tlbl,stat):
                w.bind("<Button-1>",_on_click)

    def _load_history_video_and_jump(self, path, rank):
        """v20: 履歴から動画を読み込んで指定 rank のCPにジャンプ"""
        if not os.path.exists(path):
            messagebox.showerror("読み込み",
                f"動画ファイルが見つかりません:\n{path}"); return
        # 既に同じ動画が読込済なら ジャンプだけ
        if os.path.abspath(self.video_path.get()) == os.path.abspath(path):
            self._jump_to_rank(rank)
            self.tabs.select(self.tab_main)
            return
        # v34: 解析済みならポップアップスキップ
        self._pending_jump_rank=rank
        self.video_path.set(path)
        self._cached_video_path = path
        self._proceed_video_load(path)
        self.tabs.select(self.tab_main)

    def _jump_to_rank(self, rank):
        """指定の rank の CP を選択"""
        for i,p in enumerate(self.peaks):
            if p.get("rank")==rank:
                self.peak_idx=i; self.frame_offset=0
                try:
                    self.peak_list.selection_clear(0,"end")
                    self.peak_list.selection_set(i); self.peak_list.see(i)
                except Exception: pass
                self._update_view()
                return True
        return False

    def _load_history_video(self,path):
        if not os.path.exists(path):
            messagebox.showerror("読み込み",f"動画ファイルが見つかりません:\n{path}"); return
        # v34: メイン画面に即切替
        self.tabs.select(self.tab_main)
        self.update_idletasks()
        self.video_path.set(path)
        # v34: 解析済み (peaks.jsonが存在) ならポップアップをスキップ
        db_path = get_db_path(path)
        peaks_file = os.path.join(os.path.dirname(db_path),
                                   os.path.splitext(os.path.basename(path))[0] + "_peaks.json")
        if os.path.exists(db_path) or os.path.exists(peaks_file):
            self._cached_video_path = path
            self._proceed_video_load(path)
        else:
            self._on_video_selected()

    def _remove_history_entry(self,path):
        reg=load_registry()
        ap=os.path.abspath(path)
        reg["videos"]=[v for v in reg["videos"] if v.get("path")!=ap]
        save_registry(reg)
        self._refresh_history_tab()

    def _pick_video_from_history(self,target_var):
        """v24: 履歴サムネからショット比較用の動画を選択するモーダル"""
        reg=load_registry()
        videos=reg.get("videos",[])
        if not videos:
            messagebox.showinfo("動画選択","解析済の動画がありません"); return

        win=tk.Toplevel(self,bg=PANEL)
        win.title("動画を選択 (履歴から)"); win.geometry("780x560")
        win.transient(self); win.grab_set()

        tk.Label(win,text="サムネをクリックして動画を選択",bg=PANEL,fg=GOLD,
                 font=_tk_font(12,bold=True)).pack(pady=(10,4))
        tk.Label(win,text=f"解析済: {len(videos)} 件",bg=PANEL,fg=SUBTEXT,
                 font=_tk_font(9)).pack(pady=(0,8))

        # スクロール可能領域
        outer=tk.Frame(win,bg=PANEL); outer.pack(fill="both",expand=True,padx=8,pady=4)
        canv=tk.Canvas(outer,bg=PANEL,highlightthickness=0)
        vsb=tk.Scrollbar(outer,orient="vertical",command=canv.yview)
        canv.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right",fill="y"); canv.pack(side="left",fill="both",expand=True)
        grid=tk.Frame(canv,bg=PANEL)
        canv.create_window((0,0),window=grid,anchor="nw")
        grid.bind("<Configure>",lambda e: canv.configure(scrollregion=canv.bbox("all")))
        # マウスホイール (A+B ハイブリッド: unbind_all + winfo_exists チェック)
        def _on_mw(ev):
            try:
                if canv.winfo_exists():
                    canv.yview_scroll(int(-ev.delta/120),"units")
            except Exception: pass
        def _mw_enter(e):
            canv.bind_all("<MouseWheel>",_on_mw)
        def _mw_leave(e):
            try: canv.unbind_all("<MouseWheel>")
            except Exception: pass
        canv.bind("<Enter>",_mw_enter)
        canv.bind("<Leave>",_mw_leave)
        # モーダルが閉じる時も必ず unbind_all
        def _on_win_destroy():
            try: canv.unbind_all("<MouseWheel>")
            except Exception: pass
            win.destroy()
        win.protocol("WM_DELETE_WINDOW",_on_win_destroy)

        photo_refs=[]
        cols=4
        # 最終更新が新しい順
        videos_sorted=sorted(videos,key=lambda v: v.get("last_updated",""),reverse=True)
        for i,v in enumerate(videos_sorted):
            row_i=i//cols; col_i=i%cols
            p=v.get("path",""); fn=v.get("filename","")
            alias=v.get("alias","") or ""
            cell=tk.Frame(grid,bg=DARK2,cursor="hand2",
                          highlightbackground=BORDER,highlightthickness=1)
            cell.grid(row=row_i,column=col_i,padx=4,pady=4,sticky="nsew")

            # サムネ
            thumb_path=v.get("first_thumb","")
            thumb_lbl=None
            if not (thumb_path and os.path.exists(thumb_path)):
                thumb_path=find_any_thumb(p)
            if thumb_path and os.path.exists(thumb_path):
                try:
                    img=Image.open(thumb_path); img.thumbnail((170,100),Image.LANCZOS)
                    photo=ImageTk.PhotoImage(img); photo_refs.append(photo)
                    thumb_lbl=tk.Label(cell,image=photo,bg=DARK2)
                except Exception: thumb_lbl=None
            if thumb_lbl is None:
                thumb_lbl=tk.Label(cell,text="(no thumb)",bg=DARK2,fg=SUBTEXT,
                                   width=22,height=6)
            thumb_lbl.pack(padx=4,pady=4)

            # タイトル / ファイル名
            title_text=alias if alias else fn
            tk.Label(cell,text=title_text[:32],bg=DARK2,
                     fg=GOLD if alias else ACCENT,
                     font=_tk_font(9,bold=True),wraplength=170,justify="center"
                     ).pack(padx=4)
            n_cp=v.get("num_cps",0); n_lab=v.get("num_labeled",0)
            n_yolo=v.get("num_yolo",0)
            tk.Label(cell,text=f"CP:{n_cp}  ラベル:{n_lab}  検出:{n_yolo}",
                     bg=DARK2,fg=SUBTEXT,font=_tk_font(8)).pack(padx=4,pady=(0,4))

            def _on_click(event,pp=p):
                try: canv.unbind_all("<MouseWheel>")
                except Exception: pass
                target_var.set(pp)
                win.destroy()
            cell.bind("<Button-1>",_on_click)
            thumb_lbl.bind("<Button-1>",_on_click)
            for child in cell.winfo_children():
                child.bind("<Button-1>",_on_click)

        win._photo_refs=photo_refs  # GC防止

        # キャンセル
        tk.Button(win,text="キャンセル",bg=DARK2,fg=TEXT,relief="flat",
                  font=_tk_font(10),cursor="hand2",command=_on_win_destroy
                  ).pack(pady=6,ipady=4,ipadx=12)

    def _edit_title_from_history(self,path):
        """v23: 履歴カードからタイトル (alias) を編集"""
        if not path:
            messagebox.showwarning("タイトル編集","パス情報なし"); return
        cur=get_video_alias(path)
        win=tk.Toplevel(self,bg=PANEL)
        win.title("タイトル編集")
        win.geometry("420x220")
        win.transient(self); win.grab_set()
        tk.Label(win,text="タイトル編集",bg=PANEL,fg=ACCENT,
                 font=_tk_font(13,bold=True)).pack(pady=(12,4))
        tk.Label(win,text=os.path.basename(path),bg=PANEL,fg=SUBTEXT,
                 font=_tk_font(9)).pack(pady=(0,8))
        tk.Label(win,text="タイトル (空にすると削除):",bg=PANEL,fg=TEXT,
                 font=_tk_font(10)).pack(anchor="w",padx=16)
        var=tk.StringVar(value=cur)
        ent=tk.Entry(win,textvariable=var,bg=DARK2,fg=TEXT,
                     insertbackground=TEXT,relief="flat",font=_tk_font(11))
        ent.pack(fill="x",padx=16,pady=4,ipady=6)
        ent.focus_set(); ent.icursor("end")
        def _save_close():
            set_video_alias(path,var.get().strip())
            # 現在開いている動画なら左パネルも更新
            if os.path.abspath(self.video_path.get())==os.path.abspath(path):
                self._refresh_alias_display()
            self._refresh_history_tab()
            win.destroy()
        def _delete_close():
            set_video_alias(path,"")
            if os.path.abspath(self.video_path.get())==os.path.abspath(path):
                self._refresh_alias_display()
            self._refresh_history_tab()
            win.destroy()
        btn_row=tk.Frame(win,bg=PANEL); btn_row.pack(fill="x",pady=12,padx=16)
        tk.Button(btn_row,text="保存",bg=ACCENT,fg="white",relief="flat",
                  font=_tk_font(10,bold=True),cursor="hand2",
                  command=_save_close).pack(side="left",padx=2,ipady=5,ipadx=14)
        tk.Button(btn_row,text="タイトル削除",bg=DARK2,fg=ACCENT,relief="flat",
                  font=_tk_font(10),cursor="hand2",
                  command=_delete_close).pack(side="left",padx=4,ipady=5,ipadx=8)
        tk.Button(btn_row,text="キャンセル",bg=DARK2,fg=TEXT,relief="flat",
                  font=_tk_font(10),cursor="hand2",
                  command=win.destroy).pack(side="right",padx=2,ipady=5,ipadx=8)
        ent.bind("<Return>",lambda e: _save_close())
        ent.bind("<Escape>",lambda e: win.destroy())

    def _export_registry_xlsx(self):
        reg=load_registry()
        videos=reg.get("videos",[])
        if not videos:
            messagebox.showinfo("Excel出力","解析済の動画がありません"); return
        try:
            import pandas as pd
            rows=[]
            for v in videos:
                row={"alias":v.get("alias",""),    # v21
                     "filename":v.get("filename",""),
                     "path":v.get("path",""),
                     "duration_sec":v.get("duration_sec",0),
                     "num_cps":v.get("num_cps",0),
                     "num_labeled":v.get("num_labeled",0),
                     "num_yolo":v.get("num_yolo",0),       # v20
                     "num_refined":v.get("num_refined",0), # v20
                     "first_analyzed":v.get("first_analyzed",""),
                     "last_updated":v.get("last_updated","")}
                sc=v.get("shot_counts",{})
                for st_ja,st_en in SHOT_TYPES:
                    row[st_ja]=sc.get(st_en,0)
                rows.append(row)
            df=pd.DataFrame(rows)
            outf=os.path.join(os.path.dirname(get_registry_path()),
                              "analyzed_videos.xlsx")
            df.to_excel(outf,index=False)
            messagebox.showinfo("Excel出力",f"書き出しました:\n{outf}")
        except Exception as e:
            messagebox.showerror("Excel出力",f"エラー: {e}")

    # ══════════════════════════════════════════
    #  キーボードショートカット
    # ══════════════════════════════════════════
    def _global_key(self,event):
        # フォーカスが Entry/Text/Combobox にあるときは無視 (タイプ中)
        try:
            w=self.focus_get()
            if w is not None and w.winfo_class() in ("Entry","Text","TCombobox","TEntry","Spinbox"):
                return
        except Exception: pass
        # スペースで再生/停止
        if event.keysym=="space":
            self._toggle_play(); return
        # 再生中はラベル/コマ送り操作を無視
        if self._play_running: return
        key_shot={"1":"serve","2":"forehand","3":"backhand",
                  "4":"fore_volley","5":"back_volley","6":"smash","0":"noise"}
        key_spin={"q":"flat","w":"topspin","e":"slice","r":"kick"}
        key_rating={"z":"super","x":"nice","c":"normal","v":"miss"}
        ch=event.char.lower()
        if ch in key_shot: self._select_shot(key_shot[ch],auto_save=True)
        elif ch in key_spin: self._select_spin(key_spin[ch],auto_save=True)
        elif ch in key_rating: self._select_rating(key_rating[ch],auto_save=True)
        elif event.keysym=="Right":
            if event.state & 0x1: self._next_peak()
            else: self._next_frame()
        elif event.keysym=="Left":
            if event.state & 0x1:
                if self.peak_idx>0:
                    self.peak_idx-=1; self.frame_offset=0
                    self.peak_list.selection_clear(0,"end")
                    self.peak_list.selection_set(self.peak_idx)
                    self.peak_list.see(self.peak_idx)
                    self._update_view()
            else: self._prev_frame()
        elif event.keysym in ("Return","KP_Enter"):
            # Enter: 現在のラベルを確定して次のチェックポイントへ
            self._auto_save()
            self._next_peak()
        elif event.keysym=="Delete":
            self._delete_current_checkpoint()


# ──────────────────────────────────────────────


# ══════════════════════════════════════════════════════════════
#  以下 YOLO Refiner (統合版)  — 元 yolo_refiner_gui.py v2.9
# ══════════════════════════════════════════════════════════════
KP_EXT_NAMES = RFN.KP_NAMES + ["ラケット先端", "ボール", "重心"]

# v47: マーカー形状  ○=左, □=右, ◇=中央, ★=特殊
# 0鼻 1左目 2右目 3左耳 4右耳 5左肩 6右肩 7左肘 8右肘
# 9左手首 10右手首 11左腰 12右腰 13左膝 14右膝 15左足首 16右足首
# 17ラケット先端 18ボール 19重心
KP_SHAPES = [
    "diamond",  # 0 鼻
    "circle","square",  # 1左目, 2右目
    "circle","square",  # 3左耳, 4右耳
    "circle","square",  # 5左肩, 6右肩
    "circle","square",  # 7左肘, 8右肘
    "circle","square",  # 9左手首, 10右手首
    "circle","square",  # 11左腰, 12右腰
    "circle","square",  # 13左膝, 14右膝
    "circle","square",  # 15左足首, 16右足首
    "star","star","star",  # 17ラケット先端, 18ボール, 19重心
]

KP_COLORS = [
    "#ff4d4d", "#ff9933", "#ffcc00", "#cc6600", "#996633",
    "#66b3ff", "#0066cc", "#66cc66", "#006633", "#ffff66",
    "#ff66ff", "#cc99ff", "#6600cc", "#ff99cc", "#cc0066",
    "#cccccc", "#666666",
    "#00ffff", "#aaff00", "#ffd700",
]

VIDEO_EXTS = (".mp4", ".mov", ".avi", ".mkv", ".m4v",
              ".MP4", ".MOV", ".AVI", ".MKV", ".M4V")


def _font(size=10, bold=False):
    return ("Helvetica", size, "bold") if bold else ("Helvetica", size)


def _star_polygon(cx, cy, r):
    pts = []
    for k in range(10):
        ang = -math.pi/2 + k*math.pi/5
        rad = r if k % 2 == 0 else r * 0.42
        pts.append((cx + rad*math.cos(ang), cy + rad*math.sin(ang)))
    return pts

def _diamond_polygon(cx, cy, r):
    return [(cx, cy-r), (cx+r, cy), (cx, cy+r), (cx-r, cy)]

def _draw_kp_shape_canvas(canvas, shape, cx, cy, r, fill, outline="white", width=2, tags=""):
    """v47: Canvas上にKPマーカーを描画"""
    if shape == "square":
        canvas.create_rectangle(cx-r,cy-r,cx+r,cy+r,fill=fill,outline=outline,width=width,tags=tags)
    elif shape == "diamond":
        flat = [v for xy in _diamond_polygon(cx,cy,r) for v in xy]
        canvas.create_polygon(flat,fill=fill,outline=outline,width=width,tags=tags)
    elif shape == "star":
        flat = [v for xy in _star_polygon(cx,cy,r) for v in xy]
        canvas.create_polygon(flat,fill=fill,outline=outline,width=width,tags=tags)
    else:  # circle
        canvas.create_oval(cx-r,cy-r,cx+r,cy+r,fill=fill,outline=outline,width=width,tags=tags)

def _draw_kp_shape_pil(draw, shape, cx, cy, r, fill, outline="white", width=1):
    """v47: PIL上にKPマーカーを描画"""
    if shape == "square":
        draw.rectangle([cx-r,cy-r,cx+r,cy+r],fill=fill,outline=outline,width=width)
    elif shape == "diamond":
        draw.polygon(_diamond_polygon(cx,cy,r),fill=fill,outline=outline)
    elif shape == "star":
        flat = [v for xy in _star_polygon(cx,cy,r) for v in xy]
        draw.polygon(flat,fill=fill,outline=outline)
    else:  # circle
        draw.ellipse([cx-r,cy-r,cx+r,cy+r],fill=fill,outline=outline,width=width)


def _detect_video(json_path):
    """YOLO JSON のパスから動画ファイルを推定"""
    yolo_dir = os.path.dirname(json_path)
    parent = os.path.dirname(yolo_dir)
    if os.path.basename(yolo_dir).lower() == "yolo":
        video_dir = parent
    else:
        video_dir = yolo_dir
    fn = os.path.basename(json_path)
    stem = fn.split("_cp")[0] if "_cp" in fn else os.path.splitext(fn)[0]
    for ext in VIDEO_EXTS:
        p = os.path.join(video_dir, stem + ext)
        if os.path.exists(p):
            return p
    # フォールバック: 同じ stem を持つ動画を検索
    if os.path.isdir(video_dir):
        for f in os.listdir(video_dir):
            base, ext = os.path.splitext(f)
            if base == stem and ext.lower() in (e.lower() for e in VIDEO_EXTS):
                return os.path.join(video_dir, f)
    return None


class RefinerFrame(tk.Frame):
    def __init__(self, parent, analyzer=None):
        super().__init__(parent, bg=BG)
        self.analyzer = analyzer  # 統合版: TennisApp への参照

        # 状態
        self.json_path = None
        self.cp_files = []
        self.raw_data = None
        self.raw_frames = None
        self.refined_auto = None     # 手動編集なしの自動洗練結果
        self.refined_frames = None   # refined_auto + 手動編集 + 波及
        self.hit_t = 0.0
        self._debounce_id = None

        # 動画関連
        self.video_path = None
        self.frames_cache = {}
        self.crop_rect = None
        self._extracting = False
        self._extract_progress = (0, 0)   # (done, total)
        self.video_w = None
        self.video_h = None

        # 編集関連
        self.manual_edits = {}            # (idx, ki) -> (x,y) or None (削除)
        self.selected_frame_idx = None
        self.selected_kp = None
        self.dragging = False
        self._placement_kp = None   # v2.5: KP追加モード (配置対象のKPインデックス)
        self._inferred_overrides = set()  # v2.9: 手動で三角(低信頼)に設定した (frame_idx, kp_idx)
        self._drag_undo_pushed = False   # v2.4: ドラッグ内 undo push 済みフラグ

        # v2.4: アンドゥ スタック (編集前の manual_edits のスナップショットを保持)
        from collections import deque
        self._undo_stack = deque(maxlen=50)

        # ホバー (凡例↔写真ハイライト)
        self.hover_kp = None
        self.kp_rows = []                 # 凡例行ウィジェット参照
        self._hover_render_id = None
        # v2.3: 総合ビュー双方向ホバー
        self._cv_hover_frame_idx = None  # 写真→グラフ用 (今ホバーしている写真のidx)
        self._cv_prev_hover_idx = None   # 前回ハイライトした idx (border 復元用)
        self._cv_chart_vline = None      # 写真ホバーで描いたグラフ縦線
        self._cv_hover_after_id = None
        # v2.3 後修正: ホバー時に再描画せず widget の border 属性だけ更新するため
        # 写真ラベルへの参照と「平常時の border」情報を保持
        self._cv_photo_widgets = {}      # idx -> Label widget
        self._cv_photo_normal_border = {} # idx -> (color, thickness)

        # Tk Vars (パラメータ)
        self.p_kp_th      = tk.DoubleVar(value=RFN.DEFAULT_KP_CONF_TH)
        self.p_obj_th     = tk.DoubleVar(value=RFN.DEFAULT_OBJ_CONF_TH)
        self.p_vel_k      = tk.DoubleVar(value=RFN.VELOCITY_MAD_K)
        self.p_acc_k      = tk.DoubleVar(value=RFN.ACCEL_MAD_K)
        self.p_link_dev   = tk.DoubleVar(value=RFN.LINK_DEVIATION_FRAC)
        self.p_savgol_w   = tk.IntVar(value=RFN.SAVGOL_WINDOW)
        self.p_savgol_o   = tk.IntVar(value=RFN.SAVGOL_ORDER)
        self.p_edit_window = tk.IntVar(value=4)   # 編集波及範囲 (コマ数)

        defaults = {10, 17, 18, 19}
        self.kp_vars = [tk.BooleanVar(value=(i in defaults)) for i in range(20)]
        self.axis = tk.StringVar(value="y")
        self.status = tk.StringVar(value="[ JSON 読込 ] でファイルを選んでください")
        self.edit_count_var = tk.StringVar(value="編集: 0")

        # コンタクトシートの列数 (v2.3 後修正: デフォルト 3、空欄対策)
        self.contact_cols = tk.IntVar(value=3)
        # v2.4: 表示時間範囲 (TA と同じ)
        self._rf_start = tk.DoubleVar(value=-1.5)
        self._rf_end   = tk.DoubleVar(value=0.5)
        self._rf_interval = tk.StringVar(value="0.05")

        # v2.4: 3D キーポイント (MediaPipe Pose)
        self._mp3d_frames = []    # [{time, landmarks:[{x,y,z,vis}×33]}, ...]
        self._mp3d_anim_id = None # after() アニメーション ID
        self._mp3d_play = False
        self._mp3d_fig = None
        self._mp3d_canvas = None
        self._mp3d_ax = None
        self._mp3d_cur_idx = 0    # 現在表示フレームインデックス
        self._3d_ground_shift = 0.0  # v2.5: 地面基準のZオフセット

        self._build_ui()

    # ════════════════════════════════════════
    #  UI 構築
    # ════════════════════════════════════════
    def _build_ui(self):
        # ── 上部: ファイル操作 ──
        topbar = tk.Frame(self, bg=PANEL); topbar.pack(fill="x", padx=4, pady=4)
        # 統合版: analyzer 経由でない場合のみ表示
        if self.analyzer is None:
            tk.Button(topbar, text="履歴から選択", bg=ACCENT2, fg="white", relief="flat",
                      font=_font(10, True), cursor="hand2",
                      command=self._pick_from_history
                      ).pack(side="left", padx=4, ipady=4, ipadx=6)
            tk.Button(topbar, text="フォルダ", bg=DARK2, fg=TEXT, relief="flat",
                      font=_font(10), cursor="hand2",
                      command=self._load_folder).pack(side="left", padx=2, ipady=4, ipadx=4)
            tk.Button(topbar, text="HP を選択", bg=ACCENT2, fg="white", relief="flat",
                      font=_font(10, True), cursor="hand2",
                      command=self._show_cp_thumb_picker
                      ).pack(side="left", padx=(12, 2), ipady=4, ipadx=6)
        else:
            pass  # v46: 連動ラベル削除
        self.cur_cp_var = tk.StringVar(value="(HP未選択)")
        tk.Label(topbar, textvariable=self.cur_cp_var, bg=PANEL, fg=GOLD,
                 font=_font(10, True)).pack(side="left", padx=4)
        # 非表示の Combobox (内部用、互換性のため残す)
        self.cp_sel = ttk.Combobox(topbar, width=2, state="readonly", font=_font(9))
        # pack しない (非表示)
        self.cp_sel.bind("<<ComboboxSelected>>", lambda e: self._switch_cp())

        # v2.3: 保存ボタンは廃止 (常時自動保存)。代わりに保存状態インジケータ表示
        self.autosave_status = tk.StringVar(value="")
        tk.Label(topbar, textvariable=self.autosave_status, bg=PANEL, fg=GREEN,
                 font=_font(9, True)).pack(side="right", padx=8)
        # v46: topbar右端にコンパクトに配置
        tk.Button(topbar, text="⚙", bg=DARK2, fg=TEXT, relief="flat",
                  font=_font(10), cursor="hand2", width=2,
                  command=self._show_params_popup).pack(side="right",padx=2,ipady=2)
        tk.Button(topbar, text="学習DB", bg=DARK2, fg=GOLD, relief="flat",
                  font=_font(9), cursor="hand2",
                  command=self._open_learning_db_dialog).pack(side="right",padx=2,ipady=2)
        tk.Label(topbar, textvariable=self.edit_count_var, bg=PANEL, fg=GOLD,
                 font=_font(10, True)).pack(side="right", padx=4)
        tk.Label(topbar, textvariable=self.status, bg=PANEL, fg=SUBTEXT,
                 font=_font(9)).pack(side="right", padx=4)
        self.stats_lbl = tk.Label(topbar, text="", bg=PANEL, fg=SUBTEXT,
                                  font=("Courier", 9))
        self.stats_lbl.pack(side="right", padx=4)

        # ── 右パネル: マーカー凡例 + KPフィルタ ──
        right = tk.Frame(self, bg=PANEL, width=220)
        right.pack(side="right", fill="y", padx=(2, 4), pady=4)
        right.pack_propagate(False)

        # マーカー種別の凡例
        leg = tk.LabelFrame(right, text="マーカーの意味", bg=PANEL, fg=ACCENT2,
                            font=_font(9, True), relief="flat")
        leg.pack(fill="x", padx=4, pady=(4, 6))
        leg_rows = [
            ("oh", "中空 小円  =  生 (YOLO)"),
            ("fl", "塗潰 大円  =  洗練後"),
            ("ed", "金縁 大円  =  手動編集"),
            ("st", "星 (★)    =  重心"),
            ("dl", "X (赤)     =  削除済 (右クで取消)"),
        ]
        for kind, txt in leg_rows:
            r = tk.Frame(leg, bg=PANEL); r.pack(fill="x", padx=2, pady=1)
            cnv = tk.Canvas(r, width=18, height=14, bg=PANEL, highlightthickness=0)
            sample_color = "#66b3ff"
            if kind == "oh":
                cnv.create_oval(5, 4, 11, 10, outline=sample_color, width=1)
            elif kind == "fl":
                cnv.create_oval(3, 2, 13, 12, fill=sample_color, outline="white", width=1)
            elif kind == "ed":
                cnv.create_oval(3, 2, 13, 12, fill=sample_color, outline=GOLD, width=2)
            elif kind == "st":
                pts = _star_polygon(9, 7, 6)
                flat = [v for xy in pts for v in xy]
                cnv.create_polygon(flat, fill=GOLD, outline="white")
            elif kind == "dl":
                cnv.create_text(9, 7, text="X", fill=RED, font=_font(10, True))
            cnv.pack(side="left", padx=(2, 4))
            tk.Label(r, text=txt, bg=PANEL, fg=TEXT, font=_font(8), anchor="w"
                     ).pack(side="left", fill="x", expand=True)

        tk.Label(right, text="表示 KP  (マウスオーバーで強調)",
                 bg=PANEL, fg=ACCENT2, font=_font(10, True)
                 ).pack(pady=(6, 2), anchor="w", padx=8)

        kp_outer = tk.Frame(right, bg=PANEL)
        kp_outer.pack(fill="both", expand=True, padx=4, pady=2)
        kp_canvas = tk.Canvas(kp_outer, bg=PANEL, highlightthickness=0)
        sb = tk.Scrollbar(kp_outer, orient="vertical", command=kp_canvas.yview)
        kp_canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        kp_canvas.pack(side="left", fill="both", expand=True)
        kp_inner = tk.Frame(kp_canvas, bg=PANEL)
        kp_canvas.create_window((0, 0), window=kp_inner, anchor="nw")
        kp_inner.bind("<Configure>",
            lambda e: kp_canvas.configure(scrollregion=kp_canvas.bbox("all")))

        self.kp_rows = []
        for i, name in enumerate(KP_EXT_NAMES):
            row = tk.Frame(kp_inner, bg=PANEL); row.pack(fill="x", padx=2, pady=1)
            cb = tk.Checkbutton(row, variable=self.kp_vars[i], bg=PANEL, fg=TEXT,
                                activebackground=PANEL, selectcolor=DARK2,
                                command=self._on_kp_filter_change)
            cb.pack(side="left")
            c = tk.Canvas(row, width=16, height=16, bg=PANEL, highlightthickness=0)
            color = KP_COLORS[i] if i < len(KP_COLORS) else "#888"
            # v58: KP形状対応
            kp_sh = KP_SHAPES[i] if i < len(KP_SHAPES) else "circle"
            _draw_kp_shape_canvas(c, kp_sh, 8, 8, 6, fill=color, outline="white", width=1)
            c.pack(side="left", padx=(2, 4))
            lbl = tk.Label(row, text=name, bg=PANEL, fg=TEXT, font=_font(9), anchor="w")
            lbl.pack(side="left", fill="x", expand=True)
            # ホバーバインド (写真側のマーカーをハイライト)
            for w in (row, cb, c, lbl):
                w.bind("<Enter>", lambda e, k=i: self._set_hover_kp(k))
                w.bind("<Leave>", lambda e: self._set_hover_kp(None))
            # v2.5: クリックで配置モード切り替え
            for w in (c, lbl):
                w.bind("<Button-1>", lambda e, k=i: self._toggle_placement_kp(k))
            self.kp_rows.append(row)

        bf = tk.Frame(right, bg=PANEL); bf.pack(fill="x", padx=4, pady=4)
        tk.Button(bf, text="全選択", bg=DARK2, fg=TEXT, relief="flat", font=_font(8),
                  command=self._sel_all, cursor="hand2"
                  ).pack(side="left", padx=2, fill="x", expand=True)
        tk.Button(bf, text="全解除", bg=DARK2, fg=TEXT, relief="flat", font=_font(8),
                  command=self._sel_none, cursor="hand2"
                  ).pack(side="left", padx=2, fill="x", expand=True)

        af = tk.Frame(right, bg=PANEL); af.pack(fill="x", padx=4, pady=4)
        tk.Label(af, text="グラフ軸:", bg=PANEL, fg=TEXT, font=_font(9)
                 ).pack(side="left", padx=4)
        tk.Radiobutton(af, text="y", variable=self.axis, value="y",
                       bg=PANEL, fg=TEXT, selectcolor=DARK2, activebackground=PANEL,
                       command=self._update_chart).pack(side="left")
        tk.Radiobutton(af, text="x", variable=self.axis, value="x",
                       bg=PANEL, fg=TEXT, selectcolor=DARK2, activebackground=PANEL,
                       command=self._update_chart).pack(side="left")

        # ── 中央: タブ ──
        nb_style = ttk.Style()
        try: nb_style.theme_use("clam")
        except Exception: pass
        nb_style.configure("Refiner.TNotebook", background=BG, borderwidth=0,
                           tabmargins=[0, 4, 0, 0])
        nb_style.configure("Refiner.TNotebook.Tab",
                           background=PANEL, foreground=TEXT,
                           padding=[16, 6], borderwidth=0,
                           font=_font(10, True))
        nb_style.map("Refiner.TNotebook.Tab",
                     background=[("selected", ACCENT2), ("active", PANEL2)],
                     foreground=[("selected", "white"), ("active", TEXT)],
                     expand=[("selected", [1, 1, 1, 0])])
        self.notebook = ttk.Notebook(self, style="Refiner.TNotebook")
        self.notebook.pack(side="left", fill="both", expand=True, padx=4, pady=4)
        # v2.3: 総合ビュータブを一番左に
        self.tab_combined = tk.Frame(self.notebook, bg=BG)
        self.tab_chart   = tk.Frame(self.notebook, bg=BG)
        self.tab_contact = tk.Frame(self.notebook, bg=BG)
        self.tab_editor  = tk.Frame(self.notebook, bg=BG)
        # v58: 統合版ではtab_3dはメイン側が提供、単体版では自前生成
        if self.analyzer is not None:
            pass  # tab_3dは_activate_refiner_tabで設定される
        else:
            self.tab_3d = tk.Frame(self.notebook, bg=BG)
            self.notebook.add(self.tab_3d, text="3D")
        self.notebook.add(self.tab_combined, text="総合ビュー")
        # v27: グラフ・連続写真タブは総合ビューに統合したため非表示
        # (tab_chart / tab_contact は内部互換のためウィジェットとしては維持)
        self.notebook.add(self.tab_editor,   text="編集")
        # v56: 3Dタブはメイン側に移設
        self.notebook.bind("<<NotebookTabChanged>>",
                           lambda e: self._on_tab_changed())

        self._build_combined_tab()
        self._build_chart_tab()
        self._build_contact_tab()
        self._build_editor_tab()
        if hasattr(self, "tab_3d") and self.tab_3d:
            self._build_3d_tab()

        # パラメータ変更でデバウンス再計算
        for var in (self.p_kp_th, self.p_obj_th, self.p_vel_k, self.p_acc_k,
                    self.p_link_dev, self.p_savgol_w, self.p_savgol_o,
                    self.p_edit_window):
            var.trace_add("write", lambda *_: self._on_param_change())

    def _slider(self, parent, label, var, lo, hi, res, accent=False):
        f = tk.Frame(parent, bg=PANEL2); f.pack(side="left", padx=4)
        fg = GOLD if accent else TEXT
        tk.Label(f, text=label, bg=PANEL2, fg=fg, font=_font(8, bold=accent)
                 ).pack(anchor="w")
        tk.Scale(f, variable=var, from_=lo, to=hi, orient="horizontal",
                 resolution=res, bg=PANEL2, fg=fg, troughcolor=DARK2,
                 highlightbackground=PANEL2, relief="flat",
                 length=92, sliderlength=12, showvalue=True,
                 font=_font(8)).pack()

    # ── タブ構築 ──
    def _build_combined_tab(self):
        """v2.3: グラフ + 連続写真を1画面で同時表示
        v46: 全体をスクロール可能に"""
        # v46: スクロール可能な外枠
        outer = tk.Frame(self.tab_combined, bg=BG)
        outer.pack(fill="both", expand=True)
        cv_scroll = tk.Canvas(outer, bg=BG, highlightthickness=0)
        vsb = tk.Scrollbar(outer, orient="vertical", command=cv_scroll.yview)
        cv_scroll.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        cv_scroll.pack(side="left", fill="both", expand=True)
        self._cv_scroll_canvas = cv_scroll  # v55: 参照保持
        self._cv_scroll_inner = tk.Frame(cv_scroll, bg=BG)
        win_id = cv_scroll.create_window((0,0), window=self._cv_scroll_inner, anchor="nw")
        def _on_inner_configure(e):
            cv_scroll.configure(scrollregion=cv_scroll.bbox("all"))
        def _on_canvas_configure(e):
            # v55: 幅を親キャンバスに合わせ、高さは内容に任せる
            cv_scroll.itemconfig(win_id, width=e.width)
        self._cv_scroll_inner.bind("<Configure>", _on_inner_configure)
        cv_scroll.bind("<Configure>", _on_canvas_configure)
        # マウスホイールでスクロール (v55: 子ウィジェットでも動作)
        def _on_mousewheel(e):
            cv_scroll.yview_scroll(int(-1*(e.delta/120)), "units")
        def _bind_mw(e): cv_scroll.bind_all("<MouseWheel>", _on_mousewheel)
        def _unbind_mw(e): cv_scroll.unbind_all("<MouseWheel>")
        cv_scroll.bind("<Enter>", _bind_mw)
        cv_scroll.bind("<Leave>", _unbind_mw)
        self._cv_scroll_inner.bind("<Enter>", _bind_mw)
        self._cv_scroll_inner.bind("<Leave>", _unbind_mw)
        # 以降、self.tab_combined → self._cv_scroll_inner に配置
        parent = self._cv_scroll_inner

        # コントロール行 (上部)
        ctrl = tk.Frame(parent, bg=PANEL2)
        ctrl.pack(side="top", fill="x", padx=2, pady=(2,1))
        # ショット種別表示
        self._cv_shot_var = tk.StringVar(value="")
        tk.Label(ctrl, text="HP:", bg=PANEL2, fg=SUBTEXT, font=_font(9)
                 ).pack(side="left", padx=(6,2))
        tk.Label(ctrl, textvariable=self._cv_shot_var, bg=PANEL2, fg=GOLD,
                 font=_font(10, True)).pack(side="left", padx=(0,12))
        # 写真倍率プルダウン
        tk.Label(ctrl, text="写真:", bg=PANEL2, fg=SUBTEXT, font=_font(9)
                 ).pack(side="left", padx=(0,2))
        self._cv_scale_var = tk.StringVar(value="1x")
        cb_scale = ttk.Combobox(ctrl, textvariable=self._cv_scale_var,
                                values=["0.75x","1x","1.5x","2x","3x"],
                                state="readonly", width=5, font=_font(9))
        cb_scale.pack(side="left", padx=(0,8))
        cb_scale.bind("<<ComboboxSelected>>",
                      lambda e: self._render_contact_sheet())
        # v2.4: 表示時間範囲
        tk.Label(ctrl, text="開始:", bg=PANEL2, fg=SUBTEXT, font=_font(8)
                 ).pack(side="left", padx=(8,1))
        cb_start = ttk.Combobox(ctrl, textvariable=self._rf_start,
                                values=[-2.0,-1.5,-1.0,-0.5],
                                state="readonly", width=4, font=_font(8))
        cb_start.pack(side="left", padx=(0,4))
        self._cb_start = cb_start  # v41: 自動調整用
        tk.Label(ctrl, text="終了:", bg=PANEL2, fg=SUBTEXT, font=_font(8)
                 ).pack(side="left", padx=(0,1))
        cb_end = ttk.Combobox(ctrl, textvariable=self._rf_end,
                              values=[0.0,0.5,1.0,1.5,2.0],
                              state="readonly", width=4, font=_font(8))
        cb_end.pack(side="left", padx=(0,4))
        self._cb_end = cb_end
        tk.Label(ctrl, text="間隔:", bg=PANEL2, fg=SUBTEXT, font=_font(8)
                 ).pack(side="left", padx=(0,1))
        cb_iv = ttk.Combobox(ctrl, textvariable=self._rf_interval,
                             values=["最短",0.03,0.05,0.10,0.15,0.20,0.50],
                             state="readonly", width=4, font=_font(8))
        cb_iv.pack(side="left", padx=(0,4))
        self._cb_iv = cb_iv
        # 変更時に再描画
        for cb in (cb_start, cb_end, cb_iv):
            cb.bind("<<ComboboxSelected>>",
                    lambda e: (self._update_chart(), self._render_contact_sheet()))

        # v27: グラフ表示トグル + 拡大モード
        self._cv_show_graph = tk.BooleanVar(value=True)
        tk.Checkbutton(ctrl, text="グラフ", variable=self._cv_show_graph,
                       bg=PANEL2, fg=TEXT, activebackground=PANEL2, selectcolor=DARK2,
                       font=_font(9), command=self._cv_toggle_graph
                       ).pack(side="left", padx=(12,2))
        self._cv_graph_large = tk.BooleanVar(value=False)
        tk.Checkbutton(ctrl, text="グラフ拡大", variable=self._cv_graph_large,
                       bg=PANEL2, fg=TEXT, activebackground=PANEL2, selectcolor=DARK2,
                       font=_font(9), command=self._cv_toggle_graph
                       ).pack(side="left", padx=2)
        # v28: グラフ2 (XY軌跡) トグル
        self._cv_show_graph2 = tk.BooleanVar(value=False)
        tk.Checkbutton(ctrl, text="グラフ2(XY軌跡)", variable=self._cv_show_graph2,
                       bg=PANEL2, fg=TEXT, activebackground=PANEL2, selectcolor=DARK2,
                       font=_font(9), command=self._cv_toggle_graph2
                       ).pack(side="left", padx=(8,2))
        self._cv_graph2_large = tk.BooleanVar(value=True)  # v29: 常に拡大サイズ
        # v31: グラフ3 (角度の時系列) トグル
        self._cv_show_graph3 = tk.BooleanVar(value=False)
        tk.Checkbutton(ctrl, text="グラフ3(角度)", variable=self._cv_show_graph3,
                       bg=PANEL2, fg=TEXT, activebackground=PANEL2, selectcolor=DARK2,
                       font=_font(9), command=self._cv_toggle_graph3
                       ).pack(side="left", padx=(8,2))
        # v27: 列数 (旧・連続写真タブから統合)
        tk.Label(ctrl, text="列数:", bg=PANEL2, fg=SUBTEXT, font=_font(8)
                 ).pack(side="left", padx=(12,1))
        cols_sp = tk.Spinbox(ctrl, from_=3, to=12, width=3, textvariable=self.contact_cols,
                             font=_font(8), command=self._render_contact_sheet)
        cols_sp.pack(side="left")

        # 上半分: チャート (高さ固定、コンパクトに)
        top = tk.Frame(parent, bg=BG, height=200)
        top.pack(side="top", fill="x", padx=2, pady=(0, 1))
        top.pack_propagate(False)
        self._cv_graph_container = top  # v27: トグル用に保持
        self.combined_chart_frame = tk.Frame(top, bg=BG)
        self.combined_chart_frame.pack(fill="both", expand=True)
        self._combined_fig = None
        self._combined_chart_canvas = None

        # v28: グラフ2 (XY軌跡) エリア — デフォルト非表示
        # v53: 画面サイズに応じてグラフ2の高さを自動調整
        try:
            screen_h = self.winfo_toplevel().winfo_screenheight()
            g2_h = min(500, max(250, int(screen_h * 0.35)))
        except Exception:
            g2_h = 400
        g2 = tk.Frame(parent, bg=BG, height=g2_h)
        g2.pack_propagate(False)
        self._cv_graph2_container = g2
        self.combined_chart2_frame = tk.Frame(g2, bg=BG)
        self.combined_chart2_frame.pack(fill="both", expand=True)
        self._combined_fig2 = None
        self._combined_chart2_canvas = None
        self._cv_chart2_hl = None  # ホバーハイライト点

        # v31: グラフ3 (角度) エリア — デフォルト非表示
        g3 = tk.Frame(parent, bg=BG, height=250)
        g3.pack_propagate(False)
        self._cv_graph3_container = g3
        self.combined_chart3_frame = tk.Frame(g3, bg=BG)
        self.combined_chart3_frame.pack(fill="both", expand=True)
        self._combined_fig3 = None
        self._combined_chart3_canvas = None

        # 区切り
        sep = tk.Frame(parent, bg=BORDER, height=2)
        sep.pack(side="top", fill="x", padx=4)
        self._cv_sep = sep  # v27: グラフ再パック用アンカー

        # 下半分: 連続写真 (横スクロール対応)
        bot = tk.Frame(parent, bg=BG)
        bot.pack(side="top", fill="both", expand=True, padx=2, pady=(1, 2))
        canvas = tk.Canvas(bot, bg=BG, highlightthickness=0)
        vsb = tk.Scrollbar(bot, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        self.combined_contact_grid = tk.Frame(canvas, bg=BG)
        win = canvas.create_window((0, 0), window=self.combined_contact_grid, anchor="nw")
        self.combined_contact_grid.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
            lambda e: canvas.itemconfig(win, width=e.width))
        self._combined_contact_canvas = canvas
        self._combined_thumb_refs = []
        self._render_empty_combined()

    def _cv_toggle_graph(self):
        """v27: 総合ビューのグラフ表示トグル + 拡大モード (高さ2倍)"""
        if not hasattr(self, "_cv_graph_container"): return
        if not self._cv_show_graph.get():
            self._cv_graph_container.pack_forget()
        else:
            h = 400 if self._cv_graph_large.get() else 200
            self._cv_graph_container.config(height=h)
            # 連続写真エリアの前に再パック
            self._cv_graph_container.pack(side="top", fill="x", padx=2, pady=(0,1),
                                          before=self._cv_sep)
            self._update_chart()

    def _cv_toggle_graph2(self):
        """v28: グラフ2 (XY軌跡) の表示トグル + 拡大 (高さ2倍)"""
        if not hasattr(self, "_cv_graph2_container"): return
        if not self._cv_show_graph2.get():
            self._cv_graph2_container.pack_forget()
        else:
            h = 560 if self._cv_graph2_large.get() else 280
            self._cv_graph2_container.config(height=h)
            self._cv_graph2_container.pack(side="top", fill="x", padx=2, pady=(0,1),
                                           before=self._cv_sep)
            # v33: 常にフル再描画（背景写真含む）
            self._combined_fig2 = None
            self._combined_chart2_canvas = None
            self._update_chart2()

    def _update_chart2(self):
        """v29: XY軌跡グラフ — 背景に写真を表示、KPマーカーをオーバーレイ。
           写真ホバーで背景切替 + 点ハイライト"""
        if self.raw_frames is None or self.refined_frames is None: return
        if not self._cv_show_graph2.get(): return
        selected = [i for i, v in enumerate(self.kp_vars) if v.get()]
        kp_th = float(self.p_kp_th.get())
        obj_th = float(self.p_obj_th.get())
        if self._combined_chart2_canvas:
            try: self._combined_chart2_canvas.get_tk_widget().destroy()
            except Exception: pass
        if self._combined_fig2:
            try: plt.close(self._combined_fig2)
            except Exception: pass
        fig = plt.Figure(figsize=(10, 5.6), dpi=85, facecolor=BG)
        ax = fig.add_subplot(111, facecolor=DARK2)
        ax.tick_params(colors=TEXT, labelsize=10)
        for sp in ax.spines.values(): sp.set_color(SUBTEXT)
        # v29: 打点フレームの背景写真を表示
        hit_i = min(range(len(self.refined_frames)),
                    key=lambda i: abs(self.refined_frames[i]["time"]-self.hit_t))
        self._cv_chart2_hit_idx = hit_i
        self._cv_chart2_bg_idx = hit_i  # 現在の背景フレーム
        bg_frame = self.frames_cache.get(hit_i)
        self._cv_chart2_crop = None  # v33: クロップ情報保持
        if bg_frame is not None:
            bg_rgb = bg_frame
            # v33: crop_rect があればクロップ適用
            if self.crop_rect:
                h_, w_ = bg_rgb.shape[:2]
                cx1, cy1, cx2, cy2 = [int(v) for v in self.crop_rect]
                cx1 = max(0, cx1); cy1 = max(0, cy1)
                cx2 = min(w_, cx2); cy2 = min(h_, cy2)
                if cx2 > cx1 and cy2 > cy1:
                    bg_rgb = bg_rgb[cy1:cy2, cx1:cx2]
                    self._cv_chart2_crop = (cx1, cy1, cx2, cy2)
            img_h, img_w = bg_rgb.shape[:2]
            ax.imshow(bg_rgb, extent=[0, img_w, img_h, 0], aspect="equal", alpha=0.35, zorder=0)
            ax.set_xlim(0, img_w); ax.set_ylim(img_h, 0)
            ax.set_aspect("equal", adjustable="box")
        any_plotted = False
        self._cv_chart2_pts = {}
        # v33: クロップオフセット
        crop_ox = self._cv_chart2_crop[0] if self._cv_chart2_crop else 0
        crop_oy = self._cv_chart2_crop[1] if self._cv_chart2_crop else 0
        for ki in selected:
            color = KP_COLORS[ki] if ki < len(KP_COLORS) else "#fff"
            xs, ys, fidx = [], [], []
            for i, f_ref in enumerate(self.refined_frames):
                pf = self._kp_position(f_ref, ki, kp_th, obj_th)
                if pf is not None:
                    xs.append(pf[0] - crop_ox); ys.append(pf[1] - crop_oy); fidx.append(i)
            if not xs: continue
            ax.plot(xs, ys, color="white", linewidth=0.8, alpha=0.5, zorder=3)
            marker = "*" if ki == 19 else "o"
            ms = 9 if ki == 19 else 5
            ax.plot(xs, ys, linestyle="", marker=marker, markersize=ms,
                    color=color, alpha=0.9, zorder=5,
                    gid=f"kp_trail_{ki}")  # v34: hover用にID付与
            if hit_i in fidx:
                j = fidx.index(hit_i)
                ax.plot([xs[j]], [ys[j]], marker=marker, markersize=ms+6,
                        color=color, markeredgecolor=GOLD, markeredgewidth=2,
                        linestyle="", zorder=7)
            for j, fi_ in enumerate(fidx):
                self._cv_chart2_pts.setdefault(fi_, []).append((xs[j], ys[j]))
            any_plotted = True
        if not any_plotted:
            ax.text(0.5, 0.5, "表示KPを選択してください",
                    ha="center", va="center", color=SUBTEXT,
                    fontsize=13, transform=ax.transAxes)
        ax.set_xlabel("x (px)", color=TEXT, fontsize=10)
        ax.set_ylabel("y (px)", color=TEXT, fontsize=10)
        ax.grid(True, alpha=0.15)
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.combined_chart2_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self._combined_fig2 = fig
        self._combined_chart2_canvas = canvas
        self._cv_chart2_hl = None

    def _cv_toggle_graph3(self):
        """v31: グラフ3 (角度時系列) の表示トグル"""
        if not hasattr(self, "_cv_graph3_container"): return
        if not self._cv_show_graph3.get():
            self._cv_graph3_container.pack_forget()
        else:
            self._cv_graph3_container.config(height=250)
            self._cv_graph3_container.pack(side="top", fill="x", padx=2, pady=(0,1),
                                           before=self._cv_sep)
            self._update_chart3()

    def _update_chart3(self):
        """v31: 角度の時系列グラフ — face_yaw, face_pitch, body_yaw を表示"""
        if self.raw_frames is None or self.refined_frames is None: return
        if not self._cv_show_graph3.get(): return
        if self._combined_chart3_canvas:
            try: self._combined_chart3_canvas.get_tk_widget().destroy()
            except Exception: pass
        if self._combined_fig3:
            try: plt.close(self._combined_fig3)
            except Exception: pass
        fig = plt.Figure(figsize=(10, 2.5), dpi=85, facecolor=BG)
        ax = fig.add_subplot(111, facecolor=DARK2)
        ax.tick_params(colors=TEXT, labelsize=9)
        for sp in ax.spines.values(): sp.set_color(SUBTEXT)
        # データ収集 (refined_frames + raw_frames の両方から検索)
        times_rel = []
        face_yaws, face_pitches, body_yaws = [], [], []
        src_frames = self.refined_frames
        for i, f in enumerate(src_frames):
            t_rel = f["time"] - self.hit_t
            times_rel.append(t_rel)
            fy = f.get("face_yaw")
            fp = f.get("face_pitch")
            by = f.get("body_yaw")
            # v32: 角度データがなければ動的に計算
            if fy is None and fp is None and by is None:
                try:
                    angles = TennisApp._calc_face_body_angles(f)
                    if angles:
                        fy = angles.get("face_yaw")
                        fp = angles.get("face_pitch")
                        by = angles.get("body_yaw")
                        # キャッシュ
                        if fy is not None: f["face_yaw"] = fy
                        if fp is not None: f["face_pitch"] = fp
                        if by is not None: f["body_yaw"] = by
                except Exception: pass
            face_yaws.append(fy)
            face_pitches.append(fp)
            body_yaws.append(by)
        # プロット
        any_data = False
        t_valid = [t for t, v in zip(times_rel, face_yaws) if v is not None]
        v_valid = [v for v in face_yaws if v is not None]
        if v_valid:
            ax.plot(t_valid, v_valid, color="#ff7b46", linewidth=1.5, label="顔 水平角",
                    marker="o", markersize=3, alpha=0.9)
            any_data = True
        t_valid = [t for t, v in zip(times_rel, face_pitches) if v is not None]
        v_valid = [v for v in face_pitches if v is not None]
        if v_valid:
            ax.plot(t_valid, v_valid, color="#3fb950", linewidth=1.5, label="顔 仰角",
                    marker="s", markersize=3, alpha=0.9)
            any_data = True
        t_valid = [t for t, v in zip(times_rel, body_yaws) if v is not None]
        v_valid = [v for v in body_yaws if v is not None]
        if v_valid:
            ax.plot(t_valid, v_valid, color="#6a5acd", linewidth=1.5, label="体 水平角",
                    marker="^", markersize=3, alpha=0.9)
            any_data = True
        ax.axvline(0, color=GOLD, linewidth=1.5, alpha=0.7, linestyle="--", label="打点")
        ax.set_xlabel("時間 (秒)", color=TEXT, fontsize=10)
        ax.set_ylabel("角度 (°)", color=TEXT, fontsize=10)
        if any_data:
            ax.legend(loc="upper right", fontsize=11, facecolor=DARK2,
                      edgecolor=SUBTEXT, labelcolor=TEXT, ncol=3,
                      handlelength=1.5, columnspacing=1.0)
        else:
            ax.text(0.5, 0.5, "角度データなし (KP検出を実行してください)",
                    ha="center", va="center", color=SUBTEXT,
                    fontsize=12, transform=ax.transAxes)
        ax.grid(True, alpha=0.2)
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.combined_chart3_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self._combined_fig3 = fig
        self._combined_chart3_canvas = canvas

    def _render_empty_combined(self):
        """総合ビュータブの初期状態"""
        if self._combined_chart_canvas:
            try: self._combined_chart_canvas.get_tk_widget().destroy()
            except Exception: pass
        if self._combined_fig:
            try: plt.close(self._combined_fig)
            except Exception: pass
        fig = plt.Figure(figsize=(10, 2.0), dpi=85, facecolor=BG)
        ax = fig.add_subplot(111, facecolor=DARK2)
        ax.tick_params(colors=TEXT, labelsize=10)
        for sp in ax.spines.values(): sp.set_color(SUBTEXT)
        ax.text(0.5, 0.5, "履歴から選択 で動画を読み込んでください",
                ha="center", va="center", color=SUBTEXT,
                fontsize=13, transform=ax.transAxes)
        ax.set_xticks([]); ax.set_yticks([])
        fig.tight_layout()
        self._combined_fig = fig
        self._combined_chart_canvas = FigureCanvasTkAgg(fig,
                                            master=self.combined_chart_frame)
        self._combined_chart_canvas.draw()
        self._combined_chart_canvas.get_tk_widget().pack(fill="both", expand=True)

    # ── タブ構築 (既存) ──
    def _build_chart_tab(self):
        self.chart_frame = tk.Frame(self.tab_chart, bg=BG)
        self.chart_frame.pack(fill="both", expand=True)
        self._fig = None
        self._chart_canvas = None
        self._render_empty_chart()

    def _build_contact_tab(self):
        ctl = tk.Frame(self.tab_contact, bg=PANEL2); ctl.pack(fill="x", padx=4, pady=4)
        tk.Label(ctl, text="連続写真モード", bg=PANEL2, fg=ACCENT,
                 font=_font(11, True)).pack(side="left", padx=8)
        tk.Label(ctl, text="サムネをクリックで編集モードへ",
                 bg=PANEL2, fg=SUBTEXT, font=_font(9)).pack(side="left", padx=12)
        tk.Label(ctl, text="列数:", bg=PANEL2, fg=TEXT, font=_font(9)
                 ).pack(side="left", padx=(20, 2))
        cols_sp = tk.Spinbox(ctl, from_=3, to=12, width=4, textvariable=self.contact_cols,
                             font=_font(9), command=self._render_contact_sheet)
        cols_sp.pack(side="left")
        # v2.4: 表示時間範囲 (combined と共有変数)
        tk.Label(ctl, text="開始:", bg=PANEL2, fg=SUBTEXT, font=_font(8)
                 ).pack(side="left", padx=(12,1))
        ttk.Combobox(ctl, textvariable=self._rf_start,
                     values=[-2.0,-1.5,-1.0,-0.5],
                     state="readonly", width=4, font=_font(8)
                     ).pack(side="left", padx=(0,4))
        tk.Label(ctl, text="終了:", bg=PANEL2, fg=SUBTEXT, font=_font(8)
                 ).pack(side="left", padx=(0,1))
        ttk.Combobox(ctl, textvariable=self._rf_end,
                     values=[0.0,0.5,1.0,1.5,2.0],
                     state="readonly", width=4, font=_font(8)
                     ).pack(side="left", padx=(0,4))
        tk.Label(ctl, text="間隔:", bg=PANEL2, fg=SUBTEXT, font=_font(8)
                 ).pack(side="left", padx=(0,1))
        ttk.Combobox(ctl, textvariable=self._rf_interval,
                     values=[0.05,0.10,0.15,0.20,0.50],
                     state="readonly", width=4, font=_font(8)
                     ).pack(side="left", padx=(0,4))

        outer = tk.Frame(self.tab_contact, bg=BG); outer.pack(fill="both", expand=True)
        canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
        vsb = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        self.contact_grid = tk.Frame(canvas, bg=BG)
        win = canvas.create_window((0, 0), window=self.contact_grid, anchor="nw")
        self.contact_grid.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
            lambda e: canvas.itemconfig(win, width=e.width))
        self._contact_canvas = canvas
        self._contact_thumb_refs = []

    def _build_editor_tab(self):
        ctl = tk.Frame(self.tab_editor, bg=PANEL2); ctl.pack(fill="x", padx=4, pady=4)
        tk.Label(ctl, text="編集モード", bg=PANEL2, fg=ACCENT,
                 font=_font(11, True)).pack(side="left", padx=8)
        tk.Button(ctl, text="<<前", bg=DARK2, fg=TEXT, relief="flat", font=_font(9),
                  cursor="hand2", command=lambda: self._nav_frame(-1)
                  ).pack(side="left", padx=4, ipady=2, ipadx=4)
        tk.Button(ctl, text="次>>", bg=DARK2, fg=TEXT, relief="flat", font=_font(9),
                  cursor="hand2", command=lambda: self._nav_frame(+1)
                  ).pack(side="left", padx=4, ipady=2, ipadx=4)
        self.editor_status = tk.StringVar(value="連続写真からフレームを選んでください")
        tk.Label(ctl, textvariable=self.editor_status, bg=PANEL2, fg=GOLD,
                 font=_font(10, True)).pack(side="left", padx=20)
        tk.Label(ctl, text="左ドラッグ=移動  右クリック=取消  Del=削除  KP選択→クリック=追加  T=「見えない点」に切替",
                 bg=PANEL2, fg=SUBTEXT, font=_font(9)).pack(side="right", padx=8)

        self.editor_canvas = tk.Canvas(self.tab_editor, bg=DARK2, highlightthickness=0)
        self.editor_canvas.pack(fill="both", expand=True, padx=4, pady=(0, 4))
        self.editor_canvas.bind("<Button-1>",        self._editor_mouse_down)
        self.editor_canvas.bind("<B1-Motion>",       self._editor_mouse_drag)
        self.editor_canvas.bind("<ButtonRelease-1>", self._editor_mouse_up)
        self.editor_canvas.bind("<Button-3>",        self._editor_right_click)
        self.editor_canvas.bind("<Double-Button-1>", self._editor_double_click)  # v2.5: KP追加
        self.editor_canvas.bind("<Motion>",          self._editor_motion)
        self.editor_canvas.bind("<Leave>",           lambda e: self._set_hover_kp(None))
        self.editor_canvas.bind("<Configure>",       lambda e: self._render_editor_frame())
        # キーボードナビゲーション + 削除
        self.winfo_toplevel().bind("<Left>",      lambda e: self._nav_frame(-1) if self._on_editor_tab() else None)
        self.winfo_toplevel().bind("<Right>",     lambda e: self._nav_frame(+1) if self._on_editor_tab() else None)
        # v55: キーバインド（editor_canvas直接、フォーカス管理付き）
        self.editor_canvas.config(takefocus=True)
        self.editor_canvas.bind("<Delete>",    lambda e: self._editor_delete_kp())
        self.editor_canvas.bind("<BackSpace>", lambda e: self._editor_delete_kp())
        self.editor_canvas.bind("<Insert>",    lambda e: self._editor_place_kp_at_center())
        self.editor_canvas.bind("<t>",         lambda e: self._toggle_inferred_debug())
        self.editor_canvas.bind("<T>",         lambda e: self._toggle_inferred_debug())
        # クリック時にcanvasにフォーカスを移す（Tキーを受け取るため必須）
        def _focus_and_mousedown(e):
            self.editor_canvas.focus_set()
            self._editor_mouse_down(e)
        self.editor_canvas.bind("<Button-1>", _focus_and_mousedown)
        # v2.4: Ctrl+Z でアンドゥ (どのタブでも有効)
        self.winfo_toplevel().bind("<Control-z>", lambda e: self._undo())
        self.winfo_toplevel().bind("<Control-Z>", lambda e: self._undo())
        # 座標変換パラメータ
        self._ed_scale = 1.0
        self._ed_offx  = 0; self._ed_offy  = 0
        self._ed_cropx = 0; self._ed_cropy = 0

    def _on_editor_tab(self):
        """統合版: Refinerタブ表示中 かつ 編集サブタブ選択中"""
        try:
            if self.analyzer is not None:
                if str(self.analyzer.tabs.select()) != str(self.analyzer.tab_refiner):
                    return False
            return str(self.notebook.select()) == str(self.tab_editor)
        except Exception: return False

    # ════════════════════════════════════════
    #  ファイル読込
    # ════════════════════════════════════════
    def _tennis_analyzer_registry_path(self):
        """v2.3: Tennis Analyzer のレジストリ analyzed_videos.json を探す"""
        # 候補1: 本 GUI と同じディレクトリ
        cand = [os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "analyzed_videos.json")]
        # 候補2: ユーザーホームの .tennis_analyzer
        try:
            home = os.path.expanduser("~")
            cand.append(os.path.join(home, ".tennis_analyzer",
                                      "analyzed_videos.json"))
        except Exception: pass
        for p in cand:
            if os.path.exists(p): return p
        return None

    def _pick_from_history(self):
        """v2.3: Tennis Analyzer の履歴からサムネ付きで動画を選択"""
        reg_path = self._tennis_analyzer_registry_path()
        if not reg_path:
            messagebox.showinfo("履歴",
                "Tennis Analyzer のレジストリ analyzed_videos.json が見つかりません。\n"
                "本ファイルを Tennis Analyzer と同じフォルダに置いてください。"); return
        try:
            with open(reg_path, "r", encoding="utf-8") as f:
                reg = json.load(f)
        except Exception as e:
            messagebox.showerror("履歴", f"レジストリ読込失敗: {e}"); return
        videos = reg.get("videos", [])
        if not videos:
            messagebox.showinfo("履歴", "解析済の動画がありません"); return

        # v2.3 後修正: 全動画表示 (検出済 のみフィルタは廃止)
        # 検出済を上に来るようソートして、未検出は薄く表示
        videos.sort(key=lambda v: (
            -(v.get("num_yolo", 0) > 0),       # 検出済を上
            v.get("last_updated", ""),
        ), reverse=False)
        # last_updated は新しい順
        videos.sort(key=lambda v: v.get("last_updated", ""), reverse=True)
        videos.sort(key=lambda v: v.get("num_yolo", 0) > 0, reverse=True)

        win = tk.Toplevel(self, bg=PANEL)
        win.title("履歴から動画を選択"); win.geometry("820x600")
        win.transient(self); win.grab_set()
        tk.Label(win, text="動画を選択 (検出済 のみ)", bg=PANEL, fg=GOLD,
                 font=_font(12, True)).pack(pady=(10, 4))

        # スクロール領域
        outer = tk.Frame(win, bg=PANEL); outer.pack(fill="both", expand=True, padx=8, pady=4)
        canv = tk.Canvas(outer, bg=PANEL, highlightthickness=0)
        vsb = tk.Scrollbar(outer, orient="vertical", command=canv.yview)
        canv.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y"); canv.pack(side="left", fill="both", expand=True)
        grid = tk.Frame(canv, bg=PANEL)
        canv.create_window((0, 0), window=grid, anchor="nw")
        grid.bind("<Configure>", lambda e: canv.configure(scrollregion=canv.bbox("all")))
        def _mw_scroll(ev):
            try:
                if canv.winfo_exists(): canv.yview_scroll(int(-ev.delta/120), "units")
            except Exception: pass
        def _mw_enter(e): canv.bind_all("<MouseWheel>", _mw_scroll)
        def _mw_leave(e):
            try: canv.unbind_all("<MouseWheel>")
            except Exception: pass
        canv.bind("<Enter>", _mw_enter)
        canv.bind("<Leave>", _mw_leave)

        photo_refs = []; cols = 4
        _app2 = self   # v2.4 fix: ループ外でキャプチャ
        for i, v in enumerate(videos):
            row_i = i // cols; col_i = i % cols
            p = v.get("path", ""); fn = v.get("filename", "")
            alias = v.get("alias", "") or ""
            n_yolo = v.get("num_yolo", 0); n_ref = v.get("num_refined", 0)
            # v2.3 後修正: 未検出は視覚的に薄く
            is_detected = (n_yolo > 0)
            cell_bg = DARK2 if is_detected else "#0e1115"
            cell = tk.Frame(grid, bg=cell_bg, cursor="hand2",
                            highlightbackground=BORDER, highlightthickness=1)
            cell.grid(row=row_i, column=col_i, padx=4, pady=4, sticky="nsew")
            tp = v.get("first_thumb", "")
            thumb_lbl = None
            if tp and os.path.exists(tp):
                try:
                    img = Image.open(tp); img.thumbnail((170, 100), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img); photo_refs.append(photo)
                    thumb_lbl = tk.Label(cell, image=photo, bg=cell_bg)
                except Exception: pass
            if thumb_lbl is None:
                thumb_lbl = tk.Label(cell, text="(no thumb)", bg=cell_bg,
                                      fg=SUBTEXT, width=22, height=6)
            thumb_lbl.pack(padx=4, pady=4)
            title_text = alias if alias else fn
            tk.Label(cell, text=title_text[:32], bg=cell_bg,
                     fg=GOLD if alias else (ACCENT if is_detected else SUBTEXT),
                     font=_font(9, True), wraplength=170,
                     justify="center").pack(padx=4)
            # 検出状態ラベル
            if is_detected:
                stat_text = f"検出: {n_yolo}"
                if n_ref > 0: stat_text += f"  refined: {n_ref}"
                stat_fg = SUBTEXT
            else:
                stat_text = "未検出 (要 Tennis Analyzer)"
                stat_fg = RED
            tk.Label(cell, text=stat_text, bg=cell_bg, fg=stat_fg,
                     font=_font(8)).pack(padx=4, pady=(0, 4))

            _app2_ref = _app2   # イテレーション内キャプチャ不要だが明確化
            def _on_click(event, pp=p, vv=v, det=is_detected, _w=win):
                if not det:
                    messagebox.showinfo("未検出",
                        "この動画はまだキーポイント検出されていません。\n"
                        "Tennis Analyzer で「キーポイント検出」を実行してください。")
                    return
                try: canv.unbind_all("<MouseWheel>")
                except Exception: pass
                try: _w.grab_release()
                except Exception: pass
                try: _w.destroy()
                except Exception: pass
                # grab_release + destroy 後に安全に実行
                _app2.after(10, lambda _pp=pp, _vv=vv:
                            _app2._load_from_history_video(_pp, _vv))
            cell.bind("<Button-1>", _on_click)
            thumb_lbl.bind("<Button-1>", _on_click)
            for child in cell.winfo_children():
                child.bind("<Button-1>", _on_click)
        win._photo_refs = photo_refs

        def _win_close_hist():
            try: canv.unbind_all("<MouseWheel>")
            except Exception: pass
            win.destroy()
        win.protocol("WM_DELETE_WINDOW", _win_close_hist)
        tk.Button(win, text="キャンセル", bg=DARK2, fg=TEXT, relief="flat",
                  font=_font(10), cursor="hand2", command=_win_close_hist
                  ).pack(pady=6, ipady=4, ipadx=12)

    def _load_from_history_video(self, video_path, video_meta):
        """v2.3: 指定動画のすべての YOLO JSON をロード"""
        video_dir = os.path.dirname(video_path)
        yolo_dir = os.path.join(video_dir, "yolo")
        if not os.path.isdir(yolo_dir):
            messagebox.showwarning("読込",
                f"yolo フォルダが見つかりません:\n{yolo_dir}"); return
        stem = os.path.splitext(os.path.basename(video_path))[0]
        candidates = []
        for f in sorted(os.listdir(yolo_dir)):
            if (f.startswith(stem + "_cp")
                    and f.endswith(".json")
                    and not f.endswith("_refined.json")):
                candidates.append(os.path.join(yolo_dir, f))
        if not candidates:
            messagebox.showinfo("読込", "JSON が見つかりません"); return
        self.cp_files = candidates
        self.cp_sel["values"] = [os.path.basename(p) for p in candidates]
        self.cp_sel.current(0)
        # タイトルバー更新
        alias = video_meta.get("alias", "") or ""
        title = alias if alias else os.path.basename(video_path)
        self.title_bar_var.set(f"  {title}")
        if not self.title_bar.winfo_ismapped():
            self.title_bar.pack(side="top", fill="x", before=self.notebook
                                if self.notebook.winfo_ismapped() else None)
        # v2.3 後修正: 自動的に CP[0] をロードせず、CP サムネピッカーを表示
        self._current_video_path = video_path
        self._current_video_meta = video_meta
        self._show_cp_thumb_picker()

    def _show_cp_thumb_picker(self, parent_win=None):
        """v2.3 後修正: 現在ロード中の動画の全 CP のサムネ (offset 0) を並べて選択"""
        if not self.cp_files:
            messagebox.showinfo("CP選択", "先に動画を読込んでください"); return
        # cp_files から rank と対応サムネパスを集める
        import re
        video_path = getattr(self, "_current_video_path", None)
        if video_path is None:
            # ファイルパスから推測
            try: video_path = self.cp_files[0]
            except Exception: video_path = None
        # サムネディレクトリ (Tennis Analyzer の出力規約)
        video_dir = (os.path.dirname(video_path) if video_path and not video_path.endswith(".json")
                     else os.path.dirname(os.path.dirname(self.cp_files[0])))
        # JSONから動画ファイル名を取り、サムネディレクトリを構築
        actual_video_file = None
        try:
            with open(self.cp_files[0], "r", encoding="utf-8") as f:
                d0 = json.load(f)
            actual_video_file = d0.get("video", "")
        except Exception: pass
        if not actual_video_file:
            actual_video_file = os.path.basename(video_path or "")
        stem = os.path.splitext(os.path.basename(actual_video_file))[0]
        # サムネディレクトリの候補
        thumb_dirs = []
        if video_path:
            base = os.path.dirname(video_path)
            thumb_dirs.append(os.path.join(base, "1_thumbnails", stem))
        # JSON フォルダの兄弟も試す
        json_parent = os.path.dirname(os.path.dirname(self.cp_files[0]))
        thumb_dirs.append(os.path.join(json_parent, "1_thumbnails", stem))

        # 各 CP の rank を抽出してサムネを探す
        cp_entries = []
        for jp in self.cp_files:
            m = re.search(r"_cp(\d+)\.json$", jp)
            rank = int(m.group(1)) if m else 0
            # rank に対応する hit サムネを探す
            tp = None
            for td in thumb_dirs:
                if not os.path.isdir(td): continue
                for fn in os.listdir(td):
                    if fn.endswith(".jpg") and f"_rank{rank}_hit_" in fn:
                        tp = os.path.join(td, fn); break
                if tp: break
            # refined 済かチェック
            ref_path = jp[:-5] + "_refined.json" if jp.endswith(".json") else None
            has_ref = bool(ref_path and os.path.exists(ref_path))
            cp_entries.append({"json": jp, "rank": rank, "thumb": tp,
                                "refined": has_ref})

        # サブモーダル
        win = tk.Toplevel(self, bg=PANEL)
        win.title("HP を選択")
        win.geometry("820x600")
        win.transient(self); win.grab_set()
        if parent_win is not None:
            try: win.transient(parent_win)
            except Exception: pass
        tk.Label(win, text="ヒットポイントを選択 (打点フレーム / オフセット 0)",
                 bg=PANEL, fg=GOLD, font=_font(12, True)).pack(pady=(10, 4))
        tk.Label(win, text=f"{len(cp_entries)} CP",
                 bg=PANEL, fg=SUBTEXT, font=_font(9)).pack(pady=(0, 8))

        outer = tk.Frame(win, bg=PANEL); outer.pack(fill="both", expand=True, padx=8, pady=4)
        canv = tk.Canvas(outer, bg=PANEL, highlightthickness=0)
        vsb = tk.Scrollbar(outer, orient="vertical", command=canv.yview)
        canv.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y"); canv.pack(side="left", fill="both", expand=True)
        grid = tk.Frame(canv, bg=PANEL)
        canv.create_window((0, 0), window=grid, anchor="nw")
        grid.bind("<Configure>", lambda e: canv.configure(scrollregion=canv.bbox("all")))
        def _mw_scroll(ev):
            try:
                if canv.winfo_exists(): canv.yview_scroll(int(-ev.delta/120), "units")
            except Exception: pass
        def _mw_enter(e): canv.bind_all("<MouseWheel>", _mw_scroll)
        def _mw_leave(e):
            try: canv.unbind_all("<MouseWheel>")
            except Exception: pass
        canv.bind("<Enter>", _mw_enter)
        canv.bind("<Leave>", _mw_leave)

        photo_refs = []; cols = 5
        _app = self   # v2.4 fix: ループの外でキャプチャ
        # v2.4: サムネがない場合に動画から生成するため、cap を一時的に開く
        _video_cap = None
        _video_path = getattr(self, "_current_video_path", None)
        for i, ent in enumerate(cp_entries):
            row_i = i // cols; col_i = i % cols
            rank = ent["rank"]; tp = ent["thumb"]; has_ref = ent["refined"]
            cell = tk.Frame(grid, bg=DARK2, cursor="hand2",
                            highlightbackground=BORDER, highlightthickness=1)
            cell.grid(row=row_i, column=col_i, padx=4, pady=4, sticky="nsew")
            thumb_lbl = None
            if tp and os.path.exists(tp):
                try:
                    img = Image.open(tp); img.thumbnail((140, 90), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img); photo_refs.append(photo)
                    thumb_lbl = tk.Label(cell, image=photo, bg=DARK2)
                except Exception: pass
            # v2.4: サムネなし → JSON の hit_time から動画フレームを取得
            if thumb_lbl is None and _video_path and os.path.exists(_video_path):
                try:
                    if _video_cap is None:
                        _video_cap = cv2.VideoCapture(_video_path)
                    jp = ent["json"]
                    with open(jp, "r", encoding="utf-8") as f:
                        jd = json.load(f)
                    ht = jd.get("hit_time", 0.0)
                    fps_ = _video_cap.get(cv2.CAP_PROP_FPS) or 30
                    _video_cap.set(cv2.CAP_PROP_POS_FRAMES, int(ht * fps_))
                    ret, frm = _video_cap.read()
                    if ret:
                        rgb = cv2.cvtColor(frm, cv2.COLOR_BGR2RGB)
                        img = Image.fromarray(rgb)
                        img.thumbnail((140, 90), Image.LANCZOS)
                        photo = ImageTk.PhotoImage(img); photo_refs.append(photo)
                        thumb_lbl = tk.Label(cell, image=photo, bg=DARK2)
                except Exception: pass
            if thumb_lbl is None:
                thumb_lbl = tk.Label(cell, text="(thumb なし)", bg=DARK2,
                                      fg=SUBTEXT, width=20, height=5)
            thumb_lbl.pack(padx=4, pady=4)
            badge = " ◆ refined" if has_ref else ""
            tk.Label(cell, text=f"HP #{rank}{badge}", bg=DARK2,
                     fg=GOLD if has_ref else ACCENT,
                     font=_font(10, True)).pack(padx=4, pady=(0, 4))

            def _on_click(event, jp=ent["json"], _w=win):
                try: canv.unbind_all("<MouseWheel>")
                except Exception: pass
                # grab_set を解放してから destroy
                try: _w.grab_release()
                except Exception: pass
                try: _w.destroy()
                except Exception: pass
                # cp_sel 同期
                try:
                    fnm = os.path.basename(jp)
                    vals = _app.cp_sel["values"]
                    if fnm in vals:
                        _app.cp_sel.current(list(vals).index(fnm))
                except Exception: pass
                # メインスレッドで安全に _load_one を実行
                _app.after(10, lambda p=jp: _app._load_one(p))
            cell.bind("<Button-1>", _on_click)
            for child in cell.winfo_children():
                child.bind("<Button-1>", _on_click)
        win._photo_refs = photo_refs
        # v2.4: サムネ生成用の動画 cap を解放
        if _video_cap is not None:
            try: _video_cap.release()
            except Exception: pass

        def _win_close_cp():
            try: canv.unbind_all("<MouseWheel>")
            except Exception: pass
            win.destroy()
        win.protocol("WM_DELETE_WINDOW", _win_close_cp)
        tk.Button(win, text="キャンセル", bg=DARK2, fg=TEXT, relief="flat",
                  font=_font(10), cursor="hand2", command=_win_close_cp
                  ).pack(pady=6, ipady=4, ipadx=12)

    def _load_json(self):
        path = filedialog.askopenfilename(
            title="YOLO JSON",
            filetypes=[("YOLO JSON", "*.json"), ("All", "*.*")])
        if not path: return
        if path.endswith("_refined.json"):
            messagebox.showwarning("JSON",
                "_refined.json を指定しました。raw 側 (_cpNN.json) を選んでください。")
            return
        self.cp_files = [path]
        self.cp_sel["values"] = [os.path.basename(path)]
        self.cp_sel.current(0)
        self._load_one(path)

    def _load_folder(self):
        d = filedialog.askdirectory(title="YOLO JSON のあるフォルダ")
        if not d: return
        candidates = []
        for sub in ["", "yolo"]:
            base = os.path.join(d, sub) if sub else d
            if os.path.isdir(base):
                for f in sorted(os.listdir(base)):
                    p = os.path.join(base, f)
                    if (f.endswith(".json") and "_cp" in f
                            and not f.endswith("_refined.json")):
                        candidates.append(p)
        if not candidates:
            messagebox.showinfo("フォルダ", "YOLO JSON が見つかりませんでした")
            return
        self.cp_files = candidates
        self.cp_sel["values"] = [os.path.basename(p) for p in candidates]
        self.cp_sel.current(0)
        self._load_one(candidates[0])

    def _switch_cp(self):
        idx = self.cp_sel.current()
        if 0 <= idx < len(self.cp_files):
            self._load_one(self.cp_files[idx])

    def _adjust_pulldowns_to_data(self):
        """v44: プルダウン範囲を実データ範囲そのままに合わせる。
        開始/終了 = KPデータの実際の min/max、間隔デフォルト 0.2s"""
        if not self.raw_frames or not hasattr(self, "_cb_start"):
            return
        try:
            times_rel = [f["time"] - self.hit_t for f in self.raw_frames]
            t_min = min(times_rel); t_max = max(times_rel)
            # フレーム間隔の中央値
            times_sorted = sorted(times_rel)
            gaps = [times_sorted[i+1] - times_sorted[i] for i in range(len(times_sorted)-1)]
            gaps = [g for g in gaps if g > 0]
            dt = sorted(gaps)[len(gaps)//2] if gaps else 0.033

            # 開始プルダウン: t_min を含み 0 まで、細かい候補
            def _make_start_vals(t_min):
                # 実データ範囲の端 (t_min) を必ず含める
                vals = [round(t_min, 2)]
                # 0.25秒刻みの候補も追加
                v = round(t_min, 2)
                # t_minを起点に0.25秒ずつ進めて0まで
                while v < -0.05:
                    v += 0.25
                    if v > -0.05: break
                    vals.append(round(v, 2))
                vals.append(0.0)
                return sorted(set(vals))

            def _make_end_vals(t_max):
                vals = [0.0]
                v = 0.0
                while v < t_max - 0.05:
                    v += 0.25
                    if v > t_max + 0.05: break
                    vals.append(round(v, 2))
                # 実データの端 (t_max) も必ず含める
                vals.append(round(t_max, 2))
                return sorted(set(vals))

            start_vals = _make_start_vals(t_min)
            end_vals = _make_end_vals(t_max)
            self._cb_start["values"] = start_vals
            self._cb_end["values"] = end_vals
            # デフォルト: 実データの端を選択
            self._rf_start.set(round(t_min, 2))
            self._rf_end.set(round(t_max, 2))

            # 間隔プルダウン: 0.2秒をデフォルトに
            iv_vals = ["最短", round(dt, 3), 0.05, 0.1, 0.15, 0.2, 0.25, 0.5]
            iv_vals = sorted(set(iv_vals),
                             key=lambda x: float("-inf") if x == "最短" else float(x))
            self._cb_iv["values"] = iv_vals
            # 実データ範囲が広い場合は 0.2、狭い場合は最短
            span = t_max - t_min
            if span >= 1.0:
                self._rf_interval.set("0.2")
            else:
                self._rf_interval.set("最短")
        except Exception as e:
            print(f"プルダウン自動調整失敗: {e}")

    def _full_reset(self):
        """v48: 動画/HP切替時に全状態を徹底クリア"""
        self.frames_cache.clear()
        self.raw_frames = None
        self.refined_frames = None
        self.refined_auto = None
        self.raw_data = None
        self.manual_edits.clear()
        self._inferred_overrides.clear()
        self._mp3d_frames = []
        self._scene_check_enabled = False
        self.selected_frame_idx = None
        self.selected_kp = None
        self.hover_kp = None
        self._placement_kp = None
        self.video_w = None; self.video_h = None
        # グラフクリア
        for attr in ("_combined_fig","_combined_fig2","_combined_fig3",
                     "_combined_chart_canvas","_combined_chart2_canvas","_combined_chart3_canvas",
                     "_fig","_chart_canvas"):
            obj = getattr(self, attr, None)
            if obj is not None:
                try:
                    if hasattr(obj, "get_tk_widget"):
                        obj.get_tk_widget().destroy()
                    elif hasattr(obj, "clf"):
                        import matplotlib.pyplot as plt
                        plt.close(obj)
                except Exception: pass
                setattr(self, attr, None)

    def _load_one(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            messagebox.showerror("読込", f"JSON 読込失敗: {e}"); return
        frames = data.get("frames", [])
        # v38: 過去バージョンで混入したplaceholderフレームを除去
        frames = [f for f in frames if not f.get("_placeholder")]
        if not frames:
            messagebox.showwarning("読込", "frames が空"); return

        # v48: 徹底クリア
        self._full_reset()
        self.json_path = path
        self.raw_data = data
        self.raw_frames = frames
        loaded_hit_t = data.get("hit_time",
                                frames[len(frames)//2].get("time", 0.0))
        # v43: 壊れたhit_time検出 (フレーム範囲外なら中央値で代替)
        f_min = min(f["time"] for f in frames)
        f_max = max(f["time"] for f in frames)
        if loaded_hit_t < f_min - 0.5 or loaded_hit_t > f_max + 0.5:
            # hit_timeがフレーム範囲外 → 中央フレームを使用
            loaded_hit_t = frames[len(frames)//2].get("time", (f_min + f_max) / 2)
        self.hit_t = loaded_hit_t
        # v41: 実データ範囲に合わせてプルダウン自動調整
        try: self._adjust_pulldowns_to_data()
        except Exception: pass
        # v62: 3D HP表示を更新
        try:
            import re
            m = re.search(r"_cp(\d+)", path)
            if m and hasattr(self, "_3d_hp_var"):
                rank_ = int(m.group(1))
                shot = ""
                if self.analyzer:
                    for pk in self.analyzer.peaks:
                        if pk["rank"] == rank_:
                            shot = pk.get("shot_type", "") or ""; break
                self._3d_hp_var.set(f"HP#{rank_}  t={self.hit_t:.2f}s  {shot}")
        except Exception: pass
        # v2.3 後修正: トップバーの現在 CP 表示を更新
        try:
            import re
            m = re.search(r"_cp(\d+)\.json$", path)
            if m and hasattr(self, "cur_cp_var"):
                self.cur_cp_var.set(f"HP#{int(m.group(1))}")
        except Exception: pass
        # v2.4: 総合ビューのショット種別表示更新
        try:
            shot = data.get("shot_type","") or ""
            cp_rank = data.get("cp_rank", "")
            shot_ja_map = {"forehand":"フォアハンド","backhand":"バックハンド",
                           "serve":"サーブ","volley":"ボレー","smash":"スマッシュ"}
            shot_ja = shot_ja_map.get(shot, shot)
            cp_lbl = f"#{cp_rank}" if cp_rank else ""
            if hasattr(self, "_cv_shot_var"):
                self._cv_shot_var.set(f"{cp_lbl}  {shot_ja}")
        except Exception: pass

        # 動画自動検出
        self.video_path = _detect_video(path)
        if self.video_path is None:
            self.status.set(f"⚠ 動画見つからず — グラフのみ可")
        else:
            self.status.set(f"動画: {os.path.basename(self.video_path)}")

        # 既存 refined.json があれば手動編集を読み込む
        self.manual_edits.clear()
        refined_path = path[:-5] + "_refined.json" if path.endswith(".json") else None
        if refined_path and os.path.exists(refined_path):
            try:
                with open(refined_path, "r", encoding="utf-8") as f:
                    prev = json.load(f)
                for idx, pf in enumerate(prev.get("frames", [])):
                    for ki in range(17):
                        if pf.get(f"kp{ki:02d}_deleted"):
                            self.manual_edits[(idx, ki)] = None
                        elif pf.get(f"kp{ki:02d}_manual"):
                            self.manual_edits[(idx, ki)] = (
                                pf[f"kp{ki:02d}_x"], pf[f"kp{ki:02d}_y"])
                    if pf.get("racket_tip_deleted"):
                        self.manual_edits[(idx, 17)] = None
                    elif pf.get("racket_tip_manual"):
                        self.manual_edits[(idx, 17)] = (
                            pf["racket_tip_x"], pf["racket_tip_y"])
                    if pf.get("ball_deleted"):
                        self.manual_edits[(idx, 18)] = None
                    elif pf.get("ball_manual"):
                        self.manual_edits[(idx, 18)] = (
                            pf["ball_refined_x"], pf["ball_refined_y"])
            except Exception:
                pass
        self._update_edit_count()

        # 表示用クロップ算出
        self.crop_rect = self._compute_crop_rect()

        # フレーム抽出 (バックグラウンド)
        self.frames_cache.clear()
        self.video_w = None
        self.video_h = None
        self.selected_frame_idx = None
        self.selected_kp = None
        self.hover_kp = None
        if self.video_path:
            self._extract_frames_async()
        else:
            self._refine_now()

    def _compute_crop_rect(self):
        if not self.raw_frames: return None
        boxes = [f.get("person_bbox") for f in self.raw_frames if f.get("person_bbox")]
        if not boxes: return None
        x1 = min(b[0] for b in boxes); y1 = min(b[1] for b in boxes)
        x2 = max(b[2] for b in boxes); y2 = max(b[3] for b in boxes)
        # v61: パディング 15% (サーブは上方向40%)
        w = x2 - x1; h = y2 - y1
        pad = max(w, h) * 0.15
        pad_top = pad
        # サーブ/スマッシュ判定 → 上方向を拡大 (ラケット振り上げ対応)
        try:
            is_serve = False
            if self.analyzer is not None:
                shots = getattr(self.analyzer, "_video_meta_extra", {}).get("main_shots", [])
                if any(s in ("サーブ", "スマッシュ") for s in shots):
                    is_serve = True
                # 現在HPのラベルもチェック
                if not is_serve and self.analyzer.peaks and self.analyzer.peak_idx < len(self.analyzer.peaks):
                    lbl = self.analyzer.peaks[self.analyzer.peak_idx].get("shot_type", "") or ""
                    if "サーブ" in lbl or "スマッシュ" in lbl:
                        is_serve = True
            if is_serve:
                pad_top = max(w, h) * 0.40
        except Exception: pass
        return (max(0, x1 - pad), max(0, y1 - pad_top), x2 + pad, y2 + pad)

    def _extract_frames_async(self):
        if self._extracting: return
        self._extracting = True
        # v38: placeholder方式は廃止 (KP補間ゴースト・インデックス不整合の原因)
        #      JSONにあるフレームのみ抽出。範囲が狭い場合はステータスで案内
        if self.raw_frames and len(self.raw_frames) <= 15:
            try:
                t_min = min(f["time"] for f in self.raw_frames) - self.hit_t
                t_max = max(f["time"] for f in self.raw_frames) - self.hit_t
                self.status.set(
                    f"KPデータは {t_min:+.2f}s〜{t_max:+.2f}s のみ。"
                    f"広範囲は左パネル「キーポイント検出 (現在のHP)」で再検出してください")
            except Exception: pass
        self._extract_progress = (0, len(self.raw_frames))
        self._refresh_current_tab()

        def worker():
            try:
                cap = cv2.VideoCapture(self.video_path)
                fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
                total = len(self.raw_frames)
                for idx, f in enumerate(self.raw_frames):
                    t = f.get("time", 0)
                    cap.set(cv2.CAP_PROP_POS_FRAMES, int(fps * t))
                    ok, frame = cap.read()
                    if ok:
                        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        self.frames_cache[idx] = rgb
                        if self.video_h is None:
                            self.video_h, self.video_w = rgb.shape[:2]
                    self._extract_progress = (idx + 1, total)
                    # 5フレームごとに進捗UI更新
                    if (idx + 1) % 5 == 0 or idx + 1 == total:
                        self.after(0, self._update_extract_progress)
                cap.release()
                self.after(0, self._on_frames_ready)
            except Exception as e:
                err = str(e)
                self.after(0, lambda err=err: self.status.set(f"フレーム抽出失敗: {err}"))
            finally:
                self._extracting = False
        threading.Thread(target=worker, daemon=True).start()

    def _update_extract_progress(self):
        done, total = self._extract_progress
        self.status.set(f"動画フレーム抽出中…  {done} / {total}")
        # 中央の進捗表示も更新
        self._refresh_current_tab()

    def _on_frames_ready(self):
        self.status.set(f"抽出完了: {len(self.frames_cache)}フレーム")
        self._refine_now()

    # ════════════════════════════════════════
    #  パラメータ変更 → 再計算
    # ════════════════════════════════════════
    def _on_param_change(self):
        if self._debounce_id:
            try: self.after_cancel(self._debounce_id)
            except Exception: pass
        self._debounce_id = self.after(220, self._refine_now)
        # v2.3: パラメータ変更でも自動保存トリガ (refine_now 後に保存される)
        self._trigger_autosave()

    def _on_kp_filter_change(self):
        # KPフィルタは再計算不要、表示のみ更新
        self._refresh_current_tab()

    def _refine_now(self):
        """フル再計算: 自動洗練 → refined_auto に保存 → 手動編集波及 → refined_frames"""
        if self.raw_frames is None: return
        RFN.VELOCITY_MAD_K      = float(self.p_vel_k.get())
        RFN.ACCEL_MAD_K         = float(self.p_acc_k.get())
        RFN.LINK_DEVIATION_FRAC = float(self.p_link_dev.get())
        w = int(self.p_savgol_w.get())
        if w % 2 == 0: w += 1
        RFN.SAVGOL_WINDOW = w
        RFN.SAVGOL_ORDER  = int(self.p_savgol_o.get())

        kp_th  = float(self.p_kp_th.get())
        obj_th = float(self.p_obj_th.get())

        # 自動洗練 (手動編集なし)
        frames = copy.deepcopy(self.raw_frames)
        kp_stats = RFN.refine_keypoints(frames, kp_th=kp_th, verbose=False)
        rk_stats = RFN.refine_racket(frames, kp_th=kp_th, obj_th=obj_th, verbose=False)
        bl_stats = RFN.refine_ball(frames, obj_th=obj_th, verbose=False)
        RFN.recompute_cog(frames, kp_th=kp_th)
        self.refined_auto = frames

        self.stats_lbl.config(text=(
            f"低信頼:{kp_stats['low_conf_removed']:3d}  "
            f"速度:{kp_stats['velocity_outliers']:2d}  "
            f"加速:{kp_stats['accel_outliers']:2d}  "
            f"リンク:{kp_stats['link_outliers']:2d}  "
            f"ラケ置換:{rk_stats['frames_replaced']:2d}  "
            f"ボール置換:{bl_stats['frames_replaced']:2d}"))

        # 手動編集を波及付きで適用 → refined_frames
        self._apply_manual_edits_with_smoothing()

        # v31: 洗練後のフレームに角度データを計算
        if self.refined_frames:
            for f in self.refined_frames:
                try:
                    # TennisAppの静的メソッドを使用
                    angles = TennisApp._calc_face_body_angles(f)
                    if angles:
                        for ak, av in angles.items():
                            if ak != "invisible_kps":
                                f[ak] = av
                except Exception: pass

        # v2.5: シーン変化検出 — v33: 初回ロード時はスキップ
        if getattr(self, "_scene_check_enabled", False):
            self._detect_scene_changes()
        self._scene_check_enabled = True  # 次回以降は有効

        self._refresh_current_tab()

    def _detect_scene_changes(self):
        """v2.5: 洗練後のフレーム間でKP座標が大きくジャンプするフレームを検出し警告。
           主要KP (鼻, 両肩, 両腰, 両手首) の移動量の中央値が閾値を超えたら異常。"""
        frames = self.refined_frames
        if not frames or len(frames) < 3: return
        MONITOR_KPS = [0, 5, 6, 11, 12, 9, 10]  # 鼻,左肩,右肩,左腰,右腰,左手首,右手首
        JUMP_THRESH = 80.0  # px — フレーム間移動量の中央値がこれを超えたら異常
        anomalies = []
        for i in range(1, len(frames)):
            displacements = []
            for ki in MONITOR_KPS:
                x0 = frames[i-1].get(f"kp{ki:02d}_x")
                y0 = frames[i-1].get(f"kp{ki:02d}_y")
                x1 = frames[i].get(f"kp{ki:02d}_x")
                y1 = frames[i].get(f"kp{ki:02d}_y")
                c0 = frames[i-1].get(f"kp{ki:02d}_c", 0) or 0
                c1 = frames[i].get(f"kp{ki:02d}_c", 0) or 0
                if x0 is None or y0 is None or x1 is None or y1 is None: continue
                if c0 < 0.3 or c1 < 0.3: continue
                d = ((x1-x0)**2 + (y1-y0)**2) ** 0.5
                displacements.append(d)
            if len(displacements) >= 3:
                displacements.sort()
                median_d = displacements[len(displacements)//2]
                if median_d > JUMP_THRESH:
                    t = frames[i].get("time", 0.0)
                    anomalies.append((i, t, median_d))
        self._scene_anomalies = anomalies
        if anomalies:
            times_str = ", ".join(f"f{a[0]}({a[1]:.2f}s)" for a in anomalies[:5])
            extra = f" 他{len(anomalies)-5}件" if len(anomalies) > 5 else ""
            messagebox.showwarning("シーン変化検出",
                f"時系列異常を {len(anomalies)} フレームで検出しました。\n"
                f"カメラ切替やトラッキングロスの可能性があります。\n\n"
                f"{times_str}{extra}\n\n"
                f"該当フレームのKPを確認・修正してください。")
        else:
            self._scene_anomalies = []

    def _apply_manual_edits_with_smoothing(self):
        """refined_auto をベースに、self.manual_edits を三角形重みで前後Nコマに波及。
           結果は self.refined_frames に格納し、その後COGを更新。"""
        if self.refined_auto is None: return
        frames = copy.deepcopy(self.refined_auto)
        n = len(frames)
        kp_th  = float(self.p_kp_th.get())
        obj_th = float(self.p_obj_th.get())
        window = int(self.p_edit_window.get())

        if self.manual_edits:
            edits_by_kp = {}
            for (idx, ki), val in self.manual_edits.items():
                edits_by_kp.setdefault(ki, []).append((idx, val))

            for ki, edits in edits_by_kp.items():
                edits.sort()
                # 移動編集のみ波及対象 (val が None = 削除はそのコマだけ)
                move_edits = [(i, v) for (i, v) in edits if v is not None]
                for target in range(n):
                    # 完全一致 (削除含む)
                    exact = next((e for e in edits if e[0] == target), None)
                    if exact is not None:
                        _, val = exact
                        if val is None:
                            self._apply_edit_to_frame(frames[target], ki, None, None)
                        else:
                            self._apply_edit_to_frame(frames[target], ki, val[0], val[1])
                        continue
                    if window <= 0 or not move_edits:
                        continue
                    best = None; best_d = window + 1
                    for edit_idx, val in move_edits:
                        d = abs(target - edit_idx)
                        if d < best_d:
                            best_d = d; best = (edit_idx, val[0], val[1])
                    if best is None or best_d > window:
                        continue
                    weight = max(0.0, 1.0 - best_d / (window + 1))
                    edit_auto = self._kp_position(self.refined_auto[best[0]], ki, kp_th, obj_th)
                    target_auto = self._kp_position(self.refined_auto[target], ki, kp_th, obj_th)
                    if edit_auto is None or target_auto is None:
                        continue
                    dx = best[1] - edit_auto[0]
                    dy = best[2] - edit_auto[1]
                    new_x = target_auto[0] + dx * weight
                    new_y = target_auto[1] + dy * weight
                    self._apply_edit_to_frame(frames[target], ki, new_x, new_y)

        # 編集の影響を受けるフレームのCOGを再計算
        affected = set()
        for (idx, ki) in self.manual_edits.keys():
            if ki >= 17: continue
            for delta in range(-window, window + 1):
                t = idx + delta
                if 0 <= t < n: affected.add(t)
        for idx in affected:
            cog = RFN.compute_cog_one(frames[idx], kp_th)
            if cog is not None:
                frames[idx]["cog_x"] = cog[0]
                frames[idx]["cog_y"] = cog[1]

        self.refined_frames = frames

    def _apply_edit_to_frame(self, frame, ki, x, y):
        """1フレームにキーポイント編集を適用。x=None or y=None なら削除。"""
        deleting = (x is None) or (y is None)
        if ki < 17:
            if deleting:
                frame[f"kp{ki:02d}_x"] = None
                frame[f"kp{ki:02d}_y"] = None
                frame[f"kp{ki:02d}_c"] = 0.0
            else:
                frame[f"kp{ki:02d}_x"] = float(x)
                frame[f"kp{ki:02d}_y"] = float(y)
                frame[f"kp{ki:02d}_c"] = RFN.REFINED_CONF
        elif ki == 17:
            if deleting:
                frame["racket_tip_x"] = None
                frame["racket_tip_y"] = None
                frame["racket_conf"] = 0.0
            else:
                frame["racket_tip_x"] = float(x)
                frame["racket_tip_y"] = float(y)
                frame["racket_conf"] = RFN.REFINED_CONF
        elif ki == 18:
            if deleting:
                frame["ball_refined_x"] = None
                frame["ball_refined_y"] = None
            else:
                frame["ball_refined_x"] = float(x)
                frame["ball_refined_y"] = float(y)

    def _undo_push(self):
        """v2.4: 現在の manual_edits スナップショットをアンドゥスタックに積む"""
        self._undo_stack.append(dict(self.manual_edits))

    def _undo(self):
        """v2.4: 直前の編集を取り消す"""
        if not self._undo_stack:
            self.status.set("アンドゥできる操作がありません")
            return
        prev = self._undo_stack.pop()
        self.manual_edits.clear()
        self.manual_edits.update(prev)
        self._update_edit_count()
        self._apply_manual_edits_with_smoothing()
        self._refresh_current_tab()
        self.status.set(f"アンドゥ完了 (残り {len(self._undo_stack)})")
        self._trigger_autosave()

    def _ball_delete_propagate(self, center_idx, spread=3):
        """v2.4: ボール (ki=18) 削除時に前後 spread フレームも自動削除。
        前後フレームでボールが検出されていたフレームのみ削除 (既に未検出なら無視)。
        """
        if self.refined_frames is None: return
        kp_th = float(self.p_kp_th.get())
        obj_th = float(self.p_obj_th.get())
        n = len(self.refined_frames)
        lo = max(0, center_idx - spread)
        hi = min(n - 1, center_idx + spread)
        deleted = []
        for i in range(lo, hi + 1):
            # そのフレームでボールが検出されているか確認
            pos = self._kp_position(self.refined_frames[i], 18, kp_th, obj_th)
            if pos is not None or i == center_idx:
                self.manual_edits[(i, 18)] = None
                deleted.append(i)
        count = len(deleted)
        self.status.set(f"ボールを {count} フレームから削除 (#{lo}〜#{hi})")

    def _update_edit_count(self):
        """v2.4 fix: 編集件数表示を更新 (このメソッドが欠落していた)"""
        self.edit_count_var.set(f"編集: {len(self.manual_edits)}")
        # 編集件数変更時に自動保存トリガ
        self._trigger_autosave()

    def _clear_all_edits(self):
        if not self.manual_edits:
            return
        if not messagebox.askyesno("編集取消",
                f"{len(self.manual_edits)} 件の手動編集を全て取消しますか?"):
            return
        self._undo_push()  # v2.4
        self.manual_edits.clear()
        self._update_edit_count()
        self._apply_manual_edits_with_smoothing()
        self._refresh_current_tab()
        self._trigger_autosave()

    # ════════════════════════════════════════
    #  座標変換とKP位置取得
    # ════════════════════════════════════════
    def _kp_position(self, frame, ki, kp_th, obj_th):
        pos = None
        if ki < 17:
            kx = frame.get(f"kp{ki:02d}_x"); ky = frame.get(f"kp{ki:02d}_y")
            kc = frame.get(f"kp{ki:02d}_c", 0) or 0
            if kx is None or ky is None or kc < kp_th:
                return None
            # 顔の見えない場合の妥当性チェック (鼻=0, 左目=1, 右目=2)
            if ki in (0, 1, 2):
                lex = frame.get("kp03_x"); ley = frame.get("kp03_y")
                lec = frame.get("kp03_c", 0) or 0
                rex = frame.get("kp04_x"); rey = frame.get("kp04_y")
                rec = frame.get("kp04_c", 0) or 0
                if (lex is not None and rex is not None
                        and lec >= kp_th and rec >= kp_th):
                    ear_xmin = min(lex, rex); ear_xmax = max(lex, rex)
                    ear_d = abs(lex - rex)
                    margin = max(ear_d * 0.20, 8.0)
                    if kx < ear_xmin - margin or kx > ear_xmax + margin:
                        return None
                    ear_ym = (ley + rey) / 2.0
                    if abs(ky - ear_ym) > max(ear_d * 1.0, 30.0):
                        return None
            pos = (float(kx), float(ky))
        elif ki == 17:
            tx = frame.get("racket_tip_x"); ty = frame.get("racket_tip_y")
            rc = frame.get("racket_conf", 0) or 0
            if tx is None or ty is None or rc < obj_th: return None
            pos = (float(tx), float(ty))
        elif ki == 18:
            brx = frame.get("ball_refined_x"); bry = frame.get("ball_refined_y")
            if brx is not None and bry is not None:
                pos = (float(brx), float(bry))
            else:
                bb = frame.get("ball1_bbox"); bc = frame.get("ball1_conf", 0) or 0
                if not bb or bc < obj_th: return None
                pos = ((bb[0]+bb[2])/2.0, (bb[1]+bb[3])/2.0)
        elif ki == 19:
            cx = frame.get("cog_x"); cy = frame.get("cog_y")
            if cx is not None and cy is not None:
                pos = (float(cx), float(cy))
            else:
                cog = RFN.compute_cog_one(frame, kp_th)
                if cog is None: return None
                pos = cog
        else:
            return None
        # 画面外チェック (動画フレームの外なら非表示)
        if pos is not None and self.video_w is not None and self.video_h is not None:
            margin = 4
            if (pos[0] < -margin or pos[0] > self.video_w + margin
                    or pos[1] < -margin or pos[1] > self.video_h + margin):
                return None
        return pos

    # ════════════════════════════════════════
    #  グラフタブ
    # ════════════════════════════════════════
    def _render_empty_chart(self):
        if self._chart_canvas:
            try: self._chart_canvas.get_tk_widget().destroy()
            except Exception: pass
        if self._fig:
            try: plt.close(self._fig)
            except Exception: pass
        fig = plt.Figure(figsize=(10, 5.5), dpi=90, facecolor=BG)
        ax = fig.add_subplot(111, facecolor=DARK2)
        ax.tick_params(colors=TEXT, labelsize=11)
        for sp in ax.spines.values(): sp.set_color(SUBTEXT)
        ax.text(0.5, 0.5, "JSON を読み込むとここに表示",
                ha="center", va="center", color=SUBTEXT,
                fontsize=14, transform=ax.transAxes)
        ax.set_xticks([]); ax.set_yticks([])
        fig.tight_layout()
        self._fig = fig
        self._chart_canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self._chart_canvas.draw()
        self._chart_canvas.get_tk_widget().pack(fill="both", expand=True)

    def _update_chart(self):
        if self.raw_frames is None or self.refined_frames is None:
            return
        # v34: グラフ1は表示中のみ描画（非表示タブへの描画を停止）
        if self._cv_show_graph.get():
            try:
                self._render_chart_into(self.combined_chart_frame, dpi=85, fig_h=2.0,
                                        set_attrs=("_combined_fig", "_combined_chart_canvas"))
            except Exception: pass
        # v28: グラフ2 (XY軌跡) も更新
        try: self._update_chart2()
        except Exception: pass
        # v31: グラフ3 (角度) も更新
        try: self._update_chart3()
        except Exception: pass

    def _render_chart_into(self, target_frame, dpi=90, fig_h=5.5, set_attrs=None):
        """v2.3: 指定 frame にチャートを描画。set_attrs=(fig_attr, canvas_attr) で
           前回の fig/canvas を破棄する属性名を指定する"""
        selected = [i for i, v in enumerate(self.kp_vars) if v.get()]
        axis = self.axis.get() or "y"
        kp_th = float(self.p_kp_th.get())
        obj_th = float(self.p_obj_th.get())

        if set_attrs:
            fig_attr, canvas_attr = set_attrs
            prev_canvas = getattr(self, canvas_attr, None)
            prev_fig = getattr(self, fig_attr, None)
            if prev_canvas:
                try: prev_canvas.get_tk_widget().destroy()
                except Exception: pass
            if prev_fig:
                try: plt.close(prev_fig)
                except Exception: pass

        fig = plt.Figure(figsize=(10, fig_h), dpi=dpi, facecolor=BG)
        ax = fig.add_subplot(111, facecolor=DARK2)
        ax.tick_params(colors=TEXT, labelsize=11)
        for sp in ax.spines.values(): sp.set_color(SUBTEXT)

        rel_t = np.array([f["time"] - self.hit_t for f in self.raw_frames])

        any_plotted = False
        for ki in selected:
            color = KP_COLORS[ki] if ki < len(KP_COLORS) else "#fff"
            raw_vals, ref_vals = [], []
            for f_raw, f_ref in zip(self.raw_frames, self.refined_frames):
                pr = self._kp_position(f_raw, ki, kp_th, obj_th)
                raw_vals.append((pr[1] if axis == "y" else pr[0]) if pr else np.nan)
                pf = self._kp_position(f_ref, ki, kp_th, obj_th)
                ref_vals.append((pf[1] if axis == "y" else pf[0]) if pf else np.nan)
            marker = "*" if ki == 19 else "."
            ms_raw = 6 if ki == 19 else 3
            ms_ref = 9 if ki == 19 else 5
            if not np.all(np.isnan(raw_vals)):
                ax.plot(rel_t, raw_vals, linestyle=":", color=color, linewidth=1.0,
                        marker=marker, markersize=ms_raw, alpha=0.55, zorder=3)
                any_plotted = True
            if not np.all(np.isnan(ref_vals)):
                ax.plot(rel_t, ref_vals, linestyle="-", color=color, linewidth=2.0,
                        marker=marker, markersize=ms_ref, alpha=1.0, zorder=5)
                any_plotted = True

        ax.axvline(0, color=GOLD, linestyle="--", alpha=0.7, linewidth=1.5)
        if axis == "y": ax.invert_yaxis()
        ax.set_xlabel("CPからの時刻 (秒)", color=TEXT, fontsize=12)
        ax.set_ylabel(f"{axis} 座標 (px)", color=TEXT, fontsize=12)
        ax.grid(True, alpha=0.2)
        if not any_plotted:
            ax.text(0.5, 0.5, "表示KPを選択してください",
                    ha="center", va="center", color=SUBTEXT,
                    fontsize=14, transform=ax.transAxes)
        ax.text(0.99, 0.99, "点線=生  実線=洗練後",
                ha="right", va="top", color=SUBTEXT, fontsize=10,
                transform=ax.transAxes,
                bbox=dict(boxstyle="round", facecolor=PANEL,
                          edgecolor=BORDER, alpha=0.8))
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=target_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        if set_attrs:
            setattr(self, set_attrs[0], fig)
            setattr(self, set_attrs[1], canvas)
            # v2.3: 総合ビューのグラフにマウスホバー → 該当 frame をハイライト
            if set_attrs[0] == "_combined_fig":
                try:
                    canvas.mpl_connect("motion_notify_event",
                                       self._cv_on_chart_motion)
                    canvas.mpl_connect("axes_leave_event",
                                       lambda e: self._cv_hover_graph_frame(None))
                except Exception: pass

    def _cv_on_chart_motion(self, event):
        """総合ビューのグラフ上をホバー → 一番近い frame_idx を求めて写真側へ通知"""
        if event.inaxes is None or not self.raw_frames: return
        t_hover = event.xdata
        if t_hover is None: return
        # 各フレームの t_rel と比較し、最近のフレームを選ぶ
        best_idx = None
        best_d = float("inf")
        for i, f in enumerate(self.raw_frames):
            t_rel = f["time"] - self.hit_t
            d = abs(t_rel - t_hover)
            if d < best_d:
                best_d = d; best_idx = i
        # しきい値: フレーム間隔の半分以内
        if best_idx is not None and best_d < 0.10:  # 100ms 以内なら採用
            self._cv_hover_graph_frame(best_idx)

    # ════════════════════════════════════════
    #  連続写真タブ
    # ════════════════════════════════════════
    def _render_contact_sheet(self):
        # v43: 総合ビュータブのみ描画 (旧・連続写真/グラフタブは統合済み)
        try:
            self._render_contact_into(self.combined_contact_grid,
                                       self._combined_contact_canvas,
                                       self._combined_thumb_refs,
                                       force_cols=None)
        except Exception: pass

    def _render_contact_into(self, target_grid, target_canvas, refs_list,
                              force_cols=None):
        """v2.3: 指定 grid に連続写真を描画"""
        for w in target_grid.winfo_children(): w.destroy()
        refs_list.clear()
        # v2.3 後修正: 総合ビューの場合は widget 参照をクリアして再構築
        if force_cols is not None:
            self._cv_photo_widgets.clear()
            self._cv_photo_normal_border.clear()
            self._cv_prev_hover_idx = None

        if self.raw_frames is None:
            tk.Label(target_grid, text="JSON を読み込んでください",
                     bg=BG, fg=SUBTEXT, font=_font(13)).pack(pady=40); return

        if self._extracting or (self.video_path and not self.frames_cache):
            done, total = self._extract_progress
            msg = (f"動画フレーム抽出中…\n\n{done} / {total} コマ\n\n"
                   "お待ちください") if total else "処理中…"
            tk.Label(target_grid, text=msg,
                     bg=BG, fg=GOLD, font=_font(18, True),
                     justify="center").pack(pady=80)
            return

        if not self.frames_cache:
            tk.Label(target_grid, text="動画ファイルが見つかりません",
                     bg=BG, fg=SUBTEXT, font=_font(13)).pack(pady=40); return

        # v2.3 fix: Spinbox 空欄でも落ちないように防御
        try: cols_val = int(self.contact_cols.get())
        except (tk.TclError, ValueError): cols_val = 3
        cols = force_cols if force_cols else max(3, cols_val)

        # v2.4: 総合ビューは倍率プルダウンを参照
        if force_cols is not None:
            try:
                scale_str = self._cv_scale_var.get()
                cv_scale = float(scale_str.rstrip("x"))
            except Exception: cv_scale = 1.0
        else:
            cv_scale = 1.0
        kp_th = float(self.p_kp_th.get())
        obj_th = float(self.p_obj_th.get())

        if self.crop_rect:
            cx1, cy1, cx2, cy2 = [int(v) for v in self.crop_rect]
        else:
            cx1 = cy1 = 0; cx2 = cy2 = -1

        win_w = target_canvas.winfo_width() or 1100
        base_thumb = max(100 if force_cols else 140, (win_w - 30) // cols - 8)
        thumb_w = int(base_thumb * cv_scale)

        # v2.4: 表示時間範囲でフレームをフィルタ
        try: t_start = float(self._rf_start.get())
        except Exception: t_start = -2.0
        try: t_end = float(self._rf_end.get())
        except Exception: t_end = 2.0
        try:
            iv_str = str(self._rf_interval.get())
            t_interval = 0.0 if iv_str == "最短" else float(iv_str)
        except Exception: t_interval = 0.0

        display_idx = 0  # 表示上の連番 (フィルタ後)
        for idx, _f in enumerate(self.raw_frames):
            # 時間範囲フィルタ
            t_rel = _f["time"] - self.hit_t
            if t_rel < t_start - 0.001 or t_rel > t_end + 0.001:
                continue
            # 間隔フィルタ (interval > 0 の場合、interval 刻みに近いフレームだけ表示)
            if t_interval > 0.01:
                # v37: フレーム間隔の半分を許容範囲に (30fps→±0.017秒)
                tol = 0.02  # 固定許容範囲 (秒)
                offset_from_start = t_rel - t_start
                remainder = offset_from_start % t_interval
                nearest_dist = min(remainder, t_interval - remainder)
                if nearest_dist > tol:
                    continue
            frame = self.frames_cache.get(idx)
            if frame is None: continue
            H, W = frame.shape[:2]
            x1 = max(0, cx1); y1 = max(0, cy1)
            x2 = (cx2 if cx2 > 0 else W); y2 = (cy2 if cy2 > 0 else H)
            x2 = min(W, x2); y2 = min(H, y2)
            cropped = frame[y1:y2, x1:x2]
            if cropped.size == 0: continue
            ch, cw = cropped.shape[:2]
            thumb_h = int(thumb_w * ch / cw)
            scale = thumb_w / cw

            img = Image.fromarray(cropped).resize((thumb_w, thumb_h), Image.LANCZOS)
            draw = ImageDraw.Draw(img, "RGBA")
            self._draw_kps_pil(draw, idx, x1, y1, scale, kp_th, obj_th)

            photo = ImageTk.PhotoImage(img)
            refs_list.append(photo)

            row = display_idx // cols * 2
            col = display_idx % cols
            is_hit = abs(t_rel) < 0.04
            # v2.3 後修正: 平常時の border。ホバー時は config() で書換のみ (再描画なし)
            normal_color = GOLD if is_hit else BORDER
            normal_thick = 3 if is_hit else 1
            lbl = tk.Label(target_grid, image=photo, bg=BG,
                           highlightbackground=normal_color,
                           highlightthickness=normal_thick,
                           cursor="hand2")
            lbl.grid(row=row, column=col, padx=3, pady=3)
            lbl.bind("<Button-1>", lambda e, i=idx: self._open_editor(i))
            # v2.3: 総合ビュータブ専用のホバー: 写真にカーソル → グラフに縦線
            if force_cols is not None:
                # widget 参照と平常 border を保持 (ホバーで属性のみ書換)
                self._cv_photo_widgets[idx] = lbl
                self._cv_photo_normal_border[idx] = (normal_color, normal_thick)
                lbl.bind("<Enter>", lambda e, i=idx: self._cv_hover_photo(i))
                lbl.bind("<Leave>", lambda e: self._cv_hover_photo(None))
            n_edits = sum(1 for (fi, _) in self.manual_edits if fi == idx)
            tag = f"[編{n_edits}] " if n_edits else ""
            tk.Label(target_grid,
                     text=f"{tag}#{idx} {t_rel:+.2f}s",
                     bg=BG, fg=GOLD if is_hit else (RED if n_edits else TEXT),
                     font=_font(9 if not force_cols else 8, bold=bool(n_edits))
                     ).grid(row=row+1, column=col, pady=(0, 2))
            display_idx += 1

    def _draw_kps_pil(self, draw, frame_idx, crop_x, crop_y, scale, kp_th, obj_th):
        if frame_idx >= len(self.raw_frames): return
        raw_f = self.raw_frames[frame_idx]
        # v37: placeholderフレームはKPデータなし→スキップ
        if raw_f.get("_placeholder"): return
        ref_f = (self.refined_frames[frame_idx]
                 if self.refined_frames and frame_idx < len(self.refined_frames) else None)
        auto_f = (self.refined_auto[frame_idx]
                  if self.refined_auto and frame_idx < len(self.refined_auto)
                  else None)
        for ki in range(20):
            if not self.kp_vars[ki].get(): continue
            color = KP_COLORS[ki]
            is_hover = (ki == self.hover_kp)

            # 生 (中空小)
            rp = self._kp_position(raw_f, ki, kp_th, obj_th)
            if rp is not None:
                x = (rp[0] - crop_x) * scale; y = (rp[1] - crop_y) * scale
                r = 3
                shape = KP_SHAPES[ki] if ki < len(KP_SHAPES) else "circle"
                _draw_kp_shape_pil(draw, shape, x, y, r, fill=None, outline=color, width=1)

            # 削除ゴースト (auto位置にXマーク)
            is_deleted = (self.manual_edits.get((frame_idx, ki)) is None
                          and (frame_idx, ki) in self.manual_edits)
            if is_deleted and auto_f is not None:
                ap = self._kp_position(auto_f, ki, kp_th, obj_th)
                if ap is not None:
                    x = (ap[0] - crop_x) * scale; y = (ap[1] - crop_y) * scale
                    r = 5
                    draw.line([x-r, y-r, x+r, y+r], fill=RED, width=2)
                    draw.line([x-r, y+r, x+r, y-r], fill=RED, width=2)
                continue   # 削除済はrefined描画しない

            # 洗練後 (塗潰大) + ホバー強調
            if ref_f:
                pp = self._kp_position(ref_f, ki, kp_th, obj_th)
                if pp is not None:
                    x = (pp[0] - crop_x) * scale; y = (pp[1] - crop_y) * scale
                    is_manual = (frame_idx, ki) in self.manual_edits and \
                                self.manual_edits[(frame_idx, ki)] is not None
                    r = 6 if ki == 19 else 5
                    shape = KP_SHAPES[ki] if ki < len(KP_SHAPES) else "circle"
                    out = "gold" if is_manual else "white"
                    ow = 2 if is_manual else 1
                    _draw_kp_shape_pil(draw, shape, x, y, r, fill=color, outline=out, width=ow)
                    # ホバー強調リング
                    if is_hover:
                        rr = r + 5
                        draw.ellipse([x-rr, y-rr, x+rr, y+rr],
                                     outline="yellow", width=2)

    # ════════════════════════════════════════
    #  編集タブ
    # ════════════════════════════════════════
    def _open_editor(self, frame_idx):
        self.selected_frame_idx = frame_idx
        self.selected_kp = None
        self.notebook.select(self.tab_editor)
        self.after(50, self._render_editor_frame)

    def _nav_frame(self, delta):
        if self.selected_frame_idx is None or self.raw_frames is None: return
        new_idx = self.selected_frame_idx + delta
        if 0 <= new_idx < len(self.raw_frames):
            self.selected_frame_idx = new_idx
            self.selected_kp = None
            self._render_editor_frame()

    def _render_editor_frame(self):
        c = self.editor_canvas
        c.delete("all")
        c.image_ref = None

        cw = c.winfo_width() or 1000; chh = c.winfo_height() or 700

        # 抽出中の大表示
        if self._extracting or (self.video_path and not self.frames_cache):
            done, total = self._extract_progress
            msg = (f"動画フレーム抽出中…\n\n{done} / {total} コマ"
                   if total else "処理中…")
            c.create_text(cw//2, chh//2, text=msg,
                          fill=GOLD, font=_font(18, True), justify="center")
            self.editor_status.set("抽出中")
            return

        idx = self.selected_frame_idx
        if idx is None or self.refined_frames is None:
            c.create_text(cw//2, chh//2,
                          text="連続写真からフレームをクリックしてください",
                          fill=SUBTEXT, font=_font(14))
            self.editor_status.set("未選択")
            return

        frame = self.frames_cache.get(idx)
        if frame is None:
            self.editor_status.set(f"フレーム #{idx} の画像なし"); return

        H, W = frame.shape[:2]
        if self.crop_rect:
            cx1, cy1, cx2, cy2 = [int(v) for v in self.crop_rect]
        else:
            cx1 = cy1 = 0; cx2 = W; cy2 = H
        cx1 = max(0, cx1); cy1 = max(0, cy1)
        cx2 = min(W, cx2); cy2 = min(H, cy2)
        cropped = frame[cy1:cy2, cx1:cx2]
        if cropped.size == 0:
            self.editor_status.set("クロップ範囲不正"); return
        ch_, cw_ = cropped.shape[:2]
        if cw_ < 1 or ch_ < 1: return
        scale = min(cw / cw_, chh / ch_) if cw > 0 and chh > 0 else 1.0
        new_w = max(1, int(cw_ * scale)); new_h = max(1, int(ch_ * scale))
        img = Image.fromarray(cropped).resize((new_w, new_h), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        c.image_ref = photo
        x_off = (cw - new_w) // 2; y_off = (chh - new_h) // 2
        c.create_image(x_off, y_off, anchor="nw", image=photo)
        self._ed_scale = scale
        self._ed_offx  = x_off; self._ed_offy  = y_off
        self._ed_cropx = cx1;   self._ed_cropy = cy1

        kp_th = float(self.p_kp_th.get()); obj_th = float(self.p_obj_th.get())
        raw_f = self.raw_frames[idx]
        if idx >= len(self.refined_frames): return  # v32: 境界チェック
        ref_f = self.refined_frames[idx]
        auto_f = (self.refined_auto[idx]
                  if self.refined_auto and idx < len(self.refined_auto) else None)

        for ki in range(20):
            if not self.kp_vars[ki].get(): continue
            color = KP_COLORS[ki]
            is_hover = (ki == self.hover_kp)
            is_sel = (self.selected_kp == ki)

            # 生 (薄い点線)
            rp = self._kp_position(raw_f, ki, kp_th, obj_th)
            if rp is not None and ki != 19:
                x = self._to_cx(rp[0]); y = self._to_cy(rp[1])
                r = 5
                c.create_oval(x-r, y-r, x+r, y+r, outline=color, width=1,
                              dash=(2,2), tags=("raw",))

            # 削除ゴースト (auto位置にXマーク)
            is_deleted = ((idx, ki) in self.manual_edits
                          and self.manual_edits[(idx, ki)] is None)
            if is_deleted and auto_f is not None:
                ap = self._kp_position(auto_f, ki, kp_th, obj_th)
                if ap is not None:
                    x = self._to_cx(ap[0]); y = self._to_cy(ap[1])
                    r = 10
                    c.create_line(x-r, y-r, x+r, y+r, fill=RED, width=3,
                                  tags=(f"del_{ki}",))
                    c.create_line(x-r, y+r, x+r, y-r, fill=RED, width=3,
                                  tags=(f"del_{ki}",))
                continue   # 削除済はrefined描画しない

            # 洗練後 (大) + ホバー/選択強調
            pp = self._kp_position(ref_f, ki, kp_th, obj_th)
            if pp is not None:
                x = self._to_cx(pp[0]); y = self._to_cy(pp[1])
                is_manual = ((idx, ki) in self.manual_edits
                             and self.manual_edits[(idx, ki)] is not None)
                # v2.9: 信頼度が低い(推論)KPは三角マーカー
                kc_val = ref_f.get(f"kp{ki:02d}_c", 1.0) if ki < 17 else 1.0
                is_inferred = (kc_val is not None and kc_val < 0.8 and ki < 17)
                # 手動で三角に設定されたKPもチェック
                if (idx, ki) in getattr(self, "_inferred_overrides", set()):
                    is_inferred = True
                base_r = 11 if is_sel else (9 if ki == 19 else 8)
                shape = KP_SHAPES[ki] if ki < len(KP_SHAPES) else "circle"
                outline_c = ("yellow" if is_sel else
                           ("gold" if is_manual else "white"))
                ow = 4 if is_sel else (3 if is_manual else 2)
                if is_inferred:
                    # v56: 見えない点 → マーカーの上に白×印 (視認性向上)
                    _draw_kp_shape_canvas(c, shape, x, y, base_r,
                        fill=color, outline=outline_c, width=ow, tags=f"refkp_{ki}")
                    s = base_r + 1
                    c.create_line(x-s, y-s, x+s, y+s, fill="white", width=4, tags=(f"refkp_{ki}",))
                    c.create_line(x-s, y+s, x+s, y-s, fill="white", width=4, tags=(f"refkp_{ki}",))
                else:
                    _draw_kp_shape_canvas(c, shape, x, y, base_r,
                        fill=color, outline=outline_c, width=ow, tags=f"refkp_{ki}")
                # ホバー強調 (黄色リング)
                if is_hover and not is_sel:
                    rr = base_r + 6
                    c.create_oval(x-rr, y-rr, x+rr, y+rr,
                                  outline="yellow", width=3,
                                  tags=("hover",))

        # 情報 (v27: 白色化)
        t_rel = self.raw_frames[idx]["time"] - self.hit_t
        c.create_text(10, 10, anchor="nw",
                      text=f"Frame #{idx} / {len(self.raw_frames)-1}    t={t_rel:+.3f}s",
                      fill="white", font=_font(13, True))
        n_edits = sum(1 for (fi, _) in self.manual_edits if fi == idx)
        if n_edits:
            c.create_text(cw-10, 32, anchor="ne",
                          text=f"このフレームの編集: {n_edits}",
                          fill="white", font=_font(11, True))
        # v56: 右上に移動 + 状態表示
        y_info = 54
        if self._placement_kp is not None:
            kp_name = KP_EXT_NAMES[self._placement_kp] if self._placement_kp < len(KP_EXT_NAMES) else "?"
            c.create_text(cw-10, y_info, anchor="ne",
                          text=f"追加モード: {kp_name}  (写真をクリックで配置)",
                          fill="#ffee55", font=_font(12, True))
        elif self.selected_kp is not None:
            ki_ = self.selected_kp
            state_tags = []
            if (idx, ki_) in self._inferred_overrides: state_tags.append("見えない点")
            if (idx, ki_) in self.manual_edits and self.manual_edits[(idx,ki_)] is not None: state_tags.append("手動編集済")
            if (idx, ki_) in self.manual_edits and self.manual_edits[(idx,ki_)] is None: state_tags.append("削除済")
            state = f"  [{', '.join(state_tags)}]" if state_tags else ""
            c.create_text(cw-10, y_info, anchor="ne",
                          text=f"編集中: {KP_EXT_NAMES[ki_]}{state}",
                          fill="white", font=_font(11, True))
        elif self.hover_kp is not None:
            ki_ = self.hover_kp
            state_tags = []
            if (idx, ki_) in self._inferred_overrides: state_tags.append("見えない点")
            if (idx, ki_) in self.manual_edits and self.manual_edits[(idx,ki_)] is not None: state_tags.append("編集済")
            state = f"  [{', '.join(state_tags)}]" if state_tags else ""
            c.create_text(cw-10, y_info, anchor="ne",
                          text=f"ホバー: {KP_EXT_NAMES[ki_]}{state}",
                          fill="white", font=_font(10))

        # v27: 上部バーの重複表示は廃止 (キャンバス内に集約)
        self.editor_status.set("")

    def _to_cx(self, orig_x):
        return (orig_x - self._ed_cropx) * self._ed_scale + self._ed_offx

    def _to_cy(self, orig_y):
        return (orig_y - self._ed_cropy) * self._ed_scale + self._ed_offy

    def _from_cx(self, canvas_x):
        return (canvas_x - self._ed_offx) / self._ed_scale + self._ed_cropx

    def _from_cy(self, canvas_y):
        return (canvas_y - self._ed_offy) / self._ed_scale + self._ed_cropy

    def _editor_find_kp(self, cx, cy, max_dist=20):
        """カーソル位置から最寄りの編集可能refined KPを返す (idx or None)"""
        idx = self.selected_frame_idx
        if idx is None or self.refined_frames is None: return None
        if idx >= len(self.refined_frames): return None  # v32: 境界チェック
        ref_f = self.refined_frames[idx]
        kp_th = float(self.p_kp_th.get()); obj_th = float(self.p_obj_th.get())
        best = None; best_d = max_dist
        for ki in range(19):  # 重心(19)は編集不可
            if not self.kp_vars[ki].get(): continue
            # 削除済はスキップ
            if (idx, ki) in self.manual_edits and self.manual_edits[(idx, ki)] is None:
                continue
            p = self._kp_position(ref_f, ki, kp_th, obj_th)
            if p is None: continue
            x = self._to_cx(p[0]); y = self._to_cy(p[1])
            d = math.hypot(cx - x, cy - y)
            if d < best_d:
                best_d = d; best = ki
        return best

    def _editor_mouse_down(self, event):
        if self.selected_frame_idx is None: return
        # v2.8: 配置モード時はシングルクリックでKPを追加
        if self._placement_kp is not None:
            ki = self._placement_kp
            idx = self.selected_frame_idx
            if idx is None or self.refined_frames is None: return
            if idx >= len(self.refined_frames): return  # v32: 境界チェック
            new_x = self._from_cx(event.x)
            new_y = self._from_cy(event.y)
            if new_x is None or new_y is None: return  # v32: 座標変換失敗
            self._undo_push()
            self.manual_edits[(idx, ki)] = (float(new_x), float(new_y))
            # v32: 見えない点として追加する場合は信頼度を低く設定
            if ki < 17:
                self._inferred_overrides.add((idx, ki))
            # v2.9: チェックボックスも自動有効化
            if ki < len(self.kp_vars) and not self.kp_vars[ki].get():
                self.kp_vars[ki].set(True)
            self._update_edit_count()
            try: self._apply_manual_edits_with_smoothing()
            except Exception: pass
            # 配置モード解除
            self._placement_kp = None
            self._update_placement_highlight()
            try: self.editor_canvas.config(cursor="")
            except Exception: pass
            self._refresh_current_tab()
            return
        ki = self._editor_find_kp(event.x, event.y, max_dist=22)
        if ki is not None:
            self.selected_kp = ki
            self.dragging = True
        else:
            self.selected_kp = None
            self.dragging = False
        self._render_editor_frame()

    def _editor_mouse_drag(self, event):
        if not self.dragging or self.selected_kp is None: return
        idx = self.selected_frame_idx
        ki = self.selected_kp
        new_x = self._from_cx(event.x); new_y = self._from_cy(event.y)
        # v2.4: ドラッグ開始時（最初の移動）のみスナップショットを積む
        if not self._drag_undo_pushed:
            self._undo_push()
            self._drag_undo_pushed = True
        self.manual_edits[(idx, ki)] = (float(new_x), float(new_y))
        self._apply_manual_edits_with_smoothing()
        self._render_editor_frame()

    def _editor_mouse_up(self, event):
        if self.dragging:
            self._update_edit_count()
            self._refresh_current_tab()
        self.dragging = False
        self._drag_undo_pushed = False  # v2.4: ドラッグ終了でフラグリセット

    def _editor_right_click(self, event):
        idx = self.selected_frame_idx
        if idx is None: return
        best = None; best_d = 22
        for (fi, ki), val in self.manual_edits.items():
            if fi != idx: continue
            if val is None:
                if self.refined_auto is None: continue
                auto_pos = self._kp_position(self.refined_auto[fi], ki,
                                              float(self.p_kp_th.get()),
                                              float(self.p_obj_th.get()))
                if auto_pos is None: continue
                cx = self._to_cx(auto_pos[0]); cy = self._to_cy(auto_pos[1])
            else:
                cx = self._to_cx(val[0]); cy = self._to_cy(val[1])
            d = math.hypot(event.x - cx, event.y - cy)
            if d < best_d:
                best_d = d; best = (fi, ki)
        if best:
            self._undo_push()  # v2.4
            del self.manual_edits[best]
            self._update_edit_count()
            self._apply_manual_edits_with_smoothing()
            self._refresh_current_tab()

    def _editor_motion(self, event):
        if self.dragging: return
        if self.selected_frame_idx is None: return
        ki = self._editor_find_kp(event.x, event.y, max_dist=18)
        self._set_hover_kp(ki)

    def _editor_delete_kp(self):
        """選択中のKPを削除。ki=18 (ボール) なら前後伝播も実行。"""
        if self.selected_frame_idx is None or self.selected_kp is None: return
        ki = self.selected_kp
        if ki >= 19: return
        idx = self.selected_frame_idx
        self._undo_push()  # v2.4
        if ki == 18:
            # v2.4: ボール削除 → 前後 N フレームも自動削除
            self._ball_delete_propagate(idx)
        else:
            self.manual_edits[(idx, ki)] = None
        self.selected_kp = None
        self._update_edit_count()
        self._apply_manual_edits_with_smoothing()
        self._refresh_current_tab()

    # ── v2.5: KP 配置 (追加) モード ──
    def _toggle_placement_kp(self, ki):
        """右パネルのKP名クリックで配置モードを切り替え"""
        if self._placement_kp == ki:
            self._placement_kp = None  # 解除
        else:
            self._placement_kp = ki
            self.selected_kp = None  # v2.9: 編集選択をクリア
            self.dragging = False
        self._update_placement_highlight()
        # カーソル変更
        try:
            self.editor_canvas.config(
                cursor="crosshair" if self._placement_kp is not None else "")
        except Exception: pass
        self._refresh_current_tab()  # v2.9: 即座に表示を更新

    def _update_placement_highlight(self):
        """配置モードのKP行ハイライト → _update_legend_highlight に統合"""
        self._update_legend_highlight()

    def _editor_double_click(self, event):
        """ダブルクリックで配置モードのKPを追加"""
        if self.selected_frame_idx is None: return
        if self._placement_kp is None: return
        ki = self._placement_kp
        idx = self.selected_frame_idx
        new_x = self._from_cx(event.x)
        new_y = self._from_cy(event.y)
        self._undo_push()
        self.manual_edits[(idx, ki)] = (float(new_x), float(new_y))
        self._update_edit_count()
        self._apply_manual_edits_with_smoothing()
        self._refresh_current_tab()

    def _toggle_inferred_debug(self):
        """v55: Tキー デバッグラッパー"""
        idx = self.selected_frame_idx
        ki_sel = self.selected_kp
        ki_hov = self.hover_kp
        ki = ki_sel if ki_sel is not None else ki_hov
        print(f"[Tキー] idx={idx}, selected_kp={ki_sel}, hover_kp={ki_hov}, → ki={ki}")
        if ki is None:
            print(f"[Tキー] KP未選択 → 写真上のマーカーをクリックしてからTを押してください")
            return
        self._toggle_inferred()

    def _toggle_inferred(self):
        """v2.9: Tキーで選択/ホバー中のKPを丸⇔三角トグル。
           三角にした場合: 信頼度を0.3に下げ、前後±4フレームに波及"""
        idx = self.selected_frame_idx
        if idx is None: return
        ki = self.selected_kp if self.selected_kp is not None else self.hover_kp
        if ki is None or ki >= 17: return  # 拡張KPは対象外
        key = (idx, ki)
        SPREAD = 4  # 前後フレーム数
        if key in self._inferred_overrides:
            # 三角→丸に戻す (信頼度復元)
            self._inferred_overrides.discard(key)
            for d in range(-SPREAD, SPREAD+1):
                fi = idx + d
                if 0 <= fi < len(self.refined_frames):
                    self._inferred_overrides.discard((fi, ki))
        else:
            # 丸→三角に (信頼度を下げて前後に波及)
            for d in range(-SPREAD, SPREAD+1):
                fi = idx + d
                if 0 <= fi < len(self.refined_frames):
                    self._inferred_overrides.add((fi, ki))
                    decay = max(0.15, 0.3 + abs(d) * 0.1)
                    self.refined_frames[fi][f"kp{ki:02d}_c"] = decay
        self._refresh_current_tab()

    def _editor_place_kp_at_center(self):
        """Insertキー: 配置モードのKPを画像中央に追加"""
        if self.selected_frame_idx is None or self._placement_kp is None: return
        # 画像中央座標を算出
        idx = self.selected_frame_idx
        if self.refined_frames and idx < len(self.refined_frames):
            f = self.refined_frames[idx]
            # person_bbox から中央を推定
            bbox = f.get("person_bbox")
            if bbox:
                cx = (bbox[0] + bbox[2]) / 2
                cy = (bbox[1] + bbox[3]) / 2
            else:
                cx, cy = 320, 240  # フォールバック
        else:
            cx, cy = 320, 240
        ki = self._placement_kp
        self._undo_push()
        self.manual_edits[(idx, ki)] = (float(cx), float(cy))
        self._update_edit_count()
        self._apply_manual_edits_with_smoothing()
        self._refresh_current_tab()

    # ── ホバー管理 ──
    def _set_hover_kp(self, ki):
        if self.hover_kp == ki: return
        self.hover_kp = ki
        # v2.8: 凡例ハイライトは即座に更新 (デバウンスなし)
        self._update_legend_highlight()
        if self._hover_render_id:
            try: self.after_cancel(self._hover_render_id)
            except Exception: pass
        # 画像の再描画のみデバウンス (30ms)
        self._hover_render_id = self.after(30, self._do_hover_render)

    def _do_hover_render(self):
        self._hover_render_id = None
        # v29: グラフ再描画は不要（凡例ハイライトのみで十分）
        # _refresh_current_tab() はグラフ全体を再描画するので重い
        # 編集タブの場合のみキャンバス更新
        try:
            sel = str(self.notebook.select())
            if sel == str(self.tab_editor):
                self._render_editor_frame()
        except Exception:
            pass

    def _update_legend_highlight(self):
        """凡例行の背景色を更新
        v27: 黄色=ホバー中(マウスが乗っている)、オレンジ=追加モード(クリック配置待ち)"""
        HOVER_BG = "#ffee55"; HOVER_FG = "#000000"   # 黄色+黒 = ホバー
        PLACE_BG = "#ff8c00"; PLACE_FG = "#000000"   # オレンジ+黒 = 追加モード
        for i, row in enumerate(self.kp_rows):
            if not row.winfo_exists(): continue
            if i == getattr(self, "_placement_kp", None):
                bg, fg = PLACE_BG, PLACE_FG   # 追加モードが優先
            elif i == self.hover_kp:
                bg, fg = HOVER_BG, HOVER_FG
            else:
                bg, fg = PANEL, TEXT
            try:
                row.config(bg=bg)
                for child in row.winfo_children():
                    try:
                        child.config(bg=bg)
                        if isinstance(child, tk.Label):
                            child.config(fg=fg)
                    except Exception: pass
            except Exception: pass
        # v34: グラフ2のホバーKP軌跡を黄色ハイライト
        try:
            fig2 = getattr(self, "_combined_fig2", None)
            canvas2 = getattr(self, "_combined_chart2_canvas", None)
            if fig2 and canvas2 and fig2.axes:
                ax2 = fig2.axes[0]
                for line in ax2.get_lines():
                    gid = line.get_gid() or ""
                    if gid.startswith("kp_trail_"):
                        ki_id = int(gid.split("_")[-1])
                        if ki_id == self.hover_kp:
                            line.set_color("yellow"); line.set_alpha(1.0); line.set_zorder(8)
                        else:
                            orig = KP_COLORS[ki_id] if ki_id < len(KP_COLORS) else "#fff"
                            line.set_color(orig); line.set_alpha(0.9); line.set_zorder(5)
                canvas2.draw_idle()
        except Exception: pass

    # ── v2.3: 総合ビュー双方向ホバー ──
    def _cv_hover_photo(self, frame_idx):
        """写真にカーソル → グラフに縦線 + 写真側ボーダー強調 (再描画なし、軽量)"""
        if self._cv_hover_frame_idx == frame_idx: return
        self._cv_hover_frame_idx = frame_idx
        # v2.3 後修正: デバウンスは不要 (config だけなので軽い)。即時反映
        self._cv_apply_photo_hover()

    def _cv_apply_photo_hover(self):
        self._cv_hover_after_id = None
        # 1. 前回ハイライト写真の border を平常時に戻す
        prev = self._cv_prev_hover_idx
        if prev is not None and prev in self._cv_photo_widgets:
            lbl = self._cv_photo_widgets[prev]
            try:
                color, thick = self._cv_photo_normal_border.get(prev, (BORDER, 1))
                if lbl.winfo_exists():
                    lbl.config(highlightbackground=color, highlightthickness=thick)
            except Exception: pass
        # 2. 新規ハイライト写真を白枠強調
        cur = self._cv_hover_frame_idx
        if cur is not None and cur in self._cv_photo_widgets:
            lbl = self._cv_photo_widgets[cur]
            try:
                if lbl.winfo_exists():
                    lbl.config(highlightbackground="white", highlightthickness=4)
            except Exception: pass
        self._cv_prev_hover_idx = cur

        # 3. グラフに縦線を描く (Combined view fig only)
        try:
            fig = getattr(self, "_combined_fig", None)
            canvas = getattr(self, "_combined_chart_canvas", None)
            if fig and canvas and fig.axes:
                ax = fig.axes[0]
                if self._cv_chart_vline is not None:
                    try: self._cv_chart_vline.remove()
                    except Exception: pass
                    self._cv_chart_vline = None
                if (cur is not None
                        and self.raw_frames
                        and 0 <= cur < len(self.raw_frames)):
                    t_rel = self.raw_frames[cur]["time"] - self.hit_t
                    self._cv_chart_vline = ax.axvline(
                        t_rel, color="yellow", linewidth=2.0, alpha=0.85,
                        linestyle="-", zorder=10)
                canvas.draw_idle()
        except Exception: pass

        # v28: グラフ2 (XY軌跡) の該当フレーム点をハイライト
        try:
            fig2 = getattr(self, "_combined_fig2", None)
            canvas2 = getattr(self, "_combined_chart2_canvas", None)
            if (fig2 and canvas2 and fig2.axes
                    and self._cv_show_graph2.get()):
                ax2 = fig2.axes[0]
                if self._cv_chart2_hl is not None:
                    try: self._cv_chart2_hl.remove()
                    except Exception: pass
                    self._cv_chart2_hl = None
                pts = getattr(self, "_cv_chart2_pts", {}).get(cur)
                if pts:
                    hx = [p[0] for p in pts]; hy = [p[1] for p in pts]
                    self._cv_chart2_hl = ax2.scatter(
                        hx, hy, s=200, facecolors="none",
                        edgecolors="yellow", linewidths=2.5, zorder=10)
                # v29: 背景写真をホバーフレームに切替 (v33: クロップ対応)
                bg_idx = getattr(self, "_cv_chart2_bg_idx", None)
                if cur is not None and cur != bg_idx:
                    bg = self.frames_cache.get(cur)
                    if bg is not None and ax2.images:
                        try:
                            crop = getattr(self, "_cv_chart2_crop", None)
                            if crop:
                                bg = bg[crop[1]:crop[3], crop[0]:crop[2]]
                            ax2.images[0].set_data(bg)
                            ax2.images[0].set_alpha(0.4)
                            self._cv_chart2_bg_idx = cur
                        except Exception: pass
                elif cur is None and bg_idx != getattr(self, "_cv_chart2_hit_idx", 0):
                    bg = self.frames_cache.get(getattr(self, "_cv_chart2_hit_idx", 0))
                    if bg is not None and ax2.images:
                        try:
                            crop = getattr(self, "_cv_chart2_crop", None)
                            if crop:
                                bg = bg[crop[1]:crop[3], crop[0]:crop[2]]
                            ax2.images[0].set_data(bg)
                            ax2.images[0].set_alpha(0.35)
                            self._cv_chart2_bg_idx = self._cv_chart2_hit_idx
                        except Exception: pass
                canvas2.draw_idle()
        except Exception: pass

        # v32: グラフ3 (角度) の該当フレームに黄色縦線
        try:
            fig3 = getattr(self, "_combined_fig3", None)
            canvas3 = getattr(self, "_combined_chart3_canvas", None)
            if (fig3 and canvas3 and fig3.axes
                    and self._cv_show_graph3.get()):
                ax3 = fig3.axes[0]
                if hasattr(self, "_cv_chart3_vline") and self._cv_chart3_vline:
                    try: self._cv_chart3_vline.remove()
                    except Exception: pass
                    self._cv_chart3_vline = None
                if (cur is not None and self.raw_frames
                        and 0 <= cur < len(self.raw_frames)):
                    t_rel = self.raw_frames[cur]["time"] - self.hit_t
                    self._cv_chart3_vline = ax3.axvline(
                        t_rel, color="yellow", linewidth=2.0, alpha=0.85, zorder=10)
                canvas3.draw_idle()
        except Exception: pass

    def _cv_hover_graph_frame(self, frame_idx, kp_id=None):
        """グラフ側ホバーから呼ぶ: 該当写真のボーダーを白で強調"""
        self._cv_hover_photo(frame_idx)
        if kp_id is not None:
            self._set_hover_kp(kp_id)

    # ════════════════════════════════════════
    #  タブ切替時の更新
    # ════════════════════════════════════════
    # ════════════════════════════════════════
    #  3D キーポイント タブ (v2.4)
    # ════════════════════════════════════════
    # MediaPipe Pose の33KP → COCO17KP のマッピング (近似)
    # mp_idx -> coco_idx
    _MP_TO_COCO = {
        0:0,   # 鼻
        2:1,   # 左目
        5:2,   # 右目
        7:3,   # 左耳
        8:4,   # 右耳
        11:5,  # 左肩
        12:6,  # 右肩
        13:7,  # 左肘
        14:8,  # 右肘
        15:9,  # 左手首
        16:10, # 右手首
        23:11, # 左腰
        24:12, # 右腰
        25:13, # 左膝
        26:14, # 右膝
        27:15, # 左足首
        28:16, # 右足首
    }
    # MediaPipe Pose の骨格接続 (主要なもの)
    _MP_CONNECTIONS = [
        (11,12),(11,13),(13,15),(12,14),(14,16),  # 上半身
        (11,23),(12,24),(23,24),                   # 体幹
        (23,25),(25,27),(24,26),(26,28),            # 下半身
        (0,11),(0,12),                              # 頭〜肩
        (15,17),(15,19),(16,18),(16,20),            # 手先
        (27,29),(27,31),(28,30),(28,32),            # 足先
    ]

    def _build_3d_tab(self):
        p = self.tab_3d
        # v62: 現在HP表示
        self._3d_hp_var = tk.StringVar(value="HP未選択")
        tk.Label(p, textvariable=self._3d_hp_var, bg=BG, fg=GOLD,
                 font=_font(14, True), anchor="w"
                 ).pack(side="top", fill="x", padx=8, pady=(4,2))
        # ── コントロール行 ──
        ctrl = tk.Frame(p, bg=PANEL2); ctrl.pack(side="top", fill="x", padx=4, pady=4)

        # モデルパス設定
        tk.Label(ctrl, text="モデル:", bg=PANEL2, fg=TEXT, font=_font(9)
                 ).pack(side="left", padx=(4,2))
        self._mp_model_path = tk.StringVar(value="pose_landmarker_lite.task")
        tk.Entry(ctrl, textvariable=self._mp_model_path, bg=DARK2, fg=TEXT,
                 insertbackground=TEXT, relief="flat", font=_font(8), width=30
                 ).pack(side="left", padx=(0,2))
        tk.Button(ctrl, text="…", bg=DARK2, fg=TEXT, relief="flat",
                  font=_font(9), cursor="hand2",
                  command=self._pick_mp_model).pack(side="left", padx=(0,8))

        # 検出ボタン
        self.btn_mp_detect = tk.Button(ctrl, text="▶ MediaPipe 3D 検出",
                                        bg=ACCENT, fg="white", relief="flat",
                                        font=_font(10, True), cursor="hand2",
                                        command=self._run_mediapipe)
        self.btn_mp_detect.pack(side="left", padx=4, ipady=4, ipadx=6)
        self._mp_status = tk.StringVar(value="MediaPipe モデルを選択して検出を実行")
        tk.Label(ctrl, textvariable=self._mp_status, bg=PANEL2, fg=SUBTEXT,
                 font=_font(9)).pack(side="left", padx=8)

        # v55: 解析ステータスバーは左パネルに統合したため3Dタブからは削除

        # ── アニメーション行 ──
        # v49: 2行に分割 — 1行目: 再生系、2行目: 表示切替系
        anim = tk.Frame(p, bg=PANEL2); anim.pack(side="top", fill="x", padx=4, pady=(0,1))
        anim2 = tk.Frame(p, bg=PANEL2); anim2.pack(side="top", fill="x", padx=4, pady=(0,2))
        self.btn_3d_play = tk.Button(anim, text="▶ 再生", bg=ACCENT2, fg="white",
                                      relief="flat", font=_font(10, True), cursor="hand2",
                                      command=self._toggle_3d_anim)
        self.btn_3d_play.pack(side="left", padx=4, ipady=3, ipadx=6)
        tk.Button(anim, text="◀ 最初", bg=DARK2, fg=TEXT, relief="flat",
                  font=_font(9), cursor="hand2",
                  command=lambda: self._3d_goto(0)).pack(side="left", padx=2, ipady=3, ipadx=4)
        tk.Button(anim, text="⏮ 打点", bg=DARK2, fg=GOLD, relief="flat",
                  font=_font(9, True), cursor="hand2",
                  command=self._3d_goto_hit).pack(side="left", padx=2, ipady=3, ipadx=4)
        tk.Label(anim, text="フレーム:", bg=PANEL2, fg=SUBTEXT, font=_font(9)
                 ).pack(side="left", padx=(8,2))
        self._3d_frame_var = tk.IntVar(value=0)
        self._3d_slider = tk.Scale(anim, variable=self._3d_frame_var,
                                    from_=0, to=1, orient="horizontal",
                                    bg=PANEL2, fg=TEXT, troughcolor=DARK2,
                                    highlightbackground=PANEL2, relief="flat",
                                    length=300, sliderlength=14, showvalue=True,
                                    command=lambda v: self._3d_render_frame(int(float(v))))
        self._3d_slider.pack(side="left", padx=4)
        self._3d_time_var = tk.StringVar(value="t = 0.000s")
        tk.Label(anim, textvariable=self._3d_time_var, bg=PANEL2, fg=GOLD,
                 font=_font(9, True), width=12).pack(side="left", padx=4)
        tk.Label(anim, text="速度:", bg=PANEL2, fg=SUBTEXT, font=_font(9)
                 ).pack(side="left", padx=(8,2))
        self._3d_fps_var = tk.DoubleVar(value=5.0)
        ttk.Combobox(anim, textvariable=self._3d_fps_var,
                     values=[2,3,5,10,15,20,30,60], width=4, state="readonly",
                     font=_font(9)).pack(side="left", padx=2)
        tk.Label(anim, text="拡大:", bg=PANEL2, fg=SUBTEXT, font=_font(9)
                 ).pack(side="left", padx=(8,2))
        self._3d_zoom_var = tk.DoubleVar(value=1.0)
        zoom_cb = ttk.Combobox(anim, textvariable=self._3d_zoom_var,
                     values=["1.0","1.5","2.0","2.5","3.0"], width=4, state="readonly",
                     font=_font(9))
        zoom_cb.pack(side="left", padx=2)
        zoom_cb.bind("<<ComboboxSelected>>",
                     lambda e: self._3d_render_frame(self._mp3d_cur_idx))

        # ── 2行目: 表示切替チェックボックス ──
        self._3d_show_floor = tk.BooleanVar(value=True)
        tk.Checkbutton(anim2, text="地面", variable=self._3d_show_floor,
                       bg=PANEL2, fg=TEXT, activebackground=PANEL2, selectcolor=DARK2,
                       font=_font(9), command=lambda: self._3d_render_frame(self._mp3d_cur_idx)
                       ).pack(side="left", padx=(4,0))
        self._3d_show_traj = tk.BooleanVar(value=False)
        tk.Checkbutton(anim2, text="軌跡", variable=self._3d_show_traj,
                       bg=PANEL2, fg=TEXT, activebackground=PANEL2, selectcolor=DARK2,
                       font=_font(9), command=lambda: self._3d_render_frame(self._mp3d_cur_idx)
                       ).pack(side="left", padx=2)
        self._3d_show_photo = tk.BooleanVar(value=True)
        tk.Checkbutton(anim2, text="2D写真", variable=self._3d_show_photo,
                       bg=PANEL2, fg=TEXT, activebackground=PANEL2, selectcolor=DARK2,
                       font=_font(9), command=lambda: self._3d_render_frame(self._mp3d_cur_idx)
                       ).pack(side="left", padx=(8,0))
        self._3d_show_photo_kp = tk.BooleanVar(value=True)
        tk.Checkbutton(anim2, text="KPマーカー", variable=self._3d_show_photo_kp,
                       bg=PANEL2, fg=TEXT, activebackground=PANEL2, selectcolor=DARK2,
                       font=_font(9), command=lambda: self._3d_render_frame(self._mp3d_cur_idx)
                       ).pack(side="left", padx=2)
        self._3d_show_mp_compare = tk.BooleanVar(value=False)
        tk.Checkbutton(anim2, text="MP比較(×)", variable=self._3d_show_mp_compare,
                       bg=PANEL2, fg=TEXT, activebackground=PANEL2, selectcolor=DARK2,
                       font=_font(9), command=lambda: self._3d_render_frame(self._mp3d_cur_idx)
                       ).pack(side="left", padx=2)
        self._3d_global_move = tk.BooleanVar(value=False)
        tk.Checkbutton(anim2, text="実移動", variable=self._3d_global_move,
                       bg=PANEL2, fg=TEXT, activebackground=PANEL2, selectcolor=DARK2,
                       font=_font(9), command=lambda: self._3d_render_frame(self._mp3d_cur_idx)
                       ).pack(side="left", padx=(8,0))
        tk.Button(anim2, text="📷 カメラ視点", bg=DARK2, fg=TEXT, relief="flat",
                  font=_font(9), cursor="hand2",
                  command=self._3d_reset_camera
                  ).pack(side="left", padx=(8,2))

        # ── 3D canvas + 2D写真 を左右に配置 ──
        self._3d_fig_frame = tk.Frame(p, bg=BG)
        self._3d_fig_frame.pack(side="top", fill="both", expand=True)
        # v54: 右パネル幅を画面に応じて調整 (ノートPC対応)
        try:
            sw = self.winfo_toplevel().winfo_screenwidth()
            rp_w = min(500, max(300, int(sw * 0.25)))
        except Exception:
            rp_w = 400
        self._3d_right = tk.Frame(self._3d_fig_frame, bg=DARK2, width=rp_w)
        self._3d_right.pack(side="right", fill="y", padx=(2,0))
        self._3d_right.pack_propagate(False)
        self._3d_photo_lbl = tk.Label(self._3d_right, bg=DARK2)
        self._3d_photo_lbl.pack(fill="both", expand=True)
        self._3d_photo_ref = None
        # 左: 3D matplotlib (残りスペースを使用)
        self._3d_left = tk.Frame(self._3d_fig_frame, bg=BG)
        self._3d_left.pack(side="left", fill="both", expand=True)
        self._init_3d_canvas()

    def _init_3d_canvas(self):
        """初期の空 3D キャンバスを描画"""
        if self._mp3d_fig:
            try: plt.close(self._mp3d_fig)
            except Exception: pass
        if self._mp3d_canvas:
            try: self._mp3d_canvas.get_tk_widget().destroy()
            except Exception: pass
        fig = plt.Figure(figsize=(9, 7), dpi=90, facecolor=BG)
        ax = fig.add_subplot(111, projection='3d')
        ax.set_facecolor(BG)
        fig.patch.set_facecolor(BG)
        ax.tick_params(colors=TEXT, labelsize=8)
        ax.xaxis.pane.fill = False; ax.yaxis.pane.fill = False; ax.zaxis.pane.fill = False
        ax.set_xlabel("X (m)", color=TEXT, fontsize=9)
        ax.set_ylabel("Y (m)", color=TEXT, fontsize=9)
        ax.set_zlabel("Z (高さ, m)", color=TEXT, fontsize=9)
        ax.text2D(0.5, 0.5, "MediaPipe 3D 検出を実行してください",
                  transform=ax.transAxes, ha="center", va="center",
                  color=SUBTEXT, fontsize=13)
        # v2.7: カメラ視点 (初期値)
        self._3d_azim = -60.0
        self._3d_elev = 15.0
        ax.view_init(elev=self._3d_elev, azim=self._3d_azim)
        self._mp3d_fig = fig
        self._mp3d_ax = ax
        canvas = FigureCanvasTkAgg(fig, master=self._3d_left)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self._mp3d_canvas = canvas
        # v2.7: デフォルトの3D回転を無効化し、水平回転のみに制限
        self._3d_drag_x = None
        # matplotlib のデフォルト 3D マウスハンドラを切断
        if hasattr(ax, 'disable_mouse_rotation'):
            ax.disable_mouse_rotation()
        else:
            # 古い matplotlib 向け: button_press/release/motion を切断
            try:
                cids_to_remove = []
                for cid, func in list(fig.canvas.callbacks.callbacks.get('button_press_event', {}).items()):
                    if hasattr(func, '__self__') and isinstance(func.__self__, type(ax)):
                        cids_to_remove.append(cid)
                for cid in cids_to_remove:
                    fig.canvas.mpl_disconnect(cid)
            except Exception: pass
        # カスタムハンドラ: 水平回転のみ
        canvas.mpl_connect('button_press_event', self._3d_on_press)
        canvas.mpl_connect('button_release_event', self._3d_on_release)
        canvas.mpl_connect('motion_notify_event', self._3d_on_motion)

    def _3d_on_press(self, event):
        if event.button == 1:
            self._3d_drag_x = event.x

    def _3d_on_release(self, event):
        self._3d_drag_x = None

    def _3d_on_motion(self, event):
        if self._3d_drag_x is None or event.x is None: return
        dx = event.x - self._3d_drag_x
        self._3d_azim = (self._3d_azim + dx * 0.3) % 360
        self._3d_drag_x = event.x
        self._mp3d_ax.view_init(elev=self._3d_elev, azim=self._3d_azim)
        try: self._mp3d_canvas.draw_idle()
        except Exception: pass

    def _3d_reset_camera(self):
        """v39: 動画情報のカメラ方向を考慮した視点にリセット"""
        # カメラ方向 → 方位角のマッピング
        cam_dir = ""
        try:
            if self.analyzer is not None:
                cam_dir = getattr(self.analyzer, "_video_meta_extra", {}).get("camera_dir", "")
                if not cam_dir:
                    # _meta_extra.json からも試行
                    vp = self.analyzer.video_path.get()
                    if vp:
                        extra_path = os.path.splitext(vp)[0] + "_meta_extra.json"
                        if os.path.exists(extra_path):
                            with open(extra_path, "r", encoding="utf-8") as f:
                                cam_dir = json.load(f).get("camera_dir", "")
        except Exception: pass
        azim_map = {
            "後ろ": -90.0,          # 選手の背後から
            "正面": 90.0,           # 選手の正面から
            "横(フォア側)": 0.0,    # 右側から
            "横(バック側)": 180.0,  # 左側から
        }
        self._3d_azim = azim_map.get(cam_dir, -60.0)
        self._3d_elev = 15.0
        self._mp3d_ax.view_init(elev=self._3d_elev, azim=self._3d_azim)
        try: self._mp3d_canvas.draw_idle()
        except Exception: pass

    def _pick_mp_model(self):
        path = filedialog.askopenfilename(
            title="MediaPipe モデルファイル (.task)",
            filetypes=[("MediaPipe Task", "*.task"), ("全て", "*.*")])
        if path: self._mp_model_path.set(path)

    def _run_mediapipe(self):
        """MediaPipe Pose で全フレームを検出 (バックグラウンド)"""
        if not self.frames_cache:
            messagebox.showinfo("3D", "先に動画を読み込んでください"); return
        model_path = self._mp_model_path.get()
        # v2.4: 複数ディレクトリからモデルを検索
        if not os.path.exists(model_path):
            search_dirs = [
                os.path.dirname(os.path.abspath(__file__)),  # スクリプトと同じ
                os.getcwd(),                                  # カレントディレクトリ
            ]
            # ロード中の動画のディレクトリ
            if hasattr(self,"_current_video_path") and self._current_video_path:
                search_dirs.append(os.path.dirname(self._current_video_path))
            # ユーザーホーム
            try: search_dirs.append(os.path.expanduser("~"))
            except Exception: pass
            found = None
            basename = os.path.basename(model_path)
            for d in search_dirs:
                cand = os.path.join(d, basename)
                if os.path.exists(cand):
                    found = cand; break
            if found:
                model_path = found
                self._mp_model_path.set(found)
            else:
                # v2.5: 自動ダウンロード
                dl_url = ("https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
                          "pose_landmarker_lite/float16/latest/pose_landmarker_lite.task")
                save_dir = os.path.dirname(os.path.abspath(__file__))
                save_path = os.path.join(save_dir, basename)
                ans = messagebox.askyesno("3D",
                    f"モデルファイルが見つかりません:\n{basename}\n\n"
                    f"自動ダウンロードしますか?\n"
                    f"保存先: {save_dir}")
                if not ans: return
                try:
                    self._mp_status.set("モデルダウンロード中…")
                    self.update_idletasks()
                    import urllib.request
                    urllib.request.urlretrieve(dl_url, save_path)
                    model_path = save_path
                    self._mp_model_path.set(save_path)
                    self._mp_status.set("ダウンロード完了")
                except Exception as dl_err:
                    messagebox.showerror("3D",
                        f"ダウンロード失敗:\n{dl_err}\n\n"
                        f"手動でダウンロードしてください:\n{dl_url}")
                    self._mp_status.set("ダウンロード失敗")
                    return
        self.btn_mp_detect.config(state="disabled")
        self._mp_status.set("検出中…")
        threading.Thread(target=self._mp_worker, args=(model_path,), daemon=True).start()

    def _mp_worker(self, model_path):
        """バックグラウンドで MediaPipe Pose を全フレームに適用
           v2.8: 洗練済みKPのperson_bboxでクロップしてから検出"""
        try:
            import mediapipe as mp
            from mediapipe.tasks.python import BaseOptions, vision

            opts = vision.PoseLandmarkerOptions(
                base_options=BaseOptions(model_asset_path=model_path),
                running_mode=vision.RunningMode.IMAGE,
                num_poses=1,
                min_pose_detection_confidence=0.3,
                min_pose_presence_confidence=0.3,
            )
            results = []
            n = len(self.frames_cache)
            with _suppress_stderr():
                pose_detector_cm = vision.PoseLandmarker.create_from_options(opts)
            with pose_detector_cm as detector:
                for idx in sorted(self.frames_cache.keys()):
                    frame = self.frames_cache[idx]
                    if frame is None: continue
                    # frames_cache は既に RGB
                    rgb_full = frame
                    rgb_crop = None
                    # v2.9: person_bboxクロップを試行、失敗時はフル画像
                    if (self.refined_frames and idx < len(self.refined_frames)):
                        bbox = self.refined_frames[idx].get("person_bbox")
                        if bbox:
                            h, w = rgb_full.shape[:2]
                            x1, y1, x2, y2 = [int(v) for v in bbox]
                            margin = int((x2-x1) * 0.5)
                            x1 = max(0, x1-margin); y1 = max(0, y1-margin)
                            x2 = min(w, x2+margin); y2 = min(h, y2+margin)
                            if (x2-x1) > 50 and (y2-y1) > 50:
                                rgb_crop = np.ascontiguousarray(rgb_full[y1:y2, x1:x2])
                    # クロップ版で試行 → 失敗ならフル画像
                    landmarks = []
                    landmarks_2d = []  # v40: 画像ピクセル座標 (YOLO比較用)
                    crop_off = (0, 0)
                    for att_i, attempt_rgb in enumerate(
                            [rgb_crop, rgb_full] if rgb_crop is not None else [rgb_full]):
                        try:
                            mp_img = mp.Image(image_format=mp.ImageFormat.SRGB,
                                              data=np.ascontiguousarray(attempt_rgb))
                            with _suppress_stderr():
                                det = detector.detect(mp_img)
                            if det.pose_world_landmarks:
                                lms = det.pose_world_landmarks[0]
                                landmarks = [{"x": lm.x, "y": lm.y, "z": lm.z,
                                              "vis": getattr(lm, "visibility", 0.0)}
                                             for lm in lms]
                                # v40: 2Dランドマーク (正規化→ピクセル)
                                if det.pose_landmarks:
                                    ah, aw = attempt_rgb.shape[:2]
                                    off = ((x1, y1) if (att_i == 0 and rgb_crop is not None)
                                           else (0, 0))
                                    landmarks_2d = [
                                        {"x": lm.x * aw + off[0],
                                         "y": lm.y * ah + off[1],
                                         "vis": getattr(lm, "visibility", 0.0)}
                                        for lm in det.pose_landmarks[0]]
                                break
                        except Exception:
                            continue
                    frame_time = (self.raw_frames[idx]["time"]
                                  if self.raw_frames and idx < len(self.raw_frames)
                                  else float(idx))
                    results.append({"frame_idx": idx, "time": frame_time,
                                    "landmarks": landmarks,
                                    "landmarks_2d": landmarks_2d})
                    if idx % 5 == 0:
                        self.after(0, lambda d=idx, t=n:
                                   self._mp_status.set(f"検出中… {d}/{t}"))
            self._mp3d_frames = results
            self.after(0, self._mp_on_detect_done)
        except Exception as e:
            self.after(0, lambda err=e: (
                self._mp_status.set(f"エラー: {err}"),
                self.btn_mp_detect.config(state="normal"),
                messagebox.showerror("MediaPipe", f"検出失敗:\n{err}")))

    def _smooth_mp3d_landmarks(self):
        """v2.5: MediaPipe 3Dランドマークを時間軸で平滑化。
           指数移動平均 (EMA) で前後フレームとの連続性を改善。
           信頼度が低いフレームは前後の補間を優先。"""
        frames = self._mp3d_frames
        if not frames or len(frames) < 3: return
        alpha = 0.4  # 新フレームの重み (小さいほど滑らか)
        n_lm = 33  # MediaPipe Pose landmarks
        # 前方向パス
        fwd = []
        prev = None
        for f in frames:
            lms = f.get("landmarks", [])
            if not lms:
                fwd.append(prev if prev else [])
                continue
            smoothed = []
            for j in range(min(n_lm, len(lms))):
                lm = lms[j]
                if prev and j < len(prev) and prev[j].get("vis", 0) > 0.2 and lm["vis"] > 0.2:
                    sx = alpha * lm["x"] + (1 - alpha) * prev[j]["x"]
                    sy = alpha * lm["y"] + (1 - alpha) * prev[j]["y"]
                    sz = alpha * lm["z"] + (1 - alpha) * prev[j]["z"]
                    smoothed.append({"x": sx, "y": sy, "z": sz, "vis": lm["vis"]})
                else:
                    smoothed.append(dict(lm))
            fwd.append(smoothed)
            prev = smoothed
        # 後方向パス
        bwd = [None] * len(frames)
        prev = None
        for i in range(len(frames) - 1, -1, -1):
            lms = frames[i].get("landmarks", [])
            if not lms:
                bwd[i] = prev if prev else []
                continue
            smoothed = []
            for j in range(min(n_lm, len(lms))):
                lm = lms[j]
                if prev and j < len(prev) and prev[j].get("vis", 0) > 0.2 and lm["vis"] > 0.2:
                    sx = alpha * lm["x"] + (1 - alpha) * prev[j]["x"]
                    sy = alpha * lm["y"] + (1 - alpha) * prev[j]["y"]
                    sz = alpha * lm["z"] + (1 - alpha) * prev[j]["z"]
                    smoothed.append({"x": sx, "y": sy, "z": sz, "vis": lm["vis"]})
                else:
                    smoothed.append(dict(lm))
            bwd[i] = smoothed
            prev = smoothed
        # 前方・後方の平均
        for i, f in enumerate(frames):
            if not fwd[i] or not bwd[i]: continue
            merged = []
            for j in range(min(len(fwd[i]), len(bwd[i]))):
                a = fwd[i][j]; b = bwd[i][j]
                merged.append({
                    "x": (a["x"] + b["x"]) / 2,
                    "y": (a["y"] + b["y"]) / 2,
                    "z": (a["z"] + b["z"]) / 2,
                    "vis": max(a["vis"], b["vis"])
                })
            f["landmarks"] = merged

    def _compute_3d_global_positions(self):
        """v2.5: YOLOの2D bboxからグローバル位置を推定。
           地面を固定し、人が実際に動く3D表示を実現。
           - bboxの高さ → 奥行き(カメラからの距離)
           - bboxの中心X → 横位置
           打点フレームを原点(0,0)とする相対位置を計算。"""
        if not self._mp3d_frames or not self.refined_frames: return
        # 画像サイズ取得
        img_w = img_h = None
        for fi, frame in self.frames_cache.items():
            if frame is not None:
                img_h, img_w = frame.shape[:2]
                break
        if not img_w or not img_h: return
        # プレーヤー身長の推定値 (メートル)
        PLAYER_HEIGHT_M = 1.80
        focal = img_w * 1.2  # 焦点距離の近似 (スポーツカメラ向け)
        # 打点フレームの bbox を基準にする
        hit_idx = min(range(len(self._mp3d_frames)),
                      key=lambda i: abs(self._mp3d_frames[i]["time"] - self.hit_t))
        hit_fi = self._mp3d_frames[hit_idx].get("frame_idx", hit_idx)
        hit_bbox = None
        if hit_fi < len(self.refined_frames):
            hit_bbox = self.refined_frames[hit_fi].get("person_bbox")
        if not hit_bbox:
            # bboxなし → フォールバック (全フレーム offset=0)
            for f in self._mp3d_frames:
                f["global_offset"] = (0.0, 0.0, 0.0)
            return
        hit_bbox_h = max(hit_bbox[3] - hit_bbox[1], 1)
        hit_bbox_cx = (hit_bbox[0] + hit_bbox[2]) / 2
        hit_depth = PLAYER_HEIGHT_M * focal / hit_bbox_h
        hit_x = (hit_bbox_cx - img_w / 2) * hit_depth / focal
        for mp_f in self._mp3d_frames:
            fi = mp_f.get("frame_idx", 0)
            bbox = None
            if fi < len(self.refined_frames):
                bbox = self.refined_frames[fi].get("person_bbox")
            if not bbox:
                mp_f["global_offset"] = (0.0, 0.0, 0.0)
                continue
            bbox_h = max(bbox[3] - bbox[1], 1)
            bbox_cx = (bbox[0] + bbox[2]) / 2
            depth = PLAYER_HEIGHT_M * focal / bbox_h
            x_pos = (bbox_cx - img_w / 2) * depth / focal
            # 打点フレームを原点とした相対位置
            dx = x_pos - hit_x          # 横方向 (メートル)
            dy = -(depth - hit_depth)    # 奥行き (手前が正)
            mp_f["global_offset"] = (dx, dy, 0.0)
        # グローバルオフセットも時間軸で平滑化
        offsets = [f.get("global_offset", (0,0,0)) for f in self._mp3d_frames]
        if len(offsets) >= 3:
            alpha = 0.3
            # 前方向EMA
            smoothed = [offsets[0]]
            for i in range(1, len(offsets)):
                sx = alpha * offsets[i][0] + (1 - alpha) * smoothed[-1][0]
                sy = alpha * offsets[i][1] + (1 - alpha) * smoothed[-1][1]
                smoothed.append((sx, sy, 0.0))
            # 後方向EMA + 平均
            bwd = [offsets[-1]]
            for i in range(len(offsets) - 2, -1, -1):
                sx = alpha * offsets[i][0] + (1 - alpha) * bwd[0][0]
                sy = alpha * offsets[i][1] + (1 - alpha) * bwd[0][1]
                bwd.insert(0, (sx, sy, 0.0))
            for i, f in enumerate(self._mp3d_frames):
                f["global_offset"] = (
                    (smoothed[i][0] + bwd[i][0]) / 2,
                    (smoothed[i][1] + bwd[i][1]) / 2,
                    0.0)
        # v2.7: 全フレームの足の最低点から地面基準を計算 (打点フレーム優先)
        all_foot_z = []
        for mf in self._mp3d_frames:
            ml = mf.get("landmarks", [])
            for fi_mp in [27, 28, 29, 30, 31, 32]:
                if fi_mp < len(ml) and ml[fi_mp]["vis"] > 0.2:
                    all_foot_z.append(-ml[fi_mp]["y"])
        if all_foot_z:
            self._3d_ground_shift = -min(all_foot_z)
        else:
            # 足が未検出 → 腰の高さから推定 (腰は身長の約55%)
            hip_ys = []
            for mf in self._mp3d_frames:
                ml = mf.get("landmarks", [])
                if len(ml) > 24 and ml[23]["vis"] > 0.2:
                    hip_ys.append(-ml[23]["y"])
            if hip_ys:
                self._3d_ground_shift = -min(hip_ys) + 0.9
            else:
                self._3d_ground_shift = 0.9

    def _mp3d_data_path(self):
        """v2.9: 3DデータのJSONパス"""
        if not self.video_path: return None
        d = os.path.dirname(self.video_path)
        stem = os.path.splitext(os.path.basename(self.video_path))[0]
        hp_rank = ""
        if hasattr(self, "cur_cp_var"):
            hp = self.cur_cp_var.get()
            if hp.startswith("HP#"):
                hp_rank = f"_hp{hp[3:]}"
        return os.path.join(d, f"{stem}{hp_rank}_mp3d.json")

    def _save_mp3d_data(self):
        """v2.9: 3Dデータをファイルに保存"""
        path = self._mp3d_data_path()
        if not path or not self._mp3d_frames: return
        try:
            data = {
                "version": "2.9",
                "ground_shift": self._3d_ground_shift,
                "frames": self._mp3d_frames
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=1)
        except Exception as e:
            print(f"3D保存失敗: {e}")

    def _load_mp3d_data(self):
        """v2.9: 保存済み3Dデータを読込"""
        path = self._mp3d_data_path()
        if not path or not os.path.exists(path): return False
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._mp3d_frames = data.get("frames", [])
            self._3d_ground_shift = data.get("ground_shift", 0.0)
            if self._mp3d_frames:
                n = len(self._mp3d_frames)
                self._3d_slider.config(to=n-1)
                self._3d_frame_var.set(0)
                hit_idx = min(range(n),
                              key=lambda i: abs(self._mp3d_frames[i]["time"]-self.hit_t))
                self._3d_frame_var.set(hit_idx)
                self._mp_status.set(f"保存データ読込: {n} フレーム")
                self._3d_render_frame(hit_idx)
                return True
        except Exception as e:
            print(f"3D読込失敗: {e}")
        return False

    def _mp_on_detect_done(self):
        n = len(self._mp3d_frames)
        self._mp_status.set(f"検出完了: {n} フレーム → 平滑化中…")
        self.update_idletasks()
        # v2.5: 時間軸平滑化 (前後フレームとの指数移動平均)
        self._smooth_mp3d_landmarks()
        # v2.5: YOLO bbox からグローバル位置を推定
        self._compute_3d_global_positions()
        self._mp_status.set(f"検出完了: {n} フレーム (平滑化+位置推定済)")
        self.btn_mp_detect.config(state="normal")
        # v2.9: 自動保存
        self._save_mp3d_data()
        if n == 0: return
        # スライダーを更新
        self._3d_slider.config(to=n-1)
        self._3d_frame_var.set(0)
        # 打点フレームに移動してレンダリング
        self._3d_goto_hit()

    def _3d_goto_hit(self):
        """打点 (t≈0) に最も近いフレームへジャンプ"""
        if not self._mp3d_frames: return
        best = min(range(len(self._mp3d_frames)),
                   key=lambda i: abs(self._mp3d_frames[i]["time"] - self.hit_t))
        self._3d_slider.set(best)
        self._3d_render_frame(best)

    def _3d_goto(self, idx):
        idx = max(0, min(idx, len(self._mp3d_frames)-1)) if self._mp3d_frames else 0
        self._3d_slider.set(idx)
        self._3d_render_frame(idx)

    def _toggle_3d_anim(self):
        self._mp3d_play = not self._mp3d_play
        self.btn_3d_play.config(
            text="■ 停止" if self._mp3d_play else "▶ 再生",
            bg=ACCENT if self._mp3d_play else ACCENT2)
        if self._mp3d_play:
            self._3d_anim_step()

    def _3d_anim_step(self):
        if not self._mp3d_play: return
        cur = self._3d_frame_var.get()
        nxt = cur + 1
        if nxt >= len(self._mp3d_frames):
            nxt = 0  # ループ
        self._3d_slider.set(nxt)
        self._3d_render_frame(nxt)
        try: fps = float(self._3d_fps_var.get())
        except Exception: fps = 30.0
        delay = max(16, int(1000 / fps))
        self._mp3d_anim_id = self.after(delay, self._3d_anim_step)

    def _3d_render_frame(self, idx):
        """指定フレームの 3D スケルトンを描画"""
        print(f"[3D render] 呼出: idx={idx}, mp3d={len(self._mp3d_frames)}, "
              f"cache={len(self.frames_cache)}, raw={len(self.raw_frames) if self.raw_frames else 0}")
        self._mp3d_cur_idx = idx
        if not self._mp3d_frames or idx >= len(self._mp3d_frames):
            print(f"[3D render] mp3d空→standalone写真表示へ")
            # v49: 3Dデータが無くても2D写真は表示する
            self._update_3d_photo_standalone(idx)
            return
        frame_data = self._mp3d_frames[idx]
        lms = frame_data.get("landmarks", [])
        t = frame_data["time"] - self.hit_t
        self._3d_time_var.set(f"t = {t:+.3f}s")

        use_global = self._3d_global_move.get()

        # v2.7: 両モード共通で足を地面(z=0)にアンカー
        ground_shift = getattr(self, "_3d_ground_shift", 0.0)

        if use_global:
            goff = frame_data.get("global_offset", (0.0, 0.0, 0.0))
            def _conv(lm):
                return (lm["x"] + goff[0],
                        lm["z"] + goff[1],
                        -lm["y"] + ground_shift)
        else:
            # 従来モード: 打点フレームの腰X,Y中心を原点、Z は足基準
            hit_fr = next((f for f in self._mp3d_frames
                           if abs(f["time"]-self.hit_t)<0.06), self._mp3d_frames[0])
            h_lms = hit_fr.get("landmarks", [])
            origin_x = origin_y = 0.0
            if len(h_lms) > 24:
                lh = h_lms[23]; rh = h_lms[24]
                if lh["vis"]>0.2 and rh["vis"]>0.2:
                    origin_x = (lh["x"] + rh["x"]) / 2
                    origin_y = (lh["z"] + rh["z"]) / 2

            def _conv(lm):
                return (lm["x"] - origin_x,
                        lm["z"] - origin_y,
                        -lm["y"] + ground_shift)

        ax = self._mp3d_ax
        ax.cla()
        ax.set_autoscale_on(False)  # v2.6: 自動スケーリング無効
        ax.set_facecolor(DARK2)
        ax.tick_params(colors=SUBTEXT, labelsize=7)
        ax.set_xlabel("X (m)", color=SUBTEXT, fontsize=8)
        ax.set_ylabel("Y 奥行 (m)", color=SUBTEXT, fontsize=8)
        ax.set_zlabel("Z 高さ (m)", color=SUBTEXT, fontsize=8)
        # v2.6: 背景の箱枠を非表示に
        ax.xaxis.pane.fill = False; ax.yaxis.pane.fill = False; ax.zaxis.pane.fill = False
        ax.xaxis.pane.set_edgecolor((1,1,1,0.1))
        ax.yaxis.pane.set_edgecolor((1,1,1,0.1))
        ax.zaxis.pane.set_edgecolor((1,1,1,0.1))
        ax.grid(True, alpha=0.15)
        for sp in ax.spines.values():
            try: sp.set_color(BORDER)
            except Exception: pass

        # 地面 (z=0 平面) — v2.6: 半透明の緑面 + 太い枠線
        if self._3d_show_floor.get():
            from mpl_toolkits.mplot3d.art3d import Poly3DCollection
            gx = np.linspace(-1.5, 1.5, 7)
            gy = np.linspace(-1.5, 1.5, 7)
            # 半透明の地面ポリゴン
            verts = [[(-1.5,-1.5,0),(1.5,-1.5,0),(1.5,1.5,0),(-1.5,1.5,0)]]
            poly = Poly3DCollection(verts, alpha=0.12, facecolor="#228B22",
                                     edgecolor="#44aa44", linewidth=1.5)
            ax.add_collection3d(poly)
            # グリッド線 (薄く)
            for gx_ in gx:
                ax.plot([gx_,gx_], [gy[0],gy[-1]], [0,0], color="#44aa44", alpha=0.25, lw=0.5)
            for gy_ in gy:
                ax.plot([gx[0],gx[-1]], [gy_,gy_], [0,0], color="#44aa44", alpha=0.25, lw=0.5)
            # 打点マーカー (z=0)
            ax.scatter([0],[0],[0], color=GOLD, s=40, zorder=6, marker="+")

        # 軌跡 (過去フレームの腰中点)
        if self._3d_show_traj.get() and len(self._mp3d_frames) > 1:
            traj_x, traj_y, traj_z, traj_c = [], [], [], []
            n_traj = len(self._mp3d_frames)
            for fi, fd in enumerate(self._mp3d_frames):
                fl = fd.get("landmarks", [])
                if len(fl) > 24 and fl[23]["vis"]>0.15 and fl[24]["vis"]>0.15:
                    if use_global:
                        goff_t = fd.get("global_offset", (0,0,0))
                        hip_x = (fl[23]["x"]+fl[24]["x"])/2 + goff_t[0]
                        hip_y = (fl[23]["z"]+fl[24]["z"])/2 + goff_t[1]
                        hip_z = -((fl[23]["y"]+fl[24]["y"])/2) + ground_shift
                        traj_x.append(hip_x); traj_y.append(hip_y); traj_z.append(hip_z)
                    else:
                        cx_,cy_,cz_ = _conv({"x":(fl[23]["x"]+fl[24]["x"])/2,
                                              "y":(fl[23]["y"]+fl[24]["y"])/2,
                                              "z":(fl[23]["z"]+fl[24]["z"])/2,
                                              "vis":1.0})
                        traj_x.append(cx_); traj_y.append(cy_); traj_z.append(cz_)
                    traj_c.append(fi/n_traj)  # 0→1 でカラーグラデーション
            if traj_x:
                ax.scatter(traj_x, traj_y, traj_z, c=traj_c, cmap="plasma",
                           s=8, alpha=0.6, zorder=3)

        # スケルトン描画
        if lms:
            # KP 座標変換
            pts = {}
            for mi, lm in enumerate(lms):
                if lm["vis"] < 0.2: continue
                pts[mi] = _conv(lm)

            # 骨格線
            for a, b in self._MP_CONNECTIONS:
                if a in pts and b in pts:
                    ax.plot([pts[a][0], pts[b][0]],
                            [pts[a][1], pts[b][1]],
                            [pts[a][2], pts[b][2]],
                            color="#5599ff", lw=1.5, alpha=0.85)

            # 各 KP 点 (全身)
            xs = [v[0] for v in pts.values()]
            ys = [v[1] for v in pts.values()]
            zs = [v[2] for v in pts.values()]
            ax.scatter(xs, ys, zs, color="#aaccff", s=18, zorder=5)

            # 手首 (右) をハイライト (ラケット先端の代理)
            if 16 in pts:
                p = pts[16]
                ax.scatter([p[0]],[p[1]],[p[2]], color=GOLD, s=60, zorder=6)
            # 頭部
            if 0 in pts:
                p = pts[0]
                ax.scatter([p[0]],[p[1]],[p[2]], color="#ff9966", s=50, zorder=6)

            # 打点フレームマーカー
            if abs(t) < 0.06:
                ax.set_title(f"打点  (t={t:+.3f}s)", color=GOLD, fontsize=11, pad=4)
            else:
                ax.set_title(f"t = {t:+.3f}s", color=TEXT, fontsize=10, pad=4)
        else:
            ax.text2D(0.5, 0.5, f"フレーム #{idx}\nランドマーク未検出",
                      transform=ax.transAxes, ha="center", va="center",
                      color=SUBTEXT, fontsize=11)

        # 軸範囲固定 (v2.6: auto-scaling無効化で突然小さくなる問題を防止)
        try: zoom = float(self._3d_zoom_var.get())
        except Exception: zoom = 1.0
        if zoom < 0.5: zoom = 1.0
        if use_global:
            all_gx = [f.get("global_offset",(0,0,0))[0] for f in self._mp3d_frames]
            all_gy = [f.get("global_offset",(0,0,0))[1] for f in self._mp3d_frames]
            cx = (min(all_gx) + max(all_gx)) / 2 if all_gx else 0
            cy = (min(all_gy) + max(all_gy)) / 2 if all_gy else 0
            span = max(max(all_gx)-min(all_gx), max(all_gy)-min(all_gy), 2.0) / 2 + 0.8
            r = span / zoom
            ax.set_xlim3d(cx - r, cx + r)
            ax.set_ylim3d(cy - r, cy + r)
            ax.set_zlim3d(-0.1, max(2.2 / zoom, 0.5))
        else:
            r = 1.2 / zoom
            ax.set_xlim3d(-r, r)
            ax.set_ylim3d(-r, r)
            ax.set_zlim3d(-0.2/zoom, 2.2/zoom)
        # auto-scaling を無効化
        ax.set_autoscale_on(False)
        # v2.7: 現在の回転角度を適用 (地面固定)
        ax.view_init(elev=self._3d_elev, azim=self._3d_azim)

        try:
            self._mp3d_canvas.draw_idle()
        except Exception as e:
            print(f"[3D render] draw_idle例外: {e}")

        # v2.5: 2D写真パネルに同じフレームの写真を表示
        print(f"[3D render] _update_3d_photo呼出: idx={idx}")
        try:
            self._update_3d_photo(idx)
        except Exception as e:
            print(f"[3D render] _update_3d_photo例外: {e}")
            import traceback; traceback.print_exc()

    def _update_analysis_status(self):
        """v50: 解析ステータスバーを更新"""
        if not hasattr(self, "_analysis_status_var"): return
        parts = []
        # YOLO
        n_raw = len(self.raw_frames) if self.raw_frames else 0
        if n_raw > 0:
            parts.append(f"YOLO: ✅ {n_raw}フレーム")
        else:
            parts.append("YOLO: ❌ 未検出")
        # 洗練
        n_ref = len(self.refined_frames) if self.refined_frames else 0
        if n_ref > 0:
            parts.append(f"洗練: ✅ {n_ref}フレーム")
        # frames_cache
        n_cache = len(self.frames_cache)
        parts.append(f"画像: {'✅' if n_cache > 0 else '⏳'} {n_cache}枚")
        # MediaPipe 3D
        n_3d = len(self._mp3d_frames)
        if n_3d > 0:
            parts.append(f"3D: ✅ {n_3d}フレーム")
        else:
            parts.append("3D: ❌ 未実行 → 「▶ MediaPipe 3D 検出」を押してください")
        self._analysis_status_var.set("  |  ".join(parts))

    def _update_3d_photo_standalone(self, idx):
        """v50: 3Dデータが無い場合、写真を直接表示 (デバッグログ付き)"""
        def _dbg(msg):
            try: self._mp_status.set(f"[3D写真] {msg}")
            except Exception: pass
            print(f"[3D写真 standalone] {msg}")
        _dbg(f"開始 idx={idx}")
        if not hasattr(self, "_3d_photo_lbl"):
            _dbg("エラー: _3d_photo_lbl が無い"); return
        if not self._3d_show_photo.get():
            _dbg("2D写真チェック OFF"); self._3d_photo_lbl.config(image=""); self._3d_photo_ref=None; return
        frame = None
        fi = idx
        _dbg(f"frames_cache: {len(self.frames_cache)}件, raw_frames: {len(self.raw_frames) if self.raw_frames else 0}件")
        if self.frames_cache:
            keys = sorted(self.frames_cache.keys())
            if keys:
                fi = keys[min(idx, len(keys)-1)]
                frame = self.frames_cache.get(fi)
                _dbg(f"cache hit fi={fi}, frame={'OK' if frame is not None else 'None'}")
        if frame is None:
            vp = getattr(self, "_current_video_path", None) or getattr(self, "video_path", "")
            _dbg(f"cacheなし→動画直接読込: vp={vp[:50] if vp else 'None'}")
            if vp:
                try:
                    t = self.hit_t if hasattr(self, "hit_t") else 0
                    if self.raw_frames and fi < len(self.raw_frames):
                        t = self.raw_frames[fi].get("time", t)
                    cap = cv2.VideoCapture(vp)
                    fps_ = cap.get(cv2.CAP_PROP_FPS) or 30
                    cap.set(cv2.CAP_PROP_POS_FRAMES, int(t * fps_))
                    ok, bgr = cap.read(); cap.release()
                    if ok:
                        frame = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                        _dbg(f"動画読込OK: {frame.shape}")
                    else:
                        _dbg(f"動画読込NG: read失敗")
                except Exception as e:
                    _dbg(f"動画読込例外: {e}")
        if frame is None:
            _dbg("フレーム取得失敗→終了"); return
        img = Image.fromarray(frame)
        crop_ox, crop_oy = 0, 0
        if self.crop_rect:
            x1,y1,x2,y2 = [int(v) for v in self.crop_rect]
            x1=max(0,x1); y1=max(0,y1); x2=min(img.width,x2); y2=min(img.height,y2)
            if x2>x1 and y2>y1:
                crop_ox,crop_oy = x1,y1; img = img.crop((x1,y1,x2,y2))
        _dbg(f"画像サイズ: {img.width}x{img.height}")
        if self._3d_show_photo_kp.get() and self.refined_frames and fi < len(self.refined_frames):
            draw = ImageDraw.Draw(img, "RGBA")
            row = self.refined_frames[fi]
            for ki in range(20):
                if not self.kp_vars[ki].get(): continue
                kx=row.get(f"kp{ki:02d}_x"); ky=row.get(f"kp{ki:02d}_y")
                kc=row.get(f"kp{ki:02d}_c",0) or 0
                if kx is None or ky is None or kc<0.3: continue
                kx-=crop_ox; ky-=crop_oy
                color=KP_COLORS[ki] if ki<len(KP_COLORS) else "#888"
                shape=KP_SHAPES[ki] if ki<len(KP_SHAPES) else "circle"
                _draw_kp_shape_pil(draw, shape, kx, ky, 6, fill=color, outline="white", width=1)
        self._3d_right.update_idletasks()
        pw=max(self._3d_right.winfo_width()-8,200)
        ph=max(self._3d_right.winfo_height()-8,200)
        _dbg(f"パネルサイズ: {pw}x{ph}")
        sc=min(pw/img.width, ph/img.height, 1.0)
        dw=int(img.width*sc); dh=int(img.height*sc)
        if dw<1 or dh<1:
            _dbg(f"リサイズ結果が0: {dw}x{dh}→終了"); return
        img_d=img.resize((dw,dh),Image.LANCZOS)
        photo=ImageTk.PhotoImage(img_d)
        self._3d_photo_ref=photo
        self._3d_photo_lbl.config(image=photo)
        _dbg(f"表示完了 {dw}x{dh}")

    def _update_3d_photo(self, mp_idx):
        """v2.5: 3Dビューの右に同フレームの2D写真を表示"""
        def _dbg(msg):
            print(f"[3D写真 normal] {msg}")
        _dbg(f"開始 mp_idx={mp_idx}")
        if not hasattr(self, "_3d_photo_lbl"):
            _dbg("_3d_photo_lbl なし"); return
        if not self._3d_show_photo.get():
            _dbg("2D写真チェック OFF")
            self._3d_photo_lbl.config(image=""); self._3d_photo_ref = None; return
        if not self._mp3d_frames or mp_idx >= len(self._mp3d_frames):
            _dbg(f"mp3d範囲外: {len(self._mp3d_frames)}"); return
        frame_data = self._mp3d_frames[mp_idx]
        fi = frame_data.get("frame_idx", mp_idx)
        _dbg(f"frame_idx={fi}, time={frame_data.get('time',0):.3f}")
        frame = self.frames_cache.get(fi)
        _dbg(f"cache[{fi}]={'OK' if frame is not None else 'None'}, cache keys={len(self.frames_cache)}")
        if frame is None and self.frames_cache and self.raw_frames:
            t_target = frame_data.get("time", 0)
            best_fi = min(self.frames_cache.keys(),
                          key=lambda k: abs(self.raw_frames[k]["time"] - t_target)
                          if k < len(self.raw_frames) else float("inf"))
            frame = self.frames_cache.get(best_fi)
            _dbg(f"時刻ベース検索: best_fi={best_fi}, frame={'OK' if frame is not None else 'None'}")
        if frame is None:
            try:
                vp = getattr(self, "_current_video_path", None)
                _dbg(f"動画直接読込: vp={vp[:50] if vp else 'None'}")
                if vp:
                    cap = cv2.VideoCapture(vp)
                    fps_ = cap.get(cv2.CAP_PROP_FPS) or 30
                    cap.set(cv2.CAP_PROP_POS_FRAMES, int(frame_data.get("time",0)*fps_))
                    ok, bgr = cap.read(); cap.release()
                    if ok: frame = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                    _dbg(f"動画読込: {'OK' if ok else 'NG'}")
            except Exception as e:
                _dbg(f"動画読込例外: {e}")
        if frame is None:
            _dbg("フレーム取得失敗→終了"); return
        # frames_cache は既に RGB なのでそのまま使用
        try:
            img = Image.fromarray(frame)
            _dbg(f"Image変換OK: {img.width}x{img.height}")
        except Exception as e:
            _dbg(f"Image変換失敗: {e}"); return
        # crop
        crop_ox, crop_oy = 0, 0
        try:
            if self.crop_rect:
                x1, y1, x2, y2 = [int(v) for v in self.crop_rect]
                x1 = max(0, x1); y1 = max(0, y1)
                x2 = min(img.width, x2); y2 = min(img.height, y2)
                if x2 > x1 and y2 > y1:
                    crop_ox, crop_oy = x1, y1
                    img = img.crop((x1, y1, x2, y2))
            elif self.refined_frames and fi < len(self.refined_frames):
                bbox = self.refined_frames[fi].get("person_bbox")
                if bbox:
                    x1, y1, x2, y2 = [int(v) for v in bbox]
                    margin = int((x2 - x1) * 0.15)
                    x1 = max(0, x1 - margin); y1 = max(0, y1 - margin)
                    x2 = min(img.width, x2 + margin); y2 = min(img.height, y2 + margin)
                    if x2 > x1 and y2 > y1:
                        crop_ox, crop_oy = x1, y1
                        img = img.crop((x1, y1, x2, y2))
            _dbg(f"crop後: {img.width}x{img.height}")
        except Exception as e:
            _dbg(f"crop例外: {e}")
        # v54: KPマーカー描画を復元
        try:
            if self._3d_show_photo_kp.get() and self.refined_frames and fi < len(self.refined_frames):
                draw = ImageDraw.Draw(img, "RGBA")
                row = self.refined_frames[fi]
                for ki in range(20):
                    if not self.kp_vars[ki].get(): continue
                    kx = row.get(f"kp{ki:02d}_x"); ky = row.get(f"kp{ki:02d}_y")
                    kc = row.get(f"kp{ki:02d}_c", 0) or 0
                    if kx is None or ky is None or kc < 0.3: continue
                    kx -= crop_ox; ky -= crop_oy
                    color = KP_COLORS[ki] if ki < len(KP_COLORS) else "#888"
                    shape = KP_SHAPES[ki] if ki < len(KP_SHAPES) else "circle"
                    _draw_kp_shape_pil(draw, shape, kx, ky, 6, fill=color, outline="white", width=1)
                _dbg(f"KPマーカー描画完了")
        except Exception as e:
            _dbg(f"KPマーカー例外: {e}")
        # v54: MP比較描画を復元
        try:
            if self._3d_show_mp_compare.get() and self._mp3d_frames and mp_idx < len(self._mp3d_frames):
                COCO_TO_MP = {0:0, 1:2, 2:5, 3:7, 4:8, 5:11, 6:12, 7:13, 8:14,
                              9:15, 10:16, 11:23, 12:24, 13:25, 14:26, 15:27, 16:28}
                lms2d = self._mp3d_frames[mp_idx].get("landmarks_2d", [])
                if lms2d:
                    draw2 = ImageDraw.Draw(img, "RGBA")
                    for coco_i, mp_i in COCO_TO_MP.items():
                        if coco_i >= len(self.kp_vars) or not self.kp_vars[coco_i].get(): continue
                        if mp_i >= len(lms2d): continue
                        lm = lms2d[mp_i]
                        if lm.get("vis", 0) < 0.3: continue
                        mx = lm["x"] - crop_ox; my = lm["y"] - crop_oy
                        clr = KP_COLORS[coco_i] if coco_i < len(KP_COLORS) else "#888"
                        s = 7
                        draw2.line([mx-s, my-s, mx+s, my+s], fill=clr, width=3)
                        draw2.line([mx-s, my+s, mx+s, my-s], fill=clr, width=3)
                    _dbg(f"MP比較描画完了")
        except Exception as e:
            _dbg(f"MP比較例外: {e}")
        # リサイズして表示
        try:
            self._3d_right.update_idletasks()
            pw = max(self._3d_right.winfo_width() - 8, 200)
            ph = max(self._3d_right.winfo_height() - 8, 200)
            _dbg(f"パネル: {pw}x{ph}")
            scale = min(pw / img.width, ph / img.height, 1.0)
            dw = int(img.width * scale); dh = int(img.height * scale)
            if dw < 1 or dh < 1:
                _dbg(f"サイズ0: {dw}x{dh}→終了"); return
            img_disp = img.resize((dw, dh), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img_disp)
            self._3d_photo_ref = photo
            self._3d_photo_lbl.config(image=photo)
            _dbg(f"★表示完了 {dw}x{dh}")
        except Exception as e:
            _dbg(f"表示例外: {e}")
            import traceback; traceback.print_exc()

    def _on_tab_changed(self):
        # 3D アニメーション停止 (他タブに移動した時)
        try: sel = str(self.notebook.select())
        except Exception: sel = ""
        tab3d_str = str(getattr(self, "tab_3d", "")) if hasattr(self, "tab_3d") else ""
        print(f"[Refiner tab変更] sel={sel}, tab_3d={tab3d_str}, 一致={sel==tab3d_str}")
        if self._mp3d_play:
            if sel != tab3d_str:
                self._mp3d_play = False
                if hasattr(self, "btn_3d_play"):
                    try: self.btn_3d_play.config(text="▶ 再生", bg=ACCENT2)
                    except Exception: pass
        # v2.8: 3D→編集タブ切替時にフレーム同期
        if sel == str(self.tab_editor) and self._mp3d_frames:
            cur_3d_idx = self._mp3d_cur_idx
            if cur_3d_idx < len(self._mp3d_frames):
                fi = self._mp3d_frames[cur_3d_idx].get("frame_idx", cur_3d_idx)
                if fi != self.selected_frame_idx:
                    self.selected_frame_idx = fi
                    self.selected_kp = None
        self._refresh_current_tab()

    def _refresh_current_tab(self):
        """v2.3 fix: タブ widget で判定"""
        try: sel = str(self.notebook.select())
        except Exception: return
        if sel == str(self.tab_combined):
            self._update_chart()
            self._render_contact_sheet()
        elif sel == str(self.tab_chart):
            self._update_chart()
        elif sel == str(self.tab_contact):
            self._render_contact_sheet()
        elif sel == str(self.tab_editor):
            self._render_editor_frame()
            try: self._update_chart()
            except Exception: pass
            try: self._render_contact_sheet()
            except Exception: pass
        elif tab3d_str and sel == tab3d_str:
            # v2.9: 3Dデータ未ロードなら保存データを自動読込
            if not self._mp3d_frames:
                try: self._load_mp3d_data()
                except Exception: pass
            # v49: 3Dデータが無くてもスライダーとフレーム数を設定
            if not self._mp3d_frames and self.raw_frames:
                n = len(self.raw_frames)
                self._3d_slider.config(to=max(1, n-1))
            # v50: 解析ステータス更新
            try: self._update_analysis_status()
            except Exception: pass
            try: self._3d_render_frame(self._mp3d_cur_idx)
            except Exception: pass

    def _sel_all(self):
        for v in self.kp_vars: v.set(True)
        self._refresh_current_tab()

    def _sel_none(self):
        for v in self.kp_vars: v.set(False)
        self._refresh_current_tab()

    def _show_params_popup(self):
        """v2.5: パラメータをポップアップウィンドウで表示"""
        if hasattr(self, "_params_win") and self._params_win and self._params_win.winfo_exists():
            self._params_win.lift(); return
        win = tk.Toplevel(self, bg=PANEL2)
        win.title("パラメータ設定")
        win.geometry("900x200")
        win.transient(self)
        self._params_win = win

        head = tk.Frame(win, bg=PANEL2); head.pack(fill="x", padx=8, pady=(6, 2))
        tk.Label(head, text="パラメータ (手動編集は維持されます)",
                 bg=PANEL2, fg=ACCENT, font=_font(10, True)).pack(side="left")
        tk.Button(head, text="リセット", bg=DARK2, fg=TEXT, relief="flat",
                  font=_font(9), cursor="hand2",
                  command=self._reset_params).pack(side="right", padx=4, ipady=1)
        tk.Button(head, text="編集すべて取消", bg=DARK2, fg=RED, relief="flat",
                  font=_font(9), cursor="hand2",
                  command=self._clear_all_edits).pack(side="right", padx=4, ipady=1)

        row = tk.Frame(win, bg=PANEL2); row.pack(fill="x", padx=8, pady=(4, 8))
        self._slider(row, "KP信頼度",     self.p_kp_th,    0.05, 0.95, 0.05)
        self._slider(row, "速度MAD k",    self.p_vel_k,    2.0, 12.0, 0.5)
        self._slider(row, "加速度MAD k",  self.p_acc_k,    2.0, 12.0, 0.5)
        self._slider(row, "リンク偏差",   self.p_link_dev, 0.10, 0.80, 0.05)
        self._slider(row, "Savgol窓",     self.p_savgol_w, 3, 13, 2)
        self._slider(row, "Savgol次数",   self.p_savgol_o, 1, 5, 1)
        self._slider(row, "物体信頼度",   self.p_obj_th,   0.05, 0.80, 0.05)
        self._slider(row, "編集波及±",    self.p_edit_window, 0, 10, 1, accent=True)

    def _reset_params(self):
        self.p_kp_th.set(RFN.DEFAULT_KP_CONF_TH)
        self.p_obj_th.set(RFN.DEFAULT_OBJ_CONF_TH)
        self.p_vel_k.set(RFN.VELOCITY_MAD_K)
        self.p_acc_k.set(RFN.ACCEL_MAD_K)
        self.p_link_dev.set(RFN.LINK_DEVIATION_FRAC)
        self.p_savgol_w.set(RFN.SAVGOL_WINDOW)
        self.p_savgol_o.set(RFN.SAVGOL_ORDER)
        self.p_edit_window.set(4)

    # ════════════════════════════════════════
    #  保存
    # ════════════════════════════════════════
    def _open_learning_db_dialog(self):
        """v2.3: 学習DBの概要 + 初期インポート + リセット UI"""
        try:
            import learning_db as LDB
        except Exception as e:
            messagebox.showerror("学習DB", f"学習DBモジュール読込失敗: {e}"); return

        win = tk.Toplevel(self, bg=PANEL)
        win.title("学習DB")
        win.geometry("520x460")
        win.transient(self); win.grab_set()

        tk.Label(win, text="学習DB (キーポイント補正の蓄積)",
                 bg=PANEL, fg=ACCENT, font=_font(13, True)).pack(pady=(12, 4))

        db_path = LDB.get_db_path()
        tk.Label(win, text=f"DBパス: {db_path}",
                 bg=PANEL, fg=SUBTEXT, font=_font(9)).pack(pady=(0, 8))

        info_box = tk.Text(win, bg=DARK2, fg=TEXT, font=("Courier", 10),
                            relief="flat", height=14, wrap="word")
        info_box.pack(fill="both", expand=True, padx=12, pady=4)

        def _refresh_info():
            info_box.config(state="normal")
            info_box.delete("1.0", "end")
            try:
                s = LDB.get_db_summary(db_path)
            except Exception as e:
                info_box.insert("end", f"取得失敗: {e}\n")
                info_box.config(state="disabled"); return
            if not s["exists"]:
                info_box.insert("end", "DB はまだ作成されていません\n")
                info_box.config(state="disabled"); return
            kp_names = (RFN.KP_NAMES + ["ラケット先端", "ボール", "重心"])
            info_box.insert("end", f"総補正件数: {s['total']}\n")
            info_box.insert("end", f"統計グループ数: {s.get('stats_groups',0)}\n\n")
            if s["by_kp"]:
                info_box.insert("end", "KP 別:\n")
                for kp_id, n in sorted(s["by_kp"].items()):
                    name = kp_names[kp_id] if 0 <= kp_id < len(kp_names) else f"KP{kp_id}"
                    info_box.insert("end", f"  {name:12s}  {n:4d}\n")
            if s["by_shot"]:
                info_box.insert("end", "\nショット別:\n")
                for shot, n in s["by_shot"].items():
                    info_box.insert("end", f"  {shot or '(未設定)':12s}  {n:4d}\n")
            info_box.config(state="disabled")
        _refresh_info()

        # 初期インポート
        def _do_import():
            reg_path = self._tennis_analyzer_registry_path()
            if not reg_path:
                messagebox.showinfo("インポート",
                    "Tennis Analyzer のレジストリが見つかりません"); return
            try:
                with open(reg_path, "r", encoding="utf-8") as f:
                    reg = json.load(f)
            except Exception as e:
                messagebox.showerror("インポート", f"レジストリ読込失敗: {e}"); return
            videos = reg.get("videos", [])
            dirs = sorted({os.path.dirname(v.get("path", "")) for v in videos
                           if v.get("path")})
            if not dirs:
                messagebox.showinfo("インポート", "対象動画なし"); return
            self.status.set("学習DB 初期インポート中…")
            def _worker():
                try:
                    res = LDB.import_from_refined_jsons(db_path, scan_dirs=dirs)
                    self.after(0, lambda r=res: messagebox.showinfo(
                        "インポート",
                        f"完了: {r['imported']} 件追加 ({r['files']} ファイル走査)"))
                    self.after(0, _refresh_info)
                    self.after(0, lambda: self.status.set("学習DB インポート完了"))
                except Exception as e:
                    self.after(0, lambda err=e: messagebox.showerror(
                        "インポート", f"失敗: {err}"))
            threading.Thread(target=_worker, daemon=True).start()

        def _do_recompute():
            try:
                LDB.recompute_stats(db_path)
                _refresh_info()
                messagebox.showinfo("再計算", "統計を再計算しました")
            except Exception as e:
                messagebox.showerror("再計算", f"失敗: {e}")

        def _do_clear():
            if not messagebox.askyesno("クリア",
                "学習DB の全レコードを削除しますか? (取消不可)"): return
            try:
                LDB.delete_all(db_path)
                _refresh_info()
                messagebox.showinfo("クリア", "削除しました")
            except Exception as e:
                messagebox.showerror("クリア", f"失敗: {e}")

        btn_row = tk.Frame(win, bg=PANEL); btn_row.pack(fill="x", pady=8, padx=12)
        tk.Button(btn_row, text="既存 refined.json から取込",
                  bg=ACCENT2, fg="white", relief="flat",
                  font=_font(10, True), cursor="hand2",
                  command=_do_import).pack(side="left", padx=2, ipady=4, ipadx=6)
        tk.Button(btn_row, text="統計再計算", bg=DARK2, fg=TEXT, relief="flat",
                  font=_font(10), cursor="hand2",
                  command=_do_recompute).pack(side="left", padx=2, ipady=4, ipadx=6)
        tk.Button(btn_row, text="全削除", bg=DARK2, fg=RED, relief="flat",
                  font=_font(10), cursor="hand2",
                  command=_do_clear).pack(side="right", padx=2, ipady=4, ipadx=6)
        tk.Button(btn_row, text="閉じる", bg=DARK2, fg=TEXT, relief="flat",
                  font=_font(10), cursor="hand2",
                  command=win.destroy).pack(side="right", padx=2, ipady=4, ipadx=6)

    def _save_refined(self):
        """手動保存ボタン (互換用)。v2.3 では自動保存があるため通常不要"""
        result = self._do_save(silent=False)
        if result and result.get("ok"):
            messagebox.showinfo("保存",
                f"書き出しました ({len(self.manual_edits)} 件の手動編集を含む):\n"
                f"{result['path']}")

    def _do_save(self, silent=True):
        """v2.3: 共通保存処理 (silent=True で UI ダイアログ抑制)。
        保存後、手動編集を learning_db に記録する。"""
        if self.json_path is None or self.refined_frames is None:
            if not silent:
                messagebox.showinfo("保存", "先に JSON を読み込んでください")
            return {"ok": False}
        # v43: 二重 _refined.json 防止
        base = self.json_path[:-5] if self.json_path.endswith(".json") else self.json_path
        if base.endswith("_refined"):
            base = base[:-len("_refined")]
        out_path = base + "_refined.json"

        out_data = copy.deepcopy(self.raw_data)
        out_frames = copy.deepcopy(self.refined_frames)
        # v38: placeholderフレームは保存しない
        out_frames = [f for f in out_frames if not f.get("_placeholder")]
        for (idx, ki), val in self.manual_edits.items():
            if not (0 <= idx < len(out_frames)): continue
            deleted = (val is None)
            if ki < 17:
                if deleted:
                    out_frames[idx][f"kp{ki:02d}_deleted"] = True
                else:
                    out_frames[idx][f"kp{ki:02d}_manual"] = True
            elif ki == 17:
                if deleted:
                    out_frames[idx]["racket_tip_deleted"] = True
                else:
                    out_frames[idx]["racket_tip_manual"] = True
            elif ki == 18:
                if deleted:
                    out_frames[idx]["ball_deleted"] = True
                else:
                    out_frames[idx]["ball_manual"] = True
        out_data["frames"] = out_frames
        out_data["refined"] = True
        out_data["refiner_version"] = "2.3-gui"
        out_data["refiner_params"] = {
            "kp_conf_th":     float(self.p_kp_th.get()),
            "obj_conf_th":    float(self.p_obj_th.get()),
            "velocity_mad_k": float(self.p_vel_k.get()),
            "accel_mad_k":    float(self.p_acc_k.get()),
            "link_dev_frac":  float(self.p_link_dev.get()),
            "savgol_window":  RFN.SAVGOL_WINDOW,
            "savgol_order":   int(self.p_savgol_o.get()),
        }
        out_data["manual_edits_count"] = len(self.manual_edits)

        try:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(out_data, f, ensure_ascii=False, indent=1)
            self.status.set(f"保存: {os.path.basename(out_path)}")
            # v2.3: 学習DB に記録 (バックグラウンド)
            try:
                threading.Thread(target=self._record_edits_to_db,
                                 args=(out_data,), daemon=True).start()
            except Exception: pass
            return {"ok": True, "path": out_path}
        except Exception as e:
            if not silent:
                messagebox.showerror("保存", f"保存失敗: {e}")
            return {"ok": False, "error": str(e)}

    def _trigger_autosave(self):
        """v2.3: 編集・パラメータ変更時に呼び出す。800ms デバウンス後に保存"""
        if self.json_path is None: return
        if hasattr(self, "_autosave_after_id") and self._autosave_after_id:
            try: self.after_cancel(self._autosave_after_id)
            except Exception: pass
        self.autosave_status.set("● 編集中…")
        self._autosave_after_id = self.after(800, self._do_autosave)

    def _do_autosave(self):
        self._autosave_after_id = None
        result = self._do_save(silent=True)
        if result and result.get("ok"):
            self.autosave_status.set("✓ 自動保存済")
            # 5秒後にクリア
            self.after(5000, lambda: self.autosave_status.set(""))
        else:
            self.autosave_status.set("⚠ 保存失敗")

    def _record_edits_to_db(self, out_data):
        """v2.3: 手動編集を learning_corrections.db に追記"""
        try:
            import learning_db as LDB
        except Exception: return
        db_path = LDB.get_db_path()
        try: LDB.init_db(db_path)
        except Exception: return
        video_file = out_data.get("video", "")
        cp_rank = int(out_data.get("cp_rank", 0))
        shot = out_data.get("shot_type")
        cam = out_data.get("camera_dir")
        ref_frames = out_data.get("frames", [])
        raw_frames = self.raw_frames or []
        # v2.4 fix: dict を list にコピーしてから反復 (メインスレッドが同時に変更する可能性)
        edits_snapshot = list(self.manual_edits.items())
        for (idx, ki), val in edits_snapshot:
            if not (0 <= idx < len(ref_frames)): continue
            ref_fr = ref_frames[idx]
            raw_fr = raw_frames[idx] if idx < len(raw_frames) else None
            deleted = (val is None)
            mx = my = None
            if not deleted and isinstance(val, (tuple, list)) and len(val) >= 2:
                mx, my = float(val[0]), float(val[1])
            try:
                LDB.record_correction(
                    db_path,
                    video_file=video_file, cp_rank=cp_rank,
                    frame_idx=idx, frame_time=ref_fr.get("time", 0.0),
                    kp_id=ki,
                    raw_frame=raw_fr, refined_frame=ref_fr,
                    manual_x=mx, manual_y=my, deleted=deleted,
                    shot_type=shot, camera_dir=cam,
                    source="manual_delete" if deleted else "manual_edit",
                )
            except Exception:
                pass
        # 統計再計算 (重い処理は別スレッド継続)
        try: LDB.recompute_stats(db_path)
        except Exception: pass


if __name__=="__main__":
    app=TennisApp()
    app.mainloop()
