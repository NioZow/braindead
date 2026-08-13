"""
Load configuration files.
"""

import os
from pathlib import Path
from typing import Any

import yaml

from .models import Config

PROJECT_DIR = Path(__file__).resolve().parent
PROMPT_DIR = PROJECT_DIR / "prompts"

DATA_DIRECTORY = Path("~/.local/share/braindead/").expanduser()
LOG_FILE = DATA_DIRECTORY / "braindead.log"

CONFIG_DIRECTORY = Path("~/.config/braindead").expanduser()

os.makedirs(str(DATA_DIRECTORY), exist_ok=True)


def load_yaml_config(config_path: Path) -> Any:
    # load the config
    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
            return config
    except FileNotFoundError:
        print(f"File {config_path} does not exist.")
    except yaml.YAMLError as e:
        print(f"Failed to parse config of {config_path}: {e}.")


def load_config() -> Config:
    """Load the global configuration"""
    config_path = Path(CONFIG_DIRECTORY / "config.yml")
    return Config(**load_yaml_config(config_path))


config = load_config()
