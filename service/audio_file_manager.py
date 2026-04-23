import glob
import logging
import os
import wave
from datetime import datetime, timedelta
from typing import List, Optional

import numpy as np
import pyaudio

from utils.app_config import AppConfig


class AudioFileManager:
    """音声ファイルの保存と一時ファイルのクリーンアップを管理する"""

    def __init__(self, config: AppConfig):
        self._config = config

    def save_audio(self, frames: List[bytes], sample_rate: int) -> Optional[str]:
        """音声フレームをWAVファイルとして保存しパスを返す"""
        try:
            temp_dir = self._config.temp_dir
            os.makedirs(temp_dir, exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            temp_path = os.path.join(temp_dir, f'audio_{timestamp}.wav')

            raw_audio = b''.join(frames)
            processed_audio = self._trim_silence(raw_audio, sample_rate)

            with wave.open(temp_path, 'wb') as wf:
                wf.setnchannels(self._config.audio_channels)
                wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
                wf.setframerate(sample_rate)
                wf.writeframes(processed_audio)

            logging.info(f'音声ファイル保存完了: {temp_path}')
            return temp_path

        except Exception as e:
            logging.error(f'音声ファイル保存エラー: {str(e)}')
            return None

    def _trim_silence(self, raw_audio: bytes, sample_rate: int) -> bytes:
        """先頭と末尾の無音区間を振幅ベースで削除する"""
        if not self._config.vad_enabled or not raw_audio:
            return raw_audio

        samples = np.frombuffer(raw_audio, dtype=np.int16)
        if samples.size == 0:
            return raw_audio

        threshold = self._config.vad_silence_threshold
        window_size = max(1, sample_rate // 100)  # 10ms 窓
        window_count = samples.size // window_size
        if window_count == 0:
            return raw_audio

        windows = samples[: window_count * window_size].reshape(window_count, window_size)
        envelope = np.abs(windows).max(axis=1)
        active = np.where(envelope > threshold)[0]

        if active.size == 0:
            logging.info('無音のみ検出のため全音声を保持します')
            return raw_audio

        padding_windows = max(0, self._config.vad_padding_ms // 10)
        start_window = max(0, active[0] - padding_windows)
        end_window = min(window_count, active[-1] + 1 + padding_windows)

        start_sample = start_window * window_size
        end_sample = end_window * window_size
        trimmed = samples[start_sample:end_sample]

        original_ms = samples.size * 1000 // sample_rate
        trimmed_ms = trimmed.size * 1000 // sample_rate
        logging.info(f'無音トリミング: {original_ms}ms -> {trimmed_ms}ms')
        return trimmed.tobytes()

    def cleanup_temp_files(self) -> None:
        """保存期間を超えた一時ファイルを削除"""
        try:
            current_time = datetime.now()
            pattern = os.path.join(self._config.temp_dir, '*.wav')

            for file_path in glob.glob(pattern):
                file_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
                if current_time - file_modified > timedelta(minutes=self._config.cleanup_minutes):
                    try:
                        os.remove(file_path)
                        logging.info(f'古い音声ファイルを削除しました: {file_path}')
                    except Exception as e:
                        logging.error(f'ファイル削除中にエラーが発生しました: {file_path}, {e}')

        except Exception as e:
            logging.error(f'クリーンアップ処理中にエラーが発生しました: {e}')
