# llm.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    # 如果用 DeepSeek，取消下一行的注释：
    base_url="https://api.deepseek.com",
)

def chat(messages: list[dict]) -> str:
    response = client.chat.completions.create(
        model="deepseek-chat",   # DeepSeek 改成 "deepseek-chat"
        messages=messages,
        temperature=0,         # 0 = 输出更稳定，不乱发挥
    )
    return response.choices[0].message.content