import os
from getpass import getpass
from openai import OpenAI
import tiktoken
import json
def main() :
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
    # # Request the model to recite the tongue twister five times using streaming
    # stream = client.responses.create(
    #     model=MODEL,
    #     input=[{
    #         "role": "user",
    #         "content": "Recite 'Peter Piper picked a peck of pickled peppers' five times in a row."
    #     }],
    #     stream=True
    # )

    # # Iterate over streaming events and print details
    # for event in stream:
    #     # Depending on the event type, you can handle it accordingly
    #     if hasattr(event, 'type'):
    #         print(f"Event Type: {event.type}")
    #     # If the event includes a delta with content, print it
    #     if hasattr(event, 'delta') and event.delta:
    #         print(f"Delta Content: {event.delta}")
    #     # Print a separator for clarity
    #     print("-------------------------")

    # Request the model to recite the tongue twister five times using streaming
    stream = client.responses.create(
        model=MODEL,
        input=[{
            "role": "user",
            "content": "Recite 'Peter Piper picked a peck of pickled peppers' five times in a row."
        }],
        stream=True
    )

    text = ''

    # Iterate over streaming events and print details
    for event in stream:
        # Depending on the event type, you can handle it accordingly
        if event.type == 'response.output_text.delta':
            text += event.delta
            print(text)

if __name__=="__main__":
    main()

#Refer: https://github.com/BrightPool/udemy-prompt-engineering-course/blob/main/openai_features_and_functionality