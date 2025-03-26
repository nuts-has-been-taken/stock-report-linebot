#!/bin/bash
SCRIPT_DIR=$(dirname "$(realpath "$0")")
if [ -f "$SCRIPT_DIR/.env" ]; then
  export $(grep -v '^#' "$SCRIPT_DIR/.env" | xargs)
fi
ENCODED_REPORT_TYPE=$(echo -n "籌碼" | jq -sRr @uri)
curl -X GET "$HOST/line/daily-report?event_id=$LINE_ID&report_type=$ENCODED_REPORT_TYPE&data_number=20"
