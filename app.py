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
        SELECT id, titre, contenu, url, date_publication
        FROM articles
        WHERE langue = ?
        ORDER BY date_publication DESC
    """, (langue,))

    rows = cursor.fetchall()
    conn.close()

    return rows


def get_vocab(article_id):
    conn = sqlite3.connect("articles.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT mot, traduction
        FROM vocabulaire
        WHERE article_id = ?
    """, (article_id,))

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
    return GoogleTranslator(
        source="auto",
        target="french"
    ).translate(text)


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

langue = st.selectbox("Langue", ["it", "de"])
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

        article_id, title, content, url, date_pub = articles[idx]

        st.header(title)
        st.markdown(f"[Lire l'article]({url})")
        if st.button("🧹 Masquer toutes les traductions"):
           st.session_state.trans = {}

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

st.subheader("📚 Vocabulaire du jour")

score = 0
answers = {}

vocab = get_vocab(article_id)

for i, (mot, trad) in enumerate(vocab):

    user_input = st.text_input(f"Traduire : {mot}", key=f"vocab_{i}")

    answers[mot] = (user_input, trad)

    if user_input.strip().lower() == trad.strip().lower():
        score += 1

if st.button("Valider le quiz"):
    st.success(f"Score : {score}/10")
