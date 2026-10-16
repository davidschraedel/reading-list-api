import os
import re
import shutil
import sqlite3
import urllib.parse
from pathlib import Path
import pandas as pd

COVERS_DIR = Path("covers")
COVERS_DIR.mkdir(exist_ok=True)

df = pd.read_csv("books.csv")

# 1. Clean Title and Author
df["title"] = df["Title"].astype(str).str.strip()
df["author"] = df["Author"].apply(lambda v: str(v).strip() if pd.notna(v) else None)

# 2. Convert Star Rating emojis to numbers (1 to 5)
df["rating"] = df["Rating"].apply(
    lambda v: v.count("⭐") if isinstance(v, str) and "⭐" in v else None
)

# 3. Format Date Finished to YYYY-MM-DD
df["date_finished"] = pd.to_datetime(df["Date Finished"]).dt.strftime("%Y-%m-%d")

# 4. Convert Finished and Yearly Review to booleans / integers (1 or 0)
df["finished"] = (df["Finished"].astype(str).str.strip().str.lower() == "yes").astype(int)
df["yearly_review"] = (df["Yearly Review"].astype(str).str.strip().str.lower() == "yes").astype(int)

# 5. Notes
df["notes"] = df["Notes"].apply(lambda v: str(v).strip() if pd.notna(v) else None)

# 6. Extract covers from Notion's Image path and copy into 'covers/'
def process_cover(row):
    raw_img = row["Image"]
    if pd.isna(raw_img):
        return None

    # Handle multiple paths separated by comma before 'Reading' (e.g. The Trading Game)
    parts = re.split(r",\s*(?=Reading)", str(raw_img))
    decoded_src = urllib.parse.unquote(parts[0].strip())
    src_path = Path(decoded_src)

    if not src_path.exists():
        return None

    # Create a clean, slugified filename (e.g. 'the-screwtape-letters.jpg')
    slug = re.sub(r"[^\w\s-]", "", str(row["Title"]).strip().lower())
    slug = re.sub(r"[-\s]+", "-", slug)
    ext = src_path.suffix.lower()
    dest_filename = f"{slug}{ext}"
    dest_path = COVERS_DIR / dest_filename

    shutil.copy2(src_path, dest_path)
    return f"covers/{dest_filename}"

df["cover"] = df.apply(process_cover, axis=1)
print(f"Covers copied: {df['cover'].notna().sum()} / {len(df)}")
print(f"Books without covers: {df['cover'].isna().sum()}")

# 7. Write to SQLite
con = sqlite3.connect("books.db")
con.execute("DROP TABLE IF EXISTS books")
con.execute("""
CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT,
    rating REAL,
    finished INTEGER DEFAULT 0,
    date_finished TEXT,
    yearly_review INTEGER DEFAULT 0,
    notes TEXT,
    cover TEXT
)
""")

cols_to_save = [
    "title",
    "author",
    "rating",
    "finished",
    "date_finished",
    "yearly_review",
    "notes",
    "cover",
]
df[cols_to_save].to_sql("books", con, if_exists="append", index=False)
con.commit()

count = con.execute("SELECT COUNT(*) FROM books").fetchone()[0]
print(f"Successfully inserted {count} books into books.db!")
con.close()