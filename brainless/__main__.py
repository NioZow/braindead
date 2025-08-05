import argparse

from mongoengine import connect

from brainless.config import MONGODB_URI
from brainless.handlers import *
from brainless.youtube import *


def parse_arguments():
    """Defines and parses command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Brainless CLI for YouTube content management."
    )

    subparsers = parser.add_subparsers(
        dest="action", help="Action to perform", required=True
    )

    # Sub-parser for 'watch'
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

    action_handlers = {
        "channel": ChannelHandler(subparsers),
        "playlist": PlaylistHandler(subparsers),
    }

    args = parser.parse_args()

    # for vid in Playlist.from_id("PL3KpgbgtXq6BRLAtAVsGNGAMto2lF7sHv").videos:
    #     print(vid.fetch_transcript())
    #     return

    # print(Channel.from_handle(handle="Hasheur"))
    # print(Video.fetch_transcript_from_api("rvA8IbyogJ0"))

    handler = action_handlers.get(args.action)
    if handler:
        handler.dispatcher(args)
    else:
        print_json_error(f"No handler implemented for action: {args.action}")


if __name__ == "__main__":
    main()
