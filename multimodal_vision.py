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

MODEL = "gpt-5-mini"
image_url = "https://images.unsplash.com/photo-1579546929518-9e396f3cc809?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxleHBsb3JlLWZlZWR8MXx8fGVufDB8fHx8&w=1000&q=80"

response = client.responses.create(
    model=MODEL,
    input=[{
        "role": "user",
        "content": [
            {"type": "input_text", "text": "what's in this image?"},
            {
                "type": "input_image",
                "image_url": image_url,
            },
        ],
    }],
)

print(response.output_text)

# Output:
# This is an abstract, softly blended color gradient — no distinct objects or people. It transitions from warm pinks and peaches at the top/left to cyan and blues toward the center/right, with a smooth, blurred look (landscape orientation). It looks like a wallpaper or background image.