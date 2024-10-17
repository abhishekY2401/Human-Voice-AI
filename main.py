import streamlit as st
from utils.audio import extract_audio_from_video_file, convert_text_to_speech, merge_audio_with_video
from utils.transcription import transcribe_from_audio
import openai
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()


# Replace with your actual key. if you don't have one, get from Azure or from Community https://curious.pm
azure_openai_key = os.environ["AZURE_OPENAI_KEY"]
azure_openai_endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]


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

        status_text.write("transcribing audio to text..")
        audio_transcript = transcribe_from_audio(
            audio_file_path, "human-voice-audio")
        print(audio_transcript)
        current_step += 1
        progress_bar.progress(current_step / total_steps)

        status_text.write("correcting grammars and noises in human voice..")
        output_transcript = ""
        # pass the transcript to openai gpt4o
        try:
            headers = {
                "Content-Type": "application/json",
                "api-key": azure_openai_key
            }

            message_content = f"""
                Correct the mispronounced grammars, the human sounds like umms and hmms present inside the below given
                transcription. Do not paraphrase or summarize the transcript
                Transcript: {audio_transcript}
            """

            data = {
                "messages": [{"role": "user", "content": message_content}]
            }

            response = requests.post(
                azure_openai_endpoint, headers=headers, json=data)

            if response.status_code == 200:
                result = response.json()
                output_transcript = (
                    result["choices"][0]["message"]["content"].strip()
                )
                st.success(result["choices"][0]
                           ["message"]["content"].strip())
            else:
                # Handle errors if the request was not successful
                st.error(
                    f"Failed to connect or retrieve response: {
                        response.status_code} - {response.text}"
                )
        except Exception as e:
            # Handle any exceptions that occur during the request
            st.error(f"Failed to connect or retrieve response: {str(e)}")

        current_step += 1
        progress_bar.progress(current_step / total_steps)

        status_text.write("converting text to speech..")
        audio_url = convert_text_to_speech(output_transcript)

        current_step += 1
        progress_bar.progress(current_step / total_steps)

        status_text.write("merging human voice with AI voice..")
        output_video = "output_video.mp4"
        merge_audio_with_video(video_temp_file, audio_url, output_video)

        current_step += 1
        progress_bar.progress(current_step / total_steps)


if __name__ == '__main__':
    main()
