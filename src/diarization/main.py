import os
import os
import subprocess
import pandas as pd
from typing import Optional, List, TypedDict, Dict
import whisperx
from whisperx import load_align_model, align
from whisperx.types import AlignedTranscriptionResult, TranscriptionResult
from whisperx.diarize import DiarizationPipeline, assign_word_speakers
import json
import src.audio_utils.main as audio_utils
from src.audio_processors.youtube_audio_processor import YouTubeAudioProcessor
from copy import deepcopy

from dotenv import load_dotenv
load_dotenv()

class SingleSegmentSpeaker(TypedDict):
    """
    A list of segments and word segments of a speech, with the speaker. 
    """
    start: float
    end: float
    speaker: str
    text: str

class Diarization:
    def __init__(self, hf_token: str, audio_file: str, model_name: str = "large-v2", device: str = "cuda"):
        self.hf_token = hf_token
        self.model_name = model_name
        self.device = device
        self.audio_file = audio_file

    @staticmethod
    def convert_to_wav(input_file: str, output_file: Optional[str] = None) -> str:
        """
        Converts an audio file to WAV format using FFmpeg.

        Args:
            input_file: The path of the input audio file to convert.
            output_file: The path of the output WAV file. If None, the output file will be created by replacing the input file
            extension with ".wav".

        Returns:
            None
        """
        if not output_file:
            output_file = os.path.splitext(input_file)[0] + ".wav"

        command = f'ffmpeg -i "{input_file}" -vn -acodec pcm_s16le -ar 44100 -ac 1 "{output_file}"'

        try:
            subprocess.run(command, shell=True, check=True)
            print(f'Successfully converted "{input_file}" to "{output_file}"')
            return output_file
        except subprocess.CalledProcessError as e:
            print(f'Error: {e}, could not convert "{input_file}" to "{output_file}"')
            raise Exception("could not convert to wav")

    def assign_speakers(
        self, diarization_result: pd.DataFrame, aligned_segments: AlignedTranscriptionResult
    ) -> List[SingleSegmentSpeaker]:
        """
        Assign speakers to each transcript segment based on the speaker diarization result.

        Args:
            diarization_result: Dictionary representing the diarized audio file, including the speaker embeddings and the number of speakers.
            aligned_segments: Dictionary representing the aligned transcript segments.

        Returns:
            A list of dictionaries representing each segment of the transcript, including the start and end times, the
            spoken text, and the speaker ID.
        """
        result_segments = assign_word_speakers(
            diarization_result, aligned_segments
        )
        results_segments_w_speakers: List[SingleSegmentSpeaker] = []

        with open("blah/AS.txt", 'w') as file:
            file.write(json.dumps(aligned_segments, indent=4))

        with open("blah/RS.txt", 'w') as file:
            file.write(json.dumps(result_segments, indent=4))

        for result_segment in result_segments["segments"]:
            results_segments_w_speakers.append(
                {
                    "start": result_segment["start"],
                    "end": result_segment["end"],
                    "text": result_segment["text"],
                    "speaker": result_segment["speaker"],
                }
            )
        return results_segments_w_speakers

    def transcribe(self) -> TranscriptionResult:
        """
        Transcribe an audio file using a speech-to-text model.

        Returns:
            A dictionary representing the transcript, including the segments, the language code, and the duration of the audio file.
        """
        model = whisperx.load_model(self.model_name, self.device)
        result = model.transcribe(self.audio_file)
        return result

    def diarize(self) -> pd.DataFrame:
        """
        Perform speaker diarization on an audio file.

        Args:
            audio_file: Path to the audio file to diarize.
            hf_token: Authentication token for accessing the Hugging Face API.

        Returns:
            A DataFrame representing the diarized audio file with start, end, and speaker columns.
        """
        diarization_pipeline = DiarizationPipeline(use_auth_token=self.hf_token, device=self.device)
        diarization_result = diarization_pipeline(self.audio_file)
        return diarization_result


    def align_segments(
        self,
        transcriptResults: TranscriptionResult,
    ) -> AlignedTranscriptionResult:
        """
        Align the transcript segments using a pretrained alignment model.

        Args:
            segments: List of transcript segments to align.
            language_code: Language code of the audio file.
            audio_file: Path to the audio file containing the audio data.
            device: The device to use for inference (e.g., "cpu" or "cuda").

        Returns:
            A dictionary representing the aligned transcript segments.
        """

        model_a, metadata = load_align_model(language_code=transcriptResults["language"], device=self.device)
        result_aligned = align(transcriptResults["segments"], model_a, metadata, self.audio_file, self.device)
        return result_aligned

    def transcribe_and_diarize(
        self,
    ) -> List[SingleSegmentSpeaker]:
        """
        Transcribe an audio file and perform speaker diarization to determine which words were spoken by each speaker.

        Args:
            audio_file: Path to the audio file to transcribe and diarize.

        Returns:
            A list of dictionaries representing each segment of the transcript, including the start and end times, the
            spoken text, and the speaker ID.
            [
                {
                    "start": <float>
                    "end": <float>
                    "speaker": <string>
                    "text": <string>
                }, ...
            ]
        """
        if not self.audio_file or type(self.audio_file) != str:
            raise Exception("no audio file set")
        if self.audio_file == None:
            raise Exception("no audio file set")

        if not audio_utils.is_wav_file(self.audio_file):
            self.audio_file = self.convert_to_wav(self.audio_file)

        transcript = self.transcribe()
        with open("blah/transcript.txt", 'w') as file:
            file.write(json.dumps(transcript, indent=4))
        aligned_segments = self.align_segments(transcript)
        with open("blah/aligned_segments.txt", 'w') as file:
            file.write(json.dumps(aligned_segments, indent=4))
        diarization_result = self.diarize()

        results_segments_w_speakers = self.assign_speakers(diarization_result, aligned_segments)

        return results_segments_w_speakers


    def process_and_save(self, output_path: Optional[str] = None) -> List[SingleSegmentSpeaker]:
        results = self.transcribe_and_diarize()
        results = compress_segments(results)

        print(results)
        if output_path:
            with open(os.path.join(output_path, 'results_segments_w_speakers.json'), 'w') as file:
                json.dump(results, file, indent=4)

        return results

def get_speaker_parts( data: List[SingleSegmentSpeaker], speakers: str | List[str]) -> List[SingleSegmentSpeaker]:
    if isinstance(speakers, str):
        speakers = [speakers]

    parts = [item for item in data if item['speaker'] in speakers]
    return parts

def rename_speakers(
    data: List[SingleSegmentSpeaker],
    new_speaker_name: str,
    speakers_to_replace: Optional[List[str]] = None
) -> List[SingleSegmentSpeaker]:
    new_data = deepcopy(data)
    for item in new_data:
        if speakers_to_replace is None or item['speaker'] in speakers_to_replace:
            item['speaker'] = new_speaker_name
    return new_data

def merge_segments(list1: List[SingleSegmentSpeaker], list2: List[SingleSegmentSpeaker]) -> List[SingleSegmentSpeaker]:
    merged = list1 + list2
    merged.sort(key=lambda x: (x['start'], x['end']))
    return merged

def compress_segments(segments: List[SingleSegmentSpeaker]) -> List[SingleSegmentSpeaker]:
    """
    Compresses a list of speaker segments by merging consecutive segments spoken by the same speaker.

    This method takes a list of segments, each containing start and end times, text, and speaker ID, 
    and merges consecutive segments that are spoken by the same speaker. The start time of the first segment 
    and the end time of the last segment in a sequence of consecutive segments are used for the merged segment's 
    start and end times, and the texts are concatenated.

    Args:
        segments: A list of speaker segments with start time, end time, text, and speaker ID.

    Returns:
        A compressed list of speaker segments with merged consecutive segments spoken by the same speaker.
    """
    if not segments:
        return []

    compressed_segments: List[SingleSegmentSpeaker] = [segments[0]]

    for segment in segments[1:]:
        last_segment = compressed_segments[-1]

        if last_segment["speaker"] == segment["speaker"]:
            last_segment["end"] = segment["end"]
            last_segment["text"] += " " + segment["text"]
        else:
            compressed_segments.append(segment)

    return compressed_segments

def transform_data(data: List[SingleSegmentSpeaker]) -> Dict[str, List[Dict[str, str]]]:
    return {
        "conversations": [{"from": item["speaker"], "value": item["text"]} for item in data]
    }

if __name__ == "__main__":
    yt = YouTubeAudioProcessor("https://www.youtube.com/watch?v=-XE-OC2ZYB4", "", "why-so-sour")
    yt.get_audio()
    hf_token = os.getenv('HF_API_KEY') or ""
    language_code = "en"
    d = Diarization(hf_token, yt.filename)
    d.process_and_save('blah')
