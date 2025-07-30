from app.db.youtube import save_youtube_vid, get_youtube_vid
from app.util.youtube import get_latest_live_stream, get_live_stream, get_youtube_subtitles, get_youtube_img, get_youtube_audio, get_youtube_thumbnail
from app.util.llm import create_summary, create_summary_audio, audio_transcript_subtitle
from app.constants import HAO_CHANNEL_ID, HAO_CHANNEL_NAME
from app.core.config import openai_client

from datetime import date, timedelta
import datetime
import os
from typing import Tuple, Optional
from app.model.postgresql import YouTubeVideo

AUDIO_MODE = openai_client.AUDIO_MODE
TRANS_FIRST = openai_client.TRANS_FIRST

def process_youtube_data(channel_id: str, current_date: datetime.date) -> Tuple[Optional[YouTubeVideo], Optional[str]]:
    """Process YouTube video data for a specific date
    
    Args:
        channel_id (str): YouTube channel ID
        current_date (datetime.date): Date to process
    
    Returns:
        Tuple[Optional[YouTubeVideo], Optional[str]]: (data, error_message)
    """
    title, url, vid_date = get_live_stream(channel_id, current_date)

    if url:
        # 下載 youtube 字幕
        subtitle = get_youtube_subtitles(url)
        if not subtitle:
            if TRANS_FIRST:
                # 先轉錄音訊後進行 summary
                audio = get_youtube_audio(youtube_url=url, encode_string=False)
                print("使用音訊進行轉錄")
                if audio:
                    try:
                        with open(audio, "rb") as audio_file:
                            transcript = audio_transcript_subtitle(audio_file)
                        print("轉錄完成，開始進行 summary")
                        summary = create_summary(transcript)
                    finally:
                        if os.path.exists(audio):
                            try:
                                os.remove(audio)
                            except OSError as e:
                                print(f"Warning: Could not remove audio file {audio}: {e}")
                else:
                    print("音訊下載失敗")
                    return None, "音訊下載失敗"
            elif AUDIO_MODE:
                # 直接使用音訊進行 summary
                audio = get_youtube_audio(youtube_url=url, encode_string=True)
                if audio:
                    print("使用音訊進行 summary")
                    summary = create_summary_audio(audio)
                else:
                    print("音訊下載失敗")
                    return None, "音訊下載失敗"
            else:
                return None, "字幕未上傳"
        else:
            # 使用字幕進行 summary
            summary = create_summary(subtitle)
        img_url = get_youtube_img(url)
        # 儲存報告
        if vid_date and title:
            data = save_youtube_vid(HAO_CHANNEL_NAME, channel_id, vid_date, title, url, summary, img_url)
        else:
            return None, "影片資料不完整"
        return data, None
    else:
        return None, "無法取得影片"

def get_today_hao_report() -> Tuple[bool, Optional[YouTubeVideo], Optional[str]]:
    """Get today's hao report from database or process new video
    
    Returns:
        Tuple[bool, Optional[YouTubeVideo], Optional[str]]: (success, data, error_message)
    """
    data = get_youtube_vid(HAO_CHANNEL_ID, datetime.date.today())
    if not data:
        title, url, vid_date = get_latest_live_stream(HAO_CHANNEL_ID)
        if vid_date != datetime.date.today():
            return False, None, "今日無直播"
        data, error = process_youtube_data(HAO_CHANNEL_ID, datetime.date.today())
        if error:
            return False, None, error
        return True, data, None
    else:
        return True, data, None

def generate_hao_report(start_date: Optional[date] = None, end_date: Optional[date] = None) -> Tuple[bool, Optional[YouTubeVideo], Optional[str]]:
    """Generate hao report for the past week if missing
    
    Args:
        start_date (date, optional): Start date for report generation. Defaults to 7 days ago.
        end_date (date, optional): End date for report generation. Defaults to today.
    
    Returns:
        Tuple[bool, Optional[YouTubeVideo], Optional[str]]: (success, data, error_message)
    """
    if start_date is None:
        start_date = datetime.date.today() - timedelta(days=7)
    if end_date is None:
        end_date = datetime.date.today()
    
    current_date = start_date

    while current_date <= end_date:
        data = get_youtube_vid(HAO_CHANNEL_ID, current_date)
        if not data:
            data, error = process_youtube_data(HAO_CHANNEL_ID, current_date)
            if error:
                current_date += timedelta(days=1)
                continue
            return True, data, None
        current_date += timedelta(days=1)
    return False, None, "無法產生報告"
