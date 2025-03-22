from app.core.config import google_api

youtube = google_api.YOUTUBE

channel_id = 'UC0lbAQVpenvfA2QqzsRtL_g'

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
        url = f'https://www.youtube.com/watch?v={video_id}'
        return title, url
    else:
        return None, None

# 財金皓角
def get_hao_report():
    # 從資料庫取得資料
    # 如果有資料，則返回資料
    # 如果沒有資料，呼叫 gpt 生成報告
    # 儲存報告
    # 返回資料
    pass

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