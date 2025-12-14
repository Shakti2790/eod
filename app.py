from flask import Flask, render_template, redirect, url_for, session, request
import os
import requests
import csv
import io
from datetime import datetime

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

# =================================================
# GOOGLE SHEET FILE IDs (FINAL)
# =================================================

BRANCH_MASTER_ID = "17Y9f2dFSZXGZsVmVP9wvzla6haom6NntB27dkHUfSUM"
PERMISSIONS_ID   = "1nLKZAkLZhitxAos28ST6aa6bxXKO-tfoVKxZegkifhY"
REPLIES_ID       = "183oVHlHXa_YEFoWdeVGHnzVZzm2zhGRSc_XOmhsM7gA"
USERS_ID         = "1gsWjkRXCxmM8lIBxK2VCpH5Lbwdl46Y6hVEBd4BB-vs"

# =================================================
# GENERIC CSV READER
# =================================================

def read_csv(sheet_id):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    res = requests.get(url)
    if res.status_code != 200:
        return []
    data = res.content.decode("utf-8")
    return list(csv.DictReader(io.StringIO(data)))

# =================================================
# DATA ACCESS FUNCTIONS
# =================================================

def get_branches():
    rows = read_csv(BRANCH_MASTER_ID)
    branches = []
    for r in rows:
        code = str(r.get("Branch_Code", "")).strip()
        name = str(r.get("Branch_Name", "")).strip()
        if code and name:
            branches.append({"code": code, "name": name})
    return branches


def get_branch_permissions(branch_code):
    rows = read_csv(PERMISSIONS_ID)
    result = []
    branch_code = str(branch_code).strip()

    for r in rows:
        if (
            str(r.get("Branch_Code", "")).strip() == branch_code
            and str(r.get("Status", "")).strip() == "Active"
        ):
            result.append({
                "permission_id": r.get("Permission_ID"),
                "department": r.get("Department"),
                "reason": r.get("Reason"),
                "status": r.get("Status")
            })
    return result


def get_user(email):
    rows = read_csv(USERS_ID)
    for r in rows:
        if str(r.get("Email", "")).strip().lower() == email.lower():
            return r
    return None


def save_branch_reply(permission_id, branch_code, reply_text):
    # NOTE: Google Sheets append requires API.
    # For now this function is a placeholder for next step.
    pass

# =================================================
# ROUTES
# =================================================

@app.route("/")
def index():
    return render_template("login.html")


@app.route("/login")
def login():
    # TEMP LOGIN (Google OAuth later)
    session.clear()

    email = "branch.user@gmail.com"  # simulate login
    user = get_user(email)

    if not user or user.get("Active") != "Yes":
        return "Access denied"

    session["email"] = email
    session["role"] = user.get("Role")

    if user.get("Role") == "Branch":
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

# -----------------------------
# ADMIN FLOW (PLACEHOLDER)
# -----------------------------

@app.route("/admin-dashboard")
def admin_dashboard():
    if session.get("role") not in ["CentralAdmin", "DeptAdmin"]:
        return redirect(url_for("index"))

    return """
    <h3>Admin Dashboard</h3>
    <p>Permission creation & monitoring coming next.</p>
    <a href="/logout">Logout</a>
    """

# =================================================
# APP START
# =================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
