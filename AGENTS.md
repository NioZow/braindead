# Braindead — Agent Guide

This document helps OpenCode agents understand and use the braindead project effectively.

## What is Braindead?

Braindead is a CLI tool and skill collection for fetching, processing, and summarizing content (articles, YouTube videos, Kindle highlights) using AI. It is designed to be used both by humans (via CLI) and by agents (via skills and Python API).

## Architecture

```
braindead/
├── src/braindead/          # Core Python library
│   ├── __main__.py         # CLI entry point
│   ├── ai.py               # AI assistant wrappers (OpenAI-compatible)
│   ├── config.py           # Configuration loading
│   ├── fetchers.py         # Content fetchers (article, video)
│   ├── parsers.py          # Content parsers (Kindle highlights)
│   ├── models.py           # Pydantic models
│   ├── utils/              # Utilities (logger, file ops)
│   └── prompts/            # Jinja2 prompt templates
├── skills/                 # OpenCode skills
│   ├── fetch-content/      # Fetch raw content and metadata
│   ├── summarize-resource/ # Summarize articles/videos into notes
│   ├── summarize-story/    # Summarize podcasts/stories into notes
│   ├── summarize-highlights/ # Summarize Kindle highlights into notes
│   └── convert-to-markdown/  # Convert text to clean markdown
└── schemas/                # JSON schemas
```

## Configuration

Braindead requires a config file at `~/.config/braindead/config.yml`:

```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/NioZow/braindead/refs/heads/master/schemas/config.schema.json
youtube_api_key: "your-youtube-api-key"
openai_uri: "https://api.openai.com/v1"
openai_api_key: "your-api-key"
model: "gemini-2.5-flash"
notes_triage_location: "~/notes/triage/"
```

## Using Braindead as an Agent

### Option 1: Use the Skills

The `skills/` folder contains OpenCode-compatible skill definitions. Load them when you need to:

- **fetch-content**: Get raw content + metadata from URLs or files
- **summarize-resource**: Convert articles/videos into structured reference notes
- **summarize-story**: Convert podcast episodes into story-focused notes
- **summarize-highlights**: Convert Kindle highlights into book notes
- **convert-to-markdown**: Clean up and format text as markdown

### Option 2: Use the CLI

```bash
# Fetch content (use --json for machine-readable output)
braindead fetch <url> --article --json
braindead fetch <url> --video --json
braindead fetch --file <path> --highlights --json

# Summarize content
braindead summarize <url> --article --template resource
braindead summarize <url> --video --template story

# Process highlights
braindead highlight <file> --kindle

# Save as markdown
braindead save <url> --article
braindead save <url> --video

# Dry run (see the prompt without calling AI)
braindead --dry-run summarize <url> --article
```

### Option 3: Use the Python API

```python
from braindead.fetchers import fetch_article, fetch_video
from braindead.parsers import parse_kindle_highlights
from braindead.ai import summarize_resource, summarize_story, summarize_highlight, convert_to_markdown
from braindead.config import get_save_path
from braindead.utils import write_notes

# Fetch
article = fetch_article("https://example.com")
video = fetch_video("https://youtube.com/watch?v=...")

# Summarize
notes = summarize_resource(
    main_content=article.text,
    title=article.title,
    author=article.authors[0],
    content_type="Article",
    url=article.url,
)

# Save
path = get_save_path(article.title, article.publish_date)
write_notes(path, notes)
```

## Key Design Principles

1. **JSON-first for agents**: All CLI commands support `--json` for structured output
2. **Composable**: Fetch -> Process -> Save is a clean pipeline
3. **Skill-native**: Prompts and workflows are exposed as OpenCode skills
4. **Python API first**: Core functionality is importable from `braindead.fetchers`, `braindead.parsers`, and `braindead.ai`

## Adding New Skills

To add a new skill:

1. Create a directory under `skills/<skill-name>/`
2. Add a `SKILL.md` with proper YAML frontmatter
3. Reference the braindead Python API or CLI in the skill instructions
4. Update this AGENTS.md

## Installing Skills for OpenCode

To make braindead skills available to OpenCode agents:

```bash
./bin/install-skills
```

This symlinks all skills from `skills/` into `~/.config/opencode/skills/`.

## Testing

```bash
# Install in dev mode
uv tool install -e .

# Run a dry-run to test prompts
braindead --dry-run summarize <url> --article

# Test fetching
braindead fetch <url> --article --json
```
