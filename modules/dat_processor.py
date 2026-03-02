
import zipfile
import os
import re
import sqlite3
import shutil
from lxml import etree
from modules.database import DB
from modules.search import normalize

def process_dat_files(file, directory_data):
    filename = file.filename

    # Clean uploads directory
    if os.path.exists("uploads"):
        shutil.rmtree("uploads")
    os.makedirs("uploads", exist_ok=True)

    # Extract DAT files
    if filename.endswith(".zip"):
        file.save("temp.zip")
        with zipfile.ZipFile("temp.zip", 'r') as zip_ref:
            zip_ref.extractall("uploads")
        dat_files = [f for f in os.listdir("uploads") if f.endswith(".dat")]
    elif filename.endswith(".dat"):
        file.save("uploads/single.dat")
        dat_files = ["single.dat"]
    else:
        return "Invalid file format."

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # Load existing releases once
    c.execute("SELECT rls_name, dl_link FROM releases")
    existing_rows = c.fetchall()
    existing = {row[0]: row[1] for row in existing_rows}

    seen = set(existing.keys())
    to_insert = []
    to_update = []

    for dat in dat_files:
        path = os.path.join("uploads", dat)
        tree = etree.parse(path)

        match = re.search(r'PC_(.*?)_Games_Scene_(\d{4})', dat)
        if not match:
            continue

        rls_type = match.group(1)
        year = match.group(2)

        for game in tree.xpath("//game"):

            # Skip MIA games
            if game.xpath(".//rom[@mia='yes']"):
                continue

            name = game.get("name")

            # Strict case-sensitive exact match
            if name not in directory_data:
                continue

            data = directory_data[name]
            new_link = data["link"]

            if name in seen:
                # Update link only if already exists in DB and link changed
                if name in existing and existing[name] != new_link:
                    to_update.append((new_link, name))
            else:
                to_insert.append((
                    name,
                    normalize(name),
                    year,
                    rls_type,
                    data["size_str"],
                    data["size_bytes"],
                    new_link
                ))
                seen.add(name)

    # Bulk INSERT
    if to_insert:
        c.executemany("""
            INSERT INTO releases
            (rls_name, search_name, rls_year, rls_type,
             rls_size_str, rls_size_bytes, dl_link)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, to_insert)

    # Bulk UPDATE (link only)
    if to_update:
        c.executemany("""
            UPDATE releases
            SET dl_link = ?
            WHERE rls_name = ?
        """, to_update)

    conn.commit()
    conn.close()

    return f"Done. Inserted: {len(to_insert)}, Updated links: {len(to_update)}"
