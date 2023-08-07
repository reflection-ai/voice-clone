import os
from pydub import AudioSegment
from pydub.utils import mediainfo
import logging
from typing import List

log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.basicConfig(level=getattr(logging, log_level),
                    format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger()

MAX_SIZE = 7 * 1024 * 1024

def get_file_size(file_path: str) -> int:
    """
    Returns the size of the file at the given path.

    Args:
    - file_path (str): Path to the file.

    Returns:
    - int: Size of the file in bytes.
    """
    return os.path.getsize(file_path)

def split_audio_file(file_path: str, max_size: int = MAX_SIZE) -> List[str]:
    """
    Splits an audio file into multiple parts if its size exceeds the specified max size. 
    Each part will be approximately of max_size or less.
    If the audio doesn't need splitting, the list contains the original file path.

    Args:
    - file_path (str): Path to the audio file to be split.
    - max_size (int, optional): Maximum size in bytes for each audio part. Default is 7MB.

    Returns:
    - list[str]: List of paths to the audio parts.
    """
    audio = AudioSegment.from_file(file_path)
    audio_info = mediainfo(file_path)
    bitrate = audio_info['bit_rate']
    
    length_audio = len(audio)  # Duration of audio in milliseconds
    total_bytes = os.path.getsize(file_path)  # Total size in bytes

    bytes_per_millisecond = total_bytes / length_audio  # Bytes per millisecond
    max_size_in_milliseconds = max_size / bytes_per_millisecond  # Max size in milliseconds

    start = 0
    end = max_size_in_milliseconds  # Now in milliseconds
    counter = 0
    parts = []

    while start < length_audio:
        chunk = audio[start:int(end)]
        filename_chunk = f"{file_path[:-4]}_part{counter}.mp3"
        chunk.export(filename_chunk, format="mp3", bitrate=bitrate)  # Keep the original format 'mp3'
        parts.append(filename_chunk)
        counter += 1
        start = end
        end += max_size_in_milliseconds  # Increment the end point

    if not parts:
        parts.append(file_path)

    logger.info(f"File split into {len(parts)} parts.")
    return parts
