# Braindead

This summarizes books, youtube videos and articles because I'm too lazy to take notes by myself.

## Installation

```sh
git clone git@gitea.emp:niozow/braindead.git
cd braindead
uv tool install .
```

You then need to set up a configuration file at `~/.config/braindead/config.yml`.

For example :

```sh
# yaml-language-server: $schema=https://raw.githubusercontent.com/NioZow/braindead/refs/heads/master/schemas/config.schema.json
youtube_api_key: "redacted"
litellm_uri: "https://api.openai.com/v1"
litellm_api_key: "redacted"
notes_triage_location: "~/notes/triage/"
```

## Features

```
usage: __main__.py [-h] [--dry-run] {highlight,save,summarize} ...

Braindead CLI to easily summarize things by AI.

positional arguments:
  {highlight,save,summarize}
                        Action to perform
    highlight           Get highlights from read books
    save                Save an article or video transcript
    summarize           Summarize an article or video transcript

options:
  -h, --help            show this help message and exit
  --dry-run, -d         Dry run
```

### Video/Article summarizer

```
$ braindead summarize -v https://www.youtube.com/watch?v=Le0DLrn7ta0
[+] Successfully written notes to ~/notes/triage/2025-12-16-a-deepdive-on-my-personal-ai-infrastructure-(pai-v20-december-2025).md.
```

### Kindle highlights summarizer

Summarize kindle highlights create notes for a book out of it.

You can go at `https://read.amazon.com/notebook` and "Save Page as..." and then use the following command to parse and ingest it.

```sh
braindead highlight ~/Downloads/kindle.html --kindle
```
