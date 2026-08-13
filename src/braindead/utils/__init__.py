import re
import unicodedata
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from braindead.config import config

from .logger import logger


def convert_to_filename(name: str):
    """
    Convert a title into a filename. This removes bad characters like spaces, apostrophes...
    """
    return (
        re.sub(
            r"(\-{2,})",
            "-",
            re.sub(
                r"([\/:\.'\",|?<>])",
                "",
                unicodedata.normalize("NFD", name)
                .encode("ascii", "ignore")
                .decode("ascii")
                .lower()
                .replace(" ", "-")
                .replace("'", "-"),
            ),
        )
        + ".md"
    ).strip()


def write_notes(save_path: Path, response: Optional[str]):
    if response:
        with open(save_path, "w") as f:
            f.write(response)
        logger.info(f"Successfully written notes to {save_path}.")
    else:
        logger.fatal_error("No notes were generated.")


def format_duration(duration: timedelta) -> str:
    """Format duration in a verbose format (e.g., '1h 23m 45s')."""
    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")

    return " ".join(parts)


def get_save_path(title: str, publish_date: Optional[datetime | str] = None):
    formatted_date = ""
    if isinstance(publish_date, str):
        formatted_date = f"{publish_date}-"
    elif isinstance(publish_date, datetime):
        formatted_date = f"{publish_date.strftime('%Y-%m-%d')}-"

    return Path(config.notes_triage_location).expanduser().resolve() / (
        formatted_date + convert_to_filename(title)
    )


__all__ = ["logger"]
