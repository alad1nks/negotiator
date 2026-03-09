from typing import List

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from prompt import PROMPT

client = OpenAI()

messages: List[ChatCompletionMessageParam] = [
    {"role": "system", "content": PROMPT},
    {"role": "user", "content": ""}
]

response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=messages
)

print(response.choices[0].message.content)
