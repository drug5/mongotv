import os
import json
import time
import subprocess
from pathlib import Path
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_KEY = os.getenv('API_KEY')
CHANNEL_ID = "UCEpaYNj2MkfNaFabfYkCxdQ"
DOWNLOAD_PATH = "/home/cf/mongotv/media/"
CHECK_INTERVAL = 6000  # Check every 60 minutes
MAX_RESULTS = 10  # Number of recent videos to check
CACHE_FILE = "video_cache.json"  # File to cache video data

# Initialize YouTube Data API
youtube = build("youtube", "v3", developerKey=API_KEY)

def load_cached_videos():
    """Load cached video data from file."""
    if Path(CACHE_FILE).exists():
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cached_videos(cached_videos):
    """Save cached video data to file."""
    with open(CACHE_FILE, "w") as f:
        json.dump(cached_videos, f)

def fetch_latest_videos():
    """Fetch the latest videos from the channel."""
    request = youtube.search().list(
        part="snippet",
        channelId=CHANNEL_ID,
        order="date",
        maxResults=MAX_RESULTS,
        type="video"
    )
    response = request.execute()
    
    videos = []
    for item in response.get("items", []):
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        videos.append((video_id, title))
    
    return videos

def download_video(video_id, title):
    """Download YouTube video using yt-dlp."""
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        sanitized_title = "".join(c for c in title if c.isalnum() or c in " .-_()").rstrip()
        file_path = Path(DOWNLOAD_PATH) / f"{sanitized_title}.mp4"

        if file_path.exists():
            print(f"Already downloaded: {title}")
            return

        print(f"Downloading: {title}")
        subprocess.run(
            [
                "yt-dlp", "-f", "bestvideo[height<=720]+bestaudio/best[height<=720]",
                "-o", str(file_path), url
            ],
            check=True
        )
        print(f"Downloaded: {file_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error during download: {e}")

def main():
    """Main function to monitor and download videos."""
    Path(DOWNLOAD_PATH).mkdir(parents=True, exist_ok=True)

    cached_videos = load_cached_videos()
    downloaded_videos = set(f.stem for f in Path(DOWNLOAD_PATH).glob("*.mp4"))

    while True:
        try:
            videos = fetch_latest_videos()
            new_videos = []

            for video_id, title in videos:
                if video_id not in cached_videos:
                    cached_videos[video_id] = title
                    new_videos.append((video_id, title))

            save_cached_videos(cached_videos)

            for video_id, title in new_videos:
                if title not in downloaded_videos:
                    download_video(video_id, title)
                    downloaded_videos.add(title)
                else:
                    print(f"Already downloaded: {title}")
        except Exception as e:
            print(f"Error: {e}")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()