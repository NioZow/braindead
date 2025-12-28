import re
from pathlib import Path
from typing import List

from lxml import html


def clean_highlight(text):
    """Clean highlight text for markdown list formatting."""
    return re.sub(r"[\x00-\x1f\x7f-\x9f]", "", re.sub(r"\s+", " ", text)).strip()


def parse_kindle_highlights(file: Path) -> tuple[str, str, List[str]]:
    """Get highlights from a kindle html file and ask an AI assistant to summarize it for my notes.

    Args:
        file: Path to the kindle file.

    Returns:
        Title of the book, its author and its highlights
    """
    # open the html file containing highlights and parse it
    with open(file, "r") as f:
        tree = html.parse(f)

    highlight_nodes = tree.xpath(
        '//div[contains(@class, "kp-notebook-highlight")]//span[@id="highlight"]'
    )

    title = (
        tree.xpath(
            "/html/body/div[1]/div[3]/div/div[2]/div/div/div[1]/div/div/div[1]/div[2]/h3"
        )[0]
        .text_content()
        .strip()
    )

    author = (
        tree.xpath(
            "/html/body/div[1]/div[3]/div/div[2]/div/div/div[1]/div/div/div[1]/div[2]/p[2]"
        )[0]
        .text_content()
        .strip()
    )

    # extract highlights
    highlights = [
        clean
        for node in highlight_nodes
        if (clean := clean_highlight(node.text_content()))
    ]

    return title, author, highlights
