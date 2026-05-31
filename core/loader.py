import json
import os


def load_config_from_json(path=None):
    if path is None:
        raise IOError

    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        print(f"path {path} not found.")
