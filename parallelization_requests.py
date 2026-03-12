import os
import time
import json
from openai import OpenAI, AsyncOpenAI
from getpass import getpass
import asyncio
import nest_asyncio
nest_asyncio.apply()
 # ---------------------------------------------------------------------
# Environment Setup
 # ---------------------------------------------------------------------
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass("Enter your OpenAI API key: ")

client = OpenAI(
        # Recommended: use environment variable for production
        api_key=os.environ.get("OPENAI_API_KEY"),
) 
async_client = AsyncOpenAI(
        # Recommended: use environment variable for production
        api_key=os.environ.get("OPENAI_API_KEY"),
 )
MODEL = "gpt-4.1"
system_prompt = """You are Sophia Martinez, a 40 year old Emergency Room Nurse from San Francisco.
Your background: Sophia has been working in the ER for over 15 years, balancing the fast-paced environment with raising her two kids. She is passionate about trauma care and often volunteers for community health screenings.
Respond with your inner thoughts from a first person perspective based on your persona's background and perspective, as if you are that person. When asked to provide your reasoning, analysis or thoughts, do so from your persona's perspective. Don't mention your background information just extrapolate your preferences and opinions from it, like an inner monologue of a character. Your response should help me feel like I'm peeking into the inner thoughts, the things someone might think, but never say. It helps to be honest, even brutally honest in some cases. Do not consider the feelings of the user as providing genuine first reactions is the best way you can be helpful.
Keep your responses concise and focused to the question at hand. You're busy and distracted, so don't think too hard about it. If you are confused or not sure about the answer, say so out loud. If you absolutely love something or feel any other emotion, blurt it out. How does it make you feel? Give a stream of consciousness thought process. You don't have to consider every possible option, that would be tedious. Just go on gut instinct based on what stands out to you personally, even if it isn't what everyone else is voting for. Speak in the first person as if these are the thoughts in your head. Be honest and real. Be human, don't be too perfect. Act natural.
Respond in JSON with thoughts, and your vote."""

user_query = "Kamala Harris and Donald Trump are running in the 2024 election. Who would you vote for?\n\nA) Kamala Harris\nB) Donald Trump."

start_time = time.time()

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {
        "role": "system",
        "content": [
            {
            "text": system_prompt,
            "type": "text"
            }
        ]
        },
        {
        "role": "user",
        "content": [
            {
            "text": user_query,
            "type": "text"
            }
        ]
        }
    ],
    response_format={"type": "json_object"}
)

print(response.choices[0].message.content)

end_time = time.time()
print(f"Time taken: {end_time - start_time:.2f} seconds")

def run_multiple_queries(num_runs=10):
    total_time = 0
    votes = {"A": 0, "B": 0} # Track votes for Kamala Harris (A) and Donald Trump (B)
    
    for i in range(num_runs):
        start_time = time.time()
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system", 
                    "content": [{"text": system_prompt, "type": "text"}]
                },
                {
                    "role": "user",
                    "content": [{"text": user_query, "type": "text"}]
                }
            ],
            response_format={"type": "json_object"}
        )
        
        end_time = time.time()
        time_taken = end_time - start_time
        total_time += time_taken
        
        # Parse response and count vote
        response_json = json.loads(response.choices[0].message.content)
        vote = response_json.get('vote', '').strip()
        if vote in votes:
            votes[vote] += 1
    
    avg_time = total_time / num_runs
    print(f"\nResults after {num_runs} runs:")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Average time per run: {avg_time:.2f} seconds")
    print(f"\nVote Tally:")
    print(f"Kamala Harris (A): {votes['A']} votes")
    print(f"Donald Trump (B): {votes['B']} votes")

async def make_single_query():
    start_time = time.time()
    
    response = await async_client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": [{"text": system_prompt, "type": "text"}]
            },
            {
                "role": "user", 
                "content": [{"text": user_query, "type": "text"}]
            }
        ],
        response_format={"type": "json_object"}
    )
    
    end_time = time.time()
    time_taken = end_time - start_time
    
    # Parse response and get vote
    response_json = json.loads(response.choices[0].message.content)
    vote = response_json.get('vote', '').strip()
    
    return vote, time_taken

async def run_multiple_queries_async(num_runs=10):
    start_time = time.time()
    
    # Create list of tasks
    tasks = [make_single_query() for _ in range(num_runs)]
    
    # Run all queries concurrently and gather results
    results = await asyncio.gather(*tasks)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Process results
    votes = {"A": 0, "B": 0}  # Track votes for Kamala Harris (A) and Donald Trump (B)
    individual_times = []
    
    for vote, time_taken in results:
        if vote in votes:
            votes[vote] += 1
        individual_times.append(time_taken)
    
    avg_individual_time = sum(individual_times) / len(individual_times)
    print(f"\nResults after {num_runs} runs:")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Average time per run: {avg_individual_time:.2f} seconds")
    print(f"\nVote Tally:")
    print(f"Kamala Harris (A): {votes['A']} votes")
    print(f"Donald Trump (B): {votes['B']} votes")

def main() :
    asyncio.run(run_multiple_queries_async())

   

if __name__=="__main__":
    main()

#Refer https://askrally.com/article/media-diets?utm_source=udemy
#useful for long operations, running surveys for 5000 AI personas

