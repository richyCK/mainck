import os
import requests
import sqlite3

def download_video_file(video_url, file_name):
    try:
        # 修改这里的路径到你想要保存视频的目录
        local_filename = os.path.join("D:/videos", file_name)
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
            print(f"Video {file_name} downloaded successfully.")
            return local_filename
        else:
            print(f"Failed to download {video_url}: Status code {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Request error for {video_url}: {e}")
        return None
    except Exception as e:
        print(f"Error downloading video {file_name}: {e}")
        return None

def fetch_videos_from_db(db_path):
    try:
        # 连接到 SQLite 数据库
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        # 查询视频数据
        query = "SELECT downloadPath, fileName FROM videos"
        cursor.execute(query)

        # 获取查询结果
        videos = cursor.fetchall()

        cursor.close()
        connection.close()

        # 将查询结果转换为字典列表
        videos_list = [{'video_url': video[0], 'file_name': video[1]} for video in videos]

        return videos_list

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return []

def main():
    print("Starting main function...")

    # 数据库路径
    db_path = 'videos.db'  # 修改为你的 SQLite 数据库文件路径

    # 从数据库获取视频数据
    video_data = fetch_videos_from_db(db_path)

    # 下载并保存视频
    for video in video_data:
        download_video_file(video['video_url'], video['file_name'])

    print("Main function completed.")

if __name__ == "__main__":
    main()
