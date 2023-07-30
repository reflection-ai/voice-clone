import os
import sys
import time
from pydub import AudioSegment
from pytube import YouTube
from urllib.parse import urlparse
from pydub.utils import mediainfo

AUDIO_FILE_TYPE = "mp4"

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc, 'youtube' in result.netloc])
    except ValueError:
        return False

def download_audio(url, filename):
    yt = YouTube(url)
    filename_timestamped = f"{filename}_{time.strftime('%Y%m%d%H%M%S')}"
    # yt.streams.filter(only_audio=True).first().download(filename=f"{filename_timestamped}{AUDIO_FILE_TYPE}")
    yt.streams.filter(only_audio=True).first().download(filename=f"{filename_timestamped}.{AUDIO_FILE_TYPE}")
    return filename_timestamped

def get_file_size(file_path):
    return os.path.getsize(file_path)

def split_file(file_path, max_size=7 * 1024 * 1024):  # 7MB
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

    print(f"File split into {counter} parts.")

if __name__ == "__main__":
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: python script.py <YouTube_URL> <folder_path> [<filename>]")
        sys.exit(1)

    video_url = sys.argv[1]

    if not is_valid_url(video_url):
        print("You provided an invalid URL.")
        sys.exit(1)

    folder_path = sys.argv[2]
    filename = sys.argv[3] if len(sys.argv) == 4 else 'downloaded_audio'
    filename = os.path.join(folder_path, filename)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    filename = download_audio(video_url, filename)

    filename_with_ext = f"{filename}.{AUDIO_FILE_TYPE}"

    print(f"File size of {filename_with_ext} is {get_file_size(filename_with_ext)} bytes.")

    if get_file_size(filename_with_ext) > 7 * 1024 * 1024:  # File size greater than 7MB
        split_file(filename_with_ext)
