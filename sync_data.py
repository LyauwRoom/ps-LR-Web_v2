import requests, json, csv, os
from io import StringIO

CONFIG = {
    "global": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRkDFCZA4hODuZPz_owlujHkHizAuSGuTAgRoZkzIkhF_e9PsJRl-2fhtxt96hOnLvjmXNNDCoydQkd/pub?gid=0&single=true&output=csv",
    "static_pages": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRkDFCZA4hODuZPz_owlujHkHizAuSGuTAgRoZkzIkhF_e9PsJRl-2fhtxt96hOnLvjmXNNDCoydQkd/pub?gid=999625505&single=true&output=csv",
    "blog": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRkDFCZA4hODuZPz_owlujHkHizAuSGuTAgRoZkzIkhF_e9PsJRl-2fhtxt96hOnLvjmXNNDCoydQkd/pub?gid=1581291519&single=true&output=csv"
}

def fetch_csv_dicts(url):
    try:
        resp = requests.get(url, timeout=15)
        resp.encoding = 'utf-8-sig'
        if resp.status_code != 200: return []
        f = StringIO(resp.text)
        reader = csv.DictReader(f)
        return [{str(k).strip(): str(v).strip() for k, v in row.items() if k} for row in reader if any(row.values())]
    except: return []

def get_v(row, keys):
    for k in keys:
        if k in row: return row[k]
    return ''

def sync():
    cms_data = {"global": {}, "static_pages": {}, "blog": []}
    
    # 1. Global
    for r in fetch_csv_dicts(CONFIG["global"]):
        kid = get_v(r, ['ID', 'id'])
        if kid: cms_data["global"][kid] = get_v(r, ['content', 'Content'])

    # 2. Static Pages (升级：存储 content 和 animation)
    for r in fetch_csv_dicts(CONFIG["static_pages"]):
        hid = get_v(r, ['html_ID', 'html_id'])
        if hid:
            cms_data["static_pages"][hid] = {
                "content": get_v(r, ['content', 'Content']),
                "animation": get_v(r, ['animation', 'Animation'])
            }

    # 3. Blog
    cms_data["blog"] = fetch_csv_dicts(CONFIG["blog"])

    os.makedirs('web_v1', exist_ok=True)
    with open('web_v1/data.json', 'w', encoding='utf-8') as f:
        json.dump(cms_data, f, ensure_ascii=False, indent=4)
    print("Sync Done")

if __name__ == "__main__": sync()
