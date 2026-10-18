# Hit Moment Analyzer 引継ぎガイド

更新基準: v118-batch / 2026-10-18

## 1. アプリの目的

テニス動画から打球音候補を抽出し、姿勢・ボール軌跡を組み合わせてヒットポイント候補を検証するWindows向けPython/Tkinterアプリです。壁打ちでの壁音、反響音、周囲の打球音を確認できるよう、採用候補と除外候補の両方を画面に残します。

## 2. 現在の主要機能

- 音声エネルギーから候補ピークを抽出
- 壁打ちでは候補間隔を0.8秒以上に制限し、後続の壁音・反響候補を除外
- カメラまで3mを初期値とした音速遅延補正
- RTMPoseによる人物キーポイント検出
- YOLOによる人物・ボール検出
- 「ヒットポイント一覧」「ヒットポイント詳細」「フレーム検証（実験）」「フォルダ一括検証」
- 側面映像では、信頼できるボール方向転換の1フレーム前を打点として優先
- 動画別コメント、HP別コメント、ユーザー指定の正確なHPを保存
- 複数動画の結果を `HitMomentAnalyzer_batch_report.txt` に出力

## 3. 実行環境

- Windows 11
- PowerShell
- Git for Windows
- Miniforge3
- Python 3.10（`setup.ps1`がプロジェクト内の`.venv`を作成）

初回セットアップ:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\setup.ps1"
```

起動:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\run.ps1"
```

## 4. 重要なファイル

- `tennis_analyzer.py` — メインアプリ
- `requirements.txt` — Python依存パッケージ
- `setup.ps1` — Miniforge環境作成・依存パッケージ導入
- `run.ps1` — アプリ起動
- `tests/test_fast_hp_pose.py` — 主要ロジックの回帰テスト
- `README.md` — バージョン別の変更履歴
- `MIGRATION.md` — 新PCへの移行手順
- `NEW_PC_CHECKLIST.md` — 新PCでの確認チェックリスト

## 5. 動画別データの保存方式

動画本体はGit管理しません。動画と同じフォルダに、動画の拡張子を除いた同名フォルダを作成して解析結果を保存します。

```text
D:\TennisVideos\sample.mp4
D:\TennisVideos\sample\
  metadata.json
  tennis_labels.db
  音声解析キャッシュ（npz）
  姿勢・ボール検出JSON
  batch_validation.json
  review_comments.json
  サムネイル等
```

新PCへ移すときは、動画ファイルと同名フォルダを必ずセットでコピーしてください。フォルダ一括検証を行った親フォルダには `HitMomentAnalyzer_batch_report.txt` も作成されます。

## 6. コメントと人手による正解指定

`review_comments.json` に次を保存します。

- ヒットポイント詳細の候補別コメント
- フレーム検証全体のコメント
- ユーザーが指定した正確なHPのフレーム番号・時刻・理由
- 自動選択されたフレーム番号

一括レポートを再生成すると、これらの情報がテキストにも反映されます。

## 7. フレーム検証の現在の判定

基本スコア:

- 音声時刻への近さ 30%
- 手首速度 28%
- 手首速度変化 18%
- ボール変化 16%
- 手とボールの近さ 8%

撮影方向が「横」の場合、音声候補の近傍で十分なConfidenceを持つボール方向転換が見つかれば、方向転換点の1フレーム前を優先します。ボールが未検出、方向転換が弱い、軌跡の信頼性が低い場合は基本スコアへ戻ります。

## 8. キャッシュと再解析

- 同じ動画を再度選ぶと、保存済み音声解析や検証結果を可能な範囲で再利用します。
- 解析ロジックのバージョンが変わった場合、互換性のないキャッシュは自動的に無効化されます。
- 一括画面の「完了済みも再解析」をオンにすると、保存済みの完了結果も再計算します。
- `.venv`、AIモデル、一時キャッシュはPC間でコピーせず、新PCで再作成する方が安全です。

## 9. Git運用

安定版は `main` です。変更は作業ブランチで行い、テスト後にPull Requestまたは明示的なマージで `main` へ統合します。

```powershell
git switch main
git pull
git switch -c feature/短い作業名
# 編集・テスト
git add .
git commit -m "変更内容"
git push -u origin feature/短い作業名
```

動画、`.venv`、DB、npz、AIモデルは `.gitignore` の対象です。

## 10. テスト

このリポジトリの仮想環境にはpytestが含まれない場合があります。現在は引数なしテスト関数を読み込む軽量ランナーでも検証できます。

```powershell
.\.venv\python.exe -m py_compile .\tennis_analyzer.py
.\.venv\python.exe -c "import importlib.util,inspect,pathlib; p=pathlib.Path('tests/test_fast_hp_pose.py').resolve(); s=importlib.util.spec_from_file_location('local_tests',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); fs=[f for n,f in inspect.getmembers(m,inspect.isfunction) if n.startswith('test_') and not inspect.signature(f).parameters]; [f() for f in fs]; print(f'{len(fs)} tests passed')"
```

v118時点では72件が成功しています。

## 11. 既知の課題

- ボールが小さい、ブレる、人物やラケットに隠れる映像ではYOLOのボール検出が不安定
- 壁の近くにカメラを置いた映像では、打球音と壁音の時間差が小さく音声だけでは分離困難
- 側面打点補正はボール軌跡が複数フレーム連続で検出された場合に最も有効
- `tennis_analyzer.py`が大きいため、今後は音声・姿勢・UI・永続化をモジュール分割する余地がある
- `HANDOFF.md`よりREADMEの新しい版番号が進んでいる場合はREADME先頭の変更履歴を優先して確認する

## 12. Web版ChatGPTへ渡す情報

GitHubリポジトリ、`README.md`、この`HANDOFF.md`を最初に読ませてください。実動画の評価を依頼するときは、動画そのものより先に `HitMomentAnalyzer_batch_report.txt`、該当画面のスクリーンショット、必要なら `review_comments.json` を渡すと効率的です。
