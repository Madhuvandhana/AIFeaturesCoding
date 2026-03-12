import os
from getpass import getpass
from openai import OpenAI
import tiktoken
import json
import requests

def get_weather(latitude, longitude):
    """Get current temperature for provided coordinates using a public weather API."""
    response = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m"
    )
    data = response.json()
    return data['current']['temperature_2m']

def agent_loop() :
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
   # Define the get_weather tool with a strict JSON schema
    weather_tool = {
        "type": "function",
        "name": "get_weather",
        "description": "Get current temperature for provided coordinates in celsius.",
        "parameters": {
            "type": "object",
            "properties": {
                "latitude": { "type": "number", "description": "Latitude of the location." },
                "longitude": { "type": "number", "description": "Longitude of the location." }
            },
            "required": ["latitude", "longitude"],
            "additionalProperties": False
        },
        "strict": True
    }

    tools = [weather_tool]

    # Input message asking about the weather in Paris
    messages = [{"role": "user", "content": "What's the weather like in Paris today? Before replying I want you to get weather for Berlin"}]

    while True:
        response = client.responses.create(
            model=MODEL,
            input=messages,
            tools=tools
        )
        
        # Process all function calls in the response
        if response.output:
            for output_item in response.output:
                if hasattr(output_item, 'type') and output_item.type == "function_call":
                    # Append the function call to the messages:
                    messages.append(output_item)

                    tool_call = output_item
                    args = json.loads(tool_call.arguments)
                    
                    # Execute the function, e.g. get_weather (simulate using our get_weather function)
                    result = get_weather(args['latitude'], args['longitude'])
                    print(f"Executed {tool_call.name}: Result = {result}°C")

                    # Append the function call output to the conversation
                    messages.append({
                        "type": "function_call_output",
                        "call_id": tool_call.call_id,
                        "output": str(result)
                    })
        
        # If the final output text is provided, break the loop
        if hasattr(response, 'output_text') and response.output_text:
            print("Final Agent Output:", response.output_text)
            break

        # Otherwise, continue the loop (in a full implementation, you might update the conversation further)
        
        # For simplicity, break if no further tool calls are made
        if not response.output:
            break


if __name__=="__main__":
    agent_loop()

# Output:
# Executed get_weather: Result = 10.4°C
# Final Agent Output: It’s about **10.4 °C** in **Paris** right now.