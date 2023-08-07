from .base_audio_processor import AudioProcessor
from pytube import YouTube
import os
import time
import logging
from typing import Optional

log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.basicConfig(level=getattr(logging, log_level),
                    format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger()

AUDIO_FILE_TYPE = "mp4"

class YouTubeAudioProcessor(AudioProcessor):
    def __init__(self, 
                 url: str, 
                 folder_path: str, 
                 filename: str):
        super().__init__(folder_path, filename)
        if not self.is_valid_url(url):
            logger.info("You provided an invalid URL.")
            raise Exception("You provided an invalid URL")
        self.url = url

    def get_audio(self) -> None:
        filename = os.path.join(self.folder_path, self.filename)
        filename_timestamped = f"{filename}_{time.strftime('%Y%m%d%H%M%S')}.{AUDIO_FILE_TYPE}"

        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)

        self.filename = self.download_audio(filename_timestamped)

    def download_audio(self, filename: str) -> str:
        """
        Downloads a YouTube video from the given URL and saves it to the specified output path or the current directory.

        Args:
            url: The URL of the YouTube video to download.
            output_path: The path where the downloaded video will be saved. If None, the video will be saved to the current
            directory.
        Returns:
            filename
        """
        yt = YouTube(self.url)

        video_stream = yt.streams.filter(only_audio=True).first()

        video_stream.download(filename=filename)
        print(f"Video successfully downloaded to {filename}")

        return filename
