# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run all tests
python -m pytest tests/ -v --tb=short

# Run a single test file
python -m pytest tests/service/test_audio_recorder.py -v

# Run a single test
python -m pytest tests/service/test_audio_recorder.py::TestAudioRecorder::test_method_name -v

# Run tests with coverage
python -m pytest tests/ -v --tb=short --cov=app --cov-report=html

# Type check
pyright app service utils

# Build executable
python build.py
```

## Architecture

LocalVoice is a Windows desktop app that records microphone input, transcribes it locally via whisper.cpp, and pastes the result into the active window. Entry point: `main.py`.

**Layers (top to bottom):**

- `app/` — Tkinter UI. `VoiceInputManager` (main_window.py) owns the window. All cross-thread UI updates go through `UIQueueProcessor.schedule_callback()`.
- `service/` — Business logic. `RecordingLifecycle` orchestrates the full pipeline via callbacks: `AudioRecorder` → `AudioFileManager` → `TranscriptionHandler` → `TextTransformer` → `ClipboardManager` → `paste_backend`.
- `external_service/` — 文字起こしバックエンド。`TranscriptionBackend` プロトコルと `WhisperCppBackend`（オフライン、pywhispercpp 経由）を提供。
- `utils/` — Config loading (`AppConfig` wraps `config.ini`), logging, crash/signal setup.

**Threading model:** Audio capture and transcription run in background threads. UI updates must be queued via `UIQueueProcessor`; never update Tkinter directly from a non-main thread.

**Configuration:** `utils/config.ini` controls audio settings, whisper.cpp model path、keyboard shortcuts, auto-stop timer, paste backend, and paths.

**オフライン文字起こし:** `python scripts/download_whisper_model.py` で `ggml-small.bin` を取得。日本語固定、CPU 推論。

**Text replacement:** `data/replacements.txt` (CSV) defines post-transcription substitutions applied by `TextTransformer`.