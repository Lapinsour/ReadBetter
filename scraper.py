from datetime import date
import sqlite3
import random
import re
from collections import Counter

from db import get_connection, init_db
from scrapers import fetch_article_italian, fetch_article_german
from deep_translator import GoogleTranslator


# -----------------------------
# ARTICLES
# -----------------------------
def insert_article(langue, title, url, content):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO articles (langue, titre, contenu, url, date_publication)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """, (langue, title, content, url, date.today()))

    article_id = cursor.fetchone()[0]

    conn.commit()
    conn.close()

    return article_id


# -----------------------------
# CLEANUP
# -----------------------------
def cleanup():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM articles
        WHERE date_publication < CURRENT_DATE - INTERVAL '2 days'
    """)

    conn.commit()
    conn.close()

# -----------------------------
# VOCAB EXTRACTION
# -----------------------------
def extract_keywords(text, n=10):
    words = re.findall(r"\b[a-zA-ZÀ-ÿ]{4,}\b", text.lower())

    freq = Counter(words)

    common_words = [w for w, _ in freq.most_common(50)]

    return random.sample(common_words, min(n, len(common_words)))


def translate_words(words, src, tgt):
    return [
        (w, GoogleTranslator(source=src, target=tgt).translate(w))
        for w in words
    ]


# -----------------------------
# VOCAB INSERT
def insert_vocab(article_id, vocab_list):
    conn = get_connection()
    cursor = conn.cursor()

    for mot, trad in vocab_list:
        cursor.execute("""
            INSERT INTO vocabulaire (article_id, mot, traduction)
            VALUES (%s, %s, %s)
        """, (article_id, mot, trad))

    conn.commit()
    conn.close()



# -----------------------------
# MAIN PIPELINE
# -----------------------------
if __name__ == "__main__":
    init_db()

    # ---------------- ITALIEN ----------------
    it_title, it_url, it_content = fetch_article_italian()

    if it_content:
        it_article_id = insert_article("it", it_title, it_url, it_content)

        words = extract_keywords(it_content)
        vocab = translate_words(words, "it", "fr")
        insert_vocab(it_article_id, vocab)


    # ---------------- ALLEMAND ----------------
    de_title, de_url, de_content = fetch_article_german()

    if de_content:
        de_article_id = insert_article("de", de_title, de_url, de_content)

        words = extract_keywords(de_content)
        vocab = translate_words(words, "de", "fr")
        insert_vocab(de_article_id, vocab)


    cleanup()
