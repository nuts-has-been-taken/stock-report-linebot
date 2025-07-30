from app.core.config import google_api
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import subprocess
import base64
import os
import re

youtube = google_api.YOUTUBE

@contextmanager
def temp_file_cleanup(file_path: str):
    """Context manager for temporary file cleanup."""
    try:
        yield file_path
    finally:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError as e:
                print(f"Warning: Could not remove temporary file {file_path}: {e}")

def get_latest_live_stream(channel_id: str):
    """
    獲取指定頻道的最新直播
    
    Args:
        channel_id (str): YouTube 頻道 ID
    
    Returns:
        tuple: (title, url, date) or (None, None, None) if not found
    """
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

def get_live_stream(channel_id: str, date):
    """
    獲取指定頻道在指定日期的直播
    
    Args:
        channel_id (str): YouTube 頻道 ID
        date (datetime.date): 指定的日期
    
    Returns:
        tuple: (title, url, date) or (None, None, None) if not found
    """
    
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

def get_youtube_subtitles(youtube_url: str) -> Optional[str]:
    """
    使用 yt-dlp 下載 YouTube 影片的字幕
    
    Args:
        youtube_url (str): YouTube 影片的 URL
    
    Returns:
        Optional[str]: 字幕內容，如果沒有字幕則返回 None
    """
    from app.constants import SUBTITLE_FILE_PATTERN, SUBTITLE_DOWNLOAD_TIMEOUT
    subtitle_file = SUBTITLE_FILE_PATTERN
    
    command = [
        "yt-dlp",
        "--write-subs",
        "--sub-lang", "zh-TW",
        "-o", "subtitle",
        "--skip-download",
        youtube_url
    ]
    
    try:
        with temp_file_cleanup(subtitle_file):
            subprocess.run(command, check=True, timeout=SUBTITLE_DOWNLOAD_TIMEOUT)
            
            if os.path.exists(subtitle_file):
                with open(subtitle_file, "r", encoding="utf-8") as file:
                    content = file.read()
                content = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}', '', content)
                content = re.sub(r'(WEBVTT|Kind:.*|Language:.*)', '', content)
                
                return ' '.join(line.strip() for line in content.splitlines() if line.strip())
        return None
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as e:
        print(f"Error downloading subtitles: {e}")
        return None

def get_youtube_audio(youtube_url: str, encode_string: bool = True) -> Optional[str]:
    """
    使用 yt-dlp 下載 YouTube 影片的音訊
    
    Args:
        youtube_url (str): YouTube 影片的 URL
        encode_string (bool): 是否將音訊檔案編碼為 base64 字串
    
    Returns:
        Optional[str]: 如果 encode_string 為 True，返回 base64 編碼的音訊字串；否則返回音訊檔案路徑
    """
    from app.constants import AUDIO_FILE_PATTERN, AUDIO_DOWNLOAD_TIMEOUT
    audio_file = AUDIO_FILE_PATTERN
    
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
        subprocess.run(command, check=True, timeout=AUDIO_DOWNLOAD_TIMEOUT)
        
        if os.path.exists(audio_file):
            if encode_string:
                try:
                    with open(audio_file, "rb") as audio:
                        encoded_string = base64.b64encode(audio.read()).decode('utf-8')
                    os.remove(audio_file)
                    return encoded_string
                except (OSError, IOError) as e:
                    print(f"Error processing audio file: {e}")
                    if os.path.exists(audio_file):
                        os.remove(audio_file)
                    return None
            else:
                return audio_file
        return None
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print(f"Error downloading audio: {e}")
        if os.path.exists(audio_file):
            try:
                os.remove(audio_file)
            except OSError:
                pass
        return None

def get_youtube_img(youtube_url: str) -> Optional[str]:
    """return youtube video thumbnail url"""
    from app.constants import THUMBNAIL_TIMEOUT
    command = [
        "yt-dlp",
        "--get-thumbnail",
        youtube_url
    ]
    try:
        result = subprocess.run(command, capture_output=True, timeout=THUMBNAIL_TIMEOUT, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"Error getting thumbnail: {result.stderr}")
            return None
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
        print(f"Error getting thumbnail: {e}")
        return None

def get_youtube_thumbnail(youtube_url: str) -> Optional[str]:
    """Alias for get_youtube_img for consistency"""
    return get_youtube_img(youtube_url)

def search_channel_id(channel_name: str):
    """
    根據頻道名稱搜尋頻道 ID
    
    Args:
        channel_name (str): YouTube 頻道名稱
    
    Returns:
        tuple: (channel_id, channel_name) or None if not found
    """
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
