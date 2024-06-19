from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

# API端点，用于获取视频数据，支持分页
@app.route('/api/videos')
def get_videos():
    # 获取分页参数，默认值page=1, pageSize=10y

    page = request.args.get('page', 1, type=int)
    pageSize = request.args.get('pageSize', 10, type=int)

    # 计算起始行
    start = (page - 1) * pageSize

    conn = sqlite3.connect('videos.db')
    cursor = conn.cursor()
    
    # 查询总条目数以计算总页数
    cursor.execute("SELECT COUNT(*) FROM videos")
    total_count = cursor.fetchone()[0]
    total_pages = (total_count + pageSize - 1) // pageSize  # 计算总页数

    # 执行分页查询
    cursor.execute("SELECT * FROM videos LIMIT ? OFFSET ?", (pageSize, start))
    rows = cursor.fetchall()
    conn.close()

    # 将数据库查询结果转换为JSON格式
    videos = [
        {
            'rid': row[0],
            'fileName': row[1],
            'size': row[2],
            'duration': row[3],
            'type': row[4],
            'orgCode': row[5],
            'orgName': row[6],
            'userCode': row[7],
            'userName': row[8],
            'startTime': row[9],
            'endTime': row[10],
            'importTime': row[11],
            'insertTime': row[12],
            'deviceId': row[13],
            'downloadPath': row[14],
            'thumbnailUrl': row[15]
        } for row in rows
    ]

    return jsonify({
        'total_pages': total_pages,
        'total_count': total_count,
        'current_page': page,
        'page_size': pageSize,
        'videos': videos
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
