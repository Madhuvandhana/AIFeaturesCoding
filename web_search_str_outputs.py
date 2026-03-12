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

    class NewsArticle(BaseModel):
        title: str
        date: str
        summary: str
        source: str

    class NewsResults(BaseModel):
        articles: list[NewsArticle]

    response = client.responses.parse(
        model=MODEL,
        tools=[{"type": "web_search"}],
        input="Find 3 recent positive news stories from this week about technology or science.",
        text_format=NewsResults,
    )

    if not response.output_parsed:
        news = []
    else:
        news = response.output_parsed.articles

    for i, article in enumerate(news, 1):
        print(f"Article {i}")
        print(f"Title:   {article.title}")
        print(f"Date:    {article.date}")
        print(f"Source:  {article.source}")
        print(f"Summary: {article.summary}")
        print()

if __name__=="__main__":
    main()

#Output:
# Article 1
# Title:   Apple’s new M5-powered MacBook Air and MacBook Pro begin arriving to customers
# Date:    March 3 & March 11, 2026
# Source:  Apple Newsroom
# Summary: Apple announced new MacBook Air (M5) and MacBook Pro models (M5 Pro / M5 Max) in early March; pre-orders opened March 4 and units began arriving in stores and to customers starting Wednesday, March 11, 2026. The releases emphasize faster on‑device AI, improved performance, and environmental/recycled‑materials improvements. ([apple.com](https://www.apple.com/newsroom/2026/03/apple-introduces-the-new-macbook-air-with-m5/?utm_source=openai))

# Article 2
# Title:   Google/Android’s March 2026 security update patches 129 vulnerabilities (including an actively exploited zero‑day)
# Date:    March 2–5, 2026
# Source:  Android Open Source Project / TechRepublic
# Summary: Google published the March 2026 Android Security Bulletin (patch levels 2026‑03‑01 and 2026‑03‑05), which fixes 129 vulnerabilities across the Android ecosystem and includes a patch for CVE‑2026‑21385 — a Qualcomm graphics component bug that Google reported may be under limited, targeted exploitation. This rollout is a significant security win for users and enterprises. ([source.android.com](https://source.android.com/docs/security/bulletin/2026/2026-03-01?utm_source=openai))

# Article 3
# Title:   Nature reports a push to normalize self‑correction in science — Center for Scientific Integrity launches a ‘Ctrl‑Z’ award
# Date:    March 10, 2026
# Source:  Nature
# Summary: Nature published a piece (10 March 2026) highlighting cultural progress in science around transparency and self‑correction. The article notes that the Center for Scientific Integrity (parent of Retraction Watch) launched a Ctrl‑Z Award this week to recognize researchers who find and correct substantial errors in their published work — an initiative that promotes research integrity and healthier scientific practice. ([nature.com](https://www.nature.com/articles/d41586-026-00763-x?utm_source=openai))
