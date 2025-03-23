from app.db.youtube import save_youtube_vid, get_today_youtube_vid
from app.util.youtube import get_latest_live_stream, get_youtube_subtitles
from app.util.llm import create_summary

from datetime import date

# 游庭皓的財經皓角
def get_hao_report():
    # 從資料庫取得資料
    channel_id = 'UC0lbAQVpenvfA2QqzsRtL_g'
    data = get_today_youtube_vid(channel_id)
    if not data:
        title, url, vid_date = get_latest_live_stream(channel_id)
        if vid_date != date.today():
            return False, None, "今日無直播"
        if url:
            # 下載 youtube 字幕
            subtitle = get_youtube_subtitles(url)
            # 呼叫 gpt 生成報告
            summary = create_summary(subtitle)
            # 儲存報告
            data = save_youtube_vid('游庭皓的財經皓角', channel_id, vid_date, title, url, summary)
            return True, data, None
        else:
            return False, None, "取得影片失敗"
    else:
        return True, data, None