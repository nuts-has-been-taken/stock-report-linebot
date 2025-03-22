from app.core.config import openai_client
import tiktoken

client = openai_client.client

def count_tokens(input_str: str, model: str="gpt-4o-mini") -> int:
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(input_str)
    return len(tokens)

def llm_create(prompt):
    messages = [{"role": "user", "content": prompt}]
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    return completion.choices[0].message.content