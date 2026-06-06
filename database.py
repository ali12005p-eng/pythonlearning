import sqlite3

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
        history TEXT DEFAULT ''
    )
    """)

    conn.commit()
    conn.close()


def user_exists(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT user_id FROM users WHERE user_id = ?",
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
        story_type
    )
    VALUES (?, ?, ?, ?)
    """, (
        user_id,
        character_name,
        gender,
        story_type
    ))

    conn.commit()
    conn.close()


def get_user(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        user_id,
        character_name,
        gender,
        story_type,
        level,
        xp,
        history
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
