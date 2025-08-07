import os

from dotenv import load_dotenv

load_dotenv()

# HACK: bypass some linter typing errors
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY") or ""
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL") or ""
LITELLM_URI = os.getenv("LITELLM_URI") or ""
LITELLM_API_KEY = os.getenv("LITELLM_API_KEY") or ""
CTBB_NOTES_LOCATION = os.getenv("CTBB_NOTES_LOCATION") or ""

MONGODB_URI = os.getenv("MONGODB_URI") or ""
assert MONGODB_URI != "", "Missing MONGODB_URI env variable"
