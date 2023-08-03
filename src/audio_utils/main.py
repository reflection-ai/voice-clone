import os
from pydub import AudioSegment
from pydub.utils import mediainfo
import logging

log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.basicConfig(level=getattr(logging, log_level),
                    format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger()

AUDIO_FILE_TYPE = "mp4"

def get_file_size(file_path):
    return os.path.getsize(file_path)

def split_audio_file(file_path, max_size=7 * 1024 * 1024):  # 7MB
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

    while start < length_audio:
        chunk = audio[start:int(end)]
        filename_chunk = f"{file_path[:-4]}_part{counter}.mp3"
        chunk.export(filename_chunk, format="mp3", bitrate=bitrate)  # Keep the original format 'mp3'
        counter += 1
        start = end
        end += max_size_in_milliseconds  # Increment the end point

    logger.info(f"File split into {counter} parts.")
