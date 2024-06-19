import sqlite3

def view_data():
    conn = sqlite3.connect('videos.db')
    c = conn.cursor()
    c.execute('SELECT * FROM videos')
    rows = c.fetchall()
    for row in rows:
        print(row)
    conn.close()

view_data()