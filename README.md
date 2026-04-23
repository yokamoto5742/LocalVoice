# VoiceScribe

**日本語の専門用語に強いWindows 用ショートカット型音声入力ツール**

Pause キー で録音開始/終了 、文字起こし結果をアクティブウィンドウへ直接貼り付け。1 日 200 回以上の短文作成が可能な設計です。

---

## 目次

- [VoiceScribe 開発の経緯](#VoiceScribe-開発の経緯)
- [想定ユーザーと使用シーン](#想定ユーザーと使用シーン)
- [特徴](#特徴)
- [置換辞書のサンプル](#置換辞書のサンプル)
- [クイックスタート](#クイックスタート)
- [使い方](#使い方)
- [設計のポイント](#設計のポイント)
- [設定](#設定)
- [開発者向け情報](#開発者向け情報)
- [システム要件](#システム要件)
- [トラブルシューティング](#トラブルシューティング)
- [バージョン情報](#バージョン情報)
- [ライセンス](#ライセンス)
- [更新履歴](#更新履歴)
- [免責事項](#免責事項)

---

## VoiceScribe 開発の経緯

既存の音声入力アプリには、以下のような不都合がありました。

- ❌ **Windows 標準の音声入力は日本語の認識精度が弱い**
- ❌ **ファイル名の変更欄などに貼り付けられない**
- ❌ **クラウド型アプリではネット瞬断時に音声が消失して再発声が必要**

VoiceScribe はこれらを次の組み合わせで解決します。

- **whisper.cpp によるオフライン日本語認識**
- **Win32 SendInput** による貼り付け先非依存の入力
- **ローカル WAV 保存** による通信瞬断への耐性（F8 キーで再送可能）

<div align="right"><a href="#目次">▲ 目次へ戻る</a></div>

---

## 想定ユーザーと使用シーン

パソコンで事務作業を行う方が、以下の用途で使うことを想定しています。

- 業務メール文章の作成
- ファイル名、チャット欄などへの直接入力
- 生成 AI へのプロンプト入力
- 議事録の作成

**想定ワークフロー:** 1 日 200 回 × 1 回 10 秒以下の **短文作成** 型。長時間音声の文字起こしではなく、思いついたときにショートカットキーで素早く短文を入力する用途に最適化しています。

<div align="right"><a href="#目次">▲ 目次へ戻る</a></div>

---

## 特徴

1. **ショートカットで録音** — Pause キーで録音開始/終了(録音中は画面右下のツールバーにマイクマークが出ます)
2. **貼り付け先を選ばない** — Win32 SendInput 採用で、ファイル名やダイアログ等にも入力可能
3. **ネット瞬断に強い** — 音声はローカルに WAV ファイルで一時保存されるため通信失敗時も F8 キーで再送可能
4. **専門用語辞書による後処理置換** — `data/replacements.txt` に登録して誤認識を修正

<div align="right"><a href="#目次">▲ 目次へ戻る</a></div>

---

## 置換辞書のサンプル

`data/replacements.txt` に CSV 形式で登録します。実際の運用例を抜粋します。

```csv
# 医療系の同音異義語を補正
小児体,硝子体
焼死体,硝子体

# 漢数字をアラビア数字へ
二千二十六,2026
一,1

# 全角英数字を半角へ
Ａ,A
１,1

# 「1部」→「一部」などの誤字を補正
1部,一部
1旦,一旦

# 不要な疑問符を句点に
?,。
```

辞書はアプリ内の置換エディタから直接編集できます。

<div align="right"><a href="#目次">▲ 目次へ戻る</a></div>

---

## クイックスタート

### 1. リポジトリをクローン

```bash
git clone https://github.com/your-repo/VoiceScribe.git
cd VoiceScribe
```

### 2. 仮想環境の作成と依存パッケージのインストール

事前に [uv](https://docs.astral.sh/uv/getting-started/installation/) のインストールが必要です。

```bash
# 仮想環境の作成とパッケージのインストールを一度に行う
uv sync
```

仮想環境を有効化する：

```bash
# Windows (Command Prompt)
.venv\Scripts\activate.bat

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Mac / Linux
source .venv/bin/activate
```

### 3. whisper.cpp モデルを取得

```bash
python scripts/download_whisper_model.py
```

`config.ini` の `[WHISPERCPP] model_path` で指定された場所に `ggml-small.bin` が配置されます。

### 4. 起動

```bash
python main.py
```

起動後、Pause キーを押して録音 → 話す → Pause キーで停止すると、アクティブウィンドウへテキストが貼り付けられます。

<div align="right"><a href="#目次">▲ 目次へ戻る</a></div>

---

## 使い方

### キーボードショートカット

| キー | 機能                          |
|------|-----------------------------|
| Pause | 録音開始 / 停止                   |
| Esc | アプリケーション終了                  |
| **F8** | **直前の音声を再変換（ネット瞬断時の再送に使用）** |
| F9 | 句読点機能の有効 / 無効を切り替え          |

### 基本フロー

1. Pause キーを押して録音開始
2. マイクに向かって話す（デフォルトは最大 60 秒で自動停止）
3. Pause キーで停止(無発声で自動終了)
4. テキストが自動的にアクティブウィンドウへ貼り付けられる

ネット切断などで変換に失敗した場合は、**F8 キーで直前の音声を再送信** できます。音声データはローカルに保存されているため、発声し直す必要がありません。

<div align="right"><a href="#目次">▲ 目次へ戻る</a></div>

---

## 設計のポイント

### UIQueueProcessor の導入経緯

初期実装ではバックグラウンドスレッドから Tkinter を直接更新していたため、**原因不明のフリーズが頻発** していました。API 処理側を疑って試行錯誤しましたが改善せず、最終的にすべての UI 更新を `UIQueueProcessor.schedule_callback()` 経由に統一したところ、安定性が劇的に改善しました。Tkinter + バックグラウンドスレッド構成のアプリを作る方への落とし穴共有として記録しておきます。

### レイヤー構成

- **`app/`** — Tkinter UI レイヤー。`VoiceInputManager` がメインウィンドウを保持。全 UI 更新は `UIQueueProcessor` 経由
- **`service/`** — ビジネスロジック。`RecordingLifecycle` が `AudioRecorder` → `AudioFileManager` → `TranscriptionHandler` → `TextTransformer` → `ClipboardManager` → `paste_backend` のパイプラインを統合
- **`external_service/`** — 文字起こしバックエンド（whisper.cpp）
- **`utils/`** — 設定 (`AppConfig`)、ロギング、クラッシュログ、シグナル設定

<div align="right"><a href="#目次">▲ 目次へ戻る</a></div>

---

## 設定

### 主要な設定 (utils/config.ini)

| セクション | 用途 |
|-----------|------|
| `[TRANSCRIPTION]` | 文字起こしバックエンド (`whispercpp`) |
| `[WHISPERCPP]` | モデルパス、スレッド数 |
| `[KEYS]` | ショートカット割り当て |
| `[RECORDING]` | 自動停止タイマー（デフォルト 60 秒） |

その他のセクションは `config.ini` 内のコメントを参照してください。

<div align="right"><a href="#目次">▲ 目次へ戻る</a></div>

---

## 開発者向け情報

### テスト

```bash
python -m pytest tests/ -v --tb=short
python -m pytest tests/ -v --tb=short --cov=app --cov-report=html
```

### 型チェック

```bash
pyright app service utils
```

### 実行ファイルのビルド

```bash
python build.py
```

成果物は `dist/VoiceScribe.exe` に出力されます。

<div align="right"><a href="#目次">▲ 目次へ戻る</a></div>

---

## システム要件

- Windows 11
- Python 3.12 以上
- マイク入力デバイス
- whisper.cpp モデル (`ggml-small.bin`)

<div align="right"><a href="#目次">▲ 目次へ戻る</a></div>

---

## トラブルシューティング

### whisper.cpp モデルが読み込めない

- `config.ini` の `[WHISPERCPP] model_path` に指定したパスに `ggml-small.bin` が存在するか確認
- `python scripts/download_whisper_model.py` でモデルを取得

### 音声が録音されない

1. Windows の設定でマイクが有効か確認
2. 他のアプリがマイクを占有していないか確認
3. PyAudio の動作確認: `python -c "import pyaudio; print('OK')"`

### テキスト貼り付けが機能しない

1. `utils/config.ini` で `use_sendinput = True` を確認
2. 貼り付け先アプリが標準的なテキスト入力に対応しているか確認

<div align="right"><a href="#目次">▲ 目次へ戻る</a></div>

---

## バージョン情報

- **現在のバージョン**: 0.0.14
- **最終更新日**: 2026年04月22日

## ライセンス

ライセンス情報は [LICENSE](docs/LICENSE) を参照してください。

## 更新履歴

更新履歴は [CHANGELOG.md](docs/CHANGELOG.md) を参照してください。

## 免責事項

本ツールはローカルで動作する whisper.cpp を利用しており、音声データは外部サーバーへ送信されません。ただし、文字起こしの精度や誤認識に起因するいかなる損害についても、責任を負いかねます。

<div align="right"><a href="#目次">▲ 目次へ戻る</a></div>

