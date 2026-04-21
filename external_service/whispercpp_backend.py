import logging
import os
import traceback
from typing import Any, Optional

from utils.app_config import AppConfig


class WhisperCppBackend:
    """whisper.cpp によるオフライン文字起こしバックエンド"""

    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._model: Optional[Any] = None
        self._model_path = config.whispercpp_model_path
        self._n_threads = config.whispercpp_n_threads

    def _ensure_model_loaded(self) -> None:
        if self._model is not None:
            return

        if not os.path.exists(self._model_path):
            raise FileNotFoundError(
                f'whisper.cpp モデルファイルが見つかりません: {self._model_path}\n'
                f'scripts/download_whisper_model.py でダウンロードしてください'
            )

        try:
            from pywhispercpp.model import Model
        except ImportError as e:
            raise ImportError(
                'pywhispercpp がインストールされていません。'
                'pip install pywhispercpp を実行してください'
            ) from e

        logging.info(f'whisper.cpp モデル読み込み開始: {self._model_path}')
        self._model = Model(
            self._model_path,
            n_threads=self._n_threads,
            language='ja',
            print_realtime=False,
            print_progress=False,
        )
        logging.info('whisper.cpp モデル読み込み完了')

    def transcribe(self, audio_file_path: str) -> Optional[str]:
        if not audio_file_path:
            logging.warning('音声ファイルパスが未指定です')
            return None

        if not os.path.exists(audio_file_path):
            logging.error(f'音声ファイルが存在しません: {audio_file_path}')
            return None

        if os.path.getsize(audio_file_path) == 0:
            logging.error('音声ファイルサイズが0バイトです')
            return None

        try:
            self._ensure_model_loaded()
            assert self._model is not None

            logging.info('whisper.cpp 文字起こし開始')
            segments = self._model.transcribe(audio_file_path)
            text_result = ''.join(segment.text for segment in segments).strip()

            if len(text_result) == 0:
                logging.warning('文字起こし結果が空です')
                return ''

            logging.info(f'文字起こし完了: {len(text_result)}文字')
            return text_result

        except FileNotFoundError as e:
            logging.error(str(e))
            return None
        except Exception as e:
            logging.error(f'whisper.cpp 文字起こしエラー: {str(e)}')
            logging.debug(f'詳細: {traceback.format_exc()}')
            return None
