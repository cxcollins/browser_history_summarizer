import sqlite3

def setup():
    conn = sqlite3.connect("summaries.db")
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS summaries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE,
        title TEXT NOT NULL,
        summary TEXT NOT NULL,
        visit_time DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup()
    print("Database setup complete")
