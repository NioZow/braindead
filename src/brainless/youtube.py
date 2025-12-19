from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import requests
from mongoengine import (
    DateTimeField,
    Document,
    DoesNotExist,
    ListField,
    ReferenceField,
    StringField,
)
from youtube_transcript_api import YouTubeTranscriptApi

from brainless.config import YOUTUBE_API_KEY


def youtube_api_request(url: str, params: Dict[str, Any]) -> Dict[str, Any]:
    assert YOUTUBE_API_KEY != "", "Missing YOUTUBE_API_KEY env variable"

    params["key"] = YOUTUBE_API_KEY
    response = requests.get(url, params=params)
    response.raise_for_status()

    return response.json()


class Video(Document):
    """Video document - each video exists only once in the database"""

    video_id = StringField(max_length=100, unique=True, required=True)
    title = StringField(max_length=200, required=True)
    description = StringField()
    published_date = DateTimeField()
    transcript = StringField()
    updated_at = DateTimeField()
    seen_at = DateTimeField(null=True, default=None)
    channel = ReferenceField("Channel")

    meta = {
        "collection": "videos",
        "indexes": ["video_id", "-published_date", "-seen_at"],
    }

    def fetch_transcript(self):
        if not self.transcript:
            self.transcript = " ".join(
                [
                    t.text
                    for t in list(
                        YouTubeTranscriptApi().fetch(
                            str(self.video_id), languages=["fr", "en"]
                        ),
                    )
                ],
            )
            self.save()

        return self.transcript

    def get_video_link(self):
        return f"https://www.youtube.com/watch?v={self.video_id}"

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Video({self.title})"

    def mark_as_seen(self):
        """Marks the video as seen and saves it."""
        self.seen_at = datetime.now(timezone.utc)
        self.save()

    def mark_as_unseen(self):
        """Marks the video as unseen and saves it."""
        self.seen_at = None
        self.save()

    @classmethod
    def get_watched_videos(cls) -> List["Video"]:
        """Returns all videos that have been watched, most recent first."""
        return cls.objects(seen_at__ne=None).order_by("-seen_at")

    @classmethod
    def get_random_video(cls, unseen_only: bool = True) -> Optional["Video"]:
        """
        Fetches a random video from the database.
        """

        pipeline = []
        if unseen_only:
            pipeline.append({"$match": {"seen_at": None}})

        # $sample is the most efficient way to get random documents in MongoDB
        pipeline.append({"$sample": {"size": 1}})

        # Execute the aggregation pipeline
        random_videos_cursor = cls.objects.aggregate(pipeline)

        try:
            random_video_data = next(random_videos_cursor)
            return cls.objects.with_id(random_video_data["_id"])
        except StopIteration:
            # This happens if no videos match the criteria
            return None


class Playlist(Document):
    """Playlist document"""

    playlist_id = StringField(max_length=100, unique=True, required=True)
    title = StringField(max_length=200, required=True)
    description = StringField()
    videos = ListField(ReferenceField(Video))
    published_date = DateTimeField()
    updated_at = DateTimeField()
    channel = ReferenceField("Channel")

    meta = {
        "collection": "playlists",
        "indexes": ["playlist_id", "-published_date"],
    }

    def save(self, *args, **kwargs):
        """Override save to update timestamp"""
        self.updated_at = datetime.now(timezone.utc)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Playlist({self.title})"

    @classmethod
    def from_id(cls, playlist_id: str) -> "Playlist":
        return cls.objects.get(playlist_id=playlist_id)

    @classmethod
    def fetch_from_api(cls, playlist_id: str) -> "Playlist":
        """
        get a playlist using its id
        """

        # get the playlist information
        data = youtube_api_request(
            "https://www.googleapis.com/youtube/v3/playlists",
            params={
                "part": "id,snippet",
                "id": playlist_id,
            },
        )

        playlist_data = data["items"][0]["snippet"]

        next_page_token = None
        videos = []

        # get the videos of a playlists
        while True:
            # request the api
            params = {
                "part": "snippet,contentDetails,id",
                "playlistId": playlist_id,
                "maxResults": 50,
            }
            if next_page_token:
                params["pageToken"] = next_page_token

            data = youtube_api_request(
                "https://www.googleapis.com/youtube/v3/playlistItems", params=params
            )

            for item in data["items"]:
                video_id = item["snippet"]["resourceId"]["videoId"]
                title = item["snippet"]["title"]

                if title not in ("Private video", "Deleted video"):
                    try:
                        video = Video.objects.get(video_id=video_id)
                    except DoesNotExist:
                        video = Video(
                            video_id=video_id,
                            title=title,
                            description=item["snippet"]["description"],
                            published_date=datetime.fromisoformat(
                                item["snippet"]["publishedAt"].replace("Z", "+00:00")
                            ),
                            channel=Channel.fetch_from_api(
                                channel_id=item["snippet"]["videoOwnerChannelId"]
                            ),
                        )
                        video.save()

                    videos.append(video)

            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break

        try:
            playlist = Playlist.objects.get(playlist_id=playlist_id)
            playlist.videos = videos
        except DoesNotExist:
            playlist = cls(
                playlist_id=playlist_id,
                title=playlist_data["title"],
                description=playlist_data["description"],
                videos=videos,
                published_date=datetime.fromisoformat(
                    playlist_data["publishedAt"].replace("Z", "+00:00")
                ),
                channel=Channel.from_id(playlist_data["channelId"]),
            )

        playlist.save()
        return playlist


class Channel(Document):
    """Channel document"""

    name = StringField(max_length=200)
    handle = StringField(max_length=200)
    channel_id = StringField(max_length=100, unique=True, required=True)
    playlists = ListField(ReferenceField(Playlist))
    videos = ListField(ReferenceField(Video))
    updated_at = DateTimeField()

    meta = {
        "collection": "channels",
        "indexes": ["channel_id", "name"],
    }

    @classmethod
    def from_id(cls, channel_id: str) -> "Channel":
        return cls.objects.get(channel_id=channel_id)

    @classmethod
    def from_handle(cls, handle: str) -> "Channel":
        return cls.objects.get(name=handle)

    @classmethod
    def fetch_from_api(
        cls,
        handle: Optional[str] = None,
        channel_id: Optional[str] = None,
        get_playlists: bool = False,
        get_videos: bool = False,
    ) -> "Channel":
        """Fetch channel information from the youtube api"""
        params = {"part": "snippet"}

        if channel_id:
            params["id"] = channel_id
        elif handle:
            params["forHandle"] = handle
        else:
            raise ValueError("You must specify a channel_id or handle")

        data = youtube_api_request(
            "https://www.googleapis.com/youtube/v3/channels", params=params
        )

        if not data.get("items"):
            raise ValueError(f"Channel not found: {handle}")

        channel_data = data["items"][0]
        channel_id = channel_data["id"]

        try:
            channel = cls.objects.get(channel_id=channel_id)
        except DoesNotExist:
            channel = cls(
                name=channel_data["snippet"]["title"],
                channel_id=channel_id,
                handle=channel_data["snippet"]["customUrl"][1:],
            )

        if get_playlists:
            channel.playlists = channel.fetch_playlists_from_api()

        if get_videos:
            channel.videos = channel.fetch_videos_from_api()

        channel.save()
        return channel

    def fetch_videos_from_api(self) -> List[Video]:
        """
        get all videos of a channel
        """

        # there is a playlist that contains all videos of a channel
        # get the id of that playlist
        data = youtube_api_request(
            "https://www.googleapis.com/youtube/v3/channels",
            params={"part": "contentDetails", "id": self.channel_id},
        )

        uploads_playlist_id = data["items"][0]["contentDetails"]["relatedPlaylists"][
            "uploads"
        ]

        return Playlist.fetch_from_api(uploads_playlist_id).videos

    def fetch_playlists_from_api(self) -> List[Playlist]:
        """
        get all playlists of a youtube channel
        """
        playlists = []
        next_page_token = None

        while True:
            params = {
                "part": "snippet,contentDetails",
                "channelId": self.channel_id,
                "maxResults": 50,
            }

            if next_page_token:
                params["pageToken"] = next_page_token

            data = youtube_api_request(
                "https://www.googleapis.com/youtube/v3/playlists",
                params=params,
            )

            for item in data.get("items", []):
                playlists.append(Playlist.fetch_from_api(item["id"]))

            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break

        return playlists

    def save(self, *args, **kwargs):
        """Override save to update timestamp"""
        self.updated_at = datetime.now(timezone.utc)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Channel({self.name})"
