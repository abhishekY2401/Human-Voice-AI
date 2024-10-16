# define utils for extraction and processing of voice

import time
from moviepy.editor import VideoFileClip, AudioFileClip
from google.cloud import texttospeech
from google.api_core.exceptions import GoogleAPICallError
from pydub import AudioSegment


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

    client = texttospeech.TextToSpeechClient()

    # set the transcription to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=audio_transcription)

    # build voice configuration
    voice = texttospeech.VoiceSelectionParams(
        language_code='en-US', ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # create new audio file
    with open("output_transcription.mp3", "wb") as out:
        # write the response to audio file
        out.write(response.audio_content)
        print('Audio content written to file "output.mp3"')
