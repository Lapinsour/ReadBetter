import psycopg2
import os
import streamlit as st

def get_connection():

    # ---- STREAMLIT CLOUD ----
    if not os.getenv("DB_HOST"):

        import streamlit as st

        return psycopg2.connect(
            host=st.secrets["DB_HOST"],
            database=st.secrets["DB_NAME"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"],
            port=st.secrets["DB_PORT"]
        )

    # ---- GITHUB ACTIONS ----
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        port=os.environ["DB_PORT"]
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
            score INTEGER,
            langue TEXT
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
