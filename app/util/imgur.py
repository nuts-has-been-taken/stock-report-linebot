import os
import requests
from dotenv import load_dotenv

def upload_imgur(image_path:str="./"):
    """Upload image to imgur"""
    
    load_dotenv()
    
    client_id = os.getenv('IMGUR_CLIENT_ID')

    if not client_id:
        print("環境變數 IMGUR_CLIENT_ID 未設定。")
        exit(1)

    # 檢查檔案是否存在
    if not os.path.exists(image_path):
        print(f"檔案不存在：{image_path}")
        exit(1)
        
    url = 'https://api.imgur.com/3/image'
    
    data = {
        'type': 'image',
        'title': 'tw stock bot img',
        'description': ''
    }
    
    files = {
        'image': open(image_path, 'rb')
    }
    
    headers = {
        'Authorization': f'Client-ID {client_id}'
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, files=files)
        response.raise_for_status()
        # print(response.json())
        print(f"imgur 上傳成功：{response.json()['data']['link']}")
        return True, response.json()['data']['link']
    except requests.exceptions.RequestException as e:
        print("上傳失敗：", e)
        return False, e
if __name__ == "__main__":
    upload_imgur(image_path="./chicken_chiwawa.jpg")