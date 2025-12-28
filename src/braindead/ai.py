from datetime import datetime
from pathlib import Path
from typing import List, Optional

from jinja2 import Template
from openai import OpenAI

from braindead.config import PROMPT_DIR, config


def ask_ai_assistant(
    prompt_path: Path,
    model: str = "gemini/gemini-2.5-flash",
    dry_run: bool = False,
    **kwargs,
) -> Optional[str]:
    """Ask an AI assistant for a response to a given prompt and data

    Args:
        prompt_path: Path to the markdown jinja2 template user prompt file to use.
        model: Model for the AI assistant to use. The default is set to gemini-2.5-flash because it is performant, affordable and has a LARGE context windows.
        dry_run: If enabled, this will not send the prompt to the AI assistant and instead print it.
        **kwargs: Argument mapping to pass to the jinja2 template.

    Returns:
        Response of the AI assistant, if any.
    """

    client = OpenAI(
        base_url=config.litellm_uri,
        api_key=config.litellm_api_key,
    )

    # load the template
    with open(prompt_path) as f:
        template = Template(f.read())

    # render the prompt
    prompt = template.render(**kwargs)

    if dry_run:
        print(f"Dry run:\n{prompt}")
        return

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    return response.choices[0].message.content


def convert_to_markdown(text: str, **kwargs) -> Optional[str]:
    return ask_ai_assistant(PROMPT_DIR / "convert_to_markdown.md", input=text, **kwargs)


def summarize_resource(
    main_content: str,
    title: str,
    author: str,
    content_type: str,
    url: str,
    publish_date: Optional[datetime | str] = None,
    supplementary_info: Optional[str] = None,
    **kwargs,
):
    formatted_date = ""
    if isinstance(publish_date, str):
        formatted_date = publish_date
    elif isinstance(publish_date, datetime):
        formatted_date = publish_date.strftime("%Y-%m-%d")

    return ask_ai_assistant(
        PROMPT_DIR / "summarize_resource.md",
        title=title,
        author=author,
        content_type=content_type,
        url=url,
        main_content=main_content,
        supplementary_info=supplementary_info,
        publish_date=formatted_date,
        **kwargs,
    )


def summarize_highlight(title: str, author: str, highlights: List[str], **kwargs):
    return ask_ai_assistant(
        PROMPT_DIR / "summarize_highlight.md",
        title=title,
        author=author,
        highlights="\n\n".join([f"- {h}" for h in highlights]),
        **kwargs,
    )
