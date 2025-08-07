import json
import re
import sys
from argparse import ArgumentParser

from brainless.youtube import Channel, Playlist


def print_json_error(message: str, exit_code: int = 1):
    """Prints a JSON-formatted error to stderr and exits."""
    json.dump({"status": "error", "message": message}, sys.stderr, indent=2)
    sys.exit(exit_code)


class Handler:
    def __init__(self, parser_name, action_handlers):
        self.parser_name = parser_name
        self.action_handlers = action_handlers

    def dispatcher(self, args):
        handler = self.action_handlers.get(args.subaction)
        if handler:
            print(json.dumps(handler(args), indent=2))
        else:
            print_json_error(f"No handler implemented for action: {args.subaction}")

    def get_parser_name(self):
        return self.parser_name


class ChannelHandler(Handler):
    def __init__(self, subparsers):
        super().__init__(
            "channel",
            action_handlers={
                "list": self.list,
                "ls": self.list,
                "add": self.add,
                "remove": self.remove,
                "rm": self.remove,
            },
        )

        parser = subparsers.add_parser(self.parser_name, help="Channel related parser")

        channel_subparsers = parser.add_subparsers(
            dest="subaction",
            help="Channel commands",
            required=True,
        )

        channel_subparsers.add_parser(
            "list",
            help="List all managed channels",
            aliases=["ls"],
        )

        add = channel_subparsers.add_parser(
            "add",
            help="Add a channel",
        )

        add.add_argument("handle", help="Name of the channel")
        add.add_argument(
            "--playlists", "-p", help="Get all channel playlists", action="store_true"
        )
        add.add_argument(
            "--videos", "-v", help="Get all channel videos", action="store_true"
        )

        remove = channel_subparsers.add_parser(
            "remove", help="Remove a channel", aliases=["rm"]
        )

        remove.add_argument("handle", help="Name of the channel")

    def list(self, args: ArgumentParser):
        return [
            {
                "name": channel.name,
                "handle": channel.handle,
                "playlists": len(channel.playlists),
                "videos": len(channel.videos),
            }
            for channel in list(Channel.objects.all())
        ]

    def add(self, args: ArgumentParser):
        channel = Channel.fetch_from_api(
            handle=args.handle,
            get_playlists=args.playlists,
            get_videos=args.videos,
        )
        return {
            "name": channel.name,
            "handle": channel.handle,
            "playlists": len(channel.playlists),
            "videos": len(channel.videos),
        }

    def remove(self, args: ArgumentParser):
        Channel.objects(name=args.handle).delete()
        return {}


class PlaylistHandler(Handler):
    def __init__(self, subparsers):
        super().__init__(
            "playlist",
            action_handlers={
                "list": self.list,
                "ls": self.list,
                "add": self.add,
                "remove": self.remove,
                "rm": self.remove,
            },
        )

        parser = subparsers.add_parser(self.parser_name, help="Playlist related parser")

        playlist_subparsers = parser.add_subparsers(
            dest="subaction",
            help="Playlist commands",
            required=True,
        )

        list = playlist_subparsers.add_parser(
            "list",
            help="List all managed playlists",
            aliases=["ls"],
        )

        list.add_argument(
            "--videos",
            "-v",
            help="Print all videos of the playlists",
            action="store_true",
        )

        add = playlist_subparsers.add_parser(
            "add",
            help="Add a playlist",
        )

        add.add_argument("playlist_url", help="Url of the playlist")

        remove = playlist_subparsers.add_parser(
            "remove", help="Remove a playlist", aliases=["rm"]
        )

        remove.add_argument("name", help="Name of the playlist")

    def list(self, args: ArgumentParser):
        pattern = re.compile(r"^Uploads from")
        return [
            {
                "name": playlist.title,
                "description": playlist.description,
                "videos": len(playlist.videos)
                if not args.videos
                else [v.title for v in playlist.videos],
            }
            for playlist in list(Playlist.objects.all())
            if not pattern.match(playlist.title)
        ]

    def add(self, args: ArgumentParser):
        pattern = re.compile(
            r"^(?:https:\/\/www\.youtube\.com\/playlist\?list=([\w\d\-]+))$"
        )

        playlist_id = (
            match[0] if len(match := pattern.findall(args.playlist_url)) == 1 else None
        )
        if not playlist_id:
            return {"error": "Invalid playlist url"}

        playlist = Playlist.fetch_from_api(playlist_id=playlist_id)
        return {
            "name": playlist.title,
            "description": playlist.description,
            "videos": len(playlist.videos),
        }

    def remove(self, args: ArgumentParser):
        Playlist.objects(title=args.name).delete()
        return {}
