import requests

SHEET_ID = "PASTE_YOUR_SHEET_ID_HERE"
SHEET_NAME = "Branch_Master"

def get_branches():
    url = f"https://docs.google.com/spreadsheets/d/1nLKZAkLZhitxAos28ST6aa6bxXKO-tfoVKxZegkifhY/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"
    response = requests.get(url)
    lines = response.text.splitlines()

    branches = []
    for line in lines[1:]:  # skip header
        parts = line.split(",")
        if len(parts) >= 2:
            branches.append({
                "code": parts[0].strip(),
                "name": parts[1].strip()
            })
    return branches
