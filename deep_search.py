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

#  Deep research requires a higher timeout since tasks can run for several minutes(very expensive and slow operation)
# for analytics and deep research
from openai import OpenAI
deep_research_client = OpenAI(timeout=600)

# Kick off a deep research task in background mode
response = deep_research_client.responses.create(
    model="o3-deep-research",
    input="What are the latest breakthroughs in nuclear fusion energy as of 2025?",
    background=True,
    tools=[
        {"type": "web_search_preview"},
    ],
)

print(f"Response ID: {response.id}")
print(f"Status: {response.status}")