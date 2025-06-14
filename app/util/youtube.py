from app.core.config import google_api

from datetime import datetime, timedelta
import subprocess
import base64
import os
import re

youtube = google_api.YOUTUBE

def get_latest_live_stream(channel_id):
    request = youtube.search().list(
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
        date = video['snippet']['publishTime']
        date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ").date()
        url = f'https://www.youtube.com/watch?v={video_id}'
        return title, url, date
    else:
        return None, None, None

def get_live_stream(channel_id, date):
    
    start_datetime = datetime.combine(date, datetime.min.time())
    end_datetime = start_datetime + timedelta(days=1)
    start_date = start_datetime.isoformat("T") + "Z"
    end_date = end_datetime.isoformat("T") + "Z"
    request = youtube.search().list(
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
        date = video['snippet']['publishTime']
        date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ").date()
        url = f'https://www.youtube.com/watch?v={video_id}'
        return title, url, date
    else:
        return None, None, None

def get_youtube_subtitles(youtube_url):
    subtitle_file = "subtitle.zh-TW.vtt"
    command = [
        "yt-dlp",
        "--write-subs",
        "--sub-lang", "zh-TW",
        "-o", "subtitle",
        "--skip-download",
        youtube_url
    ]
    # 執行 yt-dlp 指令
    subprocess.run(command, check=True)
    
    # 確認字幕檔案是否存在
    if os.path.exists(subtitle_file):
        # 讀取字幕內容
        with open(subtitle_file, "r", encoding="utf-8") as file:
            content = file.read()
        content = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}', '', content)
        content = re.sub(r'(WEBVTT|Kind:.*|Language:.*)', '', content)
        
        # 刪除字幕檔案以清理空間
        os.remove(subtitle_file)
        
        return ' '.join(line.strip() for line in content.splitlines() if line.strip())
    else:
        return None

def get_youtube_audio(youtube_url, encode_string:bool=True):
    """return youtube video audio file, Warning: need remove audio file after use"""
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
    # 執行 yt-dlp 指令
    subprocess.run(command, check=True)
    # 確認音訊檔案是否存在
    if os.path.exists(audio_file):
        if encode_string:
            # 讀取音訊檔案並轉換為 base64 編碼
            audio = open(audio_file, "rb")
            encode_string = base64.b64encode(audio.read()).decode('utf-8')    
            os.remove(audio_file)
            return encode_string
        else:
            # 返回檔案路徑
            return audio_file
    else:
        return None

def get_youtube_img(youtube_url):
    """return youtube video thumbnail url"""
    command = [
        "yt-dlp",
        "--get-thumbnail",
        youtube_url
    ]
    result = subprocess.run(command, capture_output=True)
    if result.returncode == 0:
        return result.stdout.decode('utf-8').strip()
    else:
        return None

# 查找頻道&id
def search_channel_id(channel_name):
    response = youtube.search().list(
        part='snippet',
        q=channel_name,
        type='channel',
        maxResults=1
    ).execute()
    
    if 'items' in response and len(response['items']) > 0:
        channel_id = response['items'][0]['snippet']['channelId']
        channel_name = response['items'][0]['snippet']['title']
        print(f"Channel Name: {channel_name}")
        print(f"Channel ID: {channel_id}")
        return channel_id, channel_name
    else:
        return None