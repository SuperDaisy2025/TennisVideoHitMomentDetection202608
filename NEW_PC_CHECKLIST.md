# 新PC 起動確認チェックリスト

## 基本環境

- [ ] WindowsへGit for Windowsをインストールした
- [ ] Miniforge3を`%USERPROFILE%\miniforge3`へインストールした
- [ ] `git --version`が成功する
- [ ] `Test-Path "$env:USERPROFILE\miniforge3\Scripts\conda.exe"`が`True`

## ソースコード

- [ ] GitHubからリポジトリをcloneした
- [ ] `git switch main`を実行した
- [ ] `git pull`が成功した
- [ ] `git status`に意図しない変更がない
- [ ] README先頭がv118以降になっている

## Python環境

- [ ] `setup.ps1`がエラーなく完了した
- [ ] `.venv\python.exe`が存在する
- [ ] `tennis_analyzer.py`の構文チェックが成功した
- [ ] 回帰テストが成功した

```powershell
.\.venv\python.exe -m py_compile .\tennis_analyzer.py
```

## アプリ起動

- [ ] `run.ps1`でアプリが起動する
- [ ] ウィンドウタイトルが`Hit Moment Analyzer`である
- [ ] 「ヒットポイント一覧」が表示される
- [ ] 「ヒットポイント詳細」が表示される
- [ ] 「フレーム検証（実験）」が表示される
- [ ] 「フォルダ一括検証」が表示される

## 動画と保存データ

- [ ] 動画と同名フォルダをセットで新PCへコピーした
- [ ] 既存動画を選択できる
- [ ] 保存済み音声解析結果が読み込まれる
- [ ] ヒットポイント詳細のコメントが復元される
- [ ] フレーム検証の正確なHP指定・理由が復元される
- [ ] 必要な動画だけ「完了済みも再解析」で再計算できる

## AI検出

- [ ] RTMPoseが初期化できる
- [ ] YOLOが初期化できる
- [ ] 人物キーポイントが表示される
- [ ] ボール検出結果または未検出表示が確認できる
- [ ] 側面動画の撮影方向を「横」に設定できる

## 一括検証・レポート

- [ ] 動画フォルダを指定できる
- [ ] 前後の動画へ移動できる
- [ ] 動画別コメントを入力・保存できる
- [ ] `HitMomentAnalyzer_batch_report.txt`が生成される
- [ ] レポートにHPコメントとユーザー指定フレームが含まれる

## GitHub・Web版ChatGPT

- [ ] 新PCのGitでGitHub認証が完了した
- [ ] Web版ChatGPTからGitHubリポジトリを参照できる
- [ ] ChatGPTへREADME、HANDOFF、MIGRATIONを先に確認するよう伝えた
- [ ] 開発時は作業ブランチを作る運用にした

## 最終確認

- [ ] 旧PCのデータを消す前に、新PCで少なくとも1本の既存動画を確認した
- [ ] 外付け媒体または別ストレージに動画・同名フォルダのバックアップがある
- [ ] GitHubの`main`とローカル`main`が同じコミットである

