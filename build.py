import subprocess

from scripts.version_manager import update_version


def build_executable() -> str:
    new_version = update_version()

    subprocess.run([
        "pyinstaller",
        "--clean",
        "--noconfirm",
        "--name=VoiceScribe",
        "--windowed",
        "--icon=assets/VoiceScribe.ico",
        "--add-data", "utils/config.ini:.",
        "--add-data", "data/replacements.txt:.",
        "--collect-all", "numpy",
        "--add-binary", ".venv/Lib/site-packages/numpy.libs/*.dll:numpy.libs",
        "--hidden-import", "numpy.core._multiarray_umath",
        "--hidden-import", "numpy.core._multiarray_tests",
        "--collect-all", "pywhispercpp",
        "--collect-binaries", "pywhispercpp",
        "--collect-submodules", "pywhispercpp",
        "--collect-data", "pywhispercpp",
        "--hidden-import", "pywhispercpp",
        "--hidden-import", "pywhispercpp.model",
        "--hidden-import", "_pywhispercpp",
        "main.py"
    ])

    print(f"Executable built successfully. Version: {new_version}")
    return new_version


if __name__ == "__main__":
    build_executable()