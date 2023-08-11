import os
import os
import subprocess
import pandas as pd
from typing import Optional, List, TypedDict
import whisperx
from whisperx import load_align_model, align
from whisperx.types import AlignedTranscriptionResult, TranscriptionResult
from whisperx.diarize import DiarizationPipeline, assign_word_speakers
import json
import src.audio_utils.main as audio_utils

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

        print(results)
        if output_path:
            with open(os.path.join(output_path, 'results_segments_w_speakers.json'), 'w') as file:
                json.dump(results, file, indent=4)

        return results

if __name__ == "__main__":
    hf_token = "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"
    language_code = "en"
    audio_file = "ALex hormozi testing_20230806111200_part4.wav"
    d = Diarization(hf_token, audio_file)
    d.process_and_save('blah')
