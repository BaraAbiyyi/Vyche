# file: db.py
import sqlite3

from config import Config


def connect():
    return sqlite3.connect(Config.DATABASE_URL.replace("sqlite:///", ""))


def find_posts(term):
    conn = connect()
    rows = conn.execute(
        "SELECT id, title, body FROM posts WHERE title LIKE '%" + term + "%'"
    ).fetchall()
    conn.close()
    return rows


def find_post_by_id(post_id):
    conn = connect()
    row = conn.execute(
        "SELECT id, title, body FROM posts WHERE id = ?", (post_id,)
    ).fetchone()
    conn.close()
    return row


def delete_post(post_id):
    conn = connect()
    conn.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()
