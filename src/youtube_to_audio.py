import os
import sys
import time
from pytube import YouTube
from urllib.parse import urlparse
import logging
from src.audio_utils.main import get_file_size, split_audio_file

log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.basicConfig(level=getattr(logging, log_level),
                    format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger()

AUDIO_FILE_TYPE = "mp4"

def is_valid_url(url):
    """
    Checks if the provided URL is a valid YouTube URL.
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc, 'youtube' in result.netloc])
    except ValueError:
        return False

def download_audio(url, filename):
    """
    Downloads the audio from the provided YouTube URL and saves it with a timestamp.
    """
    yt = YouTube(url)
    filename_timestamped = f"{filename}_{time.strftime('%Y%m%d%H%M%S')}"
    yt.streams.filter(only_audio=True).first().download(filename=f"{filename_timestamped}.{AUDIO_FILE_TYPE}")
    return filename_timestamped


def process_audio(yt_url, folder_path, filename):
    """
    Processes the audio: checks if the URL is valid, downloads the audio,
    checks the file size and splits the file if it's larger than 7MB.
    """
    if not is_valid_url(yt_url):
        logger.info("You provided an invalid URL.")
        return

    filename = os.path.join(folder_path, filename)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    filename = download_audio(yt_url, filename)

    filename_with_ext = f"{filename}.{AUDIO_FILE_TYPE}"

    logger.info(f"File size of {filename_with_ext} is {get_file_size(filename_with_ext)} bytes.")

    if get_file_size(filename_with_ext) > 7 * 1024 * 1024:  # File size greater than 7MB
        split_audio_file(filename_with_ext)
    else:
        os.rename(filename_with_ext, f"{filename}_part0.{AUDIO_FILE_TYPE}")

if __name__ == "__main__":
    """
    This script downloads, processes, and possibly splits a YouTube audio file. 
    It takes in a YouTube URL, folder path, and an optional filename.
    """

    if len(sys.argv) < 3 or len(sys.argv) > 4:
        logger.info("Usage: python script.py <YouTube_URL> <folder_path> [<filename>]")
        sys.exit(1)

    video_url = sys.argv[1]
    folder_path = sys.argv[2]
    filename = sys.argv[3] if len(sys.argv) == 4 else 'downloaded_audio'

    process_audio(video_url, folder_path, filename)
