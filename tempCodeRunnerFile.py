from flask import Flask, render_template, request, redirect, session, url_for
import pandas as pd
import os
import json
from utils.analysis import analyze_data, detect_patterns
from utils.chatbot import financial_chatbot

app = Flask(__name__)
app.secret_key = "super_secret_hackathon_keyz"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # Ensure folder exists
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

users = {}  # In-memory storage

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("name")
        if name in users:
            session["user"] = name
            return redirect(url_for("dashboard"))
        else:
            return "User not found. Please register.", 400
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user_data = {
            "name": request.form.get("name"),
            "age": request.form.get("age"),
            "profession": request.form.get("profession"),
            "salary": int(request.form.get("salary", 0)),
            "marital": request.form.get("marital"),
            "investment": request.form.get("investment")
        }
        users[user_data["name"]] = user_data
        session["user"] = user_data["name"]
        return redirect(url_for("dashboard"))
    return render_template("register.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    
    user = users.get(session["user"])
    response = None

    # Retrieve existing data from session if it exists
    summary = session.get("summary", {})
    patterns = session.get("patterns", [])

    if request.method == "POST":
        file = request.files.get("file")
        if file and file.filename.endswith('.csv'):
            path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(path)
            
            df = pd.read_csv(path)
            summary = analyze_data(df)
            patterns = detect_patterns(summary)

            # Store in session so it persists during chat queries
            session["summary"] = summary
            session["patterns"] = patterns

    query = request.args.get("query")
    if query:
        response = financial_chatbot(query, user, summary)

    return render_template(
        "dashboard.html",
        user=user,
        summary=summary,
        patterns=patterns,
        response=response
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)