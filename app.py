import streamlit as st
import sqlite3
import re

def get_articles(langue):
    conn = sqlite3.connect("articles.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT titre, contenu, url, date_publication
        FROM articles
        WHERE langue = ?
        ORDER BY date_publication DESC
    """, (langue,))

    rows = cursor.fetchall()
    conn.close()

    return rows


def split_into_sentences(text):
    return re.split(r'(?<=[.!?]) +', text)


st.title("🌍 Entraînement multilingue")

langue = st.selectbox("Langue", ["it", "de"])
jour = st.selectbox("Article", ["Aujourd'hui", "Hier"])

articles = get_articles(langue)

if articles:
    idx = 0 if jour == "Aujourd'hui" else 1

    if len(articles) > idx:
        title, content, url, date_pub = articles[idx]

        st.header(title)
        st.markdown(f"[Lien vers l'article]({url})")

        sentences = split_into_sentences(content)

        for i, s in enumerate(sentences):
            if st.button(s, key=f"s_{i}"):
                st.write(s)
