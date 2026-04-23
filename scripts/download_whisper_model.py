"""whisper.cpp small モデルを既定のパスにダウンロードするスクリプト"""
import os
import sys
import urllib.request

MODEL_URL = 'https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo-q5_0.bin'
DEFAULT_MODEL_PATH = r'C:\Shinseikai\VoiceScribe\models\ggml-large-v3-turbo-q5_0.bin'


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


def download_model(dest_path: str = DEFAULT_MODEL_PATH) -> None:
    if os.path.exists(dest_path):
        print(f'既にモデルが存在します: {dest_path}')
        return

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    print(f'ダウンロード元: {MODEL_URL}')
    print(f'保存先: {dest_path}')

    urllib.request.urlretrieve(MODEL_URL, dest_path, _report_progress)
    print('\nダウンロード完了')


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MODEL_PATH
    download_model(path)
