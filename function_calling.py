import requests
import os
from getpass import getpass
from openai import OpenAI
import json


# ---------------------------------------------------------------------
# Environment Setup
# ---------------------------------------------------------------------

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass("Enter your OpenAI API key: ")

client = OpenAI(
    # Recommended: use environment variable for production
    api_key=os.environ.get("OPENAI_API_KEY"),
)

def get_weather(latitude, longitude):
    response = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m")
    data = response.json()
    return data['current']['temperature_2m']

tools = [{
    "type": "function",
    "name": "get_weather",
    "description": "Get current temperature for provided coordinates in celsius.",
    "parameters": {
        "type": "object",
        "properties": {
            "latitude": {"type": "number"},
            "longitude": {"type": "number"}
        },
        "required": ["latitude", "longitude"],
        "additionalProperties": False
    },
    "strict": True
}]

input_messages = [{"role": "user", "content": "What's the weather like in Paris today?"}]

response = client.responses.create(
    model="gpt-5.2",
    input=input_messages,
    tools=tools,
)

# Extract the tool call and arguments
tool_call = response.output[0]
print(tool_call)
args = json.loads(tool_call.arguments)
# Call the function
result = get_weather(args["latitude"], args["longitude"])
print(result)

# Append the tool call and result to the input messages
input_messages.append(tool_call) # append model's function call message
input_messages.append({ # append result message
    "type": "function_call_output",
    "call_id": tool_call.call_id,
    "output": str(result)
})

response_2 = client.responses.create(
    model="gpt-5.2",
    input=input_messages,
    tools=tools,
)
print(response_2.output_text)

# Output:
# ResponseFunctionToolCall(arguments='{"latitude":48.8566,"longitude":2.3522}', call_id='call_7CUH1h23GzHVaSvmek8temP0', name='get_weather', type='function_call', id='fc_008843bf705071850069aa142f5b70819391f53614854be2e7', status='completed')
# 12.1
# It’s about **12.1 °C** in **Paris** right now.