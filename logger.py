import logging
from logging.handlers import RotatingFileHandler

# 設定 Log 格式
LOG_FORMAT = "%(asctime)s [%(levelname)s] [%(name)s]: %(message)s"
LOG_FILE = "app.log"

# 設定 Logger
logger = logging.getLogger("LineBot")
logger.setLevel(logging.INFO)

# Console 輸出
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(console_handler)

# File 輸出 + Log Rotation (最大 1MB，保留 3 個檔案)
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=1 * 1024 * 1024, backupCount=3)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(file_handler)