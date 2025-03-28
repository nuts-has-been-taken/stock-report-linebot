from app.db.youtube import save_youtube_vid, get_youtube_vid
from app.util.youtube import get_latest_live_stream, get_live_stream, get_youtube_subtitles, get_youtube_img
from app.util.llm import create_summary

from datetime import date, timedelta

# 游庭皓的財經皓角
def get_today_hao_report():
    # 從資料庫取得資料
    channel_id = 'UC0lbAQVpenvfA2QqzsRtL_g'
    data = get_youtube_vid(channel_id, date.today())
    if not data:
        title, url, vid_date = get_latest_live_stream(channel_id)
        if vid_date != date.today():
            return False, None, "今日無直播"
        if url:
            # 下載 youtube 字幕
            subtitle = get_youtube_subtitles(url)
            if not subtitle:
                return False, None, "今日字幕還沒上傳，請稍後在試"
            img_url = get_youtube_img(url)
            # 呼叫 gpt 生成報告
            summary = create_summary(subtitle)
            # 儲存報告
            data = save_youtube_vid('游庭皓的財經皓角', channel_id, vid_date, title, url, summary, img_url)
            return True, data, None
        else:
            return False, None, "取得影片失敗"
    else:
        return True, data, None

# 下載指定時間區間內的報告
def get_hao_report(start_date:date, end_date:date):
    channel_id = 'UC0lbAQVpenvfA2QqzsRtL_g'
    current_date = start_date
    all_data = []

    while current_date <= end_date:
        # 從資料庫取得當天資料
        data = get_youtube_vid(channel_id, current_date)
        if not data:
            title, url, vid_date = get_live_stream(channel_id, current_date)
            if vid_date != current_date:
                current_date += timedelta(days=1)
                continue
            if url:
                # 下載 youtube 字幕
                subtitle = get_youtube_subtitles(url)
                if not subtitle:
                    current_date += timedelta(days=1)
                    continue
                # 呼叫 gpt 生成報告
                summary = create_summary(subtitle)
                # 儲存報告
                data = save_youtube_vid('游庭皓的財經皓角', channel_id, vid_date, title, url, summary)
                all_data.append(data)
            else:
                current_date += timedelta(days=1)
                continue
        else:
            all_data.append(data)
        
        current_date += timedelta(days=1)

    if not all_data:
        return "指定時間區間內無報告"
    else:
        return all_data