import argparse
import json
from pathlib import Path
from typing import Any

from braindead.ai import (
    convert_to_markdown,
    summarize_highlight,
    summarize_resource,
    summarize_story,
)
from braindead.config import get_save_path
from braindead.fetchers import fetch_article, fetch_video
from braindead.parsers import parse_kindle_highlights
from braindead.utils import logger, write_notes

class Dispatcher:
    @staticmethod
    def dispatch(args):
        try:
            if (func := globals().get(args.action)) is not None:
                func(args)
            else:
                logger.fatal_error(
                    f"Command {args.action} has not yet been developed."
                )
        except Exception as e:
            logger.error("Unexpected error.")
            raise e

def fetch(args):
    """Fetch content and output it, optionally as JSON."""
    data = None
    if args.article:
        content = fetch_article(args.url)
        data = {
            "url": content.url,
            "title": content.title,
            "text": content.text,
            "authors": content.authors,
            "publish_date": str(content.publish_date) if content.publish_date else None,
            "top_image": content.top_image,
        }
    elif args.video:
        content = fetch_video(args.url)
        data = {
            "id": content.id,
            "title": content.title,
            "description": content.description,
            "publish_date": str(content.publish_date),
            "transcript": content.transcript,
            "channel": content.channel,
            "duration_seconds": content.duration.total_seconds(),
        }
    elif args.highlights:
        title, author, highlights = parse_kindle_highlights(args.file)
        data = {
            "title": title,
            "author": author,
            "highlights": highlights,
        }
    else:
        return

    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        # Default output is the main text content
        print(data.get("text") or data.get("transcript") or "\n\n".join(data.get("highlights", [])))

def save(args):
    if args.article:
        content = fetch_article(args.url)
        text = content.text
        title = content.title
        publish_date = content.publish_date
    elif args.video:
        content = fetch_video(args.url)
        text = content.transcript
        title = content.title
        publish_date = content.publish_date
    else:
        return

    response = convert_to_markdown(text, dry_run=args.dry_run)

    if args.json:
        print(json.dumps({"title": title, "content": response}, indent=2, ensure_ascii=False))
        return

    save_path = get_save_path(title, publish_date)
    write_notes(save_path, response)

def summarize(args):
    if args.article:
        content = fetch_article(args.url)
        text = content.text
        title = content.title
        publish_date = content.publish_date
        author = content.authors[0] if content.authors else "Unknown"
        content_type = "Article"
        supplementary_info = None
        duration = None
    elif args.video:
        content = fetch_video(args.url)
        text = content.transcript
        title = content.title
        author = content.channel
        publish_date = content.publish_date
        content_type = "Video"
        supplementary_info = content.description
        duration = content.duration
    else:
        return

    if args.template == "resource":
        response = summarize_resource(
            text,
            title,
            author,
            content_type,
            args.url,
            publish_date=publish_date,
            supplementary_info=supplementary_info,
            dry_run=args.dry_run,
        )
    elif args.template == "story":
        response = summarize_story(
            podcast_transcript=text,
            episode_title=title,
            podcast_name=author,
            url=args.url,
            duration=duration,
            publish_date=publish_date,
            dry_run=args.dry_run,
        )
    else:
        return

    if args.json:
        print(json.dumps({"title": title, "content": response}, indent=2, ensure_ascii=False))
        return

    save_path = get_save_path(title, publish_date)
    write_notes(save_path, response)

def highlight(args):
    if args.kindle:
        title, author, highlights = parse_kindle_highlights(args.file)
    else:
        return

    print(f'Found {len(highlights)} highlights for "{title}" by {author}.')

    response = summarize_highlight(
        title=title, author=author, highlights=highlights, dry_run=args.dry_run
    )

    if args.json:
        print(json.dumps({"title": title, "author": author, "content": response}, indent=2, ensure_ascii=False))
        return

    save_path = get_save_path(title)
    write_notes(save_path, response)

def main():
    """Main entry point for the CLI application."""
    parser = argparse.ArgumentParser(description="Braindead CLI for content management.")
    parser.add_argument("--dry-run", "-d", help="Dry run", action="store_true")

    subparsers = parser.add_subparsers(dest="action", help="Action to perform", required=True)

    # Fetch command
    fetch_parser = subparsers.add_parser("fetch", help="Fetch content and metadata")
    fetch_parser.add_argument("url", nargs="?", help="Url of the video or article.")
    fetch_parser.add_argument("--file", type=Path, help="File to fetch highlights from.")
    fetch_parser.add_argument("--article", "-a", help="Attached url is an article.", action="store_true")
    fetch_parser.add_argument("--video", "-v", help="Attached url is a video.", action="store_true")
    fetch_parser.add_argument("--highlights", help="Fetch highlights from a file.", action="store_true")
    fetch_parser.add_argument("--json", help="Output as JSON", action="store_true")

    # Highlight command
    highlight_parser = subparsers.add_parser("highlight", help="Get highlights from read books")
    highlight_parser.add_argument("file", help="File to scrape highlights from.", type=Path)
    highlight_parser.add_argument("--json", help="Output as JSON", action="store_true")
    highlight_group = highlight_parser.add_mutually_exclusive_group(required=True)
    highlight_group.add_argument("--kindle", help="Parse as HTML highlights from kindle.", action="store_true")
    highlight_group.add_argument("--kobo", help="Parse as highlights from kobo reader.", action="store_true")

    # Save command
    save_parser = subparsers.add_parser("save", help="Save an article or video transcript")
    save_parser.add_argument("url", help="Url of the video or article.")
    save_parser.add_argument("--json", help="Output as JSON", action="store_true")
    save_group = save_parser.add_mutually_exclusive_group(required=True)
    save_group.add_argument("--article", "-a", help="Attached url is an article.", action="store_true")
    save_group.add_argument("--video", "-v", help="Attached url is a video.", action="store_true")

    # Summarize command
    summarize_parser = subparsers.add_parser("summarize", help="Summarize an article or video transcript")
    summarize_parser.add_argument("url", help="Url of the video or article.")
    summarize_parser.add_argument("--template", "-t", help="Prompt template to use (story or resource (default).)", default="resource", choices=["story", "resource"])
    summarize_parser.add_argument("--json", help="Output as JSON", action="store_true")
    summarize_group = summarize_parser.add_mutually_exclusive_group(required=True)
    summarize_group.add_argument("--article", "-a", help="Attached url is an article.", action="store_true")
    summarize_group.add_argument("--video", "-v", help="Attached url is a video.", action="store_true")

    args = parser.parse_args()
    Dispatcher.dispatch(args)

if __name__ == "__main__":
    main()
