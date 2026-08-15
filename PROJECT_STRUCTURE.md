# プロジェクト構成

## 想定するフォルダ構成

```
TennisFormAnalyzer/
├── tennis_analyzer.py          # メインアプリ (v62)
├── yolo_refiner.py             # YOLO洗練バックエンド (会話では変更していない/不明)
├── learning_db.py              # 学習DB (会話では変更していない/不明)
├── requirements.txt            # 依存ライブラリ
├── README.md                   # 概要
├── HANDOFF.md                  # 引き継ぎドキュメント
├── PROJECT_STRUCTURE.md        # このファイル
├── pose_landmarker_lite.task   # MediaPipe姿勢モデル (初回自動DL)
├── face_landmarker.task        # MediaPipe顔モデル (初回自動DL)
├── managed_videos/             # プロジェクト管理された動画 (v40〜)
│   └── {動画名}/
│       ├── {動画名}.mp4
│       ├── {動画名}_meta_extra.json
│       ├── {動画名}_analysis.db
│       └── yolo/
│           ├── {動画名}_cp{rank}_mp.json          # MediaPipe 2D KP (v62〜)
│           ├── {動画名}_cp{rank}_mp3d.json        # MediaPipe 3D 世界座標
│           ├── {動画名}_cp{rank}_yolo.json        # YOLO 2D KP (v62〜)
│           ├── {動画名}_cp{rank}_refined.json     # Refiner 洗練後 KP
│           └── {動画名}_cp{rank}.json             # legacy (v61 以前、後方互換)
├── analyzed_videos.json        # 履歴レジストリ (不明: 会話では確認できず)
└── (元の動画フォルダ)/          # 元ファイルは保持される
    ├── {動画名}.mp4
    └── {動画名}_meta_extra.json
```

## 各ファイルの役割

### tennis_analyzer.py（メインアプリ、v62）
- クラス `TennisApp(tk.Tk)`
  - メイン画面（ショット選定、HP リスト、再生、クロップ、ラベル付け）
  - 音声解析、ピーク検出
  - YOLO 検出ワーカー、MediaPipe 検出ワーカー
  - 検出情報パネル（左パネル下）
  - 履歴タブ、MP-YOLO 比較タブ
  - Face Mesh 補正、ヒットフレーム最適選択、顔・体の向き検出
- クラス `RefinerFrame(tk.Frame)`
  - 総合ビュー（グラフ 1/2/3 + 連続写真）
  - 編集タブ（KP 手動編集）
  - 3D タブ（メイン Notebook に移設される）
  - 洗練処理（Savgol 平滑化、リンク偏差検出）
  - 保存機能
- 共通ヘルパー
  - `_draw_kp_shape_canvas` / `_draw_kp_shape_pil`（マーカー描画）
  - `_star_polygon` / `_diamond_polygon`
  - `_suppress_stderr`（MediaPipe 警告抑制）
  - `_setup_jp_font`（matplotlib 日本語フォント）
- 定数
  - `APP_VERSION`, `APP_VERSION_DESC`
  - `KP_EXT_NAMES`, `KP_COLORS`, `KP_SHAPES`
  - 色定数（BG, PANEL, ACCENT, GOLD, RED など）

### yolo_refiner.py
- 内容: **不明**（会話では変更していない）
- 想定: 洗練アルゴリズムのバックエンド CLI
- `RFN.KP_NAMES`（COCO 17 点の日本語名）が参照されている

### learning_db.py
- 内容: **不明**（会話では変更していない）
- 想定: SQLite 学習 DB のラッパー
- `LDB.recompute_stats(db_path)` などが参照されている

### JSON ファイル形式

#### `{動画名}_meta_extra.json`
動画情報ポップアップで選んだメタデータ：
```json
{
  "camera_dir": "後ろ",
  "main_shots": ["サーブ", "フォアハンド"],
  "content_type": "壁打ち",
  "mp_auto": true
}
```

#### `{動画名}_cp{rank}_mp.json`（v62〜）
MediaPipe 検出結果（YOLO 互換形式）：
```json
{
  "video": "xxx.mp4",
  "cp_rank": 5,
  "hit_time": 12.345,
  "model": "mediapipe",
  "frames": [
    {
      "frame_idx": 0,
      "time": 10.845,
      "obj_conf": 0.9,
      "person_bbox": [x1, y1, x2, y2],
      "kp00_x": 320.5, "kp00_y": 180.2, "kp00_c": 0.95,
      "kp01_x": ..., ..., 
      "face_yaw": 90.0,
      "face_pitch": 30.0,
      "body_yaw": 180.0
    }
  ],
  "optimal_hit_time": 12.310,
  "optimal_hit_reason": "右手首最高速度"
}
```

#### `{動画名}_cp{rank}_yolo.json`（v62〜）
YOLO 検出結果。`model: "yolov8n-pose + yolov8n"`。ラケット先端（kp17）、ボール（kp18）、重心（kp19）を含む。

#### `{動画名}_cp{rank}_mp3d.json`
MediaPipe 3D 世界座標：
```json
{
  "version": "61",
  "ground_shift": 0.0,
  "frames": [
    {
      "frame_idx": 0,
      "time": 10.845,
      "landmarks": [{"x": 0.1, "y": 0.5, "z": 0.0, "vis": 0.9}, ...],  # 33点3Dメートル座標
      "landmarks_2d": [{"x": 320.5, "y": 180.2, "vis": 0.95}, ...]     # 2Dピクセル座標
    }
  ]
}
```

#### `{動画名}_cp{rank}_refined.json`
Refiner で保存した洗練後の KP。`_cp{rank}_mp.json` または `_cp{rank}_yolo.json` と同じ形式で、`manual_edits` フィールドを追加。

## タブ構成（v62 時点）

| index | タブ名 | 内容 |
|-------|-------|------|
| 0 | メイン画面 (ショット選定) | HP リスト、再生、ラベル付け |
| 1 | 連続写真 | HP 前後のフレームを並べる |
| 2 | ショット比較 | 複数 HP を並べて比較 |
| 3 | 同タイミング比較 | 打点タイミングを揃えて比較 |
| 4 | Refiner | 総合ビュー + 編集（サブタブ） |
| 5 | 3D | MediaPipe 3D スケルトン + 2D 写真 |
| 6 | MP-YOLO 比較 | ○ と × で両者を重ね描き |
| 7 | 履歴 | 解析済み動画の一覧 |

Refiner 内のサブタブ:
- 総合ビュー
- 編集

## KP ID 対応表

| KP ID | 名称 | 形状 | 由来 |
|-------|-----|------|-----|
| 0 | 鼻 | ◇ diamond | COCO |
| 1 | 左目 | ○ circle | COCO |
| 2 | 右目 | □ square | COCO |
| 3 | 左耳 | ○ circle | COCO |
| 4 | 右耳 | □ square | COCO |
| 5 | 左肩 | ○ circle | COCO |
| 6 | 右肩 | □ square | COCO |
| 7 | 左肘 | ○ circle | COCO |
| 8 | 右肘 | □ square | COCO |
| 9 | 左手首 | ○ circle | COCO |
| 10 | 右手首 | □ square | COCO |
| 11 | 左腰 | ○ circle | COCO |
| 12 | 右腰 | □ square | COCO |
| 13 | 左膝 | ○ circle | COCO |
| 14 | 右膝 | □ square | COCO |
| 15 | 左足首 | ○ circle | COCO |
| 16 | 右足首 | □ square | COCO |
| 17 | ラケット先端 | ★ star | 独自 (YOLO のみ) |
| 18 | ボール | ★ star | 独自 (YOLO のみ) |
| 19 | 重心 | ★ star | 独自 (計算) |

MediaPipe から COCO への変換は `MP_TO_COCO` 辞書で行う：
```python
{0:0, 2:1, 5:2, 7:3, 8:4, 11:5, 12:6, 13:7, 14:8,
 15:9, 16:10, 23:11, 24:12, 25:13, 26:14, 27:15, 28:16}
```

## 色定数（v62）

```python
BG      = "#0f1117"
PANEL   = "#1a1d27"
PANEL2  = "#141720"
ACCENT  = "#e8593c"    # 赤オレンジ
ACCENT2 = "#3b8bd4"    # 青
GOLD    = "#ef9f27"
GREEN   = "#1d9e75"
TEXT    = "#d4d0c8"
SUBTEXT = "#888780"
BORDER  = "#2c2e3a"
DARK2   = "#12141e"
RED     = "#ff5252"
```

## デバッグログの一覧（PowerShell 出力）

- `[Refiner tab変更]` — Refiner サブタブ変更時
- `[3D render]` — `_3d_render_frame` 呼出時
- `[3D写真 normal]` — `_update_3d_photo` の各ステップ
- `[3D写真 standalone]` — 3D データ無しの写真表示
- `[3D構築]` — 3D タブ構築成功 / 失敗
- `[Tキー]` — T キー押下時の selected_kp / hover_kp
- `[MP検出エラー]` — MediaPipe 検出失敗時のトレースバック
- `[画像抽出]` — 画像抽出ボタン押下時のエラー
- `[Refiner事前構築]` — 動画読込時の Refiner 構築失敗
- `[3Dタブ移設]` — 3D タブ移設失敗（v56 以前の残骸）
