from fastapi import FastAPI
from pydantic import BaseModel
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()

app = FastAPI()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class Question(BaseModel):
    question: str
    class_name: str
    chapter_name: str

@app.get("/")
def home():
    return {"message": "Gemini GSEB Backend Running 🚀"}


@app.post("/solve")
def solve_question(data: Question):

    prompt = f"""
You are a maths solver engine.

Solve the problem step-by-step.

Write all mathematical expressions in LaTeX format.
Wrap equations inside $ symbols.


IMPORTANT:
Return strictly valid JSON only in this format:

{{
  "steps": "step by step explanation",
  "final_answer": "only numeric answer"
}}

Do not add greetings.
Do not add extra text.
Do not use markdown.

Question:
{data.question}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.1,
            max_output_tokens=1000,
        ),
    )

    full_text = response.candidates[0].content.parts[0].text.strip()

    # Remove markdown formatting if exists
    full_text = full_text.replace("```json", "").replace("```", "").strip()

    # Try parsing JSON
    try:
        parsed = json.loads(full_text)
        return parsed
    except:
        # Fallback: extract numbers automatically
        numbers = re.findall(r"-?\d+\.?\d*", full_text)

        return {
            "steps": full_text,
            "final_answer": ", ".join(numbers) if numbers else "Not found"
        }
