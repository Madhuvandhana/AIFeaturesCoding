import os
from getpass import getpass
from openai import OpenAI
import tiktoken
import json
from typing import Optional
from pydantic import BaseModel

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
    text = """
    Marie Curie, born on November 7, 1867 in Warsaw, Poland, was a pioneering physicist 
    and chemist who conducted groundbreaking research on radioactivity. She was the first 
    woman to win a Nobel Prize. Her colleague Albert Einstein, a German-born theoretical 
    physicist born on March 14, 1879, developed the theory of relativity. Meanwhile, 
    Ada Lovelace, an English mathematician born on December 10, 1815, is often regarded 
    as the first computer programmer for her work on Charles Babbage's Analytical Engine.
    """

    # People
    # - Name
    # - Date of birth
    # - Occupation

    # List of people

    #Optional[str] = None for name to optional

    class Person(BaseModel):
        name: str
        date_of_birth: str
        occupation: str
        nationality: str

    class PeopleList(BaseModel):
        people: list[Person]

    response = client.responses.parse(
        model=MODEL,
        input=[
            {'role': 'developer', 'content': 'Extract all people mentioned in the text with their details.'},
            {'role': 'user', 'content': text}
        ],
        text_format=PeopleList
    )
    if response.output_parsed:
        people = response.output_parsed.people
    else:
        people = []
    people = response.output_parsed.people
    for person in people:
        print(f"{person.name} | Born: {person.date_of_birth} | {person.occupation} | {person.nationality}")

if __name__=="__main__":
    main()
