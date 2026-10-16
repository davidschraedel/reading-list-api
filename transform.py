import sqlite3
from pathlib import Path
import pandas as pd

COVERS = Path("covers")
df = pd.read_csv("books.csv")

# Rename to clean column names (adjust to your real columns)
df = df.rename(columns={"Title": "title", "Author": "author",
                        "Finished": "finished", "Rating": "rating",
                        "Notes": "notes"})

def find_cover(title):
    folder = COVERS / title
    if folder.is_dir():
        for f in folder.iterdir():
            if f.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
                return f.relative_to(COVERS).as_posix()
    return None

df["cover"] = df["title"].apply(find_cover)
print("Books with no cover found:", df["cover"].isna().sum())

con = sqlite3.connect("books.db")
con.execute("DROP TABLE IF EXISTS books")
con.execute("""CREATE TABLE books (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT,
    status TEXT,
    rating REAL,
    notes TEXT,
    cover TEXT
)""")
df[["title","author","status","rating","notes","cover"]].to_sql(
    "books", con, if_exists="append", index=False)
con.commit()
print(con.execute("SELECT COUNT(*) FROM books").fetchone())  # expect 107
con.close()