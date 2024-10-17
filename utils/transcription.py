import time
import os
import assemblyai
from utils.google_cloud import upload_to_gcs
from moviepy.editor import VideoFileClip, AudioFileClip
from google.cloud import speech
from utils.audio import split_audio
from google.api_core.exceptions import GoogleAPICallError
from dotenv import load_dotenv

load_dotenv()

# GCLOUD_PROJECT_ID = os.environ['GCLOUD_PROJECT']
assemblyai.settings.api_key = os.environ['ASSEMBLY_API_KEY']

# transcribe the audio using assembly ai speech to text


def transcribe_from_audio(audio_path, bucket_name):

    transcriptions = []

    # initialize assemblyai transcriber
    transcriber = assemblyai.Transcriber()

    audio_file = audio_path.split(".")[0]

    # setup the assemblyai config
    config = assemblyai.TranscriptionConfig(speaker_labels=True)

    transcript = transcriber.transcribe(audio_path, config)
    print(transcript.text)

    for utterance in transcript.utterances:
        print(f"{utterance.text}")
        transcriptions.append(utterance.text)

    if transcript.status == assemblyai.TranscriptStatus.error:
        print(f"Transcription Failed: {transcript.error}")
        return f"Transcription Failed: {transcript.error}"

    transcriptions = "".join(transcriptions)

    return transcriptions
