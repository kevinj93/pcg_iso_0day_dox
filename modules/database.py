
import sqlite3

DB = "database.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS releases (
            rls_id INTEGER PRIMARY KEY AUTOINCREMENT,
            rls_name TEXT UNIQUE,
            search_name TEXT,
            rls_year INTEGER,
            rls_type TEXT,
            rls_size_str TEXT,
            rls_size_bytes INTEGER,
            dl_link TEXT,
            dl_count INTEGER DEFAULT 0
        )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_search ON releases(search_name)")
    conn.commit()
    conn.close()

def insert_release(data):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        INSERT OR IGNORE INTO releases
        (rls_name, search_name, rls_year, rls_type,
         rls_size_str, rls_size_bytes, dl_link)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, data)
    conn.commit()
    conn.close()

def increment_download(rls_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE releases SET dl_count = dl_count + 1 WHERE rls_id = ?", (rls_id,))
    conn.commit()
    conn.close()

def get_link(rls_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    link = c.execute("SELECT dl_link FROM releases WHERE rls_id = ?", (rls_id,)).fetchone()[0]
    conn.close()
    return link

def get_stats():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    total = c.execute("SELECT COUNT(*) FROM releases").fetchone()[0]
    total_dl = c.execute("SELECT SUM(dl_count) FROM releases").fetchone()[0] or 0
    conn.close()
    return {"total": total, "downloads": total_dl}

def search_db(sql, params):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    rows = c.execute(sql, params).fetchall()
    conn.close()
    return rows
