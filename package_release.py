"""
Entire release creation - EXE.
Must use virtual environment, ensure Pyinstaller is installed.
"""
import os
import pathlib
import shutil
import subprocess


FOLDER = pathlib.Path(__file__).parent
VENV_SCRIPTS_FOLDER = FOLDER / "Scripts"
RELEASE_FOLDER = FOLDER / "release"
if RELEASE_FOLDER.is_dir():
    shutil.rmtree(RELEASE_FOLDER)
RELEASE_FOLDER.mkdir()

CODE_PACKAGE_FOLDER = RELEASE_FOLDER / "code"
CODE_PACKAGE_ZIP = RELEASE_FOLDER / "code"

ICON = FOLDER / "icon.ico"
START_SCRIPT = FOLDER / "src" / "main.py"

ADDITIONAL_DATA = {
    FOLDER / "icon.ico": "."
}
OUTPUT_EXE_NAME = RELEASE_FOLDER / "parkrunscraper.exe"


def package_exe() -> None:
    """Packages standalone EXE, ready to run."""
    # Turn on virtual environment.
    subprocess.run((str(VENV_SCRIPTS_FOLDER / "activate.bat"),))
    # Build command parts.
    command_parts = [
        str(VENV_SCRIPTS_FOLDER / "pyinstaller"),
        str(START_SCRIPT), "--noconfirm", "--onefile",
        "--windowed",  "--icon", str(ICON)]
    for add_data_src, add_data_dest in ADDITIONAL_DATA.items():
        command_parts.append("--add-data")
        command_parts.append(f"{add_data_src};{add_data_dest}")
    # Run Pyinstaller.
    os.chdir(RELEASE_FOLDER)
    subprocess.run(command_parts)
    # Renames output EXE.
    output_exe = RELEASE_FOLDER / "dist" / f"{START_SCRIPT.stem}.exe"
    output_exe.rename(OUTPUT_EXE_NAME)
    # Deletes Pyinstaller files and folders.
    (RELEASE_FOLDER / "dist").rmdir()
    shutil.rmtree(RELEASE_FOLDER / "build")
    (RELEASE_FOLDER / f"{START_SCRIPT.stem}.spec").unlink(True)


if __name__ == "__main__":
    package_exe()
