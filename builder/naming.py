"""
Naming
"""

import string
import json
import os
import re

_DEFAULT_CONFIG_PATH = os.path.join(
    os.path.dirname(__file__), "..", "config", "naming.json"
)


def load_naming_config_from_json(path=None):
    if path is None:
        path = _DEFAULT_CONFIG_PATH

    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        print(f"path {path} not found.")


def get_name(config, naming_values):

    rule = config.get("naming_rule")
    naming_tokens = config.get("naming_tokens", [])

    included = {}
    for token in string.Formatter().parse(rule):
        field_name = token[1]
        if field_name and field_name in naming_tokens:
            if field_name in naming_values:

                included[field_name] = naming_values[field_name]
            else:
                included[field_name] = ""
    name = rule.format(**included)
    name = re.sub(r"_+", "_", name)
    name = name.strip("_")
    return name
