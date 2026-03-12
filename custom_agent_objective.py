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
def objective_met(search_count, max_searches=5):
    # Stop once we've searched more than max_searches cities
    return search_count > max_searches

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
  # Initial conversation: developer sets the task, user gives the first city
    messages= [
        {
            "role": "developer",
            "content": (
                "Your goal is to gather weather for at least 5 different cities. "
                "Once you've done that, respond with 'task complete'."
            )
        },
        {"role": "user", "content": "Search the weather in Berlin."}
    ]

    search_count = 0
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

    while True:
        response = client.responses.create(
            model=MODEL,
            input=messages,
            tools=tools
        )
        
        # 1) Handle any function calls (e.g. get_weather)
        for item in response.output or []:
            if getattr(item, 'type', None) == "function_call":
                messages.append(item)  # pass the function call back into context
                
                # parse and execute
                args = json.loads(item.arguments)
                temp = get_weather(args['latitude'], args['longitude'])
                print(f"Executed {item.name}: {temp}°C")
                
                # append function result
                messages.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": str(temp)
                })
                
                search_count += 1
        
        # 2) Check for assistant output_text
        if hasattr(response, 'output_text') and response.output_text:
            text = response.output_text
            print("Agent says:", text)
            messages.append({"role": "assistant", "content": text})
        
        # 3) Check objective
        if objective_met(search_count):
            print(f"Objective met: searched {search_count} cities. Task complete.")
            break
        
        # 4) If not done, prompt for the next city
        messages.append({
            "role": "user",
            "content": f"We've searched {search_count} so far. Please search another city."
        })


if __name__=="__main__":
    agent_loop()

# Output:
# Executed get_weather: 8.8°C
# Executed get_weather: 10.5°C
# Executed get_weather: 9.4°C
# Executed get_weather: 15.5°C
# Executed get_weather: 9.6°C
# Executed get_weather: 28.3°C
# Objective met: searched 6 cities. Task complete.