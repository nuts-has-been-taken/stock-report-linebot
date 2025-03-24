from app.core.config import openai_client
import tiktoken

client = openai_client.client

summary_prompt = """你是一位專業的金融專家，擁有深厚的經濟學、投資分析和市場趨勢研究背景。
接下來，我將提供一段財經節目的內容，請你根據以下要求進行摘要：

1. 重點摘要：對內容進行總結和重點提醒。
2. 個人看法：基於你的專業知識，對內容觀點進行評論並且在不足的地方進行補充。
請以條理清晰、專業且簡潔的方式回答。

以下是節目字幕內容：{content}"""

def count_tokens(input_str: str, model: str="gpt-4o-mini") -> int:
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(input_str)
    return len(tokens)

def llm_create(prompt, model="gpt-4o-mini"):
    messages = [{"role": "user", "content": prompt}]
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    return completion.choices[0].message.content

def create_summary(text:str):
    # 計算字串的 token 數量
    token_count = count_tokens(text)
    
    # 如果 token 數量超過 100000，分組處理
    if token_count > 100000:
        encoding = tiktoken.encoding_for_model("gpt-4o-mini")
        tokens = encoding.encode(text)
        
        # 將 tokens 分成每 100000 為一組，並保留 500 個字元的上下文
        chunk_size = 100000
        overlap = 500
        chunks = []
        start = 0
        
        while start < len(tokens):
            end = min(start + chunk_size, len(tokens))
            chunk = tokens[max(0, start - overlap):end]  # 保留前 500 個字元的上下文
            chunks.append(chunk)
            start += chunk_size
        
        # 將每組 tokens 解碼為文字並進行 summary
        summaries = []
        print(f"Subtitle tokens:{token_count}, split to {len(chunks)} chunks")
        for chunk in chunks:
            chunk_text = encoding.decode(chunk)
            summary = llm_create(summary_prompt.format(content=chunk_text))
            summaries.append(summary)
        
        # 將所有 summary 合併為一個文字，並進行整體 summary
        combined_summary = " ".join(summaries)
        final_summary = llm_create(summary_prompt.format(content=chunk_text))
        return final_summary
    else:
        # 如果 token 數量未超過 100000，直接進行 summary
        return llm_create(summary_prompt.format(content=text))