from datetime import date
from db import get_connection, init_db
from your_streamlit_file import fetch_article_italian, fetch_article_german

def insert_article(langue, title, url, content):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO articles
        (langue, titre, contenu, url, date_publication)
        VALUES (?, ?, ?, ?, ?)
    """, (langue, title, content, url, date.today()))

    conn.commit()
    conn.close()

def cleanup():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM articles
        WHERE date_publication < DATE('now', '-1 day')
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()

    it_title, it_url, it_content = fetch_article_italian()
    de_title, de_url, de_content = fetch_article_german()

    if it_content:
        insert_article("it", it_title, it_url, it_content)

    if de_content:
        insert_article("de", de_title, de_url, de_content)

    cleanup()
