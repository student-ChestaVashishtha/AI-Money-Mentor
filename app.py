from flask import Flask, render_template, request, redirect, session, url_for, flash
import pandas as pd
import os
import re
import markdown
from flask_session import Session

from utils.analysis import analyze_data, detect_patterns
from utils.chatbot import financial_chatbot, detect_scenario

app = Flask(__name__)
app.secret_key = "super_secret_hackathon_key"

# ===============================
# SESSION CONFIG
# ===============================
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# ===============================
# FILE UPLOAD CONFIG
# ===============================
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Temporary user storage (hackathon OK)
users = {}

# ===============================
# LOGIN
# ===============================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("name")

        if name in users:
            session["user"] = name
            return redirect(url_for("dashboard"))
        else:
            flash("You are not registered. Please register first.", "error")
            return redirect(url_for("register"))

    return render_template("login.html")


# ===============================
# REGISTER
# ===============================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user_data = {
            "name": request.form.get("name"),
            "age": request.form.get("age"),
            "gender": request.form.get("gender", "Not specified"),
            "profession": request.form.get("profession"),
            "salary": int(request.form.get("salary", 0)),
            "marital": request.form.get("marital"),
            "investment": request.form.get("investment"),
            
            # 🔥 NEW DEEP PROFILING FIELDS CAPTURED HERE
            "has_children": request.form.get("has_children", "No"),
            "child_count": request.form.get("child_count", "0"),
            "child_ages": request.form.get("child_ages", "N/A"),
            "child_fees": request.form.get("child_fees", "0"),
            "health_issues": request.form.get("health_issues", "None"),
            "monthly_emi": request.form.get("monthly_emi", "0"),

            "expense": 0,
            "savings": 0,
            "debt": 0
        }

        users[user_data["name"]] = user_data
        session["user"] = user_data["name"]

        return redirect(url_for("dashboard"))

    return render_template("register.html")


# ===============================
# DASHBOARD
# ===============================
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    user = users.get(session["user"])

    if user is None:
        session.clear()
        flash("Session expired. Please register again.", "error")
        return redirect(url_for("register"))

    # Initialize session variables
    if "chat_history" not in session:
        session["chat_history"] = []

    summary = session.get("summary", {})
    patterns = session.get("patterns", [])

    # ==========================================
    # FILE UPLOAD + REAL AGENT ANALYSIS LOGGING
    # ==========================================
    if request.method == "POST":
        file = request.files.get("file")

        if file and file.filename.endswith(".csv"):
            path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(path)
            session["current_file"] = file.filename

            # --- START REAL LOGGING ---
            workflow_steps = []
            workflow_steps.append(">_ INITIATING AGENTIC WORKFLOW...")

            # Agent 1: Transaction Analyzer
            workflow_steps.append(f"⏳ Transaction Analyzer: Ingesting {file.filename}...")
            df = pd.read_csv(path)
            summary = analyze_data(df)
            workflow_steps.append(f"✅ Transaction Analyzer: Parsed {len(df)} rows and categorized spending.")

            # Agent 2: Behavioral Regex Engine
            workflow_steps.append("⏳ Regex Engine: Scanning for behavioral anomalies...")
            patterns = detect_patterns(df, summary)
            workflow_steps.append(f"✅ Regex Engine: Detected {len(patterns)} pattern alerts.")

            # Financial Updates
            total_income = df[df["Type"].str.lower() == "credit"]["Amount"].sum()
            total_expense = df[df["Type"].str.lower() == "debit"]["Amount"].sum()
            user["expense"] = total_expense / 3 if total_expense else 0
            user["savings"] = max(total_income - total_expense, 0)
            user["debt"] = int(user.get("monthly_emi", 0))

            session["summary"] = summary
            session["patterns"] = patterns
            session["chat_history"] = []
            csv_string = df.to_csv(index=False)

            # Agent 3: Scenario Classifier
            workflow_steps.append("⏳ Scenario Classifier: Evaluating debt and investable surplus...")
            scenario = detect_scenario(user, summary, patterns)
            workflow_steps.append(f"✅ Scenario Classifier: Locked User Persona as {scenario}.")

            # Agent 4: Financial Advisor (Gemini)
            workflow_steps.append("⏳ Financial Advisor: Compiling context & calling AI Engine...")
            auto_query = "Analyze my financial data and give complete financial diagnosis, action plan, and future outlook."
            raw_response = financial_chatbot(
                auto_query, user, summary, patterns, session["chat_history"], csv_string, scenario
            )
            workflow_steps.append("✅ Financial Advisor: Comprehensive Action Plan Generated.")

            session["workflow"] = workflow_steps

            # Clean up and render markdown
            raw_response = re.sub(r'\[UPDATE_CATEGORY.*?\]', '', raw_response)
            html_response = markdown.markdown(raw_response.strip())

            session["chat_history"].append({
                "role": "model",
                "text": raw_response.strip(),
                "html": html_response
            })
            session.modified = True

    # ==========================================
    # CHAT HANDLING
    # ==========================================
    query = request.args.get("query")

    if query:
        csv_string = ""
        if "current_file" in session:
            path = os.path.join(app.config["UPLOAD_FOLDER"], session["current_file"])
            if os.path.exists(path):
                temp_df = pd.read_csv(path)
                csv_string = temp_df.to_csv(index=False)
                
        workflow_steps = []
        workflow_steps.append(f"💬 User Query Received: '{query}'")

        scenario = detect_scenario(user, summary, patterns)
        workflow_steps.append(f"🎯 Evaluating against persona: {scenario}")

        workflow_steps.append("🤖 Calling AI Engine...")
        raw_response = financial_chatbot(
            query, user, summary, patterns, session["chat_history"], csv_string, scenario
        )
        workflow_steps.append("✅ Response Generated.")

        session["workflow"] = workflow_steps

        raw_response = re.sub(r'\[UPDATE_CATEGORY.*?\]', '', raw_response)
        html_response = markdown.markdown(raw_response.strip())

        session["chat_history"].append({"role": "user", "text": query})
        session["chat_history"].append({
            "role": "model",
            "text": raw_response.strip(),
            "html": html_response
        })
        session.modified = True

    return render_template(
        "dashboard.html",
        user=user,
        summary=summary,
        patterns=patterns,
        chat_history=session.get("chat_history", []),
        workflow=session.get("workflow", [])   
    )

# ===============================
# LOGOUT
# ===============================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ===============================
# CLEAR CHAT
# ===============================
@app.route("/clear_chat")
def clear_chat():
    session.pop("chat_history", None)
    return redirect(url_for("dashboard"))


# ===============================
# RUN
# ===============================
if __name__ == "__main__":
    app.run(debug=True)