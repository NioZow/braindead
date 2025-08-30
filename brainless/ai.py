from pathlib import Path

from openai import OpenAI

from brainless.config import LITELLM_API_KEY, LITELLM_URI, OLLAMA_MODEL

assert OLLAMA_MODEL != "", "Missing OLLAMA_MODEL env variable"
assert LITELLM_URI != "", "Missing OLLAMA_MODEL env variable"
assert LITELLM_API_KEY != "", "Missing OLLAMA_MODEL env variable"


def convert_to_markdown(text: str):
    system_prompt_path = Path("./prompts/convert_to_markdown.md")
    if not system_prompt_path.exists():
        raise ValueError("System prompt not found")

    with open(system_prompt_path, "r") as f:
        system_prompt = f.read()

    client = OpenAI(
        base_url=LITELLM_URI,
        api_key=LITELLM_API_KEY,
    )

    response = client.chat.completions.create(
        model="gemini/gemini-2.5-flash-preview-05-20",
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": f"Please convert the provided content to markdown format : \n\n{text}",
            },
        ],
    )

    return response.choices[0].message.content


def sec_summary(resource: str, description: str):
    system_prompt_path = Path("./prompts/sec_summary.md")
    if not system_prompt_path.exists():
        raise ValueError("System prompt not found")

    with open(system_prompt_path, "r") as f:
        system_prompt = f.read()

    client = OpenAI(
        base_url=LITELLM_URI,
        api_key=LITELLM_API_KEY,
    )

    response = client.chat.completions.create(
        model="gemini/gemini-2.5-flash-preview-05-20",
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": f"""
<MAIN_CONTENT>
{resource}
</MAIN_CONTENT>

<SUPPLEMENTARY_INFO>
{description}
</SUPPLEMENTARY_INFO>
""",
            },
        ],
    )

    return response.choices[0].message.content


def ctbb_summary(transcript: str, description: str):
    system_prompt_path = Path("./prompts/ctbb_summary.md")
    if not system_prompt_path.exists():
        raise ValueError("System prompt not found")

    with open(system_prompt_path, "r") as f:
        system_prompt = f.read()

    client = OpenAI(
        base_url=LITELLM_URI,
        api_key=LITELLM_API_KEY,
    )

    response = client.chat.completions.create(
        model="gemini/gemini-2.5-flash-preview-05-20",
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": f"""
<TRANSCRIPT>
{transcript}
</TRANSCRIPT>

<DESCRIPTION>
{description}
</DESCRIPTION>
""",
            },
        ],
    )

    return response.choices[0].message.content
