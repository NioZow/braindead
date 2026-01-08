import re
from dataclasses import dataclass
from datetime import datetime, timedelta

from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

from braindead.config import config
from braindead.utils import logger


@dataclass
class Video:
    id: str
    title: str
    description: str
    publish_date: datetime
    transcript: str
    channel: str
    duration: timedelta


def extract_video_id(url: str) -> str:
    """Extract video ID from various YouTube URL formats using regex."""
    patterns = [
        r"(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})",
        r"(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})",
        r"(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})",
        r"(?:https?://)?(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]{11})",
    ]

    # check if it's already a video ID
    if re.match(r"^[a-zA-Z0-9_-]{11}$", url):
        return url

    # check patterns
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    raise ValueError(f"Could not extract video ID from: {url}")


def parse_iso8601_duration(duration: str) -> timedelta:
    """Parse ISO 8601 duration format (e.g., 'PT1H2M10S') to timedelta."""
    pattern = r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?"
    match = re.match(pattern, duration)

    if not match:
        return timedelta()

    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)

    return timedelta(hours=hours, minutes=minutes, seconds=seconds)


def fetch_video(video_id: str) -> Video:
    """Fetch video information and transcript from YouTube."""
    video_id = extract_video_id(video_id)

    youtube = build("youtube", "v3", developerKey=config.youtube_api_key)

    # Request both snippet and contentDetails
    request = youtube.videos().list(part="snippet,contentDetails", id=video_id)
    response = request.execute()

    if not response["items"]:
        raise ValueError(f"Video not found: {video_id}")

    video_data = response["items"][0]["snippet"]
    content_details = response["items"][0]["contentDetails"]

    # parse published date
    publish_date = datetime.fromisoformat(
        video_data["publishedAt"].replace("Z", "+00:00")
    )

    # parse duration
    duration = parse_iso8601_duration(content_details["duration"])

    # fetch transcript
    try:
        transcript = " ".join(
            [
                t.text
                for t in YouTubeTranscriptApi().fetch(video_id, languages=["fr", "en"])
            ]
        )
        return Video(
            id=video_id,
            title=video_data["title"],
            description=video_data["description"],
            publish_date=publish_date,
            transcript=transcript,
            channel=video_data["channelTitle"],
            duration=duration,
        )
    except Exception as e:
        logger.fatal_error(f"Transcript not available: {str(e)}")
