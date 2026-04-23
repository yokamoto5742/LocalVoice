import logging
import os
import sys
import threading
import traceback
from typing import Any, Optional

from utils.app_config import AppConfig


class WhisperCppBackend:
    """whisper.cpp によるオフライン文字起こしバックエンド"""

    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._model: Optional[Any] = None
        self._model_lock = threading.Lock()
        self._model_path = config.whispercpp_model_path
        self._n_threads = config.whispercpp_n_threads
        self._initial_prompt = self._load_initial_prompt()
        self._inference_params = self._build_inference_params()

    def _load_initial_prompt(self) -> str:
        prompt_file = self._config.whispercpp_initial_prompt_file
        if not prompt_file:
            return ''
        path = self._resolve_prompt_path(prompt_file)
        if not os.path.exists(path):
            logging.warning(f'initial_prompt ファイルが見つかりません: {path}')
            return ''
        try:
            with open(path, encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            logging.warning(f'initial_prompt ファイル読み込み失敗: {e}')
            return ''

    @staticmethod
    def _resolve_prompt_path(prompt_file: str) -> str:
        if os.path.isabs(prompt_file):
            return prompt_file
        if getattr(sys, 'frozen', False):
            base = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        else:
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base, prompt_file)

    def _build_inference_params(self) -> dict:
        params: dict = {
            'language': 'ja',
            'n_threads': self._n_threads,
            'print_realtime': False,
            'print_progress': False,
            'beam_size': self._config.whispercpp_beam_size,
            'best_of': self._config.whispercpp_best_of,
            'no_speech_thold': self._config.whispercpp_no_speech_thold,
            'logprob_thold': self._config.whispercpp_logprob_thold,
            'temperature': self._config.whispercpp_temperature,
            'suppress_blank': self._config.whispercpp_suppress_blank,
            'single_segment': self._config.whispercpp_single_segment,
        }
        if self._initial_prompt:
            params['initial_prompt'] = self._initial_prompt
        return params

    def preload(self) -> None:
        """モデルをバックグラウンドで事前ロードする"""
        try:
            self._ensure_model_loaded()
        except Exception as e:
            logging.warning(f'モデル事前ロード失敗: {e}')

    def _ensure_model_loaded(self) -> None:
        if self._model is not None:
            return

        with self._model_lock:
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
                logging.error(f'pywhispercpp の読み込みに失敗: {e}')
                logging.debug(f'詳細: {traceback.format_exc()}')
                raise ImportError(
                    f'pywhispercpp の読み込みに失敗しました: {e}. '
                    'ビルド済み実行ファイルの場合、ネイティブ DLL が同梱されていない可能性があります'
                ) from e

            logging.info(f'whisper.cpp モデル読み込み開始: {self._model_path}')
            model = self._construct_model(Model, self._inference_params)
            self._model = model
            logging.info('whisper.cpp モデル読み込み完了')

    def _construct_model(self, model_cls: Any, params: dict) -> Any:
        """pywhispercpp バージョン差異を吸収して Model を生成する"""
        try:
            return model_cls(self._model_path, **params)
        except TypeError as e:
            logging.warning(f'全パラメータ指定で Model 生成失敗、最小構成で再試行: {e}')
            minimal = {
                'language': params.get('language', 'ja'),
                'n_threads': params.get('n_threads', self._n_threads),
                'print_realtime': False,
                'print_progress': False,
            }
            return model_cls(self._model_path, **minimal)

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
            segments = self._invoke_transcribe(audio_file_path)
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

    def _invoke_transcribe(self, audio_file_path: str) -> Any:
        """transcribe 呼び出し時に追加パラメータを渡す(バージョン差異吸収)"""
        assert self._model is not None
        call_params = {
            k: v for k, v in self._inference_params.items()
            if k in ('beam_size', 'best_of', 'no_speech_thold', 'logprob_thold',
                     'temperature', 'suppress_blank', 'single_segment', 'initial_prompt')
        }
        try:
            return self._model.transcribe(audio_file_path, **call_params)
        except TypeError:
            return self._model.transcribe(audio_file_path)
