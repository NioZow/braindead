import argparse
from pathlib import Path

from newspaper import Article

from braindead.ai import convert_to_markdown, summarize_highlight, summarize_resource
from braindead.config import get_save_path
from braindead.resources.kindle import parse_kindle_highlights
from braindead.resources.youtube import fetch_video
from braindead.utils import logger, write_notes


class Dispatcher:
    @staticmethod
    def dispatch(args):
        try:
            if (func := globals().get(args.action)) is not None:
                func(args)
            else:
                logger.fatal_error(
                    f"Command {args.action} has not yet been developped."
                )
        except Exception as e:
            logger.error("Unexpected error.")
            raise e


def save(args):
    if args.article:
        article = Article(args.url)
        article.download()
        article.parse()

        text = article.text
        title = article.title
        publish_date = article.publish_date
    elif args.video:
        video = fetch_video(args.video)
        text = video.transcript
        title = video.title
        publish_date = video.publish_date
    else:
        return

    response = convert_to_markdown(text, dry_run=args.dry_run)

    save_path = get_save_path(title, publish_date)
    write_notes(save_path, response)


def summarize(args):
    if args.article:
        article = Article(args.url)
        article.download()
        article.parse()

        text = article.text
        title = article.title
        publish_date = article.publish_date
        author = article.authors[0] if len(article.authors) > 0 else "Unknown"
        content_type = "Article"
        supplementary_info = None
    elif args.video:
        video = fetch_video(args.url)
        text = video.transcript
        title = video.title
        author = video.channel
        publish_date = video.publish_date
        content_type = "Video"
        supplementary_info = video.description
    else:
        return

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

    save_path = get_save_path(title)
    write_notes(save_path, response)


def main():
    """Main entry point for the CLI application."""
    # fmt: off
    parser = argparse.ArgumentParser(description="Braindead CLI for YouTube content management.")
    parser.add_argument("--dry-run", "-d", help="Dry run", action="store_true")

    subparsers = parser.add_subparsers(dest="action", help="Action to perform", required=True)

    highlight_parser = subparsers.add_parser( "highlight", help="Get highlights from read books")
    highlight_parser.add_argument( "file", help="File to scrape highlights from.", type=Path)
    highlight_group = highlight_parser.add_mutually_exclusive_group(required=True)
    highlight_group.add_argument( "--kindle", help="Parse as HTML highlights from kindle.", action="store_true")
    highlight_group.add_argument( "--kobo", help="Parse as highlights from kobo reader.", action="store_true")

    save_parser = subparsers.add_parser("save", help="Save an article or video transcript")
    save_parser.add_argument("url", help="Url of the video or article.")
    save_group = save_parser.add_mutually_exclusive_group(required=True)
    save_group.add_argument("--article", "-a", help="Attached url is an article.", action="store_true")
    save_group.add_argument("--video", "-v", help="Attached url is a video.", action="store_true")

    summarize_parser = subparsers.add_parser( "summarize", help="Summarize an article or video transcript")
    summarize_parser.add_argument("url", help="Url of the video or article.")
    summarize_group = summarize_parser.add_mutually_exclusive_group(required=True)
    summarize_group.add_argument("--article", "-a", help="Attached url is an article.", action="store_true")
    summarize_group.add_argument("--video", "-v", help="Attached url is a video.", action="store_true")
    # fmt: on

    args = parser.parse_args()
    Dispatcher.dispatch(args)


if __name__ == "__main__":
    main()
