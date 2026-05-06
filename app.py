import streamlit as st
import sqlite3
import re
from deep_translator import GoogleTranslator

# -----------------------------
# DB
# -----------------------------
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


# -----------------------------
# Utils
# -----------------------------
def split_into_sentences(text):
    return re.split(r'(?<=[.!?]) +', text)


@st.cache_data
def translate(text, src, tgt):
    return GoogleTranslator(source=src, target=tgt).translate(text)


# -----------------------------
# Init session state
# -----------------------------
if "trans" not in st.session_state:
    st.session_state.trans = {}

if "sentences" not in st.session_state:
    st.session_state.sentences = []


# -----------------------------
# UI
# -----------------------------
st.title("🌍 Entraînement multilingue")

langue = st.selectbox("Langue", ["Italien", "Allemand"])
jour = st.selectbox("Article", ["Aujourd'hui", "Hier"])

articles = get_articles(langue)

# mapping langue
src = langue
tgt = "fr"


# -----------------------------
# Chargement article
# -----------------------------
if articles:

    idx = 0 if jour == "Aujourd'hui" else 1

    if len(articles) > idx:

        title, content, url, date_pub = articles[idx]

        st.header(title)
        st.markdown(f"[Lire l'article]({url})")

        sentences = split_into_sentences(content)
        st.session_state.sentences = sentences
        st.session_state.src = src
        st.session_state.tgt = tgt

        # -----------------------------
        # Affichage phrases
        # -----------------------------
        st.divider()

        for i, s in enumerate(sentences):

            key = f"{langue}_{jour}_{i}"
        
            if st.button(s, key=key):
        
                if i not in st.session_state.trans:
                    st.session_state.trans[i] = translate(
                        s,
                        st.session_state.src,
                        st.session_state.tgt
                    )
                else:
                    del st.session_state.trans[i]
        
            if i in st.session_state.trans:
                st.markdown(
                    f"<div style='color:green; margin-left:10px;'>{st.session_state.trans[i]}</div>",
                    unsafe_allow_html=True
                )

else:
    st.warning("Aucun article disponible dans la base.")
