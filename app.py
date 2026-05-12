import streamlit as st
import sqlite3
import re
from deep_translator import GoogleTranslator
from db import get_connection
import pandas as pd


# -----------------------------
# DB
# -----------------------------




def get_articles(langue):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, titre, contenu, url, date_publication
        FROM articles
        WHERE langue = %s
        ORDER BY date_publication DESC
    """, (langue,))

    rows = cursor.fetchall()
    

    return rows


def get_vocab(article_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT mot, traduction
        FROM vocabulaire
        WHERE article_id = %s
    """, (article_id,))

    rows = cursor.fetchall()
    
    return rows

def save_stats(username, langue, score):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO stats (username, langue, date, score)
        VALUES (%s, %s, CURRENT_DATE, %s)
    """, (username, langue, score))

    conn.commit()
    


def save_dictionary(username, langue, vocab):
    conn = get_connection()
    cursor = conn.cursor()

    for mot, trad in vocab:
        cursor.execute("""
            INSERT INTO dictionnaire (username, langue, date, mot, traduction)
            VALUES (%s, %s, CURRENT_DATE, %s, %s)
            ON CONFLICT (username, langue, mot) DO NOTHING
        """, (username, langue, mot, trad))

    conn.commit()
    


def get_stats(username, langue):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT date, score
        FROM stats
        WHERE username = %s AND langue = %s
        ORDER BY date DESC
    """, (username, langue))

    return cursor.fetchall()


def get_dictionary(username, langue):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT mot, traduction
        FROM dictionnaire
        WHERE username = %s AND langue = %s
        ORDER BY LOWER(mot) ASC
    """, (username, langue))

    rows = cursor.fetchall()
    
    return rows

def has_already_done_quiz(username, langue):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 1
        FROM stats
        WHERE username = %s
          AND langue = %s
          AND date = CURRENT_DATE
        LIMIT 1
    """, (username, langue))

    return cursor.fetchone() is not None

# -----------------------------
# Utils
# -----------------------------
def split_into_sentences(text):
    return re.split(r'(?<=[.!?]) +', text)


@st.cache_data(show_spinner=False, ttl=86400)
def translate(text, src, tgt):
    return GoogleTranslator(
        source=src,
        target=tgt
    ).translate(text)

if "username" not in st.session_state:
    username_input = st.text_input("Ton nom")

    if not username_input:
        st.stop()

    st.session_state.username = username_input
    st.rerun()

if st.session_state.username:
    # -----------------------------
    # Init session state
    # -----------------------------
    if "trans" not in st.session_state:
        st.session_state.trans = {}
    
    if "sentences" not in st.session_state:
        st.session_state.sentences = []
    
    LANGUE_MAP = {
        "Italien": "it",
        "Allemand": "de"
    }
    
    # -----------------------------
    # UI
    # -----------------------------
    menu = st.sidebar.selectbox(
        "Navigation",
        ["Lecture", "Quiz", "Dictionnaire", "Progression"]
    )
    st.sidebar.markdown(f"👤 **{st.session_state.username}**")
    
    if st.sidebar.button("🚪 Changer d'utilisateur"):
        del st.session_state.username
        st.rerun()
    
    if menu == "Progression":

        col1, col2 = st.columns(2)
    
        with col1:
            st.markdown("### 🇮🇹 Italien")
    
            stats_it = get_stats(st.session_state.username, "it")
    
            df_it = pd.DataFrame(
                stats_it,
                columns=["date", "score"]
            )
    
            if not df_it.empty:
                df_it["date"] = pd.to_datetime(df_it["date"])
                df_it = df_it.sort_values("date")
                df_it = df_it.set_index("date")
    
                st.line_chart(df_it["score"])
    
            else:
                st.info("Aucune donnée")
        

    

        with col2:
            st.markdown("###  Allemand")
    
            stats_de = get_stats(st.session_state.username, "de")
    
            df_de = pd.DataFrame(
                stats_de,
                columns=["date", "score"]
            )
    
            if not df_de.empty:
                df_de["date"] = pd.to_datetime(df_de["date"])
                df_de = df_de.sort_values("date")
                df_de = df_de.set_index("date")
    
                st.line_chart(df_de["score"])
    
            else:
                st.info("Aucune donnée")


    
    if menu == "Dictionnaire":
        
        st.subheader("📖 Dictionnaire")

        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🇮🇹 Italien")
            for mot, trad in get_dictionary(st.session_state.username, "it"):
                st.write(f"{mot} → {trad}")
        
        with col2:
            st.markdown("### 🇩🇪 Allemand")
            for mot, trad in get_dictionary(st.session_state.username, "de"):
                st.write(f"{mot} → {trad}")
    
    if menu == "Lecture":
        st.title("ReadBetter")
        
        langue_label = st.selectbox(
            "Langue",
            ["Italien", "Allemand"]
        )
        
        langue = LANGUE_MAP[langue_label]
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
                if "vocab_article_id" not in st.session_state or st.session_state.vocab_article_id != article_id:
                    st.session_state.vocab = get_vocab(article_id)
                    st.session_state.vocab_article_id = article_id
                st.session_state.langue = langue
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
    
    if menu == "Quiz":

        st.subheader("📚 Vocabulaire du jour")
    
        langue = st.session_state.get("langue")
    
        if not langue:
            st.warning("Sélectionne d'abord un article.")
            st.stop()
    
        if has_already_done_quiz(st.session_state.username, langue):
            st.info("✔️ Quiz déjà complété aujourd’hui.")
            st.stop()
    
        vocab = st.session_state.get("vocab", [])
    
        if not vocab:
            st.warning("Aucun vocabulaire chargé.")
            st.stop()
    
        for i, (mot, trad) in enumerate(vocab):
            st.text_input(f"Traduire : {mot}", key=f"vocab_{i}")
    
        if st.button("Valider le quiz"):
    
            score = 0
    
            for i, (mot, trad) in enumerate(vocab):
                user_input = st.session_state.get(f"vocab_{i}", "")
    
                if user_input.strip().lower() == trad.strip().lower():
                    score += 1
    
            st.success(f"Score : {score}/10")
    
            save_stats(st.session_state.username, langue, score)
            save_dictionary(st.session_state.username,langue, vocab)
