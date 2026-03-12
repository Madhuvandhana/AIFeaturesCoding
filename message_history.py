#https://colab.research.google.com/drive/1f05NaSyjAYYTO5cfAO9MNg-kNNa11ibx?usp=sharing
#Useful when you want to compact the message token history for a conversation when it reaches a certain token size
import os
from getpass import getpass
from openai import OpenAI
import tiktoken
import json

def num_tokens_from_messages(messages, model="gpt-5.2"):
    """Return the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using o200k_base encoding.")
        encoding = tiktoken.get_encoding("o200k_base")

    if model in {
        "gpt-5.2",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
        "gpt-4o",
        "gpt-4o-2024-08-06",
        "gpt-5-mini",
    }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif "gpt-5.2" in model:
        print(
            "Warning: gpt-5.2 may update over time. Returning num tokens assuming gpt-5.2."
        )
        return num_tokens_from_messages(messages, model="gpt-5.2")
    elif "gpt-4o" in model:
        print(
            "Warning: gpt-4o may update over time. Returning num tokens assuming gpt-4o-2024-08-06."
        )
        return num_tokens_from_messages(messages, model="gpt-4o-2024-08-06")
    elif "gpt-4" in model:
        print(
            "Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613."
        )
        return num_tokens_from_messages(messages, model="gpt-4-0613")
    elif "gpt-5-mini" in model:
        print(
            "Warning: gpt-5-mini may update over time. Returning num tokens assuming gpt-5-mini."
        )
        return num_tokens_from_messages(messages, model="gpt-5-mini")
    else:
        raise NotImplementedError(
            f"num_tokens_from_messages() is not implemented for model {model}."
        )

    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
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
    MODEL = "gpt-5-mini"
    article_headings = [
    "I. Introduction A. Definition of the 2008 Financial Crisis B. Overview of the Causes and Effects of the Crisis C. Importance of Understanding the Crisis",
    "II. Historical Background A. Brief History of the US Financial System B. The Creation of the Housing Bubble C. The Growth of the Subprime Mortgage Market",
    "III. Key Players in the Crisis A. Government Entities B. Financial Institutions C. Homeowners and Borrowers",
    "IV. Causes of the Crisis A. The Housing Bubble and Subprime Mortgages B. The Role of Investment Banks and Rating Agencies C. The Failure of Regulatory Agencies D. Deregulation of the Financial Industry",
    "V. The Domino Effect A. The Spread of the Crisis to the Global Financial System B. The Impact on the Real Economy C. The Economic Recession",
    "VI. Government Responses A. The Troubled Asset Relief Program (TARP) B. The American Recovery and Reinvestment Act C. The Dodd-Frank Wall Street Reform and Consumer Protection Act",
    "VII. Effects on Financial Institutions A. Bank Failures and Bailouts B. Stock Market Decline C. Credit Freeze",
    "VIII. Effects on Homeowners and Borrowers A. Foreclosures and Bankruptcies B. The Loss of Home Equity C. The Impact on Credit Scores",
    "IX. Effects on the Global Economy A. The Global Financial Crisis B. The Impact on Developing Countries C. The Role of International Organizations",
    "X. Criticisms and Controversies A. Bailouts for Financial Institutions B. Government Intervention in the Economy C. The Role of Wall Street in the Crisis",
    "XI. Lessons Learned A. The Need for Stronger Regulation B. The Importance of Transparency C. The Need for Better Risk Management",
    "XII. Reforms and Changes A. The Dodd-Frank Wall Street Reform and Consumer Protection Act B. Changes in Regulatory Agencies C. Changes in the Financial Industry",
    "XIII. Current Economic Situation A. Recovery from the Crisis B. Impact on the Job Market C. The Future of the US Economy",
    "XIV. Comparison to Previous Financial Crises A. The Great Depression B. The Savings and Loan Crisis C. The Dot-Com Bubble",
    "XV. Economic and Social Impacts A. The Widening Wealth Gap B. The Rise of Populist Movements C. The Long-Term Effects on the Economy",
    "XVI. The Role of Technology A. The Use of Technology in the Financial Industry B. The Impact of Technology on the Crisis C. The Future of the Financial Industry",
    "XVII. Conclusion A. Recap of the Causes and Effects of the Crisis B. The Importance of Learning from the Crisis C. Final Thoughts",
    "XVIII. References A. List of Sources B. Additional Reading C. Further Research",
    "XIX. Glossary A. Key Terms B. Definitions",
    "XX. Appendix A. Timeline of the Crisis B. Financial Statements of Key Players C. Statistical Data on the Crisis",
]
    #Trim back context window real time based on the estimated number of tokens inside the message history
    system_prompt = "You are a helpful assistant for a financial news website. You are writing a series of articles about the 2008 financial crisis. You have been given a list of headings for each article. You need to write a short paragraph for each heading. You can use the headings as a starting point for your writing.\n\n"
    system_prompt += "All of the subheadings:\n"

    #Set up our messages:
    messages = []

    # Add all of the subheadings to the system prompt to give the model context:
    for heading in article_headings:
        system_prompt += f"{heading}\n"
    # Append the first developer/system message to the messages list:
    messages.append({"role": "developer", "content": system_prompt})

    # This will ensure that if the token count goes over the limit, the last message will be removed,
    # to ensure that the token count is reduced as the chat history grows:
    MAX_TOKEN_SIZE = 2048 #specifically for input tokens
    CURRENT_TOKEN_COUNT = 0 # Use this for tracking the internal token count
    ALL_RESPONSES = [] # Using this to store all of the responses, so we control the primitive of message state

    # Loop over all of the headings and generate a chunk for each one
    for heading in article_headings:

        # Add on a user prompt to the chat history object:
        #1. Set up the message
        messages.append(
            {"role": "user", "content": f"Write a very large paragraph about {heading}. Make it very long and detailed."}
        )

        # Tell ChatGPT to generate a response:
        #2. Call the model
        response = client.responses.create(
            model=MODEL,
            input=messages,
            store=False
        )

        # Add token count for the response to the CURRENT_TOKEN_COUNT variable:
        #3. Store the meta data
        CURRENT_TOKEN_COUNT = response.usage.input_tokens

        # Update the conversation history with the assistant's response(message came from AI)
        #4. Append the response of the LLM back to messages list
        messages.append({"role": "assistant", "content": response.output_text})
        # print("Current message count", len(messages))
        # print("Current token count", num_tokens_from_messages(messages))

        # Add the AI response to the all_responses list and also add the token count for the response:
        ALL_RESPONSES.append(response.output_text)
        CURRENT_TOKEN_COUNT += response.usage.output_tokens # This is from the output tokens, because we have used them in an input yet

        # Whilst the Chat history object is more than 2048 tokens, remove the oldest non-system/developer message:
        #5. See whether or not we need to TRIM the messages (based on the current token count)
        while num_tokens_from_messages(messages, model='gpt-5.2') > MAX_TOKEN_SIZE:

            # Find the index of the first message that is not a system or developer message:
            non_system_msg_index = next(
                (i for i, msg in enumerate(messages) if msg["role"] not in ["system", "developer"]), None
            )

            # If there is a non-system message, remove it:
            if non_system_msg_index is not None:
                messages.pop(non_system_msg_index)
            print("Removed a message to reduce token count!")
        print("current message count", len(messages))
        print("Current token count", CURRENT_TOKEN_COUNT)

if __name__=="__main__":
    main()