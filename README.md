# Braindead

This summarizes books, youtube videos and articles because I'm too lazy to take notes by myself.

## Installation

```sh
git clone git@gitea.emp:niozow/braindead.git
cd braindead
uv tool install .
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

### Kindle highlights parser

Parse kindle highlights create notes for a book out of it.

You can go at `https://read.amazon.com/notebook` and "Save Page as..." and then use the following command to parse and ingest it.

```sh
braindead highlight ~/Downloads/kindle.html --kindle
```
