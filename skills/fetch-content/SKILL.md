---
name: fetch-content
description: Fetch content from articles, YouTube videos, and Kindle highlights with full metadata
license: MIT
metadata:
  audience: agents
  workflow: content
---

# Content Fetcher

Specialized skill for fetching content and metadata from articles, YouTube videos, and Kindle highlights. This skill provides raw content and metadata for downstream processing.

## When to Load This Skill

Load this skill when an agent needs to:

- Fetch an article's text and metadata
- Get a YouTube video transcript and metadata
- Extract Kindle highlights from an HTML file
- Obtain raw content before summarization or analysis

**Trigger phrases**:

- "fetch this article"
- "get this video transcript"
- "extract highlights"
- "download content"
- "get metadata"
- User provides URL and asks for raw content

## How to Use This Skill

### From the CLI (braindead)

```bash
# Fetch article
braindead fetch <url> --article --json

# Fetch video transcript
braindead fetch <url> --video --json

# Fetch Kindle highlights
braindead fetch --file <path> --highlights --json
```

### From Python

```python
from braindead.fetchers import fetch_article, fetch_video
from braindead.parsers import parse_kindle_highlights

# Article
content = fetch_article("https://example.com/article")
print(content.title, content.text)

# Video
content = fetch_video("https://youtube.com/watch?v=...")
print(content.transcript, content.title)

# Kindle highlights
title, author, highlights = parse_kindle_highlights(Path("kindle.html"))
```

## Output Schemas

### Article

```json
{
  "url": "string",
  "title": "string",
  "text": "string",
  "authors": ["string"],
  "publish_date": "ISO-8601 datetime or null",
  "top_image": "string or null"
}
```

### Video

```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "publish_date": "ISO-8601 datetime",
  "transcript": "string",
  "channel": "string",
  "duration_seconds": 1234
}
```

### Highlights

```json
{
  "title": "string",
  "author": "string",
  "highlights": ["string"]
}
```

## Integration Notes

- Use `--json` flag for machine-readable output
- Works seamlessly with `summarize-resource`, `summarize-story`, and `summarize-highlights` skills
- Can be chained: fetch content -> pass to AI for summarization
- All fetchers handle errors gracefully and return structured data
