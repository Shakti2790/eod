from flask import Flask, render_template, redirect, url_for, session
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

# Google OAuth setup
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id='YOUR_GOOGLE_CLIENT_ID',
    client_secret='YOUR_GOOGLE_CLIENT_SECRET',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'},
)

CENTRAL_ADMINS = [
    "batskt@gmail.com",
    "sktpathak@gmail.com"
]

@app.route("/")
def index():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/login")
def login():
    session["user"] = "test@demo.com"
    session["role"] = "CentralAdmin"
    return redirect(url_for("dashboard"))

@app.route("/authorize")
def authorize():
    token = google.authorize_access_token()
    user_info = google.get('userinfo').json()
    email = user_info["email"]

    session["user"] = email

    if email in CENTRAL_ADMINS:
        session["role"] = "CentralAdmin"
        return redirect(url_for("dashboard"))

    # Default: Branch user
    session["role"] = "Branch"
    return redirect(url_for("select_branch"))

@app.route("/select-branch")
def select_branch():
    return render_template("branch_select.html")

@app.route("/dashboard")
def dashboard():
    role = session.get("role")
    if role == "CentralAdmin":
        return render_template("admin_dashboard.html")
    return render_template("branch_dashboard.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
