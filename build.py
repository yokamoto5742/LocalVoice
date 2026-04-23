import subprocess


def build_executable() -> None:
    subprocess.run([
        "pyinstaller",
        "--clean",
        "--noconfirm",
        "--name=LocalVoice",
        "--windowed",
        "--icon=assets/LocalVoice.ico",
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

    print("Executable built successfully.")


if __name__ == "__main__":
    build_executable()
