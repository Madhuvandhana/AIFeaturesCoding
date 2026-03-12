import os
from getpass import getpass
from openai import OpenAI
import tiktoken
import json
import requests

def get_weather(latitude, longitude):
    response = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    )
    data = response.json()
    return data['current']['temperature_2m']

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
    MODEL = "gpt-5.2"
    # Define the get_weather tool with strict mode
    tools = [{
        "type": "function",
        "name": "get_weather",
        "description": "Get current temperature for provided coordinates in celsius.",
        "parameters": {
            "type": "object",
            "properties": {
                "latitude": {"type": "number", "description": "Latitude of the location."},
                "longitude": {"type": "number", "description": "Longitude of the location."}
            },
            "required": ["latitude", "longitude"],
            "additionalProperties": False
        },
        "strict": True
    }]

    # Input message asking about the weather in Paris
    input_messages = [{"role": "user", "content": "What's the weather like in Paris today?"}]

    # Call the API
    response = client.responses.create(
        model=MODEL,
        input=input_messages,
        tools=tools
    )

    # Print the model's output (expected to include a function call)
    print("Get Weather Response Output:", response.output)

    # If the model calls the function, access its attributes (note the use of dot-access).
    #We get the args from the tool and then tell the tool, we know  you have that tool call to make and here
    #is the result
    if response.output and response.output[0].type == "function_call":
        tool_call = response.output[0]
        args = json.loads(tool_call.arguments)
        weather_result = get_weather(args['latitude'], args['longitude'])
        print(f"Weather Result: {weather_result}°C")

    # Add the function call output to the input messages and call the API again.
    #model uses the tool results okay great, here's the temperature
    input_messages.append(tool_call)  # append model's function call message
    input_messages.append({                               # append result message
        "type": "function_call_output",
        "call_id": tool_call.call_id,
        "output": str(json.dumps(weather_result) )
    })

    # Call the API again with the updated input messages
    response = client.responses.create(
        model=MODEL,
        input=input_messages,
        tools=tools
    )

    print("Get Weather Response Output:", response.output_text)

    # stream = client.responses.create(
    #     model=MODEL,
    #     input=[{"role": "user", "content": "What's the weather like in Paris today?"}],
    #     tools=tools,
    #     stream=True
    # )

    # for event in stream:
    #     print(event)

if __name__=="__main__":
    main()

#Output: Get Weather Response Output: [ResponseFunctionToolCall(arguments='{"latitude":48.8566,"longitude":2.3522}', call_id='call_L8vZQxBneLLzUMwCXfbXpsFM', name='get_weather', type='function_call', id='fc_09dc83d0b79292db0069b110bb6b708194a5e14f975d085243', status='completed')]
# Weather Result: 10.5°C
# Get Weather Response Output: It’s **about 10.5 °C** in **Paris** right now (based on the latest available reading for central Paris at **48.8566, 2.3522**).