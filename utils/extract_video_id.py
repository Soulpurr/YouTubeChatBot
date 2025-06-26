import re
from urllib.parse import urlparse, parse_qs
def extract_video_id(url_or_id):
    """
    Accepts a YouTube full URL or direct video ID and returns the video ID.
    """
    # If it's already a video ID
    if len(url_or_id) == 11 and '/' not in url_or_id:
        return url_or_id

    # Parse full YouTube URL
    try:
        parsed_url = urlparse(url_or_id)
        if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
            return parse_qs(parsed_url.query).get("v", [None])[0]
        elif parsed_url.hostname == "youtu.be":
            return parsed_url.path.lstrip("/")
    except Exception:
        return None