import sys
import types
from unittest.mock import Mock, patch

from external_service.whispercpp_backend import WhisperCppBackend
from tests.conftest import dict_to_app_config


def _make_config(model_path: str = '/test/model.bin', n_threads: int = 2):
    return dict_to_app_config({
        'WHISPERCPP': {'MODEL_PATH': model_path, 'N_THREADS': n_threads}
    })


def _install_fake_pywhispercpp(mock_model_class) -> None:
    """pywhispercpp をインストール済みに見せかける"""
    pkg = types.ModuleType('pywhispercpp')
    submodule = types.ModuleType('pywhispercpp.model')
    submodule.Model = mock_model_class
    pkg.model = submodule
    sys.modules['pywhispercpp'] = pkg
    sys.modules['pywhispercpp.model'] = submodule


class TestWhisperCppBackendInit:

    def test_init(self):
        """正常系: 初期化時はモデルをロードしない"""
        config = _make_config('/model.bin', 4)
        backend = WhisperCppBackend(config)

        assert backend._model is None
        assert backend._model_path == '/model.bin'
        assert backend._n_threads == 4


class TestWhisperCppBackendTranscribe:

    def setup_method(self):
        self.config = _make_config('/test/model.bin', 2)

    def test_transcribe_empty_path(self):
        """異常系: ファイルパスが空"""
        backend = WhisperCppBackend(self.config)
        assert backend.transcribe('') is None

    @patch('external_service.whispercpp_backend.os.path.exists')
    def test_transcribe_file_not_exists(self, mock_exists):
        """異常系: 音声ファイルが存在しない"""
        mock_exists.return_value = False
        backend = WhisperCppBackend(self.config)

        assert backend.transcribe('/not/found.wav') is None

    @patch('external_service.whispercpp_backend.os.path.getsize')
    @patch('external_service.whispercpp_backend.os.path.exists')
    def test_transcribe_zero_size(self, mock_exists, mock_getsize):
        """異常系: 0 バイトファイル"""
        mock_exists.return_value = True
        mock_getsize.return_value = 0
        backend = WhisperCppBackend(self.config)

        assert backend.transcribe('/empty.wav') is None

    @patch('external_service.whispercpp_backend.os.path.getsize')
    @patch('external_service.whispercpp_backend.os.path.exists')
    def test_transcribe_model_missing(self, mock_exists, mock_getsize):
        """異常系: モデルファイルが存在しない"""
        # 音声ファイルは存在、モデルファイルは存在しない
        def exists_side_effect(path: str) -> bool:
            return path == '/audio.wav'

        mock_exists.side_effect = exists_side_effect
        mock_getsize.return_value = 1024
        backend = WhisperCppBackend(self.config)

        assert backend.transcribe('/audio.wav') is None

    @patch('external_service.whispercpp_backend.os.path.getsize')
    @patch('external_service.whispercpp_backend.os.path.exists')
    def test_transcribe_success(self, mock_exists, mock_getsize):
        """正常系: 文字起こし成功"""
        mock_exists.return_value = True
        mock_getsize.return_value = 1024

        segment1 = Mock()
        segment1.text = 'こんにちは'
        segment2 = Mock()
        segment2.text = '世界'
        mock_model_instance = Mock()
        mock_model_instance.transcribe.return_value = [segment1, segment2]
        mock_model_class = Mock(return_value=mock_model_instance)
        _install_fake_pywhispercpp(mock_model_class)

        backend = WhisperCppBackend(self.config)
        result = backend.transcribe('/audio.wav')

        assert result == 'こんにちは世界'
        assert mock_model_class.call_count == 1
        args, kwargs = mock_model_class.call_args
        assert args == ('/test/model.bin',)
        assert kwargs['n_threads'] == 2
        assert kwargs['language'] == 'ja'
        assert kwargs['print_realtime'] is False
        assert kwargs['print_progress'] is False
        assert mock_model_instance.transcribe.call_count == 1
        call_args, _ = mock_model_instance.transcribe.call_args
        assert call_args == ('/audio.wav',)

    @patch('external_service.whispercpp_backend.os.path.getsize')
    @patch('external_service.whispercpp_backend.os.path.exists')
    def test_transcribe_model_loaded_once(self, mock_exists, mock_getsize):
        """正常系: モデルは1度だけロードされる"""
        mock_exists.return_value = True
        mock_getsize.return_value = 1024

        segment = Mock()
        segment.text = 'テスト'
        mock_model_instance = Mock()
        mock_model_instance.transcribe.return_value = [segment]
        mock_model_class = Mock(return_value=mock_model_instance)
        _install_fake_pywhispercpp(mock_model_class)

        backend = WhisperCppBackend(self.config)
        backend.transcribe('/audio1.wav')
        backend.transcribe('/audio2.wav')

        assert mock_model_class.call_count == 1
        assert mock_model_instance.transcribe.call_count == 2

    @patch('external_service.whispercpp_backend.os.path.getsize')
    @patch('external_service.whispercpp_backend.os.path.exists')
    def test_transcribe_empty_segments(self, mock_exists, mock_getsize):
        """正常系: セグメントが空の場合は空文字を返す"""
        mock_exists.return_value = True
        mock_getsize.return_value = 1024

        mock_model_instance = Mock()
        mock_model_instance.transcribe.return_value = []
        _install_fake_pywhispercpp(Mock(return_value=mock_model_instance))

        backend = WhisperCppBackend(self.config)
        assert backend.transcribe('/audio.wav') == ''

    @patch('external_service.whispercpp_backend.os.path.getsize')
    @patch('external_service.whispercpp_backend.os.path.exists')
    def test_transcribe_raises_exception(self, mock_exists, mock_getsize):
        """異常系: 推論中に例外発生"""
        mock_exists.return_value = True
        mock_getsize.return_value = 1024

        mock_model_instance = Mock()
        mock_model_instance.transcribe.side_effect = RuntimeError('推論エラー')
        _install_fake_pywhispercpp(Mock(return_value=mock_model_instance))

        backend = WhisperCppBackend(self.config)
        assert backend.transcribe('/audio.wav') is None
