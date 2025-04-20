from app.db.youtube import save_youtube_vid, get_youtube_vid
from app.util.youtube import get_latest_live_stream, get_live_stream, get_youtube_subtitles, get_youtube_img, get_youtube_audio
from app.util.llm import create_summary, create_summary_audio
from app.core.config import openai_client

from datetime import date, timedelta

AUDIO_MODE = openai_client.AUDIO_MODE

def process_youtube_data(channel_id, current_date, url=None):
    if not url:
        title, url, vid_date = get_live_stream(channel_id, current_date)
    else:
        title, vid_date = None, current_date  # 如果 URL 已提供，則不需要再取得

    if url:
        # 下載 youtube 字幕
        subtitle = get_youtube_subtitles(url)
        if not subtitle and not AUDIO_MODE:
            return None, "字幕未上傳"
        elif not subtitle and AUDIO_MODE:
            audio = get_youtube_audio(url)
            print("使用音訊進行 summary")
            summary = create_summary_audio(audio)
        else:
            # 呼叫 gpt 生成報告
            summary = create_summary(subtitle)
        img_url = get_youtube_img(url) if title else None
        # 儲存報告
        data = save_youtube_vid('游庭皓的財經皓角', channel_id, vid_date, title, url, summary, img_url)
        return data, None
    else:
        return None, "無法取得影片"

# 游庭皓的財經皓角
def get_today_hao_report():
    # 從資料庫取得資料
    channel_id = 'UC0lbAQVpenvfA2QqzsRtL_g'
    data = get_youtube_vid(channel_id, date.today())
    if not data:
        title, url, vid_date = get_latest_live_stream(channel_id)
        if vid_date != date.today():
            return False, None, "今日無直播"
        data, error = process_youtube_data(channel_id, date.today(), url)
        if error:
            return False, None, error
        return True, data, None
    else:
        return True, data, None

# 下載指定時間區間內的報告
def get_hao_report(start_date:date, end_date:date):
    channel_id = 'UC0lbAQVpenvfA2QqzsRtL_g'
    current_date = start_date
    all_data = []

    while current_date <= end_date:
        data = get_youtube_vid(channel_id, current_date)
        if not data:
            data, error = process_youtube_data(channel_id, current_date)
            if error:
                current_date += timedelta(days=1)
                continue
        if data:
            all_data.append(data)
        current_date += timedelta(days=1)

    if not all_data:
        return "指定時間區間內無報告"
    else:
        return all_data