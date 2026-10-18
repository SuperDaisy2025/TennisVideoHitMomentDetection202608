# 新しいPCへの移行手順

対象: Hit Moment Analyzer v118以降

## A. 旧PCで準備する

1. GitHubの`main`が最新であることを確認します。

```powershell
Set-Location "C:\Users\USER\Projects\TennisHitMomentDetect202608"
git switch main
git pull
git status
```

2. 動画保管フォルダを外付けSSD等へコピーします。各動画と、拡張子を除いた同名フォルダをセットでコピーしてください。

```text
sample.mp4
sample\
```

3. フォルダ一括検証を利用している場合は、親フォルダの `HitMomentAnalyzer_batch_report.txt` もコピーします。

4. 次はコピー不要です。

- プロジェクト内の`.venv`
- `__pycache__`
- `.ultralytics`
- `*.pt`、`*.task`など再取得可能なAIモデル

## B. 新PCへ必要ソフトを導入する

1. Git for Windowsをインストール
2. Miniforge3を標準のユーザーフォルダへインストール
3. PowerShellを開いて確認

```powershell
git --version
Test-Path "$env:USERPROFILE\miniforge3\Scripts\conda.exe"
```

2行目が`True`になれば`setup.ps1`の想定場所と一致しています。

## C. GitHubから取得する

```powershell
New-Item -ItemType Directory -Path "$env:USERPROFILE\Projects" -Force
Set-Location "$env:USERPROFILE\Projects"
git clone https://github.com/SuperDaisy2025/TennisVideoHitMomentDetection202608.git
Set-Location ".\TennisVideoHitMomentDetection202608"
git switch main
git pull
```

GitHub認証画面が出た場合は、対象リポジトリへアクセスできるアカウントで認証します。

## D. Python環境を作る

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\setup.ps1"
```

初回はPythonパッケージとAIモデルの取得に時間がかかります。ネットワーク接続が必要です。

## E. 起動する

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\run.ps1"
```

別の場所から起動する場合:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\Projects\TennisVideoHitMomentDetection202608\run.ps1"
```

## F. 動画データを配置する

動画と同名フォルダの相対関係を変えないでください。

```text
D:\TennisVideos\sample.mp4
D:\TennisVideos\sample\review_comments.json
```

アプリから`sample.mp4`を選び、保存済み解析結果とコメントが表示されることを確認します。

## G. Web版ChatGPTを使う

ChatGPTの設定からGitHubを接続し、このリポジトリへの読み取りを許可します。最初の会話で次を伝えてください。

```text
Hit Moment Analyzerを引き継いで開発します。
リポジトリのREADME.md、HANDOFF.md、MIGRATION.mdを最初に確認してください。
Windows 11、Python 3.10、Miniforge、PowerShellを使用します。
変更は作業ブランチで行い、テスト結果を明記してからmainへ統合してください。
```

通常のChatGPT GitHub接続はコードの参照・分析が中心です。ローカル動画を使った実行確認、コミット、pushには新PCのGit/Codex環境を使ってください。

## H. 移行後に問題が起きた場合

- `Miniforge was not found`: Miniforgeの場所を確認
- `Python environment not found`: `setup.ps1`を先に実行
- スクリプト実行ポリシーエラー: 必ず`-ExecutionPolicy Bypass -File`形式で実行
- AIモデル取得エラー: ネット接続、プロキシ、セキュリティソフトを確認
- 古い解析が出ない: 動画と同名フォルダを同じ親フォルダへ置いたか確認
- 動画を移動した後に一部結果だけ出ない: 互換性のないキャッシュは再解析し、コメントJSONは保持

