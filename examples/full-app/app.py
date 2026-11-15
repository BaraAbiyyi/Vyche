# file: app.py
from flask import Flask, abort, jsonify, render_template, request

from config import Config
from db import delete_post, find_post_by_id, find_posts

app = Flask(__name__)
app.config.from_object(Config)


@app.get("/")
def index():
    term = request.args.get("q", "")
    return render_template("index.html", posts=find_posts(term))


@app.get("/posts/<int:post_id>")
def post_detail(post_id):
    row = find_post_by_id(post_id)
    if row is None:
        abort(404)
    return jsonify({"id": row[0], "title": row[1], "body": row[2]})


@app.post("/admin/posts/<int:post_id>/delete")
def admin_delete_post(post_id):
    delete_post(post_id)
    return jsonify({"deleted": post_id})


@app.get("/health")
def health():
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
