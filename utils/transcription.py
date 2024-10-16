import time
import os
from utils.google_cloud import upload_to_gcs
from moviepy.editor import VideoFileClip, AudioFileClip
from google.cloud import speech
from utils.audio import split_audio
from google.api_core.exceptions import GoogleAPICallError
from dotenv import load_dotenv

load_dotenv()

GCLOUD_PROJECT_ID = os.environ['GCLOUD_PROJECT']

# transcribe the audio using google speech to text


def transcribe_from_audio(audio_path, bucket_name):
    client = speech.SpeechClient()

    transcriptions = []
    # audio_chunks = split_audio(audio_path)
    audio_file = audio_path.split(".")[0]

    gcs_uri = upload_to_gcs(bucket_name, audio_path, f"temp_{audio_file}.wav")

    # for i, chunk in enumerate(audio_chunks):

    #     # create a temp file chunk to read audio chunk content
    #     temp_chunk_path = f"audios/temp_chunk_{i}.wav"
    #     chunk.export(temp_chunk_path, format="wav")

    #     with open(temp_chunk_path, "rb") as audio_file:
    #         audio_content = audio_file.read()

    audio_recognition = speech.RecognitionAudio(uri=gcs_uri)

    config = speech.RecognitionConfig(
        enable_automatic_punctuation=True,
        # encoding='LINEAR16',
        language_code='en-US',
        sample_rate_hertz=44100,
        audio_channel_count=2,
    )

    # continue transcription in the background
    operation = client.long_running_recognize(
        config=config, audio=audio_recognition)

    try:
        # poll the operation until the transcription is finish running
        response = operation.result(timeout=600)

    except GoogleAPICallError as error:
        print(f"An error occurred: {error}")

    for result in response.results:
        transcriptions.append(result.alternatives[0].transcript)

    # os.remove(temp_chunk_path)

    audio_transcript = "".join(transcriptions)
    print(audio_transcript)

    return audio_transcript
