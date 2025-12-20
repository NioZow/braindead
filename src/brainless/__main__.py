import argparse
import re
from pathlib import Path

from mongoengine import connect
from newspaper import Article

from brainless.ai import convert_to_markdown, ctbb_summary, sec_summary
from brainless.article import get_article_content
from brainless.config import ARTICLES_NOTES_LOCATION, CTBB_NOTES_LOCATION, MONGODB_URI
from brainless.handlers import *
from brainless.read.kindle import get_kindle_highlights
from brainless.youtube import Video


def parse_arguments():
    """Defines and parses command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Brainless CLI for YouTube content management."
    )

    subparsers = parser.add_subparsers(
        dest="action", help="Action to perform", required=True
    )

    # sub-parser for 'watch'
    watch_parser = subparsers.add_parser("watch", help="Find and watch a video.")
    watch_parser.add_argument(
        "--unseen-only",
        "-u",
        action="store_true",
        help="Choose only from unseen videos.",
    )
    watch_parser.add_argument(
        "--no-browser",
        "-b",
        action="store_true",
        help="Do not open the video in a browser.",
    )
    watch_parser.add_argument(
        "--no-random",
        "-r",
        action="store_true",
        help="Pick the latest/oldest video instead of random.",
    )
    watch_parser.add_argument(
        "--channel",
        "-c",
        dest="channel_name",
        help="Filter videos by a specific channel name.",
    )
    watch_parser.add_argument(
        "--playlist",
        "-p",
        dest="playlist_id",
        help="Filter videos by a specific playlist ID.",
    )
    watch_parser.add_argument(
        "--mark-as-watched",
        "-w",
        action="store_true",
        help="Mark the selected video as watched.",
    )
    watch_parser.add_argument(
        "--summary",
        "-s",
        action="store_true",
        help="Request an AI summary (placeholder).",
    )

    return parser.parse_args()


def save(args):
    if args.article:
        text = get_article_content(args.article)
    elif args.ctbb:
        pattern = re.compile(r"(?:v=([\w\-]+))|(?:youtu\.be\/([\w\-]+))")
        match = pattern.findall(args.ctbb)

        if len(match) != 1:
            print("Invalid youtube URL")
            return

        video_id = match[0][0] or match[0][1]

        vid = Video.objects(video_id=video_id).get()

        if vid.channel.name != "Critical Thinking - Bug Bounty Podcast":
            raise Exception("not a video from CTBB")

        pattern = re.compile(r"(?: \(Ep. (\d{1,3})\))$")

        # get & format episode number
        ep = pattern.findall(vid.title)[0]
        ep = "0" * (3 - len(ep)) + ep

        # format title
        filename = (
            f"{ep}-"
            + re.sub(
                r"(\-{2,})",
                "-",
                pattern.sub("", vid.title).lower().replace(" ", "-").replace(",", ""),
            )
            + ".md"
        )

        assert CTBB_NOTES_LOCATION != "", "Missing CTBB_NOTES_LOCATION env variable"
        save_path = (
            Path(CTBB_NOTES_LOCATION).expanduser().resolve() / "transcript" / filename
        )

        with open(save_path, "w") as f:
            text = vid.fetch_transcript()
            f.write(convert_to_markdown(text))

    return


def summarize(args):
    if args.ctbb:
        pattern = re.compile(r"(?:v=([\w\-]+))|(?:youtu\.be\/([\w\-]+))")
        match = pattern.findall(args.ctbb)

        if len(match) != 1:
            print("Invalid youtube URL")
            return

        video_id = match[0][0] or match[0][1]

        vid = Video.objects(video_id=video_id).get()

        if vid.channel.name != "Critical Thinking - Bug Bounty Podcast":
            raise Exception("not a video from CTBB")

        pattern = re.compile(r"(?: \(Ep. (\d{1,3})\))$")

        # get & format episode number
        ep = pattern.findall(vid.title)[0]
        ep = "0" * (3 - len(ep)) + ep

        # format title
        filename = (
            f"{ep}-"
            + re.sub(
                r"(\-{2,})", "-", pattern.sub("", vid.title).lower().replace(" ", "-")
            )
            + ".md"
        )

        assert CTBB_NOTES_LOCATION != "", "Missing CTBB_NOTES_LOCATION env variable"
        save_path = (
            Path(CTBB_NOTES_LOCATION).expanduser().resolve() / "summary" / filename
        )

        with open(save_path, "w") as f:
            transcript = vid.fetch_transcript()
            f.write(ctbb_summary(transcript, vid.description) or "")
    elif args.article:
        article = Article(args.article)
        article.download()
        article.parse()

        filename = (
            re.sub(
                r"(\-{2,})",
                "-",
                re.sub(
                    r"([\/:\.])",
                    "",
                    article.title.lower().replace(" ", "-"),
                ),
            )
            + ".md"
        )

        assert ARTICLES_NOTES_LOCATION != "", (
            "Missing ARTICLES_NOTES_LOCATION env variable"
        )
        save_path = (
            Path(ARTICLES_NOTES_LOCATION).expanduser().resolve() / "summary" / filename
        )

        with open(save_path, "w") as f:
            f.write(sec_summary(article.text, "") or "")


def highlight(args):
    if args.kindle:
        get_kindle_highlights(args.file, dry_run=args.dry_run)
    elif args.kobo:
        pass


def main():
    """Main entry point for the CLI application."""
    try:
        connect(host=MONGODB_URI, alias="default")
    except Exception as e:
        print_json_error(f"Failed to connect to MongoDB: {e}")

    parser = argparse.ArgumentParser(
        description="Brainless CLI for YouTube content management."
    )

    subparsers = parser.add_subparsers(
        dest="action", help="Action to perform", required=True
    )

    save_parser = subparsers.add_parser(
        "save", help="Save an article or video transcript"
    )

    save_group = save_parser.add_mutually_exclusive_group(required=True)
    save_group.add_argument("--article", "-a", help="Article to save")
    save_group.add_argument("--video", "-v", help="Video to save")
    save_group.add_argument(
        "--ctbb", help="Video from the Critical Thinking Bug Bounty Poadcast"
    )

    highlight_parser = subparsers.add_parser(
        "highlight", help="Get highlights from read books"
    )
    highlight_parser.add_argument(
        "file", help="File to scrape highlights from.", type=Path
    )
    highlight_parser.add_argument(
        "--dry-run", "-d", help="Dry run", action="store_true"
    )
    highlight_group = highlight_parser.add_mutually_exclusive_group(required=True)
    highlight_group.add_argument(
        "--kindle", help="Parse as HTML highlights from kindle.", action="store_true"
    )
    highlight_group.add_argument(
        "--kobo", help="Parse as highlights from kobo reader.", action="store_true"
    )

    summary_parser = subparsers.add_parser(
        "sum", help="Summarize an article or video transcript"
    )

    sum_group = summary_parser.add_mutually_exclusive_group(required=True)
    sum_group.add_argument("--article", "-a", help="Article to summarize")
    sum_group.add_argument("--video", "-v", help="Video to summarize")
    sum_group.add_argument(
        "--ctbb", help="Video from the Critical Thinking Bug Bounty Poadcast"
    )

    action_handlers = {
        "channel": ChannelHandler(subparsers),
        "playlist": PlaylistHandler(subparsers),
        "save": save,
        "sum": summarize,
        "highlight": highlight,
    }

    args = parser.parse_args()

    handler = action_handlers.get(args.action)
    if handler:
        try:
            handler.dispatcher(args)
        except AttributeError:
            handler(args)
    else:
        print_json_error(f"No handler implemented for action: {args.action}")


if __name__ == "__main__":
    main()
