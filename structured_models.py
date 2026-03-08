"""
math_tutor_structured.py

Demonstrates structured LLM output parsing using Pydantic models
with the OpenAI Responses API.

This example:
- Defines structured output schemas using Pydantic
- Forces the LLM to return validated step-by-step reasoning
- Parses the response directly into typed Python objects

Why this matters:
-----------------
Instead of manually parsing JSON or relying on fragile text output,
we enforce a strict schema (`MathReasoning`) that guarantees:

- Each reasoning step contains an explanation and intermediate output
- A final answer is always present
- The result is type-safe and production-ready

Example:
--------
$ python math_tutor_structured.py

Enter your OpenAI API key: ********

Response (math reasoning):
MathReasoning(
    steps=[
        Step(explanation='Subtract 7 from both sides', output='8x = -30'),
        Step(explanation='Divide both sides by 8', output='x = -3.75')
    ],
    final_answer='x = -3.75'
)
"""

import os
from getpass import getpass
from openai import OpenAI
from pydantic import BaseModel


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


# ---------------------------------------------------------------------
# Pydantic Structured Output Models
# ---------------------------------------------------------------------

class Step(BaseModel):
    """
    Represents a single step in a math solution.

    Attributes:
        explanation (str): Description of the reasoning performed.
        output (str): Result after applying the step.

    Example:
        >>> Step(
        ...     explanation="Subtract 7 from both sides",
        ...     output="8x = -30"
        ... )
    """
    explanation: str
    output: str


class MathReasoning(BaseModel):
    """
    Structured schema for full math problem reasoning.

    Attributes:
        steps (list[Step]): Ordered list of reasoning steps.
        final_answer (str): Final solved result.

    Example:
        >>> MathReasoning(
        ...     steps=[
        ...         Step(explanation="Subtract 7", output="8x = -30")
        ...     ],
        ...     final_answer="x = -3.75"
        ... )
    """
    steps: list[Step]
    final_answer: str


# ---------------------------------------------------------------------
# LLM Structured Parsing Call
# ---------------------------------------------------------------------

response = client.responses.parse(
    model=MODEL,
    input=[
        {
            "role": "developer",
            "content": (
                "You are a helpful math tutor. "
                "Guide the user through the solution step by step."
            ),
        },
        {
            "role": "user",
            "content": "How can I solve 8x + 7 = -23?"
        },
    ],
    text_format=MathReasoning,  # Enforce structured schema
)

"""
The `responses.parse()` method:

- Sends the prompt to the model
- Forces the output to conform to the `MathReasoning` schema
- Validates and parses the response into a Pydantic object
- Raises a validation error if the structure is incorrect

Return Type:
    response.output_parsed -> MathReasoning
"""

math_reasoning: MathReasoning = response.output_parsed


# ---------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------

print("Response (math reasoning):")
print(math_reasoning)


"""
Accessing Structured Fields Example:

>>> math_reasoning.final_answer
'x = -3.75'

>>> for step in math_reasoning.steps:
...     print(step.explanation, "->", step.output)
"""