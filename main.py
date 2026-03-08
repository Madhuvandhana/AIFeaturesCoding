import os
from openai import OpenAI

MODEL = "gpt-5.2"

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass("Enter your OpenAI API key: ")

# The client automatically picks up the OPENAI_API_KEY environment variable
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

history = [
    {"role": "user", "content": "tell me a joke"}
]

# Create a response using the conversation history
# response = client.responses.create(
#     model=MODEL,
#     input=history,
#     store = False
# )

response = client.responses.create(
    model=MODEL,
    input="tell me a joke"
)
print(response.output_text)

# #update the message history with the assistant output/message
# history+= [{"role": el.role, "content": el.content} for el in response.output ]

# # Ask for another joke
# history.append({"role": "user", "content": "tell me another"})

# #Do a second response
# second_response = client.responses.create(
#     model = MODEL,
#     input = history,
#     store = False
# )

# 3. Chaining Responses with previous_response_id
second_response = client.responses.create(
    model = MODEL,
    previous_response_id=response.id,
    input = [{"role": "user", "content": "explore why it is funny"}]
)
print("Second joke", second_response.output_text)

#https://colab.research.google.com/drive/1dt1SR_J-767obypuX9TxeENgcCn53jfi?usp=sharing#scrollTo=b3cbe4c1-cf8f-4b8b-a3fb-4f4e85eec168
