from typing import Dict
from pathlib import Path

import yaml


def load_yaml_file(path_to_file: Path) -> Dict:
    """Loads and yaml from a file"""
    if not path_to_file.is_file():
        raise ValueError(
            f"Could not read yaml file '{str(path_to_file)}' because it was not found."
        )

    return yaml.safe_load(path_to_file.read_text())
