# Reading List API & Gallery

A minimal Flask app and SQLite database serving a personal reading list exported from Notion.

## Quickstart

Requires Python 3.14+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run python transform.py   # Imports data/books.csv into books.db & covers/
uv run flask run --debug
```

- **Web Gallery:** [http://localhost:5000/gallery](http://localhost:5000/gallery)
- **JSON API:** [http://localhost:5000/api/books](http://localhost:5000/api/books)

## Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/gallery` | Interactive browser shelf with search, filters, stats, and notes modal |
| `GET` | `/api/books` | List books (`?q=<text>`, `?finished=0\|1`, `?yearly_review=0\|1`) |
| `GET` | `/api/books/<id>` | Single book, including full personal notes |
| `GET` | `/api/covers` | List books that have covers |
| `GET` | `/api/covers/<filename>` | Serve cover image file |

## Examples

### 1. Search books (`GET /api/books?q=measure`)

```bash
curl "http://localhost:5000/api/books?q=measure"
```

```json
[
  {
    "id": 55,
    "title": "How will you measure your life",
    "author": "Clayton m christensen",
    "rating": 5.0,
    "finished": 1,
    "date_finished": "2024-07-04",
    "yearly_review": 1,
    "cover": "how-will-you-measure-your-life.jpg",
    "cover_url": "http://localhost:5000/api/covers/how-will-you-measure-your-life.jpg"
  }
]
```

### 2. Get one book (`GET /api/books/55`)

```bash
curl "http://localhost:5000/api/books/55"
```

```json
{
  "id": 55,
  "title": "How will you measure your life",
  "author": "Clayton m christensen",
  "rating": 5.0,
  "finished": 1,
  "date_finished": "2024-07-04",
  "yearly_review": 1,
  "notes": "Theories help us know how to think about things we have not done yet. We can learn without experiencing the pain of every failure. Great lives are a byproduct of happiness and meaning.",
  "cover": "how-will-you-measure-your-life.jpg",
  "cover_url": "http://localhost:5000/api/covers/how-will-you-measure-your-life.jpg"
}
```

### 3. List books with cover images (`GET /api/covers`)

```bash
curl "http://localhost:5000/api/covers"
```

```json
[
  {
    "id": 55,
    "title": "How will you measure your life",
    "author": "Clayton m christensen",
    "rating": 5.0,
    "cover_url": "http://localhost:5000/api/covers/how-will-you-measure-your-life.jpg"
  }
]
```

## Project Structure

```text
├── app.py           # Flask routes and gallery view
├── transform.py     # CSV import & cover extraction
├── books.db         # SQLite database
├── covers/          # Extracted book cover images
├── data/            # Notion export (books.csv & images)
└── templates/       # HTML template (gallery.html)
```
