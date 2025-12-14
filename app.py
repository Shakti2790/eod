from flask import Flask, render_template, redirect, url_for, session, request
import os
import requests
import csv
import io
from datetime import datetime

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

# =================================================
# GOOGLE SHEET FILE IDs
# =================================================

BRANCH_MASTER_ID = "17Y9f2dFSZXGZsVmVP9wvzla6haom6NntB27dkHUfSUM"
PERMISSIONS_ID   = "1nLKZAkLZhitxAos28ST6aa6bxXKO-tfoVKxZegkifhY"
REPLIES_ID       = "183oVHlHXa_YEFoWdeVGHnzVZzm2zhGRSc_XOmhsM7gA"
USERS_ID         = "1gsWjkRXCxmM8lIBxK2VCpH5Lbwdl46Y6hVEBd4BB-vs"

# =================================================
# GENERIC CSV READER (READ-ONLY)
# =================================================

def read_csv(sheet_id):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    res = requests.get(url)
    if res.status_code != 200:
        return []
    return list(csv.DictReader(io.StringIO(res.content.decode("utf-8"))))

# =================================================
# DATA FUNCTIONS
# =================================================

def get_branches():
    rows = read_csv(BRANCH_MASTER_ID)
    return [
        {
            "code": str(r.get("Branch_Code", "")).strip(),
            "name": str(r.get("Branch_Name", "")).strip()
        }
        for r in rows
        if r.get("Branch_Code") and r.get("Branch_Name")
    ]


def get_branch_permissions(branch_code):
    rows = read_csv(PERMISSIONS_ID)
    branch_code = str(branch_code).strip()

    permissions = []
    for r in rows:
        if (
            str(r.get("Branch_Code", "")).strip() == branch_code
            and str(r.get("Status", "")).strip() == "Active"
        ):
            permissions.append({
                "permission_id": r.get("Permission_ID"),
                "department": r.get("Department"),
                "reason": r.get("Reason"),
                "status": r.get("Status")
            })
    return permissions


def get_user(email):
    rows = read_csv(USERS_ID)
    for r in rows:
        if str(r.get("Email", "")).lower() == email.lower():
            return r
    return None


# =================================================
# REPLY SAVE (VIA GOOGLE FORM – PLACEHOLDER)
# =================================================

def save_branch_reply(permission_id, branch_code, reply_text):
    """
    NOTE:
    Google Sheets does NOT allow write via CSV.
    This function will work AFTER we connect a Google Form.

    Replace:
    - YOUR_FORM_ID
    - entry.xxxxxx values
    """

    form_url = "https://docs.google.com/forms/d/e/YOUR_FORM_ID/formResponse"

    payload = {
        "entry.111111": permission_id,
        "entry.222222": branch_code,
        "entry.333333": reply_text,
        "entry.444444": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    requests.post(form_url, data=payload)


# =================================================
# ROUTES
# =================================================

@app.route("/")
def index():
    return render_template("login.html")


@app.route("/login")
def login():
    """
    TEMP LOGIN
    (Google login will replace this later)
    """
    session.clear()

    email = "branch.user@gmail.com"  # simulated login
    user = get_user(email)

    if not user or user.get("Active") != "Yes":
        return "Access denied"

    session["email"] = email
    session["role"] = user.get("Role")

    if session["role"] == "Branch":
        return redirect(url_for("select_branch"))
    else:
        return redirect(url_for("admin_dashboard"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# -----------------------------
# BRANCH FLOW
# -----------------------------

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

    branch_code = session.get("branch_code")
    branch_name = session.get("branch_name")

    permissions = get_branch_permissions(branch_code)

    return render_template(
        "branch_dashboard.html",
        branch_code=branch_code,
        branch_name=branch_name,
        permissions=permissions
    )


@app.route("/submit-reply", methods=["POST"])
def submit_reply():
    if session.get("role") != "Branch":
        return redirect(url_for("index"))

    permission_id = request.form.get("permission_id")
    branch_code = request.form.get("branch_code")
    reply_text = request.form.get("reply_text")

    save_branch_reply(permission_id, branch_code, reply_text)

    return redirect(url_for("branch_dashboard"))

# -----------------------------
# ADMIN FLOW (PLACEHOLDER)
# -----------------------------

@app.route("/admin-dashboard")
def admin_dashboard():
    if session.get("role") not in ["CentralAdmin", "DeptAdmin"]:
        return redirect(url_for("index"))

    return """
    <h3>Admin Dashboard</h3>
    <p>Admin features coming next.</p>
    <a href="/logout">Logout</a>
    """

# =================================================
# APP START (RENDER SAFE)
# =================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
