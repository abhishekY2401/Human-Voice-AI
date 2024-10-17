# define utils for extraction and processing of voice
import os
import time
from moviepy.editor import VideoFileClip, AudioFileClip
import uuid
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from google.api_core.exceptions import GoogleAPICallError
from pydub import AudioSegment
from dotenv import load_dotenv

load_dotenv()


ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')


def extract_audio_from_video_file(video_path):
    '''
    Extract human voice from uploaded video file 
    '''

    video = VideoFileClip(f"videos/{video_path}")

    # get video filename
    filename = video_path.split(".")[0]

    audio_path = f'audios/{filename}_audio.wav'

    time.sleep(2)
    # copy the audio content to temp file
    video.audio.write_audiofile(audio_path)

    return audio_path


# split the audio in chunk
def split_audio(audio_path, max_duration_per_chunk=30):

    audio = AudioSegment.from_file(audio_path)
    audio = audio.set_channels(1)

    # calculate total duration for the audio
    total_duration = len(audio)
    print("duration: ", total_duration)

    max_duration_per_chunk_ms = max_duration_per_chunk * 1000

    num_chunks = int(total_duration // max_duration_per_chunk_ms) + \
        (total_duration % (max_duration_per_chunk_ms) > 0)
    print("chunks:", num_chunks)

    # maintain a buffer to store the audio chunks
    audio_chunks = []

    for i in range(num_chunks):
        start_time = i * max_duration_per_chunk_ms
        end_time = min((i + 1) * max_duration_per_chunk_ms *
                       1000, total_duration)

        chunk = audio[start_time: end_time]

        audio_chunks.append(chunk)

    return audio_chunks


def convert_text_to_speech(audio_transcription):

    client = ElevenLabs(
        api_key=ELEVENLABS_API_KEY,
    )

    # setup voice configuration
    voice_config = VoiceSettings(
        stability=0.0,
        similarity_boost=1.0,
        style=0.0,
        use_speaker_boost=True
    )

    response = client.text_to_speech.convert(
        voice_id="pNInz6obpgDQGcFmaJgB",  # Adam pre-made voice
        output_format="mp3_22050_32",
        text=audio_transcription,
        model_id="eleven_turbo_v2_5",  # use the turbo model for low latency
        voice_settings=voice_config
    )

    audio_file = f"{uuid.uuid4()}.mp3"

    with open(audio_file, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)

    print(f"{audio_file}: A new audio file was saved successfully!")

    # Return the path of the saved audio file
    return audio_file


def merge_audio_with_video(video_path, audio_path, output_path):

    video_clip = VideoFileClip(video_path)

    audio_clip = AudioFileClip(audio_path)

    # set the new audio to new video
    video_with_ai_audio = video_clip.set_audio(audio_clip)

    video_with_ai_audio.write_videofile(
        output_path, codec="libx264", audio_codec="aac")

    print(f"Video with merged audio saved at: {output_path}")
