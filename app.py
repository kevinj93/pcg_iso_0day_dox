
from flask import Flask, render_template, request, jsonify
from modules.database import init_db, get_stats, increment_download, get_link
from modules.search import perform_search
from modules.dat_processor import process_dat_files
from modules.link_fetcher import fetch_directory_links

app = Flask(__name__)
init_db()

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    results = []
    stats = get_stats()

    if request.method == "POST":
        query = request.form.get("query", "")
        results, message = perform_search(query)

    return render_template("index.html",
                           results=results,
                           message=message,
                           stats=stats)

@app.route("/reveal/<int:rls_id>", methods=["POST"])
def reveal(rls_id):
    increment_download(rls_id)
    link = get_link(rls_id)
    return jsonify({"link": link})

@app.route("/release/<int:rls_id>")
def get_release(rls_id):
    from modules.database import search_db

    row = search_db(
        "SELECT * FROM releases WHERE rls_id = ?",
        (rls_id,)
    )

    if not row:
        return {}

    r = row[0]

    return {
        "id": r[0],
        "name": r[1],
        "year": r[3],
        "type": r[4],
        "size": r[5],
        "downloads": r[8]
    }

@app.route("/admin", methods=["GET", "POST"])
def admin():
    message = ""
    if request.method == "POST":
        file = request.files.get("file")
        links_raw = request.form.get("links")
        directory_data = {}

        if links_raw:
            directory_data = fetch_directory_links(links_raw)

        if file:
            message = process_dat_files(file, directory_data)

    return render_template("admin.html", message=message)

if __name__ == "__main__":
    app.run(debug=True)
