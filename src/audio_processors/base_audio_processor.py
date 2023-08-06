from abc import ABC, abstractmethod
from src.audio_utils.main import get_file_size, split_audio_file
from urllib.parse import urlparse
import os
import logging
from typing import List

log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.basicConfig(level=getattr(logging, log_level),
                    format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger()

class AudioProcessor(ABC):
    def __init__(self, folder_path: str, filename: str, audio_file_type: str):
        self.folder_path = folder_path
        self.filename = filename
        self.audio_file_type = audio_file_type

    @abstractmethod
    def get_audio(self) -> None:
        """
        Gets the audio file and saves to disk, 
        setting the filename attribute to the file
        """
        pass

    @classmethod
    def is_valid_url(cls, url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc, 'youtube' in result.netloc])
        except ValueError:
            return False

    def split_audio(self) -> List[str]:
        filename_with_ext = self.filename

        logger.info(f"File size of {filename_with_ext} is {get_file_size(filename_with_ext)} bytes.")

        return split_audio_file(filename_with_ext)

    def process_audio(self) -> List[str]:
        self.get_audio()
        return self.split_audio()
