from flask import Flask, render_template, request, redirect, session, url_for
import pandas as pd
import os
from utils.analysis import analyze_data, detect_patterns
from utils.chatbot import financial_chatbot

app = Flask(__name__)
app.secret_key = "secret"

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# create uploads folder if not exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

users = {}  # temporary storage

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("name")

        if name in users:
            session["user"] = name
            return redirect(url_for("dashboard"))
        else:
            return "User not found. Please register."

    return render_template("login.html")


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        
        name = request.form.get("name")
        salary_input = request.form.get("salary")

        # validation first
        if not name or not salary_input:
            return "Please fill all required fields"

        try:
            salary = int(salary_input)
        except ValueError:
            salary = 0

        user_data = {
            "name": name,
            "age": request.form.get("age"),
            "profession": request.form.get("profession"),
            "salary": salary,
            "marital": request.form.get("marital"),
            "investment": request.form.get("investment")
        }

        users[name] = user_data
        session["user"] = name

        return redirect(url_for("dashboard"))

    return render_template("register.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    
    # 🔐 protect route
    if "user" not in session:
        return redirect(url_for("login"))

    user = users.get(session["user"])

    summary = None
    patterns = []
    response = None

    # 📄 FILE UPLOAD
    if request.method == "POST" and "file" in request.files:
        file = request.files["file"]

        if file.filename != "":
            path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(path)

            df = pd.read_csv(path)

            summary = analyze_data(df)
            patterns = detect_patterns(summary)

            session["summary"] = summary.to_dict()

    # 🤖 CHATBOT
    query = request.form.get("query")

    if query:
        response = financial_chatbot(
            query,
            user,
            session.get("summary", {})
        )

    return render_template(
        "dashboard.html",
        user=user,
        summary=summary,
        patterns=patterns,
        response=response
    )


if __name__ == "__main__":
    app.run(debug=True)