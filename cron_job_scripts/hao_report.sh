#!/bin/bash
# 載入 .env 檔案
SCRIPT_DIR=$(dirname "$(realpath "$0")")
if [ -f "$SCRIPT_DIR/.env" ]; then
  export $(grep -v '^#' "$SCRIPT_DIR/.env" | xargs)
fi
curl -X GET "$HOST/line/hao-report?event_id=$LINE_ID&cron_mode=True"
