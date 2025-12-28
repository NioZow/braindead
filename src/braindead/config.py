"""
Load configuration files.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import yaml

from .models import Config
from .utils import convert_to_filename, logger

PROJECT_DIR = Path(sys.argv[0]).resolve().parent / ".." / ".."
PROMPT_DIR = PROJECT_DIR / "prompts"

DATA_DIRECTORY = Path("~/.local/share/braindead/").expanduser()
LOG_FILE = DATA_DIRECTORY / "contaibox.log"

CONFIG_DIRECTORY = Path("~/.config/braindead").expanduser()

os.makedirs(str(DATA_DIRECTORY), exist_ok=True)


def load_yaml_config(config_path: Path) -> Any:
    # load the config
    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
            return config
    except FileNotFoundError:
        logger.fatal_error(f"File {config_path} does not exist.")
    except yaml.YAMLError as e:
        logger.fatal_error(f"Failed to parse config of {config_path}: {e}.")


def load_config() -> Config:
    """Load the global configuration"""
    config_path = Path(CONFIG_DIRECTORY / "config.yml")
    return Config(**load_yaml_config(config_path))


config = load_config()


def get_save_path(title: str, publish_date: Optional[datetime | str] = None):
    formatted_date = ""
    if isinstance(publish_date, str):
        formatted_date = f"{publish_date}-"
    elif isinstance(publish_date, datetime):
        formatted_date = f"{publish_date.strftime('%Y-%m-%d')}-"

    return Path(config.notes_triage_location).expanduser().resolve() / (
        formatted_date + convert_to_filename(title)
    )
