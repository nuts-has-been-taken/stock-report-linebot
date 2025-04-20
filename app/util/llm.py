from app.core.config import openai_client
import tiktoken

client = openai_client.client

summary_prompt = """你是一位專業的金融專家，擁有深厚的經濟學、投資分析和市場趨勢研究背景。
接下來，我將提供一段財經節目的內容，請你根據以下要求進行摘要：

回答格式:
### 重點摘要：對內容進行結論和重點提醒。
### 個人看法：基於你的專業知識，對內容觀點進行評論並且在不足的地方進行補充。
請以條理清晰、專業且簡潔的方式回答。

範例:
### 重點摘要：
- 觀察庫存周期的變化對於未來投資機會至關重要，特別是在經濟回升期，這可能導致資產價值上升。
- 美國股市在經濟成長及出口訂單高漲的情況下，雖然有關稅戰的壓力，仍然展現出韌性。
- 美國最新的GDP數據顯示經濟表現強勁，且亞特蘭大聯準會的GDP NOW模型上調預測顯示不會進入衰退。
- 儘管面臨外資撤資，台灣證券市場仍在相對高位穩定運行，顯示出部分內資的支撐力量。
- 隨著不確定性增加，黃金價格持平或上升，成為避險資產的投資首選。

### 個人看法：
認同節目中提到的抓住庫存循環的關鍵，這是成功投資的核心策略之一。
然而，節目對於中期經濟結構性問題的探討較少，例如美國不斷上升的債務與潛在的通膨壓力，這可能在未來帶來隱患，值得投資者保持警惕。

以下是節目內容：{content}"""
            
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

def audio_llms_create(prompt, encode_string, model="gpt-4o-mini-audio-preview-2024-12-17"):
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "input_audio",
                    "input_audio":{
                        "data": encode_string,
                        "format": "mp3",
                    }
                }
            ]}
        ]
    )
    return completion.choices[0].message.content

def audio_transcript_subtitle(audio_file):
    # 使用 OpenAI 的 Whisper 模型進行音訊轉錄
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        language="zh-tw"
    )
    return transcript["text"]

def create_summary_audio(encode_string):
    # 目前沒有計算 token 數量
    return audio_llms_create(summary_prompt.format(content=""), encode_string)

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