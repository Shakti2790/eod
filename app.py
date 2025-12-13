from flask import Flask, render_template, redirect, url_for, session, request
import os
import requests
import csv
import io

app = Flask(__name__)
app.secret_key = "change-this-secret-key-123"

# =================================================
# GOOGLE SHEET CONFIG (PUBLIC – READ ONLY)
# =================================================
SHEET_ID = "PASTE_YOUR_SHEET_ID_HERE"   # <-- yahan apna Sheet ID daalo
SHEET_NAME = "Branch_Master"


def get_branches():
    """
    Reads branch master from Google Sheets (CSV export)
    """
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&sheet={SHEET_NAME}"
    response = requests.get(url)

    if response.status_code != 200:
        return []

    decoded = response.content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(decoded))

    branches = []
    for row in reader:
        if row.get("Branch_Code") and row.get("Branch_Name"):
            branches.append({
                "code": row["Branch_Code"].strip(),
                "name": row["Branch_Name"].strip()
            })

    return branches


# =================================================
# HOME / LOGIN PAGE
# =================================================
@app.route("/")
def index():
    return render_template("login.html")


# =================================================
# TEMPORARY LOGIN (NO GOOGLE OAUTH YET)
# =================================================
@app.route("/login")
def login():
    session.clear()
    session["user"] = "test@demo.com"

    # CHANGE ONLY THIS LINE FOR TESTING
    session["role"] = "Branch"      # "Branch" or "CentralAdmin"

    if session["role"] == "CentralAdmin":
        return redirect(url_for("admin_dashboard"))
    else:
        return redirect(url_for("select_branch"))


# =================================================
# LOGOUT
# =================================================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# =================================================
# BRANCH FLOW
# =================================================
@app.route("/select-branch")
def select_branch():
    if session.get("role") != "Branch":
        return redirect(url_for("index"))

    branches = get_branches()
    return render_template("branch_select.html", branches=branches)


@app.route("/set-branch", methods=["POST"])
def set_branch():
    if session.get("role") != "Branch":
        return redirect(url_for("index"))

    session["branch_code"] = request.form.get("branch_code")
    session["branch_name"] = request.form.get("branch_name")

    return redirect(url_for("branch_dashboard"))


@app.route("/branch-dashboard")
def branch_dashboard():
    if session.get("role") != "Branch":
        return redirect(url_for("index"))

    return render_template("branch_dashboard.html")


# =================================================
# ADMIN FLOW (PLACEHOLDER FOR NOW)
# =================================================
@app.route("/admin-dashboard")
def admin_dashboard():
    if session.get("role") != "CentralAdmin":
        return redirect(url_for("index"))

    return render_template("admin_dashboard.html")


# =================================================
# APP START (RENDER SAFE)
# =================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
