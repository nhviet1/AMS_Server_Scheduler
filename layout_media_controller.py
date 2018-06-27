import threading
import time
import db_query


class LayoutControlThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            change_layout()


def change_layout():
    db = db_query.get_conn()
    query = "SELECT `toName`, `isMoved` FROM `media_temp`  ORDER BY `id` DESC LIMIT 2"
    cur = db.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    if len(rows) == 2:
        if str(rows[0][1]) == "1":
            db_query.set_buffer_media(rows[0][0], "15")
        if str(rows[1][1]) == "1":
            db_query.set_streaming_media(rows[1][0], "11")
    db.close()
    time.sleep(120)


