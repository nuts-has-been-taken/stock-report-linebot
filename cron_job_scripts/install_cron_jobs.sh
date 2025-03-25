#!/bin/bash

SCRIPT_DIR=$(dirname "$(realpath "$0")")

# 設定要新增的 cron job
FUTURES_REPORT="5 15 * * * source $SCRIPT_DIR/.env && /bin/bash $SCRIPT_DIR/futures_report.sh"
MAJOR_REPORT="5 15 * * * source $SCRIPT_DIR/.env && /bin/bash $SCRIPT_DIR/major_report.sh"
MARJIN_REPORT="0 21 * * * source $SCRIPT_DIR/.env && /bin/bash $SCRIPT_DIR/margin_report.sh"
HAO_REPORT="0 11 * * * source $SCRIPT_DIR/.env && /bin/bash $SCRIPT_DIR/hao_report.sh"

# 檢查並逐一加入 cron job
(crontab -l 2>/dev/null) | grep -v "$SCRIPT_DIR" | crontab -

# 檢查並加入 FUTURES_REPORT
if ! crontab -l | grep -q "$FUTURES_REPORT"; then
  (crontab -l 2>/dev/null; echo "$FUTURES_REPORT") | crontab -
fi

# 檢查並加入 MAJOR_REPORT
if ! crontab -l | grep -q "$MAJOR_REPORT"; then
  (crontab -l 2>/dev/null; echo "$MAJOR_REPORT") | crontab -
fi

# 檢查並加入 MARJIN_REPORT
if ! crontab -l | grep -q "$MARJIN_REPORT"; then
  (crontab -l 2>/dev/null; echo "$MARJIN_REPORT") | crontab -
fi

# 檢查並加入 HAO_REPORT
if ! crontab -l | grep -q "$HAO_REPORT"; then
  (crontab -l 2>/dev/null; echo "$HAO_REPORT") | crontab -
fi