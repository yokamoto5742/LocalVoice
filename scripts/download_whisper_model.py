"""whisper.cpp モデルを config.ini の model_path にダウンロードするスクリプト"""
import sys
import os
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.app_config import AppConfig
from utils.config_manager import load_config

MODEL_URL = 'https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo-q5_0.bin'


def _get_default_model_path() -> str:
    return AppConfig(load_config()).whispercpp_model_path


def _report_progress(block_num: int, block_size: int, total_size: int) -> None:
    downloaded = block_num * block_size
    if total_size <= 0:
        sys.stdout.write(f'\rダウンロード中: {downloaded / 1024 / 1024:.1f} MB')
    else:
        percent = min(100.0, downloaded * 100 / total_size)
        sys.stdout.write(
            f'\rダウンロード中: {percent:5.1f}% '
            f'({downloaded / 1024 / 1024:.1f} / {total_size / 1024 / 1024:.1f} MB)'
        )
    sys.stdout.flush()


def download_model(dest_path: str) -> None:
    if os.path.exists(dest_path):
        print(f'既にモデルが存在します: {dest_path}')
        return

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    print(f'ダウンロード元: {MODEL_URL}')
    print(f'保存先: {dest_path}')

    urllib.request.urlretrieve(MODEL_URL, dest_path, _report_progress)
    print('\nダウンロード完了')


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else _get_default_model_path()
    download_model(path)
