# Book List Flask API

A lightweight Flask REST API and SQLite database that serves a personal reading list extracted from Notion. Includes a data pipeline (`transform.py`) that normalizes book metadata, converts star ratings, extracts cover images, and builds the SQLite database.

---

## Features

- **RESTful Endpoints**: Fetch all books with filtering or retrieve a single book with notes.
- **Search & Filters**: Search by title or author, filter by completion status and yearly reviews.
- **Cover Image Serving**: Static cover image hosting with automatic absolute URL generation.
- **CORS Enabled**: Configured with `Access-Control-Allow-Origin: *` for frontend integration.
- **Modern Python Tooling**: Managed with [`uv`](https://docs.astral.sh/uv/) and Python 3.14+.

---

## Project Structure

```text
├── app.py           # Flask application with API and cover image endpoints
├── transform.py     # ETL script: transforms Notion CSV & images into SQLite
├── data/            # Source Notion export (books.csv and exported images)
├── pyproject.toml   # Project metadata and dependencies
└── README.md
```

---

## Getting Started

### Prerequisites

- [uv](https://docs.astral.sh/uv/) installed on your machine.

### 1. Install Dependencies

Install project dependencies into a local virtual environment:

```bash
uv sync
```

### 2. Build Database & Assets (Required on first run)

Because `books.db` and `covers/` are generated artifacts and gitignored, you must run the transformation script once to initialize the SQLite database and extract cover images:

```bash
uv run python transform.py
```

> **Note**: Re-run this command whenever you update `data/books.csv` or add new cover images from Notion.

### 3. Run the Development Server

Start the Flask server in debug mode:

```bash
uv run flask run --debug
```

The API will be available at `http://127.0.0.1:5000`.

---

## API Reference

### 1. List Books

Retrieve all books sorted by `date_finished` (descending). Note that the full `notes` field is excluded from list view for performance.

- **URL**: `GET /api/books`
- **Query Parameters**:
  - `q` (string, optional): Case-insensitive search on title or author (e.g. `?q=father`).
  - `finished` (integer `0` | `1`, optional): Filter by completion status (`?finished=1`).
  - `yearly_review` (integer `0` | `1`, optional): Filter books featured in yearly reviews (`?yearly_review=1`).

**Example Request:**
```bash
curl "http://127.0.0.1:5000/api/books?q=father&finished=1"
```

**Example Response:**
```json
[
  {
    "author": "Jon tyson",
    "cover": "the-intentional-father.jpg",
    "cover_url": "http://127.0.0.1:5000/api/covers/the-intentional-father.jpg",
    "date_finished": "2026-09-17",
    "finished": 1,
    "id": 106,
    "rating": 3.0,
    "title": "The intentional father",
    "yearly_review": 0
  }
]
```

*(Note: `cover_url` is automatically omitted if a book does not have a cover).*

---

### 2. Get Book by ID

Retrieve detailed information for a single book, including personal notes. Returns HTTP `404` if not found.

- **URL**: `GET /api/books/<id>`

**Example Request:**
```bash
curl "http://127.0.0.1:5000/api/books/106"
```

**Example Response:**
```json
{
  "author": "Jon tyson",
  "cover": "the-intentional-father.jpg",
  "cover_url": "http://127.0.0.1:5000/api/covers/the-intentional-father.jpg",
  "date_finished": "2026-09-17",
  "finished": 1,
  "id": 106,
  "notes": "We might have a lot of “good men” in our culture, but most are not good at being men. Confidence comes from competence...",
  "rating": 3.0,
  "title": "The intentional father",
  "yearly_review": 0
}
```

---

### 3. Cover Images

Directly access static cover images stored on the server.

- **URL**: `GET /api/covers/<filename>`
- **Example**: `http://127.0.0.1:5000/api/covers/the-intentional-father.jpg`


