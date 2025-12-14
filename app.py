from flask import Flask, render_template, redirect, url_for, session, request
import os, requests, csv, io
from datetime import datetime

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

# =================================================
# GOOGLE SHEET FILE IDS
# =================================================
BRANCH_MASTER_ID = "17Y9f2dFSZXGZsVmVP9wvzla6haom6NntB27dkHUfSUM"
PERMISSIONS_ID   = "1nLKZAkLZhitxAos28ST6aa6bxXKO-tfoVKxZegkifhY"
REPLIES_ID       = "183oVHlHXa_YEFoWdeVGHnzVZzm2zhGRSc_XOmhsM7gA"
USERS_ID         = "1gsWjkRXCxmM8lIBxK2VCpH5Lbwdl46Y6hVEBd4BB-vs"

# =================================================
# CSV READER
# =================================================
def read_csv(sheet_id):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    r = requests.get(url)
    if r.status_code != 200:
        return []
    return list(csv.DictReader(io.StringIO(r.content.decode("utf-8"))))

# =================================================
# DATA FUNCTIONS
# =================================================
def get_branches():
    rows = read_csv(BRANCH_MASTER_ID)
    return [
        {"code": r["Branch_Code"].strip(), "name": r["Branch_Name"].strip()}
        for r in rows if r.get("Branch_Code") and r.get("Branch_Name")
    ]

def get_branch_permissions(branch_code):
    rows = read_csv(PERMISSIONS_ID)
    result = []
    for r in rows:
        if r.get("Branch_Code","").strip() == branch_code and r.get("Status","").strip() == "Active":
            result.append({
                "permission_id": r.get("Permission_ID"),
                "department": r.get("Department"),
                "reason": r.get("Reason"),
                "status": r.get("Status")
            })
    return result

def get_all_active_permissions():
    rows = read_csv(PERMISSIONS_ID)
    result = []
    for r in rows:
        if r.get("Status","").strip() == "Active":
            result.append({
                "branch_code": r.get("Branch_Code"),
                "branch_name": r.get("Branch_Name"),
                "department": r.get("Department"),
                "reason": r.get("Reason"),
                "status": r.get("Status"),
                "created_at": r.get("Created_At")
            })
    return result

def get_user(email):
    rows = read_csv(USERS_ID)
    for r in rows:
        if r.get("Email","").lower() == email.lower() and r.get("Active") == "Yes":
            return r
    return None

# =================================================
# ROUTES
# =================================================
@app.route("/")
def index():
    return render_template("login.html")

@app.route("/login")
def login():
    session.clear()

    # TEMP LOGIN (replace with Google later)
    email = "batskt@gmail.com"   # change for testing
    user = get_user(email)

    if not user:
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

# ---------------- BRANCH FLOW ----------------
@app.route("/select-branch")
def select_branch():
    if session.get("role") != "Branch":
        return redirect(url_for("index"))
    return render_template("branch_select.html", branches=get_branches())

@app.route("/set-branch", methods=["POST"])
def set_branch():
    session["branch_code"] = request.form["branch_code"]
    session["branch_name"] = request.form["branch_name"]
    return redirect(url_for("branch_dashboard"))

@app.route("/branch-dashboard")
def branch_dashboard():
    if session.get("role") != "Branch":
        return redirect(url_for("index"))

    permissions = get_branch_permissions(session["branch_code"])
    return render_template(
        "branch_dashboard.html",
        branch_code=session["branch_code"],
        branch_name=session["branch_name"],
        permissions=permissions
    )

# ---------------- ADMIN FLOW ----------------
@app.route("/admin-dashboard")
def admin_dashboard():
    if session.get("role") not in ["CentralAdmin", "DeptAdmin"]:
        return redirect(url_for("index"))

    permissions = get_all_active_permissions()
    return render_template("admin_dashboard.html", permissions=permissions)

# =================================================
# RUN
# =================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
