# Book List Flask API

A lightweight Flask REST API and SQLite database that serves a personal reading list extracted from Notion. Includes an ETL data pipeline (`transform.py`) that normalizes book metadata, converts star ratings, extracts cover images, and creates the database.

## Quickstart

Install dependencies, initialize the database, and start the development server:

```bash
uv sync
uv run python transform.py  # First time: builds books.db and extracts covers
uv run flask run --debug
```

The API will be running at `http://127.0.0.1:5000`.

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/books` | List books, newest finished first |
| GET | `/api/books/<id>` | One book, including personal notes |
| GET | `/api/covers` | List all books that have covers (JSON) |
| GET | `/api/covers/<filename>` | Direct cover image file |
| GET | `/gallery` | Interactive Reading List Gallery with statistics & book details (Browser) |

### `GET /api/books` query parameters

| Param | Type | Example | Effect |
|-------|------|---------|--------|
| `q` | string | `?q=screwtape` | Case-insensitive search on title and author |
| `finished` | integer | `?finished=1` | Only finished (`1`) or unfinished (`0`) books |
| `yearly_review` | integer | `?yearly_review=1` | Only books featured in yearly review (`1` or `0`) |

---

## Examples

### 1. Search books (`GET /api/books?q=screwtape`)

```bash
curl "http://127.0.0.1:5000/api/books?q=screwtape"
```

```json
[
  {
    "author": "C S Lewis",
    "cover": "the-screwtape-letters.jpg",
    "cover_url": "http://127.0.0.1:5000/api/covers/the-screwtape-letters.jpg",
    "date_finished": "2023-06-01",
    "finished": 1,
    "id": 1,
    "rating": 4.0,
    "title": "The Screwtape Letters",
    "yearly_review": 0
  }
]
```

### 2. Get one book (`GET /api/books/1`)

```bash
curl "http://127.0.0.1:5000/api/books/1"
```

```json
{
  "author": "C S Lewis",
  "cover": "the-screwtape-letters.jpg",
  "cover_url": "http://127.0.0.1:5000/api/covers/the-screwtape-letters.jpg",
  "date_finished": "2023-06-01",
  "finished": 1,
  "id": 1,
  "notes": "Interesting to see the follies of how we think when it comes to religious ideas",
  "rating": 4.0,
  "title": "The Screwtape Letters",
  "yearly_review": 0
}
```

### 3. List all covers (`GET /api/covers`)

```bash
curl "http://127.0.0.1:5000/api/covers"
```

```json
[
  {
    "author": "Jon tyson",
    "cover_url": "http://127.0.0.1:5000/api/covers/the-intentional-father.jpg",
    "id": 106,
    "rating": 3.0,
    "title": "The intentional father"
  }
]
```

### 4. Interactive Browser Gallery (`GET /gallery`)

Visit [http://127.0.0.1:5000/gallery](http://127.0.0.1:5000/gallery) in your browser to view the **Reading List Gallery**:
- Displays all 107 library books (with custom stylized placeholders for books without covers).
- Reading statistics and interactive charts (reading volume by year, rating breakdown).
- Click any book cover to open a detail modal overlay with notes, ratings, and status.
- Natural touchpad horizontal swipe for the shelf, smooth vertical scrolling for the page.
- *(Note: `/api/covers/gallery` automatically redirects here).*

---

## Data Notes & Errors

### Fields

- `id` *(integer)*: Unique database identifier.
- `title` *(string)*: Title of the book.
- `author` *(string | null)*: Author name.
- `rating` *(number | null)*: 1.0 to 5.0 rating (converted from Notion star emojis), or `null`.
- `finished` *(integer)*: `1` if completed, `0` otherwise.
- `date_finished` *(string | null)*: Date completed in `YYYY-MM-DD` format.
- `yearly_review` *(integer)*: `1` if highlighted in yearly review, `0` otherwise.
- `notes` *(string | null)*: Personal notes and takeaways (omitted from `/api/books` list, included in `/api/books/<id>`).
- `cover` *(string | null)*: Filename slug of the cover image (e.g. `the-screwtape-letters.jpg`).
- `cover_url` *(string)*: Absolute URL to the cover image. Omitted from response if `cover` is `null`.

### Errors

- Requesting an unknown book ID (`/api/books/<id>`) returns `404 Not Found`.
- Requesting a missing cover filename (`/api/covers/<filename>`) returns `404 Not Found`.
- CORS is enabled across all routes (`Access-Control-Allow-Origin: *`).

---

## Project Structure

```text
├── app.py           # Flask application and route handlers
├── transform.py     # ETL script: builds books.db & extracts covers
├── data/            # Source Notion export (books.csv & images)
├── templates/       # HTML templates (covers gallery)
├── pyproject.toml   # Project dependencies and configuration
└── README.md
```
