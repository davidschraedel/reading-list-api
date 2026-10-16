import sqlite3
from pathlib import Path
from flask import Flask, abort, redirect, render_template, request, send_from_directory, url_for

app = Flask(__name__)

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "books.db"
COVERS_DIR = BASE_DIR / "covers"

def query(sql, args=()):
    """Execute a parameterized SQL query on books.db and return rows as dictionaries."""
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    rows = con.execute(sql, args).fetchall()
    con.close()
    return [dict(r) for r in rows]

def with_cover_url(book):
    """Add absolute cover_url to book dictionary if cover filename is present."""
    if book.get("cover"):
        book["cover_url"] = url_for("cover", filename=book["cover"], _external=True)
    return book

@app.after_request
def enable_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

@app.get("/api/books")
def list_books():
    """List books, newest finished first. Optional filters: q (title/author), finished (0/1), yearly_review (0/1)."""
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
    """Retrieve one book by ID, including personal notes. Returns 404 if not found."""
    rows = query("SELECT * FROM books WHERE id = ?", (book_id,))
    if not rows:
        abort(404)
    return with_cover_url(rows[0])

@app.get("/api/covers")
def list_covers():
    """Return JSON list of all books that have covers with metadata and cover URLs."""
    rows = query(
        "SELECT id, title, author, rating, cover FROM books WHERE cover IS NOT NULL ORDER BY date_finished DESC"
    )
    return [
        {
            "id": r["id"],
            "title": r["title"],
            "author": r["author"],
            "rating": r["rating"],
            "cover_url": url_for("cover", filename=r["cover"], _external=True),
        }
        for r in rows
    ]

@app.get("/gallery")
def reading_list_gallery():
    """Render interactive Reading List Gallery with statistics, charts, and cover showcase."""
    rows = query("SELECT * FROM books ORDER BY (date_finished IS NULL), date_finished DESC, id DESC")
    books = [with_cover_url(b) for b in rows]

    total_books = len(books)
    finished_count = sum(1 for b in books if b["finished"])
    yearly_review_count = sum(1 for b in books if b["yearly_review"])

    ratings = [b["rating"] for b in books if b["rating"] is not None]
    avg_rating = round(sum(ratings) / len(ratings), 1) if ratings else 0.0

    # Reading stats grouped by year
    year_counts = {}
    for b in books:
        if b.get("date_finished"):
            y = b["date_finished"][:4]
            year_counts[y] = year_counts.get(y, 0) + 1
    yearly_stats = [{"year": y, "count": year_counts[y]} for y in sorted(year_counts.keys())]

    # Rating distribution breakdown
    rating_counts = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    for b in books:
        r = b.get("rating")
        if r is not None:
            r_int = int(round(r))
            if r_int in rating_counts:
                rating_counts[r_int] += 1

    stats = {
        "total": total_books,
        "finished": finished_count,
        "unread": total_books - finished_count,
        "avg_rating": avg_rating,
        "yearly_reviews": yearly_review_count,
        "yearly": yearly_stats,
        "ratings": rating_counts,
    }

    return render_template("gallery.html", books=books, stats=stats)

@app.get("/api/covers/gallery")
def covers_gallery_redirect():
    """Redirect legacy covers gallery route to /gallery."""
    return redirect(url_for("reading_list_gallery"))


@app.get("/api/covers/<path:filename>")
def cover(filename):
    """Serve a book cover image from the covers/ directory. Returns 404 if not found."""
    return send_from_directory(COVERS_DIR, filename)



