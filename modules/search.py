import re
from modules.database import search_db


def normalize(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def ordered_match(search_name, tokens):
    """
    Enforces:
    - Tokens must appear in order
    - Alphabetic tokens must match whole words
    - Numeric tokens allow substring
    """

    words = search_name.split()
    index = 0

    for token in tokens:
        found = False

        if token.isdigit():
            # numeric token: allow substring match inside word
            for i in range(index, len(words)):
                if token in words[i]:
                    index = i + 1
                    found = True
                    break
        else:
            # alphabetic token: whole word match only
            for i in range(index, len(words)):
                if words[i] == token:
                    index = i + 1
                    found = True
                    break

        if not found:
            return False

    return True


def perform_search(query):
    if len(query) < 3:
        return [], "Search term too short."

    norm_query = normalize(query)
    tokens = norm_query.split()

    # Build broad SQL filter using all tokens
    sql = "SELECT * FROM releases WHERE "
    conditions = []
    params = []

    for token in tokens:
        conditions.append("search_name LIKE ?")
        params.append(f"%{token}%")

    sql += " AND ".join(conditions)
    sql += " LIMIT 500"

    rows = search_db(sql, tuple(params))

    # Strict ordered matching in Python
    filtered = []

    for row in rows:
        search_name = row[2]

        if ordered_match(search_name, tokens):
            filtered.append(row)

        if len(filtered) >= 20:
            break

    if not filtered:
        return [], "No results."

    return filtered, ""