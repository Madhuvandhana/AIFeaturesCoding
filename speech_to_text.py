import os
from getpass import getpass
from openai import OpenAI


# ---------------------------------------------------------------------
# Environment Setup
# ---------------------------------------------------------------------

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass("Enter your OpenAI API key: ")

client = OpenAI(
    # Recommended: use environment variable for production
    api_key=os.environ.get("OPENAI_API_KEY"),
)
audio_file= open("speech.mp3", "rb")

transcription = client.audio.transcriptions.create(
    model="gpt-4o-mini-transcribe", file=audio_file
)

print(transcription.text)
audio_file.close()