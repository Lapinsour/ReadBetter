import sqlite3

DB_PATH = "articles.db"


# -----------------------------
# Connexion
# -----------------------------
def get_connection():
    return sqlite3.connect(DB_PATH)


# -----------------------------
# Init DB complète
# -----------------------------
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # -------------------------
    # ARTICLES
    # -------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            langue TEXT,
            titre TEXT,
            contenu TEXT,
            url TEXT,
            date_publication DATE
        )
    """)

    # -------------------------
    # VOCABULAIRE (10 mots / article)
    # -------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vocabulaire (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id INTEGER,
            mot TEXT,
            traduction TEXT,
            FOREIGN KEY(article_id) REFERENCES articles(id)
        )
    """)

    # -------------------------
    # STATS utilisateur
    # -------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            date DATE,
            score INTEGER
        )
    """)

    # -------------------------
    # DICTIONNAIRE utilisateur
    # -------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dictionnaire (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            date DATE,
            mot TEXT,
            traduction TEXT
        )
    """)

    conn.commit()
    conn.close()
