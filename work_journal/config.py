import os
import sys
from configparser import ConfigParser
import subprocess

def is_valid_cmd(cmd):
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
    

config = ConfigParser()
config_file_path = os.path.abspath(os.path.dirname(__file__)) + "/config.ini"
config.read(config_file_path)

if not config["PREFERENCES"]["PYTHON"]:
    config.set("PREFERENCES", "PYTHON", sys.path[0])
    with open(config_file_path, "w") as configfile:
        config.write(configfile)
    
EDITOR_CMD = config["PREFERENCES"]["EDITOR"]
PYTHON_PATH = config["PREFERENCES"]["PYTHON"]
