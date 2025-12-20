import re
from pathlib import Path

from jinja2 import Template
from lxml import html
from openai import OpenAI

from brainless.config import LITELLM_API_KEY, LITELLM_URI, PROMPT_PATH


def clean_highlight(text):
    """Clean highlight text for markdown list formatting."""
    # Replace various whitespace characters with a single space
    text = re.sub(r"\s+", " ", text)
    # Remove any remaining control characters
    text = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", text)
    # Strip leading/trailing whitespace
    text = text.strip()
    return text


def convert_to_filename(text: str):
    return re.sub(r"'", "", text.replace(" ", "-")).strip()


def get_kindle_highlights(file: Path, dry_run: bool = False):
    """Get highlights from a kindle html file and ask an AI assistant to summarize it for my notes.

    Args:
        file: Path to the kindle file.
        dry_run: Only show the prompt, do not make the AI assistant request.
    """
    assert LITELLM_URI != "", "Missing LITELLM_URI env variable"
    assert LITELLM_API_KEY != "", "Missing LITELLM_API_KEY env variable"

    highlights = []

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

    # Load the template
    with open(PROMPT_PATH / "highlight.md", "r") as f:
        template = Template(f.read())

    # Render the prompt
    prompt = template.render(
        book_title=title,
        book_author=author,
        highlights="\n\n".join([f"- {h}" for h in highlights]),
    )

    print(f'Found {len(highlights)} highlights for "{title}" by {author}.')

    if dry_run:
        print(f"Dry run:\n{prompt}")
        return

    client = OpenAI(
        base_url=LITELLM_URI,
        api_key=LITELLM_API_KEY,
    )

    response = client.chat.completions.create(
        model="gemini/gemini-2.5-flash",
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    notes = response.choices[0].message.content
    if notes:
        with open(f"{convert_to_filename(title)}.md", "w") as f:
            f.write(notes)
    else:
        print("Assistant did not return anything.")
