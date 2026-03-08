
#https://colab.research.google.com/drive/1Kj6zRAcs9ZcuupSnRNgy5g5GeR4FGgA7?usp=sharing#scrollTo=kGJyW_XRKU6F
# Before working with openAI, anthrope or google or any llm you need to figure out what token estimate is going to cost you before you make a call to model provider

import os
from getpass import getpass
from openai import OpenAI
import tiktoken
import json

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def compare_encodings(example_string: str) -> None:
    """Prints a comparision of three string encodings."""
    print(f'\nExample strings:"{example_string}"')
    for encoding_name in ["r50k_base", "p50k_base", "cl100k_base", "o200k_base"]:
        encoding = tiktoken.get_encoding(encoding_name)
        token_integers = encoding.encode(example_string)
        num_tokens = len(token_integers)
        token_bytes = [encoding.decode_single_token_bytes(token) for token in token_integers]
        print()
        print(f"{encoding_name}: {num_tokens} tokens")
        print(f"token integers: {token_integers}")
        print(f"token bytes: {token_bytes}")

#quiet useful in cost estimating budget, rate limiting(in production environment), input tokens, output tokens and cached input and output tokens, for conversation app
# Refer https://platform.claude.com/docs/en/about-claude/pricing
# https://ai.google.dev/gemini-api/docs/pricing
# https://openai.com/api/pricing/
def num_tokens_from_messages(messages, model="gpt-5"):
    """Return the number of tokens used by a list of messages"""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using o200k_ base encoding.")
        encoding = tiktoken.get_encoding("o200k_base")
    if model in {
        "gpt-5",
        "gpt-5-0314",
        "gpt-5-32k-0314",
        "gpt-5-0613",
        "gpt-5-32k-0613",
        "gpt-5-2024-08-06"
    }:
        tokens_per_message = 3
        tokens_per_name =1
    elif "gpt-5" in model:
        print("Warning: gpt-5 may update over time. Returning num tokens assuming gpt-5.")
        return num_tokens_from_messages(messages, model="gpt-5")
    elif "gpt-5" in model:
        print("Warning: gpt-5 may update over time. Returning num tokens assuming gpt-5-0314.")
        return num_tokens_from_messages(messages, model="gpt-5-0314") 
    elif "gpt-5" in model:
        print("Warning: gpt-5 may update over time. Returning num tokens assuming   gpt-5-32k-0314.")
        return num_tokens_from_messages(messages, model="gpt-5-32k-0314") 
    elif "gpt-5" in model:
        print("Warning: gpt-5 may update over time. Returning num tokens assuming   gpt-5-0613.")
        return num_tokens_from_messages(messages, model="gpt-5-0613") 
    elif "gpt-5" in model:
        print("Warning: gpt-5 may update over time. Returning num tokens assuming   gpt-5-32k-0613.")
        return num_tokens_from_messages(messages, model="gpt-5-32k-0613") 
    elif "gpt-5" in model:
        print("Warning: gpt-5 may update over time. Returning num tokens assuming   gpt-5-2024-08-06.")
        return num_tokens_from_messages(messages, model="gpt-5-2024-08-06") 
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}."""
        )
    num_tokens =0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3
    return num_tokens



def num_tokens_for_tools(tools, messages, model="gpt-5"):
    """
    Estimate the number of tokens used in a prompt that includes tool calling.

    The estimation works by:
    1. Counting tokens in the messages.
    2. Counting tokens in the semantic text of the tool schema
       (function name, descriptions, parameter names, enums).
    3. Adding approximate schema overhead tokens that the OpenAI API
       internally adds when converting the JSON schema into the model's
       internal tool representation.
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")

    num_tokens = 0

    # ---- message structure ----
    tokens_per_message = 3
    tokens_per_name = 1

    # ---- tool schema overhead ----
    func_init = 10
    prop_init = 5
    enum_init = 3
    func_end = 12

    # -------------------------
    # count messages
    # -------------------------
    for message in messages:
        num_tokens += tokens_per_message

        for key, value in message.items():
            num_tokens += len(encoding.encode(value))

            if key == "name":
                num_tokens += tokens_per_name

    num_tokens += 3  # assistant priming

    # -------------------------
    # count tools
    # -------------------------
    if tools:

        for tool in tools:

            num_tokens += func_init

            num_tokens += len(encoding.encode(tool["name"]))
            num_tokens += len(encoding.encode(tool.get("description", "")))

            params = tool.get("parameters", {})
            properties = params.get("properties", {})

            for prop_name, prop in properties.items():

                num_tokens += prop_init

                num_tokens += len(encoding.encode(prop_name))
                num_tokens += len(encoding.encode(prop.get("type", "")))
                num_tokens += len(encoding.encode(prop.get("description", "")))

                if "enum" in prop:
                    num_tokens += enum_init

                    for item in prop["enum"]:
                        num_tokens += len(encoding.encode(item))

            for req in params.get("required", []):
                num_tokens += len(encoding.encode(req))

            num_tokens += func_end

    return num_tokens


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

    enc = tiktoken.get_encoding("o200k_base") #encoding for gpt-5. As model progress there can be different encoding base

    # To get the tokeniser corresponding to a specific model in the OpenAI API:
    encModel = tiktoken.encoding_for_model("gpt-5")
    encValue = encModel.encode('tiktok is great!')
    # print(encValue) 
    # #Output: [83, 163493, 382, 2212, 0]

    # print(num_tokens_from_string("tiktok is great!", "o200k_base"))

    # print(encModel.decode(encValue))
    # #decode() can be applied to single tokens, beware that it can be lossy for tokens that aren't on utf-8 boundaries
    # print([encModel.decode_single_token_bytes(token) for token in encValue])
    # #Output: [b't', b'iktok', b' is', b' great', b'!'] (the b in front of the strings are byte strings) only use for single token for eg: encModel.encode('!')
    # compare_encodings("antidisestablishmentarianism")
    # compare_encodings("2 + 2 = 4")
    # compare_encodings("大家好 早上好")

    #Output: r50k_base: 5 tokens
    # token integers: [415, 29207, 44390, 3699, 1042]
    # token bytes: [b'ant', b'idis', b'establishment', b'arian', b'ism']

    # p50k_base: 5 tokens
    # token integers: [415, 29207, 44390, 3699, 1042]
    # token bytes: [b'ant', b'idis', b'establishment', b'arian', b'ism']

    # cl100k_base: 6 tokens
    # token integers: [519, 85342, 34500, 479, 8997, 2191]
    # token bytes: [b'ant', b'idis', b'establish', b'ment', b'arian', b'ism']

    # o200k_base: 6 tokens
    # token integers: [493, 129901, 376, 160388, 21203, 2367]
    # token bytes: [b'ant', b'idis', b'est', b'ablishment', b'arian', b'ism']

    # Example strings:"2 + 2 = 4"

    # r50k_base: 5 tokens
    # token integers: [17, 1343, 362, 796, 604]
    # token bytes: [b'2', b' +', b' 2', b' =', b' 4']

    # p50k_base: 5 tokens
    # token integers: [17, 1343, 362, 796, 604]
    # token bytes: [b'2', b' +', b' 2', b' =', b' 4']

    # cl100k_base: 7 tokens
    # token integers: [17, 489, 220, 17, 284, 220, 19]
    # token bytes: [b'2', b' +', b' ', b'2', b' =', b' ', b'4']

    # o200k_base: 7 tokens
    # token integers: [17, 659, 220, 17, 314, 220, 19]
    # token bytes: [b'2', b' +', b' ', b'2', b' =', b' ', b'4']

    messages  = [
        {
            "role": "developer",
            "content": "You are a helpful assistant that can answer to questions about the weather.",
        },
        {
            "role": "user",
            "content" : "What's the weather like in San Francisco?"
        }
    ]
    #print(num_tokens_from_messages(messages, "gpt-5")) # 33 tokens( will end up spending less if openai or anthropic cache your input tokens over time to reduce the amount you send it to gpus)

    # tool-calling call out specific python function, define tools in api format
    tools = [
        {
            "type": "function",
            "name": "get_current_weather",
            "description": "Get current temperature in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA"
                    },
                    "unit": {
                        "type": "string",
                        "description": "The unit of temperature to return",
                        "enum": ["celsius", "fahrenheit"]
                    }
                },
                "required": ["location"]
            }
        }
    ]
    example_messages  = [
        {
            "role": "developer",
            "content": "You are a helpful assistant that can answer to questions about the weather.",
        },
        {
            "role": "user",
            "content" : "What's the weather like in San Francisco?"
        }
    ]
    for model in ["gpt-5"]:
        print(model)

        estimated = num_tokens_for_tools(tools, example_messages, model)

        print(f"{estimated} prompt tokens counted by num_tokens_for_tools().")

        response = client.responses.create(
            model=model,
            input=example_messages,
            tools=tools
        )

        print(f"{response.usage.input_tokens} prompt tokens counted by OpenAI API.")
        print(f"{response.usage}")


if __name__=="__main__":
    main()






