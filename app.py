from flask import Flask, render_template, redirect, url_for, session, request
import os
import requests
import csv
import io

app = Flask(__name__)
app.secret_key = "change-this-secret-key-123"

# =================================================
# GOOGLE SHEET CONFIG (ALREADY FILLED)
# =================================================
SHEET_ID = "1nLKZAkLZhitxAos28ST6aa6bxXKO-tfoVKxZegkifhY"
BRANCH_SHEET = "Branch_Master"
PERMISSION_SHEET = "Permissions"

# =================================================
# HELPER FUNCTIONS
# =================================================

def get_branches():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&sheet={BRANCH_SHEET}"
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


def get_branch_permissions(branch_code):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&sheet={PERMISSION_SHEET}"
    response = requests.get(url)

    if response.status_code != 200:
        return []

    decoded = response.content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(decoded))

    permissions = []
    for row in reader:
        if (
            row.get("Branch_Code") == branch_code
            and row.get("Status") == "Active"
        ):
            permissions.append({
                "department": row.get("Department"),
                "reason": row.get("Reason"),
                "status": row.get("Status")
            })

    return permissions

# =================================================
# ROUTES
# =================================================

@app.route("/")
def index():
    return render_template("login.html")


@app.route("/login")
def login():
    session.clear()
    session["user"] = "test@demo.com"

    # CHANGE ONLY FOR TESTING
    session["role"] = "Branch"   # or "CentralAdmin"

    if session["role"] == "CentralAdmin":
        return redirect(url_for("admin_dashboard"))
    else:
        return redirect(url_for("select_branch"))


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
    if session.get("role") != "CentralAdmin":
        return redirect(url_for("index"))

    return """
    <h3>Admin Dashboard</h3>
    <p>Permission module coming next</p>
    <a href="/logout">Logout</a>
    """


# =================================================
# APP START (RENDER SAFE)
# =================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
