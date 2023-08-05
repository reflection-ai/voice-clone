from abc import ABC, abstractmethod
from src.audio_utils.main import get_file_size, split_audio_file
import os
import logging

log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.basicConfig(level=getattr(logging, log_level),
                    format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger()

class AudioProcessor(ABC):
    def __init__(self, folder_path, filename, audio_file_type):
        self.folder_path = folder_path
        self.filename = filename
        self.audio_file_type = audio_file_type

    @abstractmethod
    def get_audio(self):
        """
        Gets the audio file and saves to disk, setting the filename attribute to the file
        """
        pass

    def split_audio(self):
        filename_with_ext = self.filename

        logger.info(f"File size of {filename_with_ext} is {get_file_size(filename_with_ext)} bytes.")

        if get_file_size(filename_with_ext) > 7 * 1024 * 1024:  # File size greater than 7MB
            split_audio_file(filename_with_ext)
        else:
            os.rename(filename_with_ext, f"{self.filename}_part0.{self.audio_file_type}")

    def process_audio(self):
        self.get_audio()
        self.split_audio()

