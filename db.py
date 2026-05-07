import psycopg2
import streamlit as st


def get_connection():
    return psycopg2.connect(
        host=st.secrets["DB_HOST"],
        database=st.secrets["DB_NAME"],
        username=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        port=st.secrets["DB_PORT"]
    )


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # ARTICLES
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id SERIAL PRIMARY KEY,
            langue TEXT,
            titre TEXT,
            contenu TEXT,
            url TEXT,
            date_publication DATE
        )
    """)

    # VOCABULAIRE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vocabulaire (
            id SERIAL PRIMARY KEY,
            article_id INTEGER REFERENCES articles(id),
            mot TEXT,
            traduction TEXT
        )
    """)

    # STATS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stats (
            id SERIAL PRIMARY KEY,
            username TEXT,
            date DATE,
            score INTEGER
        )
    """)

    # DICTIONNAIRE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dictionnaire (
            id SERIAL PRIMARY KEY,
            username TEXT,
            date DATE,
            mot TEXT,
            traduction TEXT
        )
    """)

    conn.commit()
    conn.close()
