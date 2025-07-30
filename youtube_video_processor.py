"""
YouTube Video Processing Module

This module extracts the core functionality from the /line/hao-report API endpoint.
It provides functionality to:
1. Fetch YouTube videos from a specific channel and date
2. Extract subtitles or audio transcripts from YouTube videos
3. Generate AI summaries of the content
4. Save processed data to database

Key Features:
- YouTube API integration for video retrieval
- yt-dlp for subtitle and audio extraction
- OpenAI integration for content summarization
- Database storage using SQLAlchemy
"""

import os
import re
import base64
import subprocess
import tiktoken
from datetime import datetime, timedelta, date
from typing import Optional, Tuple
from googleapiclient.discovery import build
from openai import OpenAI
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Configuration class for API keys and settings"""
    YOUTUBE_API_KEY: str
    OPENAI_API_KEY: str
    POSTGRES_URL: str
    AUDIO_MODE: bool = False
    TRANS_FIRST: bool = False
    
    class Config:
        env_file = ".env"


class YouTubeProcessor:
    """Main class for processing YouTube videos"""
    
    def __init__(self, config: Config):
        self.config = config
        self.youtube = build('youtube', 'v3', developerKey=config.YOUTUBE_API_KEY)
        self.openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
        
        # Database setup
        self.engine = create_engine(config.POSTGRES_URL)
        self.Session = sessionmaker(bind=self.engine)
        
        # Summary prompt template
        self.summary_prompt = """你是一位專業的金融專家，擁有深厚的經濟學、投資分析和市場趨勢研究背景。
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

    def get_latest_live_stream(self, channel_id: str) -> Tuple[Optional[str], Optional[str], Optional[date]]:
        """Get the latest completed live stream from a YouTube channel"""
        request = self.youtube.search().list(
            part="snippet",
            channelId=channel_id,
            eventType="completed",
            type="video",
            order="date",
            maxResults=1
        )
        
        response = request.execute()
        
        if response['items']:
            video = response['items'][0]
            video_id = video['id']['videoId']
            title = video['snippet']['title']
            publish_date = video['snippet']['publishTime']
            publish_date = datetime.strptime(publish_date, "%Y-%m-%dT%H:%M:%SZ").date()
            url = f'https://www.youtube.com/watch?v={video_id}'
            return title, url, publish_date
        else:
            return None, None, None

    def get_live_stream(self, channel_id: str, target_date: date) -> Tuple[Optional[str], Optional[str], Optional[date]]:
        """Get live stream from a specific date"""
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = start_datetime + timedelta(days=1)
        start_date = start_datetime.isoformat("T") + "Z"
        end_date = end_datetime.isoformat("T") + "Z"
        
        request = self.youtube.search().list(
            part="snippet",
            channelId=channel_id,
            eventType="completed",
            type="video",
            order="date",
            publishedAfter=start_date,
            publishedBefore=end_date,
            maxResults=1
        )
        
        response = request.execute()
        if response['items']:
            video = response['items'][0]
            video_id = video['id']['videoId']
            title = video['snippet']['title']
            publish_date = video['snippet']['publishTime']
            publish_date = datetime.strptime(publish_date, "%Y-%m-%dT%H:%M:%SZ").date()
            url = f'https://www.youtube.com/watch?v={video_id}'
            return title, url, publish_date
        else:
            return None, None, None

    def get_youtube_subtitles(self, youtube_url: str) -> Optional[str]:
        """Extract subtitles from YouTube video using yt-dlp"""
        subtitle_file = "subtitle.zh-TW.vtt"
        command = [
            "yt-dlp",
            "--write-subs",
            "--sub-lang", "zh-TW",
            "-o", "subtitle",
            "--skip-download",
            youtube_url
        ]
        
        try:
            subprocess.run(command, check=True)
            
            if os.path.exists(subtitle_file):
                with open(subtitle_file, "r", encoding="utf-8") as file:
                    content = file.read()
                
                # Clean subtitle format
                content = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}', '', content)
                content = re.sub(r'(WEBVTT|Kind:.*|Language:.*)', '', content)
                
                os.remove(subtitle_file)
                return ' '.join(line.strip() for line in content.splitlines() if line.strip())
            else:
                return None
        except subprocess.CalledProcessError:
            return None

    def get_youtube_audio(self, youtube_url: str, encode_string: bool = True) -> Optional[str]:
        """Extract audio from YouTube video using yt-dlp"""
        audio_file = "audio.mp3"
        command = [
            "yt-dlp",
            "-f", "bestaudio",
            "--extract-audio",
            "--audio-format", "mp3",
            "--audio-quality", "0",
            "-o", audio_file,
            youtube_url
        ]
        
        try:
            subprocess.run(command, check=True)
            
            if os.path.exists(audio_file):
                if encode_string:
                    with open(audio_file, "rb") as audio:
                        encoded_string = base64.b64encode(audio.read()).decode('utf-8')
                    os.remove(audio_file)
                    return encoded_string
                else:
                    return audio_file
            else:
                return None
        except subprocess.CalledProcessError:
            return None

    def get_youtube_thumbnail(self, youtube_url: str) -> Optional[str]:
        """Get YouTube video thumbnail URL"""
        command = [
            "yt-dlp",
            "--get-thumbnail",
            youtube_url
        ]
        
        try:
            result = subprocess.run(command, capture_output=True, check=True)
            return result.stdout.decode('utf-8').strip()
        except subprocess.CalledProcessError:
            return None

    def count_tokens(self, input_str: str, model: str = "gpt-4o-mini") -> int:
        """Count tokens in text for OpenAI model"""
        encoding = tiktoken.encoding_for_model(model)
        tokens = encoding.encode(input_str)
        return len(tokens)

    def llm_create(self, prompt: str, model: str = "gpt-4o-mini") -> str:
        """Create completion using OpenAI"""
        messages = [{"role": "user", "content": prompt}]
        completion = self.openai_client.chat.completions.create(
            model=model,
            messages=messages,
        )
        return completion.choices[0].message.content

    def audio_llms_create(self, prompt: str, encode_string: str, model: str = "gpt-4o-mini-audio-preview-2024-12-17") -> str:
        """Create completion using OpenAI with audio input"""
        completion = self.openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "input_audio",
                        "input_audio": {
                            "data": encode_string,
                            "format": "mp3",
                        }
                    }
                ]}
            ]
        )
        return completion.choices[0].message.content

    def audio_transcript_subtitle(self, audio_file: str) -> str:
        """Transcribe audio to text using OpenAI Whisper"""
        with open(audio_file, "rb") as audio:
            transcript = self.openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio,
                language="zh-tw"
            )
        return transcript.text

    def create_summary_audio(self, encode_string: str) -> str:
        """Create summary directly from audio"""
        return self.audio_llms_create(self.summary_prompt.format(content=""), encode_string)

    def create_summary(self, text: str) -> str:
        """Create summary from text with token handling"""
        token_count = self.count_tokens(text)
        
        if token_count > 100000:
            encoding = tiktoken.encoding_for_model("gpt-4o-mini")
            tokens = encoding.encode(text)
            
            # Split tokens into chunks with overlap
            chunk_size = 100000
            overlap = 500
            chunks = []
            start = 0
            
            while start < len(tokens):
                end = min(start + chunk_size, len(tokens))
                chunk = tokens[max(0, start - overlap):end]
                chunks.append(chunk)
                start += chunk_size
            
            # Process each chunk
            summaries = []
            for chunk in chunks:
                chunk_text = encoding.decode(chunk)
                summary = self.llm_create(self.summary_prompt.format(content=chunk_text))
                summaries.append(summary)
            
            # Combine all summaries and create final summary
            combined_summary = " ".join(summaries)
            final_summary = self.llm_create(self.summary_prompt.format(content=combined_summary))
            return final_summary
        else:
            return self.llm_create(self.summary_prompt.format(content=text))

    def process_youtube_video(self, channel_id: str, target_date: date) -> Tuple[Optional[dict], Optional[str]]:
        """Process YouTube video: extract content and create summary"""
        title, url, vid_date = self.get_live_stream(channel_id, target_date)

        if not url:
            return None, "無法取得影片"

        # Try to get subtitles first
        subtitle = self.get_youtube_subtitles(url)
        
        if not subtitle:
            if self.config.TRANS_FIRST:
                # Transcribe audio first, then summarize
                audio = self.get_youtube_audio(youtube_url=url, encode_string=False)
                if not audio:
                    return None, "無法取得音訊"
                
                transcript = self.audio_transcript_subtitle(audio)
                os.remove(audio)
                summary = self.create_summary(transcript)
                
            elif self.config.AUDIO_MODE:
                # Direct audio summarization
                audio = self.get_youtube_audio(youtube_url=url, encode_string=True)
                if not audio:
                    return None, "無法取得音訊"
                summary = self.create_summary_audio(audio)
            else:
                return None, "字幕未上傳"
        else:
            # Use subtitles for summary
            summary = self.create_summary(subtitle)

        # Get thumbnail
        img_url = self.get_youtube_thumbnail(url)

        # Return processed data
        data = {
            'title': title,
            'url': url,
            'date': vid_date,
            'summary': summary,
            'thumbnail': img_url
        }
        
        return data, None


def main():
    """Example usage of the YouTube processor"""
    # Load configuration
    config = Config()
    
    # Initialize processor
    processor = YouTubeProcessor(config)
    
    # Example: Process video from specific channel and date
    channel_id = 'UC0lbAQVpenvfA2QqzsRtL_g'  # 財經皓角頻道
    target_date = date.today()
    
    # Process video
    data, error = processor.process_youtube_video(channel_id, target_date)
    
    if error:
        print(f"處理失敗: {error}")
    else:
        print(f"處理成功:")
        print(f"標題: {data['title']}")
        print(f"日期: {data['date']}")
        print(f"URL: {data['url']}")
        print(f"縮圖: {data['thumbnail']}")
        print(f"摘要: {data['summary']}")


if __name__ == "__main__":
    main()