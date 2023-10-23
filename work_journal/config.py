import os
from configparser import ConfigParser
import subprocess


def is_valid_cmd(cmd: str):
    try:
        subprocess.run(
            ["which", cmd],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def _find_path(cmd: str):
    return subprocess.run(["which", cmd], capture_output=True, text=True).stdout


config_file = ConfigParser()
config_file_path = os.path.abspath(os.path.dirname(__file__)) + "/config.ini"
config_file.read(config_file_path)

if not config_file["PREFERENCES"]["PYTHON"]:
    if is_valid_cmd("python"):
        python_path = _find_path("python")
    elif is_valid_cmd("python3"):
        python_path = _find_path("python3")

    config_file.set("PREFERENCES", "PYTHON", python_path)
    with open(config_file_path, "w") as configfile:
        config_file.write(configfile)

EDITOR_CMD = config_file["PREFERENCES"]["EDITOR"]
PYTHON_PATH = config_file["PREFERENCES"]["PYTHON"]
