from datetime import date
from db import get_connection, init_db
from scrapers import fetch_article_italian, fetch_article_german
import random
import re
from collections import Counter
from deep_translator import GoogleTranslator

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


def extract_keywords(text, n=10):
    words = re.findall(r"\b[a-zA-ZÀ-ÿ]{4,}\b", text.lower())

    freq = Counter(words)

    common_words = [w for w, _ in freq.most_common(50)]

    return random.sample(common_words, min(n, len(common_words)))


def translate_words(words, src, tgt):
    return [(w, GoogleTranslator(source=src, target=tgt).translate(w)) for w in words]

def insert_vocab(article_id, vocab_list):
    conn = sqlite3.connect("articles.db")
    cursor = conn.cursor()

    for mot, trad in vocab_list:
        cursor.execute("""
            INSERT INTO vocabulaire (article_id, mot, traduction)
            VALUES (?, ?, ?)
        """, (article_id, mot, trad))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()

    it_title, it_url, it_content = fetch_article_italian()
    de_title, de_url, de_content = fetch_article_german()

    if it_content:
        insert_article("Italien", it_title, it_url, it_content)
        

    if de_content:
        insert_article("Allemand", de_title, de_url, de_content)

    words = extract_keywords(content)
    vocab = translate_words(words, "it", "fr")
    insert_vocab(article_id, vocab)

    

    cleanup()
