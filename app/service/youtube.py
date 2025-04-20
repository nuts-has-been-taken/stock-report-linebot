from app.db.youtube import save_youtube_vid, get_youtube_vid
from app.util.youtube import get_latest_live_stream, get_live_stream, get_youtube_subtitles, get_youtube_img, get_youtube_audio
from app.util.llm import create_summary, create_summary_audio, audio_transcript_subtitle
from app.core.config import openai_client

from datetime import date, timedelta
import os

AUDIO_MODE = openai_client.AUDIO_MODE
TRANS_FIRST = openai_client.TRANS_FIRST

# 財經皓角頻道
HAO_CHANNEL_ID = 'UC0lbAQVpenvfA2QqzsRtL_g'

def process_youtube_data(channel_id, current_date):
    title, url, vid_date = get_live_stream(channel_id, current_date)

    if url:
        # 下載 youtube 字幕
        subtitle = get_youtube_subtitles(url)
        if not subtitle:
            if TRANS_FIRST:
                # 先轉錄音訊後進行 summary
                audio = get_youtube_audio(youtube_url=url, encode_string=False)
                print("使用音訊進行轉錄")
                transcript = audio_transcript_subtitle(audio)
                os.remove(audio) # 刪除音訊檔案
                print("轉錄完成，開始進行 summary")
                summary = create_summary(transcript)
            elif AUDIO_MODE:
                # 直接使用音訊進行 summary
                audio = get_youtube_audio(youtube_url=url, encode_string=True)
                print("使用音訊進行 summary")
                summary = create_summary_audio(audio)
            else:
                return None, "字幕未上傳"
        else:
            # 使用字幕進行 summary
            summary = create_summary(subtitle)
        img_url = get_youtube_img(url)
        # 儲存報告
        data = save_youtube_vid('游庭皓的財經皓角', channel_id, vid_date, title, url, summary, img_url)
        return data, None
    else:
        return None, "無法取得影片"

# 游庭皓的財經皓角
def get_today_hao_report():
    # 從資料庫取得資料
    data = get_youtube_vid(HAO_CHANNEL_ID, date.today())
    if not data:
        title, url, vid_date = get_latest_live_stream(HAO_CHANNEL_ID)
        if vid_date != date.today():
            return False, None, "今日無直播"
        data, error = process_youtube_data(HAO_CHANNEL_ID, date.today())
        if error:
            return False, None, error
        return True, data, None
    else:
        return True, data, None

# 下載指定時間區間內的報告
def get_hao_report(start_date:date, end_date:date):
    current_date = start_date
    all_data = []

    while current_date <= end_date:
        data = get_youtube_vid(HAO_CHANNEL_ID, current_date)
        if not data:
            data, error = process_youtube_data(HAO_CHANNEL_ID, current_date)
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