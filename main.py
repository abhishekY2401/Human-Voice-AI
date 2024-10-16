import streamlit as st
from utils.audio import extract_audio_from_video_file
from utils.transcription import transcribe_from_audio
import openai
import requests
import json


def main():

    total_steps = 5
    current_step = 0

    st.title("Transform Videos using AI Voice")

    # define file input block for uploading video
    upload_file = st.file_uploader(
        "Upload a video", type=["mp4", "mov", "avi"])

    # if the video file is uploaded start the processing
    if upload_file is not None:

        # save the uploaded video file in disk
        file_name = upload_file.name.split(".")[0]

        temp_file = f"{file_name}_temp_video.mp4"
        video_temp_file = f"videos/{file_name}_temp_video.mp4"

        with open(video_temp_file, "wb") as f:
            f.write(upload_file.read())

        status_text = st.empty()
        progress_bar = st.progress(0)

        status_text.write("extracting audio from the video file...")
        audio_file_path = extract_audio_from_video_file(temp_file)
        current_step += 1
        progress_bar.progress(current_step / total_steps)

        status_text.write("transcribing audio to text")
        audio_transcript = transcribe_from_audio(
            audio_file_path, "human-voice-audio")
        print(audio_transcript)
        current_step += 1
        progress_bar.progress(current_step / total_steps)


if __name__ == '__main__':
    main()
