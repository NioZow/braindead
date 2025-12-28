import re
import unicodedata
from pathlib import Path
from typing import Optional

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
                r"([\/:\.'\",|?])",
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


__all__ = ["logger"]
