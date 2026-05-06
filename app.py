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

def save_stats(user, score):
    conn = sqlite3.connect("articles.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO stats (user, date, score)
        VALUES (?, DATE('now'), ?)
    """, (user, score))

    conn.commit()
    conn.close()


def save_dictionary(user, vocab):
    conn = sqlite3.connect("articles.db")
    cursor = conn.cursor()

    for mot, trad in vocab:
        cursor.execute("""
            INSERT INTO dictionnaire (user, date, mot, traduction)
            VALUES (?, DATE('now'), ?, ?)
        """, (user, mot, trad))

    conn.commit()
    conn.close()


def get_stats(user):
    conn = sqlite3.connect("articles.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT date, score
        FROM stats
        WHERE user = ?
        ORDER BY date DESC
    """, (user,))

    return cursor.fetchall()

def get_dictionary(user):
    conn = sqlite3.connect("articles.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT mot, traduction, date
        FROM dictionnaire
        WHERE user = ?
    """, (user,))

    return cursor.fetchall()


# -----------------------------
# Utils
# -----------------------------
def split_into_sentences(text):
    return re.split(r'(?<=[.!?]) +', text)


@st.cache_data
def translate(text, src, tgt):
    return GoogleTranslator(
        source=src,
        target=tgt
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
menu = st.sidebar.selectbox(
    "Navigation",
    ["Lecture", "Quiz", "Dictionnaire", "Progression"]
)

if menu == "Progression":

    st.subheader("📈 Progression")

    stats = get_stats("user1")

    for d, s in stats:
        st.write(f"{d} → {s}/10")

if menu == "Dictionnaire":
    
    st.subheader("📖 Dictionnaire")
    
    dict_data = get_dictionary("user1")
    
    for mot, trad, date in dict_data:
        st.write(f"{mot} → {trad} ({date})")

if menu == "Lecture":
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
            st.session_state.article_id = article_id
            st.session_state.vocab = get_vocab(article_id)
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

if menu == "Quiz":
    st.subheader("📚 Vocabulaire du jour")
    
    score = 0
    answers = {}
    
    if "article_id" in st.session_state:
        vocab = get_vocab(st.session_state.article_id)
    else:
        st.warning("Aucun article sélectionné.")
        st.stop()
    
    for i, (mot, trad) in enumerate(vocab):
    
        user_input = st.text_input(f"Traduire : {mot}", key=f"vocab_{i}")
    
        answers[mot] = (user_input, trad)
    
        if user_input.strip().lower() == trad.strip().lower():
            score += 1
    
    if st.button("Valider le quiz"):

        score = 0
    
        for i, (mot, trad) in enumerate(vocab):
            user_input = st.session_state.get(f"vocab_{i}", "")
    
            if user_input.strip().lower() == trad.strip().lower():
                score += 1
    
        st.success(f"Score : {score}/10")
    
        save_stats("user1", score)
        save_dictionary("user1", vocab)
