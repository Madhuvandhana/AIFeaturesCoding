import os
from getpass import getpass
import openai
from openai import OpenAI
import tiktoken
import json
import os
import random
import time
from getpass import getpass
import requests
from tenacity import retry, stop_after_attempt, wait_random_exponential
import random
import time

def main() :
    # ---------------------------------------------------------------------
    # Environment Setup
    # ---------------------------------------------------------------------
    if not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = getpass("Enter your OpenAI API key: ")

    client = OpenAI(
        # Recommended: use environment variable for production
        api_key=os.environ.get("OPENAI_API_KEY"),
        max_retries=6
    )
    MODEL = "gpt-5-mini"
    headers = {
    'Authorization': f'Bearer {os.environ.get("OPENAI_API_KEY")}',
    'Content-Type': 'application/json'
}

    input_messages = [
        {"role": "user", "content": "Hello"}
    ]
    data = {
        'model': MODEL, 
        'input': input_messages,
    }

    response = requests.post('https://api.openai.com/v1/responses', headers=headers, json=data)

    # Check if request was successful and headers are present
    if response.status_code == 200:
        # Try to get rate limit headers (they may not always be present)
        remaining = response.headers.get('x-ratelimit-remaining-requests', 'Not available')
        print("Remaining requests:", remaining)
        
        # Show other rate limit headers if available
        for key, value in response.headers.items():
            if 'ratelimit' in key.lower():
                print(f"{key}: {value}")
    else:
        print(f"Request failed with status {response.status_code}")
        print(response.text)

    #Use tenacity to retry on RateLimitError.


    @retry(
        reraise=True,
        stop=stop_after_attempt(6),
        wait=wait_random_exponential(min=1, max=60)
    )
    def create_with_backoff(**kwargs):
        return client.responses.create(**kwargs)

    # call with retry logic
    resp = create_with_backoff(
        model=MODEL,
        input=[{"role":"user","content":"Tell me a joke."}]
    )
    print(resp.output_text)

    # Manual Exponential Backoff
    # Implement your own retry decorator.


    def retry_with_backoff(
        func,
        initial_delay=1,
        factor=2,
        jitter=True,
        max_retries=5
    ):
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for i in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except openai.RateLimitError as e:
                    sleep = delay * (1 + (random.random() if jitter else 0))
                    print(f"Rate limited, retrying in {sleep:.1f}s...")
                    time.sleep(sleep)
                    delay *= factor
            raise Exception("Max retries exceeded.")
        return wrapper

    @retry_with_backoff
    def create_manual(**kwargs):
        return client.responses.create(**kwargs)

    # Call with manual backoff
    resp3 = create_manual(
        model=MODEL,
        input=[{"role":"user","content":"Explain Kubernetes."}]
    )
    print(resp3.output_text)


#see https://github.com/BrightPool/udemy-prompt-engineering-course/blob/main/openai_features_and_functionality/rate_limits_and_retrying_with_tenacity.ipynb
if __name__=="__main__":
    main()