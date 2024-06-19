import requests
import sqlite3
import pytz
from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
import os
import logging


# 获取 Token 的函数
def get_token():
    auth_url = 'http://10.50.4.1:8021/api/auth/getToken'
    auth_data = {'ticket': 'faef665031bca436a38795c2016e13ce'}
    response = requests.post(auth_url, json=auth_data)
    token_data = response.json()
    if token_data['code'] == 0:
        return token_data['data']['token']
    else:
        raise Exception("Failed to get token: " + token_data['msg'])

# 使用 Token 请求数据的函数，根据当前时间计算时间窗口
def fetch_data(token):
    now = datetime.now()
    endTime = int(now.timestamp() * 1000)  # 当前时间的时间戳，单位毫秒
    beginTime = int((now - timedelta(days=0.5)).timestamp() * 1000)  # 半天前的时间戳，单位毫秒

    url = f'http://10.50.4.1:8021/api/file/list?_token={token}'
    data = {
        'page': 0,
        'pageSize': 100,
        'beginTime': beginTime,
        'endTime': endTime
    }
    response = requests.post(url, json=data)
    return response.json()


def download_video_file(video):
    try:
        video_url = video['downloadPath']
        local_filename = os.path.join("D:/videos", video['fileName'])
        os.makedirs(os.path.dirname(local_filename), exist_ok=True)

        print(f"Starting download for {video_url}...")

        # 检查 URL 是否有效
        response = requests.head(video_url)
        if response.status_code != 200:
            print(f"Failed to access {video_url}: Status code {response.status_code}")
            return None

        # 进行实际下载
        response = requests.get(video_url, stream=True)
        if response.status_code == 200:
            with open(local_filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Video {video['fileName']} downloaded successfully.")
            return local_filename
        else:
            print(f"Failed to download {video_url}: Status code {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Request error for {video_url}: {e}")
        return None
    except Exception as e:
        print(f"Error downloading video {video['fileName']}: {e}")
        return None

def timestamp_to_datetime(ts):
    try:
        # 时间戳是以毫秒为单位，转换为秒
        tz = pytz.timezone('Asia/Shanghai')
        return datetime.fromtimestamp(ts / 1000.0,tz)
    except Exception as e:
        print(f"Error converting timestamp: {e}")
        return None

# 主执行函数，增加数据库插入检查避免重复插入
def main():
    print("Starting main function...")
    try:
        print("Getting token...")
        token = get_token()
        print(f"Token obtained: {token}")

        print("Fetching data...")
        response_data = fetch_data(token)
        print(f"Data fetched: {response_data}")

        if response_data['code'] == 0 and 'currentElements' in response_data['data']:
            conn = sqlite3.connect('videos.db')
            c = conn.cursor()
            print("Database connected, checking table...")

            c.execute('''
                CREATE TABLE IF NOT EXISTS videos (
                    rid TEXT PRIMARY KEY,
                    fileName TEXT,
                    size INTEGER,
                    duration INTEGER,
                    type INTEGER,
                    orgCode TEXT,
                    orgName TEXT,
                    userCode TEXT,
                    userName TEXT,
                    startTime DATETIME,
                    endTime DATETIME,
                    importTime DATETIME,
                    insertTime DATETIME,
                    deviceId TEXT,
                    downloadPath TEXT,
                    thumbnailUrl TEXT
                )
            ''')
            print("Table checked/created...")

            for video in response_data['data']['currentElements']:
                # Check if the record already exists
                c.execute('SELECT rid FROM videos WHERE rid = ?', (video['rid'],))
                if c.fetchone() is None:
                    print(f"Inserting new record for {video['rid']}...")
                    c.execute('''
                        INSERT INTO videos (rid, fileName, size, duration, type, orgCode, orgName, userCode, userName, startTime, endTime, importTime, insertTime, deviceId, downloadPath, thumbnailUrl)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        video['rid'],
                        video['fileName'],
                        video['size'],
                        video['duration'],
                        video['type'],
                        video['orgCode'],
                        video['orgName'],
                        video['userCode'],
                        video['userName'],
                        timestamp_to_datetime(video['startTime']),
                        timestamp_to_datetime(video['endTime']),
                        timestamp_to_datetime(video['importTime']),
                        timestamp_to_datetime(video['insertTime']),
                        video['deviceId'],
                        video['downloadPath'],
                        video['thumbnailUrl']
                    ))
                else:
                    print(f"Record already exists for {video['rid']}, skipping...")

            conn.commit()
            conn.close()
            print("Data inserted successfully.")
        else:
            print("Data fetch error: ", response_data['msg'])
    except Exception as e:
        print("An error occurred:", e)


scheduler = BlockingScheduler(timezone=pytz.timezone("Asia/Shanghai"))
scheduler.add_job(main, 'interval', hours=12, next_run_time=datetime.now())
print("Scheduler started...")
scheduler.start()




