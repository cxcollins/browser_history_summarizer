import sqlite3
import datetime
import os
from dotenv import load_dotenv
from typing import List, Tuple

load_dotenv()
history_path = os.getenv("HISTORY_PATH")


def ingest_safari_history(days_back) -> List[Tuple[str, str, float]]:
    conn = sqlite3.connect(history_path)
    cursor = conn.cursor()

    # Need to subtract Mac epoch time from when we want to start, get seconds
    how_far_back = datetime.datetime.now() - datetime.timedelta(days=days_back)
    mac_epoch = datetime.datetime(2001, 1, 1)

    start_ts = int((how_far_back - mac_epoch).total_seconds())

    query = '''
    SELECT history_items.url, history_visits.visit_time
    FROM history_items
    JOIN history_visits ON history_items.id = history_visits.history_item
    WHERE history_visits.visit_time > ?
    '''

    cursor.execute(query, (start_ts,))
    rows = cursor.fetchall()
    conn.close()

    return rows


if __name__ == '__main__':
    entries = ingest_safari_history(7)
    print(f"Fetched {len(entries)} entries")
    print(entries[:5])
