import os
import json
from getpass import getpass
import numpy as np
import requests
from openai import OpenAI

# https://colab.research.google.com/drive/16oeaa8j9F6BHZdB-diJ_ATQZs9xpJynJ?usp=sharing#scrollTo=4o4QYIcsIHsI

# temperature vs top_p
#
# Both control randomness in LLM text generation, but in different ways.
#
# ------------------------------------------------------------
# Example probability distribution for next token:
#
# Token   Probability
# A       0.40
# B       0.30
# C       0.20
# D       0.05
# E       0.05
# ------------------------------------------------------------
#
# temperature:
#   - Scales the probability distribution before sampling.
#   - Lower (0.0–0.3) → sharper distribution → picks A most of the time.
#   - Higher (1.0+) → flattens distribution → D and E become more likely.
#   - temperature = 0 → always picks A (highest probability token).
#
# top_p (nucleus sampling):
#   - Selects smallest set of tokens whose cumulative probability ≥ p.
#
#   Example:
#     top_p = 0.9
#     A (0.40) + B (0.30) + C (0.20) = 0.90
#     → Only A, B, C are considered.
#     → D and E are excluded entirely.
#
# Key difference:
#   - temperature reshapes probabilities.
#   - top_p removes low-probability tokens from consideration.
#
# Practical tip:
#   - Usually tune one, not both.
#   - Common defaults: temperature=0.7, top_p=0.9–1.0
#   - Deterministic setup: temperature=0, top_p=1

# API Key Setup - uses environment variable or prompts for input
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass("Enter your OpenAI API key: ")

client = OpenAI(
    # Replace with your actual API key or use: api_key=os.environ.get("OPENAI_API_KEY")
    api_key=os.environ.get("OPENAI_API_KEY"),
)

MODEL = "gpt-5.2"

prompt = "Write a one-sentence bedtime story about a unicorn."

response = client.responses.create(
    model=MODEL,
    input=prompt
)

print(f"Prompt: {prompt}")
print(f"Response: {response.output_text}")

# Show how to control generation with parameters
print("\nWith controlled parameters:")
response = client.responses.create(
    model=MODEL,
    input=prompt,
    temperature=0.7,  # Lower for more deterministic outputs
)

print(f"Response (controlled): {response.output_text}")


str_response = client.responses.create(
   model=MODEL,
    input=[
        {"role": "developer", "content": "You are a UI generator AI. Convert the user input into a UI."},
        {"role": "user", "content": "Make a User Profile Form"}
    ],
    text={
        "format": {
            "type": "json_schema",
            "name": "ui",
            "description": "Dynamically generated UI",
            "schema": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "description": "The type of the UI component",
                        "enum": ["div", "button", "header", "section", "field", "form"]
                    },
                    "label": {
                        "type": "string",
                        "description": "The label of the UI component, used for buttons or form fields"
                    },
                    "children": {
                        "type": "array",
                        "description": "Nested UI components",
                        "items": {"$ref": "#"}
                    },
                    "attributes": {
                        "type": "array",
                        "description": "Arbitrary attributes for the UI component, suitable for any element",
                        "items": {
                            "type": "object",
                            "properties": {
                              "name": {
                                  "type": "string",
                                  "description": "The name of the attribute, for example onClick or className"
                              },
                              "value": {
                                  "type": "string",
                                  "description": "The value of the attribute"
                              }
                          },
                          "required": ["name", "value"],
                          "additionalProperties": False
                      }
                    }
                },
                "required": ["type", "label", "children", "attributes"],
                "additionalProperties": False
            },
            "strict": True,
        },
    },
)

ui = json.loads(str_response.output_text)

print(f"Response (UI): {ui}")