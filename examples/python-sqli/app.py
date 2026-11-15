# file: app.py — small read-only service
import sqlite3

from flask import Flask, jsonify, request

app = Flask(__name__)
DB = "app.db"


def connect():
    return sqlite3.connect(DB)


@app.get("/search")
def search():
    q = request.args.get("q", "")
    conn = connect()
    rows = conn.execute(
        "SELECT id, title FROM posts WHERE title LIKE '%" + q + "%'"
    ).fetchall()
    conn.close()
    return jsonify(rows)


@app.get("/user/<int:user_id>")
def get_user(user_id):
    conn = connect()
    rows = conn.execute(
        "SELECT id, email FROM users WHERE id = ?", (user_id,)
    ).fetchall()
    conn.close()
    return jsonify(rows)


@app.get("/health")
def health():
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
