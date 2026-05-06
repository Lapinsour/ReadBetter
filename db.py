import sqlite3

DB_PATH = "articles.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            langue TEXT,
            titre TEXT,
            contenu TEXT,
            url TEXT,
            date_publication DATE,
            UNIQUE(langue, date_publication)
        )
    """)

    conn.commit()
    conn.close()
