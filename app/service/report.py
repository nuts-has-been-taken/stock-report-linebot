from matplotlib.ticker import FuncFormatter
from datetime import datetime, timedelta
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import json
import os

from app.db.report import save_report, get_daily_future, get_daily_major_invest, get_daily_margin, save_daily_future, save_daily_major_invest, save_daily_margin
from app.db.minio import upload_image
from app.core.config import LOCAL_HOST

### 三大法人
def get_today_major_investors(date:datetime):
    
    major_invest = get_daily_major_invest(date)
    if major_invest:
        res = {
            '日期':date,
            '外資':major_invest.foreign_investors,
            '投信':major_invest.investment_trust,
            '自營商':major_invest.dealer
        }
        
        return res
    else:
        url = "https://www.twse.com.tw/rwd/zh/fund/BFI82U"
        body = {
            'response': 'json',
            'dayDate': date.strftime('%Y%m%d'),
            'type': 'day'
        }
        r = requests.post(url, data=body)
        r = json.loads(r.content)
        if r['stat'] != "OK":
            return None
        data = r['data']
        foreign_investors = int(data[3][3].replace(',', ''))+int(data[4][3].replace(',', ''))
        investment_trust = int(data[2][3].replace(',', ''))
        dealer = int(data[0][3].replace(',', ''))+int(data[1][3].replace(',', ''))
        error_msg = save_daily_major_invest(date, foreign_investors, investment_trust, dealer)
        res = {
            '日期':date,
            '外資':foreign_investors,
            '投信':investment_trust,
            '自營商':dealer
        }
        
        return res

def create_major_investors_jpg(df:pd.DataFrame, file_path='major_plot.png'):
    
    # 調整字形
    font_path = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
    prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = prop.get_name()
    plt.rcParams['axes.unicode_minus'] = False
    
    # 處理表格
    df.set_index('日期', inplace=True)
    df = df.sort_index()
    tw = yf.download('^TWII', start=df.index[0], end=(df.index[len(df)-1]+timedelta(days=1)).strftime('%Y-%m-%d'))
    dates = df.index
    
    # 畫圖
    def format_func(value, tick_number):
        if value == 0:
            return int(value)
        return f'{int(value/100000000)} (億)'

    fig, ax1 = plt.subplots(figsize=(10, 6))

    bar_width = 0.5
    index = np.arange(len(dates))

    global_pos = df['外資'].clip(lower=0)
    global_neg = df['外資'].clip(upper=0)
    secu_pos = df['投信'].clip(lower=0)
    secu_neg = df['投信'].clip(upper=0)
    self_pos = df['自營商'].clip(lower=0)
    self_neg = df['自營商'].clip(upper=0)

    bar1 = ax1.bar(index, global_pos, bar_width, label='外資', color='#2894FF')
    bar2 = ax1.bar(index, secu_pos, bar_width, bottom=global_pos, label='投信', color='#B15BFF')
    bar3 = ax1.bar(index, self_pos, bar_width, bottom=global_pos + secu_pos, label='自營商', color='#FF8F59')

    ax1.bar(index, global_neg, bar_width, label='外資', color='#2894FF')
    ax1.bar(index, secu_neg, bar_width, bottom=global_neg, label='投信', color='#B15BFF')
    ax1.bar(index, self_neg, bar_width, bottom=global_neg + secu_neg, label='自營商', color='#FF8F59')

    ax1.axhline(0, color='black', linewidth=0.8, linestyle='-')
    ax1.grid(axis='y', linestyle='--', linewidth=0.7)
    ax1.set_xticks(index[::int(len(dates)/6)])
    ax1.set_xticklabels(dates[::int(len(dates)/6)].strftime('%Y-%m-%d'))
    ax1.set_xlabel('日期', rotation=0, labelpad=12)
    handles = [bar1, bar2, bar3]
    ax1.legend(handles=handles)

    ax1.yaxis.set_major_formatter(FuncFormatter(format_func))

    ax2 = ax1.twinx()

    ax2.plot(index, tw['Close'], color='red', label='指數', linewidth=2, linestyle='-')
    ax2.legend(loc='lower right')

    plt.title('每日各投資方買賣超金額及成交量')
    plt.savefig(file_path)

def create_major_investors_report(data_number=20):
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    trading_data = pd.DataFrame()
    trading_data['日期'] = None
    trading_data['外資'] = None
    trading_data['投信'] = None
    trading_data['自營商'] = None
    trading_data['合計'] = None
    
    # 抓取近期法人資訊
    while len(trading_data)<data_number:
        today_data = get_today_major_investors(today)
        if today_data:
            trading_data.loc[len(trading_data)] = today_data
        elif len(trading_data)==0: # 如果當天沒盤加上目前 df 是空的代表那天很有可能放假因此不傳
            return "今日訊息還沒更新"
        today -= timedelta(days=1)
    
    # 創建圖片
    file_path='major_plot.png'
    create_major_investors_jpg(trading_data, file_path)
    # 保存到 minIO
    sucess = upload_image(bucket_name='reports', object_name=f"{today.strftime('%Y-%m-%d')}_major.png", image_data=open(file_path, 'rb').read())
    # 刪除圖片  
    if os.path.exists(file_path):
        os.remove(file_path)
    # 保存到資料庫
    if sucess:
        msg = f"""外資：{(trading_data.loc[trading_data.index[0], '外資']/100000000):.1f} 億\n投信：{(trading_data.loc[trading_data.index[0], '投信']/100000000):.1f} 億\n自營商：{(trading_data.loc[trading_data.index[0], '自營商']/100000000):.1f} 億"""
        url = LOCAL_HOST + f"/img/?bucket=reports&object_name={today.strftime('%Y-%m-%d')}_major.png"
        error_msg = save_report(date=trading_data.index[0], report_type='法人', msg=msg, url=url)
        if error_msg:
            return error_msg
        else:
            return None
    else:
        return "儲存圖片失敗"

### 融資融券
def get_margin(date:datetime):
    
    margin = get_daily_margin(date)
    if margin:
        res = {
            '日期':date,
            '融券(張)':margin.margin_ticket,
            '融資金額(億)':margin.margin_amount
        }
        
        return res
    else:
        url = f"https://www.twse.com.tw/rwd/zh/marginTrading/MI_MARGN?date={date.strftime('%Y%m%d')}&selectType=MS&response=json&_=1724655679565"

        r = requests.get(url)
        r = json.loads(r.content)
        if r['stat'] != "OK":
            return None
        data = r['tables'][0]['data']
        margin_ticket = int(data[1][5].replace(',', ''))
        margin_amount = float(int(data[2][5].replace(',', ''))/100000)
        error_msg = save_daily_margin(date, margin_ticket, margin_amount)
        res = {
            '日期':date,
            '融券(張)':margin_ticket,
            '融資金額(億)':margin_amount,
        }
        
        return res

def create_margin_jpg(df:pd.DataFrame, file_path='margin_plot.png'):
    
    # 調整字形
    font_path = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
    prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = prop.get_name()
    plt.rcParams['axes.unicode_minus'] = False
    # 處理表格
    df.set_index('日期', inplace=True)
    df = df.sort_index()
    dates = df.index
    
    # 畫圖
    def format_func(value, tick_number):
        if value == 0:
            return int(value)
        return f'{int(value)} (億)'

    fig, ax1 = plt.subplots(figsize=(10, 6))

    bar_width = 0.5
    index = np.arange(len(dates))

    margin = df['融資金額(億)']

    ax1.bar(index, margin, bar_width, label='融資金額', color='#98F5F9')
    ax1.plot(index, margin, bar_width, label='融資金額', color='#060270')

    ax1.axhline(0, color='black', linewidth=0.8, linestyle='-')
    ax1.grid(axis='y', linestyle='--', linewidth=0.7)
    ax1.set_xticks(index[::int(len(dates)/6)])
    ax1.set_xticklabels(dates[::int(len(dates)/6)].strftime('%Y-%m-%d'))
    ax1.set_xlabel('日期', rotation=0, labelpad=12)
    
    ax1.yaxis.set_major_formatter(FuncFormatter(format_func))

    plt.title('融資金額')
    plt.savefig(file_path)

def create_margin_report(data_number=7):
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)    
    trading_data = pd.DataFrame()
    trading_data['日期'] = None
    trading_data['融券(張)'] = None
    trading_data['融資金額(億)'] = None
    
    # 抓取近期融資餘額資訊
    while len(trading_data)<data_number:
        today_data = get_margin(today)
        if today_data:
            trading_data.loc[len(trading_data)] = today_data
        elif len(trading_data)==0:
            return "今日訊息還沒更新"
        today -= timedelta(days=1)
    
    # 創建圖片
    file_path='margin_plot.png'
    create_margin_jpg(trading_data, file_path)
    # 保存到 minIO
    sucess = upload_image(bucket_name='reports', object_name=f"{today.strftime('%Y-%m-%d')}_margin.png", image_data=open(file_path, 'rb').read())
    # 刪除圖片
    if os.path.exists(file_path):
        os.remove(file_path)
    # 保存到資料庫
    if sucess:
        msg = f"""融券：{(trading_data.loc[trading_data.index[0], '融券(張)'])} 張\n融資：{(trading_data.loc[trading_data.index[0], '融資金額(億)']):.1f} 億"""
        url = LOCAL_HOST + f"/img/?bucket=reports&object_name={today.strftime('%Y-%m-%d')}_margin.png"
        error_msg = save_report(date=trading_data.index[0], report_type='籌碼', msg=msg, url=url)
        if error_msg:
            return error_msg
        else:
            return None
    else:
        return "儲存圖片失敗"

### 期貨
def get_futures(date:datetime):
    futures = get_daily_future(date)
    if futures:
        res = {
            "日期":date,
            "自營商":futures.dealer,
            "投信":futures.investment_trust,
            "外資":futures.foreign_investors
        }
        
        return res
    else:
        url = "https://www.taifex.com.tw/cht/3/futContractsDate"
        data = {
            'queryType': '1',
            'goDay': '',
            'doQuery': '1',
            'dateaddcnt': '',
            'queryDate': date.strftime('%Y/%m/%d'),
            'commodityId': '',
            'button': '送出查詢'
        }
        
        response = requests.post(url, data=data)
        soup = BeautifulSoup(response.content, 'html.parser')
        content = soup.find("tbody")
        if content:
            content = content.find_all("tr")
            foreign_investors = int(content[2].find_all("td", align="right")[10].text.strip().replace(',', ''))
            investment_trust = int(content[1].find_all("td", align="right")[10].text.strip().replace(',', ''))
            dealer = int(content[0].find_all("td", align="right")[10].text.strip().replace(',', ''))
            error_msg = save_daily_future(date, foreign_investors, investment_trust, dealer)
            res = {
                "日期":date,
                "外資":foreign_investors,
                "投信":investment_trust,
                "自營商":dealer
            }
        else:
            return None
        
        return res

def create_futures_jpg(df:pd.DataFrame, file_path='future_plot.png'):
    
    # 調整字形
    font_path = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
    prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = prop.get_name()
    plt.rcParams['axes.unicode_minus'] = False
    
    # 處理表格
    df.set_index('日期', inplace=True)
    df = df.sort_index()
    dates = df.index
    
    # 畫圖
    def format_func(value, tick_number):
        if value == 0:
            return int(value)
        return f'{int(value/10000)} 萬'

    fig, ax1 = plt.subplots(figsize=(10, 6))

    bar_width = 0.5
    index = np.arange(len(dates))

    global_pos = df['外資'].clip(lower=0)
    global_neg = df['外資'].clip(upper=0)
    secu_pos = df['投信'].clip(lower=0)
    secu_neg = df['投信'].clip(upper=0)
    self_pos = df['自營商'].clip(lower=0)
    self_neg = df['自營商'].clip(upper=0)

    bar1 = ax1.bar(index, global_pos, bar_width, label='外資', color='#2894FF')
    bar2 = ax1.bar(index, secu_pos, bar_width, bottom=global_pos, label='投信', color='#B15BFF')
    bar3 = ax1.bar(index, self_pos, bar_width, bottom=global_pos + secu_pos, label='自營商', color='#FF8F59')

    ax1.bar(index, global_neg, bar_width, label='外資', color='#2894FF')
    ax1.bar(index, secu_neg, bar_width, bottom=global_neg, label='投信', color='#B15BFF')
    ax1.bar(index, self_neg, bar_width, bottom=global_neg + secu_neg, label='自營商', color='#FF8F59')

    ax1.axhline(0, color='black', linewidth=0.8, linestyle='-')
    ax1.grid(axis='y', linestyle='--', linewidth=0.7)
    ax1.set_xticks(index[::int(len(dates)/6)])
    ax1.set_xticklabels(dates[::int(len(dates)/6)].strftime('%Y-%m-%d'))
    ax1.set_xlabel('日期', rotation=0, labelpad=12)
    handles = [bar1, bar2, bar3]
    ax1.legend(handles=handles, loc="upper left")

    ax1.yaxis.set_major_formatter(FuncFormatter(format_func))

    plt.title('三大法人期貨未平倉口數')
    plt.savefig(file_path)
    
def create_futures_report(data_number=7):
    
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)    
    trading_data = pd.DataFrame()
    trading_data['日期'] = None
    trading_data['自營商'] = None
    trading_data['投信'] = None
    trading_data['外資'] = None

    # 抓取近期融資餘額資訊
    while len(trading_data)<data_number:
        today_data = get_futures(today)
        if today_data:
            trading_data.loc[len(trading_data)] = today_data
        elif len(trading_data)==0:
            return "今日訊息還沒更新"
        today -= timedelta(days=1)
    
    # 創建圖片
    file_path='future_plot.png'
    create_futures_jpg(trading_data, file_path)
    # 保存到 minIO
    sucess = upload_image(bucket_name='reports', object_name=f"{today.strftime('%Y-%m-%d')}_future.png", image_data=open(file_path, 'rb').read())
    # 刪除圖片
    if os.path.exists(file_path):
        os.remove(file_path)
    # 保存到資料庫
    if sucess:
        msg = f"""外資：{(trading_data.loc[trading_data.index[0], '外資'])}\n投信：{(trading_data.loc[trading_data.index[0], '投信'])}\n自營商：{(trading_data.loc[trading_data.index[0], '自營商'])}"""
        url = LOCAL_HOST + f"/img/?bucket=reports&object_name={today.strftime('%Y-%m-%d')}_future.png"
        error_msg = save_report(date=trading_data.index[0], report_type='期貨', msg=msg, url=url)
        if error_msg:
            return error_msg
        else:
            return None
    else:
        return "儲存圖片失敗"