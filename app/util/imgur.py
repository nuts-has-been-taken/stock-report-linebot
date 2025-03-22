from dotenv import load_dotenv
import datetime
import requests
import os

from app.db.imgur import get_token, save_token

def check_token_and_update():
    """Check if imgur token expired"""
    
    token = get_token()
    if token:
        if token.date < (datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0) - datetime.timedelta(days=25)).replace(tzinfo=None):
            print("Token soon expired, refreshing...")
            refresh_token = token.refresh_token
            load_dotenv()
            client_id = os.getenv('IMGUR_CLIENT_ID')
            client_secret = os.getenv('IMGUR_CLIENT_SECRET')
            access_token = get_oath2_token(refresh_token, client_id, client_secret)
            save_token(refresh_token, access_token)
            return access_token
        else:
            return token.access_token
    else:
        print("Database imgur token not found")
        return None
        
def get_oath2_token(refresh_token=None, client_id=None, client_secret=None):
    """Get new oath2 token"""
    
    url = 'https://api.imgur.com/oauth2/token'
    
    data = {
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'refresh_token'
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        return response.json()['access_token']
    except requests.exceptions.RequestException as e:
        print("Error getting token:", e)
        return None

def upload_imgur(image_path:str="./", name:str=""):
    """Upload image to imgur"""
    
    # 檢查檔案是否存在
    if not os.path.exists(image_path):
        print(f"檔案不存在：{image_path}")
        exit(1)
        
    url = 'https://api.imgur.com/3/image'
    
    today = datetime.date.today().strftime('%Y-%m-%d')
    
    data = {
        'type': 'image',
        'title': f'{today} tw stock {name}',
        'description': ''
    }
    
    files = {
        'image': open(image_path, 'rb')
    }
    
    access_token = check_token_and_update()
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, files=files)
        response.raise_for_status()
        print(f"imgur 上傳成功：{response.json()['data']['link']}")
        return True, response.json()['data']['link']
    except requests.exceptions.RequestException as e:
        print("上傳失敗：", e)
        return False, e
if __name__ == "__main__":
    upload_imgur(image_path="./chicken_chiwawa.jpg")