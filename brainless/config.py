import os

from dotenv import load_dotenv

load_dotenv()

# HACK: bypass some linter typing errors
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY") or ""

MONGODB_URI = os.getenv("MONGODB_URI") or ""
assert MONGODB_URI != "", "Missing MONGODB_URI env variable"
