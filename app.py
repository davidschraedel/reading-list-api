import sqlite3
from pathlib import Path
from flask import Flask, abort, request, send_from_directory, url_for

app = Flask(__name__)

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "books.db"
COVERS_DIR = BASE_DIR / "covers"

def query(sql, args=()):
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    rows = con.execute(sql, args).fetchall()
    con.close()
    return [dict(r) for r in rows]

def with_cover_url(book):
    if book.get("cover"):
        book["cover_url"] = url_for("cover", filename=book["cover"], _external=True)
    return book

@app.after_request
def enable_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

@app.get("/api/books")
def list_books():
    sql = ("SELECT id, title, author, rating, finished, date_finished, "
           "yearly_review, cover FROM books WHERE 1=1")
    args = []

    q = request.args.get("q", "").strip()
    if q:
        sql += " AND (title LIKE ? OR author LIKE ?)"
        args.extend([f"%{q}%", f"%{q}%"])

    for flag in ("finished", "yearly_review"):
        value = request.args.get(flag)
        if value in ("0", "1"):
            sql += f" AND {flag} = ?"
            args.append(int(value))

    sql += " ORDER BY date_finished DESC"
    return [with_cover_url(b) for b in query(sql, args)]

@app.get("/api/books/<int:book_id>")
def get_book(book_id):
    rows = query("SELECT * FROM books WHERE id = ?", (book_id,))
    if not rows:
        abort(404)
    return with_cover_url(rows[0])

@app.get("/api/covers/<path:filename>")
def cover(filename):
    return send_from_directory(COVERS_DIR, filename)

