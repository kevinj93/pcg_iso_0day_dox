
import requests
import re

def size_to_bytes(size_str):
    num, unit = size_str.split()
    num = float(num)
    unit = unit.upper()
    if unit == "KB":
        return int(num * 1024)
    if unit == "MB":
        return int(num * 1024**2)
    if unit == "GB":
        return int(num * 1024**3)
    return int(num)

def fetch_directory_links(raw_links):
    headers = {"User-Agent": "Mozilla/5.0"}
    results = {}

    for line in raw_links.strip().splitlines():
        url = line.strip()
        if not url:
            continue

        r = requests.get(url, headers=headers, timeout=10)
        html = r.text

        matches = re.findall(
            r'href="(https://1fichier\.com/\?[^"]+)"[^>]+title="Download ([^"]+\.rar)".*?<td class="normal">([^<]+)</td>',
            html, re.DOTALL
        )

        for link, title, size in matches:
            clean_title = title.replace(".rar", "")
            results[clean_title] = {
                "link": link,
                "size_str": size.strip(),
                "size_bytes": size_to_bytes(size.strip())
            }

    return results
