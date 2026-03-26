from flask import Flask, render_template, request, redirect, session
import pandas as pd
import os
from utils.analysis import analyze_data, detect_patterns
from utils.chatbot import financial_chatbot

app = Flask(__name__)
app.secret_key = "secret"

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

users = {}  # simple storage (hackathon)

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["name"]
        if name in users:
            session["user"] = name
            return redirect("/dashboard")
    return render_template("login.html")


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            salary = int(request.form.get("salary", 0))
        except:
            salary = 0

        user_data = {
            "name": request.form.get("name"),
            "age": request.form.get("age"),
            "profession": request.form.get("profession"),
            "salary": salary,
            "marital": request.form.get("marital"),
            "investment": request.form.get("investment")
        }

        users[user_data["name"]] = user_data
        session["user"] = user_data["name"]

        if not request.form["name"] or not request.form["salary"]:
            return "Please fill all required fields"

        return redirect("/dashboard")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    user = users.get(session.get("user"))

    summary = None
    patterns = []
    response = None

    if request.method == "POST":
        file = request.files["file"]
        
        if file:
            path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(path)
            
            df = pd.read_csv(path)
            
            summary = analyze_data(df)
            patterns = detect_patterns(summary)

            session["summary"] = summary.to_dict()

    query = request.args.get("query")

    if query:
        response = financial_chatbot(query, user, session.get("summary"))

    return render_template(
        "dashboard.html",
        user=user,
        summary=summary,
        patterns=patterns,
        response=response
    )


if __name__ == "__main__":
    app.run(debug=True)