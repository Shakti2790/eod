from flask import Flask, render_template, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = "change-this-secret-key-123"

# -----------------------------
# HOME / LOGIN PAGE
# -----------------------------
@app.route("/")
def index():
    return render_template("login.html")


# -----------------------------
# TEMPORARY LOGIN (NO OAUTH)
# -----------------------------
@app.route("/login")
def login():
    # TEMPORARY USER
    session.clear()
    session["user"] = "test@demo.com"

    # CHANGE ROLE HERE FOR TESTING:
    # "CentralAdmin" or "Branch"
    session["role"] = "Branch"

    if session["role"] == "CentralAdmin":
        return redirect(url_for("admin_dashboard"))
    else:
        return redirect(url_for("select_branch"))


# -----------------------------
# LOGOUT
# -----------------------------
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
    return render_template("branch_select.html")


@app.route("/branch-dashboard")
def branch_dashboard():
    if session.get("role") != "Branch":
        return redirect(url_for("index"))
    return render_template("branch_dashboard.html")
from flask import request

@app.route("/set-branch", methods=["POST"])
def set_branch():
    if session.get("role") != "Branch":
        return redirect(url_for("index"))

    branch_code = request.form.get("branch_code")
    session["branch_code"] = branch_code

    return redirect(url_for("branch_dashboard"))

# -----------------------------
# ADMIN FLOW
# -----------------------------
@app.route("/admin-dashboard")
def admin_dashboard():
    if session.get("role") != "CentralAdmin":
        return redirect(url_for("index"))
    return render_template("admin_dashboard.html")


# -----------------------------
# APP START (RENDER SAFE)
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
