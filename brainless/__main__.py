import argparse
import json
import sys
import webbrowser

import mongoengine as me

from brainless.config import MONGODB_URI, YOUTUBE_API_KEY
from brainless.services.youtube import (
    Channel,
    Playlist,
    Video,
    YoutubeChannel,
    get_all_playlist_progressions,
)


def print_json_error(message: str, exit_code: int = 1):
    """Prints a JSON-formatted error to stderr and exits."""
    json.dump({"status": "error", "message": message}, sys.stderr, indent=2)
    sys.exit(exit_code)


def handle_sync(args):
    """Handler for the 'sync' command."""
    try:
        yt_channel_service = YoutubeChannel(name=args.channel_name)
        channel_doc = yt_channel_service.sync_to_database()
        print(json.dumps(channel_doc.to_dict(), indent=2))
    except Exception as e:
        print_json_error(f"Failed to sync channel '{args.channel_name}': {e}")


def handle_watch(args):
    """Handler for the 'watch' command."""
    query = Video.objects.all()

    # 1. Apply filters to the query
    if args.unseen_only:
        query = query.filter(seen_at=None)

    if args.playlist_id:
        playlist = Playlist.objects(playlist_id=args.playlist_id).first()
        if not playlist:
            print_json_error(f"Playlist with ID '{args.playlist_id}' not found.")
        video_ids = [pv.video.id for pv in playlist.videos]
        query = query.filter(id__in=video_ids)

    elif args.channel_name:
        channel = Channel.objects(name__iexact=args.channel_name).first()
        if not channel:
            print_json_error(f"Channel with name '{args.channel_name}' not found.")
        video_ids = [v.id for v in channel.videos]
        query = query.filter(id__in=video_ids)

    # 2. Select a video from the filtered query
    video_to_watch = None
    if args.no_random:
        # Get the oldest unseen or newest overall
        order = "published_date" if args.unseen_only else "-published_date"
        video_to_watch = query.order_by(order).first()
    else:
        # Get a random one using an efficient pipeline
        # === FIX IS HERE ===
        # Changed 'query.query' to 'query._query'
        pipeline = [
            {"$match": query._query},  # Use the query's filter conditions
            {"$sample": {"size": 1}},
        ]
        result = list(Video.objects.aggregate(pipeline))
        if result:
            video_to_watch = Video.objects.with_id(result[0]["_id"])

    if not video_to_watch:
        print_json_error("No videos found matching the specified criteria.")

    # 3. Perform actions on the selected video
    output_data = video_to_watch.to_dict()

    if args.mark_as_watched:
        video_to_watch.mark_as_seen()
        output_data["status_update"] = "Marked as watched."
        # Refresh the dictionary with the new seen_at time
        output_data = video_to_watch.to_dict()

    if args.summary:
        output_data["summary_status"] = "Summary requested (feature not implemented)."

    if not args.no_browser:
        webbrowser.open(video_to_watch.link)
        output_data["browser_action"] = f"Opened in browser: {video_to_watch.link}"

    print(json.dumps(output_data, indent=2, default=str))


def handle_list_channels(args):
    """Handler for the 'channel' list command."""
    channels = [c.to_dict() for c in Channel.objects.all()]
    print(json.dumps(channels, indent=2))


def handle_list_playlists(args):
    """Handler for the 'playlist' list command."""
    if args.channel_name:
        channel = Channel.objects(name__iexact=args.channel_name).first()
        if not channel:
            print_json_error(f"Channel '{args.channel_name}' not found.")
        # we assume channel.playlists holds ReferenceFields to Playlist documents
        playlists = [p.get_progression_stats() for p in channel.playlists]
    else:
        # if no channel specified, list all playlists or their progressions
        playlists = get_all_playlist_progressions(sort_by_completion=True)

    print(json.dumps(playlists, indent=2, default=str))


def handle_list_videos(args):
    """Handler for the 'video' list command."""
    query = Video.objects.all()
    if args.playlist_id:
        playlist = Playlist.objects(playlist_id=args.playlist_id).first()
        if not playlist:
            print_json_error(f"Playlist with ID '{args.playlist_id}' not found.")
        video_ids = [pv.video.id for pv in playlist.videos]
        query = query.filter(id__in=video_ids)
    elif args.channel_name:
        channel = Channel.objects(name__iexact=args.channel_name).first()
        if not channel:
            print_json_error(f"Channel with name '{args.channel_name}' not found.")
        video_ids = [v.id for v in channel.videos]
        query = query.filter(id__in=video_ids)

    videos = [v.to_dict() for v in query.order_by("-published_date")]
    print(json.dumps(videos, indent=2, default=str))


def parse_arguments():
    """Defines and parses command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Brainless CLI for YouTube content management."
    )
    subparsers = parser.add_subparsers(
        dest="action", help="Action to perform", required=True
    )

    # Sub-parser for 'sync'
    sync_parser = subparsers.add_parser(
        "sync", help="Sync a YouTube channel's videos and playlists."
    )
    sync_parser.add_argument(
        "channel_name", help="The name/handle of the channel to sync."
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

    # Sub-parser for listing channels
    channel_parser = subparsers.add_parser(
        "channel", help="List all synced YouTube channels."
    )

    # Sub-parser for listing playlists
    playlist_parser = subparsers.add_parser(
        "playlist", help="List playlists or view their watch progression."
    )
    playlist_parser.add_argument(
        "--channel",
        "-c",
        dest="channel_name",
        help="Filter playlists belonging to a specific channel.",
    )

    # Sub-parser for listing videos
    video_parser = subparsers.add_parser("video", help="List synced videos.")
    video_parser.add_argument(
        "--channel", "-c", dest="channel_name", help="Filter videos by channel name."
    )
    video_parser.add_argument(
        "--playlist", "-p", dest="playlist_id", help="Filter videos by playlist ID."
    )

    return parser.parse_args()


def main():
    """Main entry point for the CLI application."""
    try:
        me.connect(host=MONGODB_URI, alias="default")
    except Exception as e:
        print_json_error(f"Failed to connect to MongoDB: {e}")

    YoutubeChannel.set_api_key(YOUTUBE_API_KEY)

    args = parse_arguments()

    action_handlers = {
        "sync": handle_sync,
        "watch": handle_watch,
        "channel": handle_list_channels,
        "playlist": handle_list_playlists,
        "video": handle_list_videos,
    }

    handler = action_handlers.get(args.action)
    if handler:
        handler(args)
    else:
        print_json_error(f"No handler implemented for action: {args.action}")


if __name__ == "__main__":
    main()
