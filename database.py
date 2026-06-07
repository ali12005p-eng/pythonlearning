import sqlite3
from datetime import datetime

DB_NAME = "game.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        character_name TEXT NOT NULL,
        gender TEXT NOT NULL,
        story_type TEXT NOT NULL,

        level INTEGER DEFAULT 1,
        xp INTEGER DEFAULT 0,

        story_summary TEXT DEFAULT '',
        history TEXT DEFAULT '',

        voice_enabled INTEGER DEFAULT 1,

        message_count INTEGER DEFAULT 0,

        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()


def user_exists(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT user_id FROM users WHERE user_id=?",
        (user_id,)
    )

    result = cursor.fetchone()

    conn.close()

    return result is not None


def create_user(
    user_id: int,
    character_name: str,
    gender: str,
    story_type: str
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO users (
        user_id,
        character_name,
        gender,
        story_type,
        created_at
    )
    VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        character_name,
        gender,
        story_type,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def get_user(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM users
    WHERE user_id = ?
    """, (user_id,))

    result = cursor.fetchone()

    conn.close()

    return result


def update_history(user_id: int, history: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE users
    SET history = ?
    WHERE user_id = ?
    """, (
        history,
        user_id
    ))

    conn.commit()
    conn.close()


def update_summary(user_id: int, summary: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE users
    SET story_summary = ?
    WHERE user_id = ?
    """, (
        summary,
        user_id
    ))

    conn.commit()
    conn.close()


def update_xp_level(user_id: int, xp: int, level: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE users
    SET xp = ?, level = ?
    WHERE user_id = ?
    """, (
        xp,
        level,
        user_id
    ))

    conn.commit()
    conn.close()


def set_voice(user_id: int, enabled: bool):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE users
    SET voice_enabled = ?
    WHERE user_id = ?
    """, (
        1 if enabled else 0,
        user_id
    ))

    conn.commit()
    conn.close()


def get_message_count(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT message_count
    FROM users
    WHERE user_id = ?
    """, (user_id,))

    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]

    return 0


def update_message_count(user_id: int, count: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE users
    SET message_count = ?
    WHERE user_id = ?
    """, (
        count,
        user_id
    ))

    conn.commit()
    conn.close()
