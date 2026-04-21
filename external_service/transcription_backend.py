from typing import Optional, Protocol


class TranscriptionBackend(Protocol):
    """文字起こしバックエンドのインターフェース"""

    def transcribe(self, audio_file_path: str) -> Optional[str]:
        """音声ファイルを文字起こししてテキストを返す"""
        ...
