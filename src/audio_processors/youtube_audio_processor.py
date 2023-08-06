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
                 filename: str, 
                 audio_file_type: Optional[str] = None):
        super().__init__(folder_path, filename, audio_file_type if audio_file_type else AUDIO_FILE_TYPE)
        if not self.is_valid_url(url):
            logger.info("You provided an invalid URL.")
            raise Exception("You provided an invalid URL")
        self.url = url

    def get_audio(self) -> None:
        filename = os.path.join(self.folder_path, self.filename)

        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)

        self.filename = self.download_audio(self.url, filename)

    def download_audio(self, url: str, filename: str) -> str:
        yt = YouTube(url)
        filename_timestamped = f"{filename}_{time.strftime('%Y%m%d%H%M%S')}.{self.audio_file_type}"
        yt.streams.filter(only_audio=True).first().download(filename=filename_timestamped)
        return filename_timestamped
