import sys
import time

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

# Create a video generation job using Sora
video = client.videos.create(
    model="sora-2",
    prompt="A timelapse of a flower blooming in a sunlit garden, cinematic quality",
)

print(f"Video generation started! ID: {video.id}")
print(f"Initial status: {video.status}")

# Poll for completion with a progress bar
bar_length = 30
while video.status in ("in_progress", "queued"):
    video = client.videos.retrieve(video.id)
    progress = getattr(video, "progress", 0)

    filled = int((progress / 100) * bar_length)
    bar = "=" * filled + "-" * (bar_length - filled)
    status_text = "Queued" if video.status == "queued" else "Processing"

    sys.stdout.write(f"\r{status_text}: [{bar}] {progress:.1f}%")
    sys.stdout.flush()
    time.sleep(5)

sys.stdout.write("\n")

if video.status == "failed":
    message = getattr(getattr(video, "error", None), "message", "Video generation failed")
    print(f"Error: {message}")
else:
    print("Video generation completed!")

    # Download the video
    content = client.videos.download_content(video.id, variant="video")
    content.write_to_file("generated_video.mp4")
    print("Saved to generated_video.mp4")

    #Output:
    # Video generation started! ID: video_6996f8bd9dac8198af9a47b1c486322c08842d2a6d3a3b7c
    # Initial status: queued
    # Processing: [==============================] 100.0%
    # Video generation completed!
    # Saved to generated_video.mp4