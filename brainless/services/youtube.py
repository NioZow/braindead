from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import requests
from mongoengine import (
    BooleanField,
    DateTimeField,
    Document,
    DoesNotExist,
    EmbeddedDocument,
    EmbeddedDocumentField,
    IntField,
    ListField,
    ReferenceField,
    StringField,
)

from brainless.services import Service


def get_all_playlist_progressions(
    sort_by_completion: bool = False,
) -> List[Dict[str, Any]]:
    """
    Gets the watch progression statistics for all playlists in the database.

    Args:
        sort_by_completion (bool): If True, sorts the playlists from most
                                   complete to least complete.

    Returns:
        A list of progression statistic dictionaries.
    """
    all_stats = [
        playlist.get_progression_stats() for playlist in Playlist.objects.all()
    ]

    if sort_by_completion:
        all_stats.sort(key=lambda x: x["completion_percentage"], reverse=True)

    return all_stats


class Video(Document):
    """Video document - each video exists only once in the database"""

    video_id = StringField(max_length=100, unique=True, required=True)
    title = StringField(max_length=200, required=True)
    description = StringField()
    link = StringField()
    thumbnail = StringField()
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    published_date = DateTimeField()
    updated_at = DateTimeField()
    seen_at = DateTimeField(null=True, default=None)
    meta = {
        "collection": "videos",
        "indexes": ["video_id", "-published_date", "-seen_at", "-created_at"],
    }

    @classmethod
    def get_or_create_video(cls, video_data: Dict[str, Any]) -> "Video":
        """Get existing video or create new one"""
        try:
            video = cls.objects(video_id=video_data["video_id"]).get()
            video.title = video_data.get("title", video.title)
            video.description = video_data.get("description", video.description)
            video.link = video_data.get("link", video.link)
            video.thumbnail = video_data.get("thumbnail", video.thumbnail)
            video.save()
            return video
        except DoesNotExist:
            allowed_keys = cls._fields.keys()
            filtered_data = {k: v for k, v in video_data.items() if k in allowed_keys}
            return cls(**filtered_data).save()

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Video({self.title})"

    def mark_as_seen(self) -> "Video":
        """Marks the video as seen and saves it."""
        self.seen_at = datetime.now(timezone.utc)
        self.save()
        return self

    def mark_as_unseen(self) -> "Video":
        """Marks the video as unseen and saves it."""
        self.seen_at = None
        self.save()
        return self

    @classmethod
    def get_watched_videos(cls) -> List["Video"]:
        """Returns all videos that have been watched, most recent first."""
        return cls.objects(seen_at__ne=None).order_by("-seen_at")

    @classmethod
    def get_random_video(cls, unseen_only: bool = True) -> Optional["Video"]:
        """
        Fetches a random video from the database.

        Args:
            unseen_only (bool): If True, only picks from videos that have not
                                been watched yet (`seen_at` is None).

        Returns:
            A random Video document or None if no matching video is found.
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

    def to_dict(self) -> Dict[str, Any]:
        """Returns a JSON-serializable dictionary representation of the video."""
        return {
            "id": self.video_id,
            "title": self.title,
            "link": self.link,
            "seen_at": self.seen_at.isoformat() if self.seen_at else None,
            "published_date": self.published_date.isoformat()
            if self.published_date
            else None,
        }


class PlaylistVideo(EmbeddedDocument):
    """Reference to a video within a playlist with playlist-specific metadata"""

    video = ReferenceField(Video, required=True)
    position = StringField()
    added_date = DateTimeField()


class Playlist(Document):
    """Playlist document"""

    playlist_id = StringField(max_length=100, unique=True, required=True)
    title = StringField(max_length=200, required=True)
    description = StringField()
    videos = ListField(EmbeddedDocumentField(PlaylistVideo))
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    published_date = DateTimeField()
    updated_at = DateTimeField()
    video_count = IntField()

    meta = {
        "collection": "playlists",
        "indexes": ["playlist_id", "-published_date", "-created_at"],
    }

    def save(self, *args, **kwargs):
        """Override save to update timestamp"""
        self.updated_at = datetime.now(timezone.utc)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Playlist({self.title})"

    def to_dict(self) -> Dict[str, Any]:
        """Returns a JSON-serializable dictionary representation of the playlist."""
        return {
            "playlist_id": self.playlist_id,
            "title": self.title,
            "video_count": self.video_count,
        }

    def add_video(
        self,
        video: Video,
        position: Optional[str] = None,
        added_date: Optional[datetime] = None,
    ):
        if any(pv.video.id == video.id for pv in self.videos):
            return
        self.videos.append(
            PlaylistVideo(video=video, position=position, added_date=added_date)
        )

    def get_progression_stats(self) -> Dict[str, Any]:
        """
        Calculates and returns the watch progression for this playlist.
        Returns a dictionary ready for JSON conversion.
        """
        watched_videos = []
        unwatched_videos = []

        for pv in self.videos:
            if pv.video and pv.video.seen_at:
                watched_videos.append(pv.video.to_dict())
            else:
                unwatched_videos.append(pv.video.to_dict())

        total_videos = len(self.videos)
        watched_count = len(watched_videos)

        percentage = (watched_count / total_videos) * 100 if total_videos > 0 else 0

        return {
            "title": self.title,
            "videos": total_videos,
            "watched_videos_count": watched_count,
            "unwatched_videos_count": len(unwatched_videos),
            "completion_percentage": round(percentage, 2),
            # "watched_videos": watched_videos,
            # "unwatched_videos": unwatched_videos,
        }


class Channel(Document):
    """Channel document"""

    name = StringField(max_length=200)
    channel_id = StringField(max_length=100, unique=True, required=True)
    playlists = ListField(ReferenceField(Playlist))
    videos = ListField(ReferenceField(Video))
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField()
    last_synced = DateTimeField()
    is_active = BooleanField(default=True)
    is_verified = BooleanField(default=False)
    meta = {
        "collection": "channels",
        "indexes": ["channel_id", "name", "-created_at"],
    }

    def save(self, *args, **kwargs):
        """Override save to update timestamp"""
        self.updated_at = datetime.now(timezone.utc)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Channel({self.name})"

    def add_video(self, video: Video):
        """Add a video to this channel if not already added"""
        if video.id not in [v.id for v in self.videos]:
            self.videos.append(video)

    def add_playlist(self, playlist: Playlist):
        """Add a playlist to this channel if not already added"""
        if playlist.id not in [p.id for p in self.playlists]:
            self.playlists.append(playlist)

    def to_dict(self):
        return {
            "name": self.name,
            "id": self.channel_id,
            "video": len(self.videos),
            "last_synced": self.last_synced.isoformat(),
            "playlists": len(self.playlists),
        }


class Youtube(Service):
    _api_key = None

    def __init__(self):
        super().__init__()
        if not self._api_key:
            raise ValueError(
                "YouTube API key not set. Use YouTube.set_api_key() first."
            )

    @classmethod
    def set_api_key(cls, key: str):
        cls._api_key = key

    def _make_request(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        params["key"] = self._api_key
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()


class YoutubeChannel(Youtube):
    """YouTube Channel API operations"""

    def __init__(self, name: Optional[str] = None, channel_id: Optional[str] = None):
        super().__init__()
        if not name and not channel_id:
            raise ValueError("You must specify either a channel name or channel_id")

        self._fetch_and_set_channel_info(name=name, channel_id=channel_id)

    def _fetch_and_set_channel_info(
        self, name: Optional[str] = None, channel_id: Optional[str] = None
    ):
        """
        Fetches channel details (ID and name) from the API and sets them
        as instance attributes.
        """
        url = "https://www.googleapis.com/youtube/v3/channels"
        params = {"part": "snippet"}
        if channel_id:
            params["id"] = channel_id
        elif name:
            params["forHandle"] = name

        data = self._make_request(url, params)
        if not data.get("items"):
            handle = name or channel_id
            raise ValueError(f"Channel not found: {handle}")

        item = data["items"][0]
        self.channel_id = item["id"]
        self.channel_name = item["snippet"]["title"]

    def get_playlists(self) -> List[Dict[str, Any]]:
        playlists = []
        next_page_token = None
        while True:
            url = "https://www.googleapis.com/youtube/v3/playlists"
            params = {
                "part": "snippet,contentDetails",
                "channelId": self.channel_id,
                "maxResults": 50,
            }
            if next_page_token:
                params["pageToken"] = next_page_token
            data = self._make_request(url, params)
            for item in data.get("items", []):
                playlist_info = {
                    "playlist_id": item["id"],
                    "title": item["snippet"]["title"],
                    "description": item["snippet"]["description"],
                    "published_date": datetime.fromisoformat(
                        item["snippet"]["publishedAt"].replace("Z", "+00:00")
                    ),
                    "video_count": item["contentDetails"]["itemCount"],
                }
                playlists.append(playlist_info)
            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break
        return playlists

    def get_playlist_videos(self, playlist_id: str) -> List[Dict[str, Any]]:
        videos = []
        next_page_token = None
        while True:
            url = "https://www.googleapis.com/youtube/v3/playlistItems"
            params = {
                "part": "snippet,contentDetails",
                "playlistId": playlist_id,
                "maxResults": 50,
            }
            if next_page_token:
                params["pageToken"] = next_page_token
            data = self._make_request(url, params)
            if "items" not in data:
                break
            for item in data["items"]:
                title = item["snippet"].get("title")
                if title in ["Deleted video", "Private video"] or not item[
                    "snippet"
                ].get("resourceId"):
                    continue
                video_info = {
                    "video_id": item["snippet"]["resourceId"]["videoId"],
                    "title": title,
                    "description": item["snippet"]["description"],
                    "link": f"https://www.youtube.com/watch?v={item['snippet']['resourceId']['videoId']}",
                    "published_date": datetime.fromisoformat(
                        item["snippet"]["publishedAt"].replace("Z", "+00:00")
                    ),
                    "position": str(item["snippet"]["position"]),
                    "thumbnail": item["snippet"]
                    .get("thumbnails", {})
                    .get("default", {})
                    .get("url"),
                }
                videos.append(video_info)
            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break
        return videos

    def get_all_channel_videos(self) -> List[Dict[str, Any]]:
        url = "https://www.googleapis.com/youtube/v3/channels"
        params = {"part": "contentDetails", "id": self.channel_id}
        data = self._make_request(url, params)
        uploads_playlist_id = data["items"][0]["contentDetails"]["relatedPlaylists"][
            "uploads"
        ]
        return self.get_playlist_videos(uploads_playlist_id)

    def sync_to_database(self) -> Channel:
        """Sync this YouTube channel to the database"""
        try:
            channel_doc = Channel.objects(channel_id=self.channel_id).get()
            channel_doc.name = self.channel_name
        except DoesNotExist:
            channel_doc = Channel(channel_id=self.channel_id, name=self.channel_name)

        all_videos_data = self.get_all_channel_videos()
        for video_data in all_videos_data:
            video = Video.get_or_create_video(video_data)
            channel_doc.add_video(video)

        playlists_data = self.get_playlists()
        for playlist_data in playlists_data:
            try:
                playlist = Playlist.objects(
                    playlist_id=playlist_data["playlist_id"]
                ).get()
                playlist.title = playlist_data.get("title", playlist.title)
                playlist.description = playlist_data.get(
                    "description", playlist.description
                )
                playlist.video_count = playlist_data.get(
                    "video_count", playlist.video_count
                )
            except DoesNotExist:
                playlist = Playlist(**playlist_data)

            channel_doc.add_playlist(playlist)
            playlist_videos_data = self.get_playlist_videos(
                playlist_data["playlist_id"]
            )
            for video_data in playlist_videos_data:
                video = Video.get_or_create_video(video_data)
                playlist.add_video(
                    video,
                    position=video_data.get("position"),
                    added_date=video_data.get("published_date"),
                )
            playlist.save()

        channel_doc.last_synced = datetime.now(timezone.utc)
        channel_doc.save()
        return channel_doc
