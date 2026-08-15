# Tennis Form Analyzer 引き継ぎドキュメント

## バージョン履歴の要点（v25 以降、v62 まで）

会話に登場した主要変更をバージョンごとに整理する。詳細は各 v の changelog を参照。

- **v25** — 動画情報ポップアップ追加、_meta_extra.json 保存
- **v26** — YOLO Refiner を Tennis Analyzer にタブ統合（案 A: 統合ファイル）
- **v27** — 動画情報にキーポイント検出プルダウン（不要/HP のみ/HP 前後）
- **v29** — 動画情報ポップアップにサムネイル自動サイクル
- **v30** — 顔・体の向き検出（face_yaw / face_pitch / body_yaw）
- **v31** — グラフ 3（角度時系列）追加、HP のみ検出を ±5 フレームに拡張
- **v33** — グラフ 2 の背景写真クロップ、シーン変化検出のスキップ、HP 切替時の refined 優先
- **v36–v38** — placeholder 方式の廃止（KP マーカーずれの根本修正）
- **v39** — ヒットフレーム最適選択（右手首ベース）、3D カメラ視点にカメラ方向反映
- **v40** — MediaPipe vs YOLO 比較（× マーカー）、プロジェクトフォルダ集約管理
- **v41–v44** — プルダウンを実データ範囲に自動調整、CP→HP 表記統一
- **v45** — MediaPipe / TF 警告抑制の強化（`_suppress_stderr`, absl FATAL）
- **v46–v48** — Refiner タブ整理、KP 選択の重複バグ修正、KP 追加時三角マーカー
- **v53** — 起動時最大化（zoomed）、KP 検出ボタンを 1 つに統合
- **v54** — KP マーカー / MP 比較の描画を復元、3D スケルトンサイズ改善
- **v55** — スクロール改善、T キーデバッグ、検出情報を左パネルに移動
- **v56** — 3D タブをメインに移設（試み、失敗）、UI 大幅改善（ホバー情報右上、状態表示、KP リスト形状）
- **v57** — 3D タブ移設のエラー修正（Notebook 制約に対応）
- **v58** — 3D タブを起動時からトップバーに表示（プレースホルダー方式）
- **v59** — 3D 構築デバッグ強化、検出情報の更新箇所追加
- **v60** — Refiner + 3D を動画読込時に事前構築
- **v61** — MediaPipe をデフォルトに、検出情報 3 行 + ボタン形式、バックグラウンド実行 + 進捗表示
- **v62** — MP と YOLO を完全に別ファイルに分離（`_mp.json` / `_yolo.json`）、MP-YOLO 比較タブ追加

## 設計上の重要な判断とその背景

### 1. 統合ファイル（v26）
- 選択肢: 案 A（1 つの Python ファイルに統合） / 案 B（別ウィンドウ起動）
- 選択: **案 A**
- 理由: UX 上、タブ切替の方が直感的。将来的なデータ共有も容易。
- 制約: RefinerGUI (`tk.Tk`) を RefinerFrame (`tk.Frame`) に変換。色定数の衝突は Refiner 側にプレフィックスなし（Tennis Analyzer 側を優先）で対処。

### 2. Placeholder 方式の廃止（v38）
- 経緯: v36 で「フレーム抽出範囲を JSON 範囲より広げる」ため placeholder フレームを raw_frames に追加した。
- 問題:
  - fps 不一致でフレーム数が膨張（例: 61 → 71）
  - 洗練処理が placeholder に対して KP を補間生成（ゴースト KP）
  - KP マーカーが写真とずれる重大バグ
- 修正: **完全廃止**。JSON にあるフレームのみ使用。範囲が狭い場合はステータス案内。
- 教訓: データ構造の膨張は副作用が広範囲に及ぶ。

### 3. MP と YOLO の別ファイル化（v62）
- 選択肢:
  - 案 A: `_cp{rank}_mp.json` / `_cp{rank}_yolo.json` に分離
  - 案 B: 現状維持で「YOLO 再検出」ボタンで上書き
  - 案 C: 1 ファイルにマージ（MP 2D + YOLO ラケット / ボール）
- 選択: **案 A**
- 理由:
  - 検出情報で両者を独立に判定・表示できる
  - 用途が違う（MP = 姿勢 + 3D、YOLO = ラケット / ボール検出）
  - 上書きの意図しない副作用を防ぐ
- 実装: `_kp_data_file(video_path, rank, source="mp"|"yolo"|"auto")` ヘルパーで一元管理。旧 `_cp{rank}.json`（legacy）は `model` フィールドで振り分けて表示（後方互換）。

### 4. 3D タブをトップバーに移設（v58）
- 経緯:
  - v56 で 3D タブを Refiner サブタブからメイン Notebook に移動しようとした
  - Tkinter の制約で「別の Notebook の子ウィジェットを他の Notebook に移動できない」エラー
- 修正: **3D タブフレームを最初からメイン Notebook の子として生成**。Refiner 構築時に `_build_3d_tab()` でその中身を構築。

### 5. 起動時最大化（v53）
- 選択: `self.state("zoomed")`
- 理由: ノート PC など小さい画面で下が切れる問題への対処
- 制約: Windows 依存。macOS / Linux では別 API が必要。

### 6. 警告抑制（v45）
- 経緯: MediaPipe が大量の警告を stderr に出す（`W0000 ... landmark_projection_calculator.cc` など）
- 対処:
  - 環境変数（`TF_CPP_MIN_LOG_LEVEL`, `GLOG_minloglevel`）をネイティブライブラリ import 前に設定
  - Python レベルは `absl.logging` を FATAL に、`google.protobuf` / `mediapipe` のロガーを ERROR に
  - C++ レベルの直接 stderr 出力は Python では消せないため、`_suppress_stderr()` コンテキストマネージャで OS レベル（`os.dup2`）にリダイレクト

### 7. KP マーカーの一元管理（v47）
- 選択: `KP_SHAPES` 配列 + `_draw_kp_shape_canvas()` / `_draw_kp_shape_pil()` ヘルパー
- 理由: エディタ / 連続写真 / 3D 写真 / KP リスト（4 箇所以上）で同じ形状を統一表示するため
- 形状: 左 = circle、右 = square、鼻 = diamond、ラケット / ボール / 重心 = star、推論 KP = 白 × 上乗せ

## 既知の問題（v62 時点で未解決）

### 高優先度
1. **Refiner の写真エリアがグラフ非表示時に最大化されない**
   - 症状: グラフ 2/3 を OFF にしても、その領域の高さが空のまま残る
   - 影響: 連続写真エリアが常に小さい
   - 修正方針: グラフ非表示時に `pack_forget` してから写真エリアを再 pack。または grid に変更してサイズ計算を委譲

2. **v62 の動作未確認項目**
   - HP 選択ハイライトの再生中維持（`selection_clear` 削除の効果）
   - 3D タブの現在 HP 表示（`_3d_hp_var` の更新タイミング）
   - 画像抽出完了時の検出情報自動更新（Refiner の `finally` 節から呼び出し）
   - YOLO 検出済み時の legacy 振り分け表示

### 中優先度
3. **タブインデックスの一貫性** — v62 で比較タブが追加されたので `idx==5, 6, 7` の分岐が正しいか要確認。特に v56 以降の変更で `_refresh_active_tab` の分岐と実際のタブ順が乖離している可能性
4. **Tkinter フォーカス問題** — T キー（見えない点トグル）は `editor_canvas.focus_set()` が必要。クリック時に `_focus_and_mousedown` で発火するが、確実性は環境依存
5. **MediaPipe 全 HP 自動検出の中断機能なし** — 動画情報で ON にすると全 HP を順次処理するが、途中で止めたい場合の UI がない

### 低優先度
6. **プロジェクトフォルダ管理の実運用テスト未実施**
7. **手ぶれ判定の閾値** — v53 で 2.0 → 1.0 に変更したが、実写での妥当性は不明
8. **履歴タブのサムネ生成タイミング** — いつ生成されるか会話では確認できず「不明」

## 次に行う作業（優先順）

1. **v62 の動作確認をユーザーに依頼**
   - 検出情報の 3 行表示
   - 画像抽出完了時の自動更新
   - MP-YOLO 比較タブ
   - 3D タブの HP 表示
   - HP 選択の常時ハイライト

2. **v63: Refiner 写真エリアの動的最大化**
   - グラフ 2/3 の pack_forget 時に、写真エリアの `expand=True` が効くようにする
   - または、全体を grid に変更してサイズ計算を委譲

3. **タブインデックスの再整理**
   - タブが増えたので `_refresh_active_tab` を辞書ベース（`tab_ref -> callback`）に変えることを検討

4. **T キーのフォーカス確実化**
   - Refiner タブ / 編集サブタブ選択時に自動で `editor_canvas.focus_set()`

5. **MP 検出の中断ボタン**
   - `_gen` トークンを使えば中断は可能（既存の設計に合わせる）

## デバッグとログ

以下は PowerShell に出力される（開発段階で意図的に残している）：

- `[Refiner tab変更]` — Refiner サブタブ変更時
- `[3D render]` — `_3d_render_frame` 呼出時
- `[3D写真 normal]` — `_update_3d_photo` の各ステップ
- `[3D写真 standalone]` — 3D データ無しの写真表示
- `[3D構築]` — 3D タブ構築成功/失敗
- `[Tキー]` — T キー押下時の selected_kp / hover_kp
- `[MP検出エラー]` — MediaPipe 検出失敗時のトレースバック
- `[画像抽出]` `[Refiner事前構築]` `[3Dタブ移設]` など

本番リリース時はこれらを一括で削除する必要がある。

## 会話から確認できなかった事項（不明扱い）

- `yolo_refiner.py`（バックエンド CLI）の内容
- `learning_db.py` の内容
- 実際の動作環境（Windows / macOS / Linux）の他バージョンでのテスト状況
- MediaPipe モデルのバージョン依存性
- ユーザーのプロジェクトフォルダの実際のパス（`C:\Users\USER\projects\TennisFormAnalyzer` 以外）
- 動画の解像度・fps の推奨値
- ライセンス
