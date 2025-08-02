import os

from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
assert YOUTUBE_API_KEY != "" and YOUTUBE_API_KEY is not None, (
    "Missing YOUTUBE_API_KEY env variable"
)

MONGODB_URI = os.getenv("MONGODB_URI")
assert MONGODB_URI != "" and MONGODB_URI is not None, "Missing MONGODB_URI env variable"
