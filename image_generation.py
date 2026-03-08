import os
from getpass import getpass
from openai import OpenAI
from pydantic import BaseModel
import base64
from IPython.display import display, Image as IPImage


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

# # Generate an image using the Responses API with the image_generation tool
# response = client.responses.create(
#     model=MODEL,
#     input="Generate a watercolor painting of a cozy coffee shop on a rainy day",
#     tools=[{
#         "type": "image_generation",
#         "quality": "high",
#         "size": "1024x1024"
#     }]
# )

# # Extract the base64-encoded image from the response output
# image_data = [
#     output.result
#     for output in response.output
#     if output.type == "image_generation_call"
# ]

# if image_data:
#     image_bytes = base64.b64decode(image_data[0])

#     # Save to file
#     with open("generated_image.png", "wb") as f:
#         f.write(image_bytes)

#     # Display inline in the notebook
#     display(IPImage(data=image_bytes))
#     print("Image generated and saved to generated_image.png")

# You can also generate images with transparent backgrounds (useful for logos, sprites, etc.)
response = client.responses.create(
    model=MODEL,
    input="A cute robot mascot giving a thumbs up, simple flat design",
    tools=[{
        "type": "image_generation",
        "background": "transparent",
        "quality": "high",
        "output_format": "png"
    }]
)

image_data = [
    output.result
    for output in response.output
    if output.type == "image_generation_call"
]

if image_data:
    image_bytes = base64.b64decode(image_data[0])

    with open("mascot_transparent.png", "wb") as f:
        f.write(image_bytes)

    display(IPImage(data=image_bytes))
    print("Transparent background image generated!")