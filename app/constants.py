"""Constants for the stock report LINE bot application."""

MAX_TOKENS_PER_CHUNK = 100000
CHUNK_OVERLAP_TOKENS = 500

SUBTITLE_DOWNLOAD_TIMEOUT = 300  # 5 minutes
AUDIO_DOWNLOAD_TIMEOUT = 600     # 10 minutes
THUMBNAIL_TIMEOUT = 30           # 30 seconds

HAO_CHANNEL_ID = "UC0lbAQVpenvfA2QqzsRtL_g"
HAO_CHANNEL_NAME = "游庭皓的財經皓角"

SUBTITLE_FILE_PATTERN = "subtitle.zh-TW.vtt"
AUDIO_FILE_PATTERN = "audio.mp3"

REPORT_TYPES = {
    "法人": "三大法人買賣超變化",
    "籌碼": "融資融券餘額變化", 
    "期貨": "三大法人期貨未平倉口數"
}
