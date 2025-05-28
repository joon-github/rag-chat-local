# backend/llm.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def stream_answer(prompt: str, model="gpt-4o-mini"):
    return client.chat.completions.create(
        model=model,
        stream=True,
        messages=[
        {"role": "system", "content": "당신은 문서 기반 질문에 답하는 AI입니다."},
        {"role": "user", "content": prompt}
    ]
)

