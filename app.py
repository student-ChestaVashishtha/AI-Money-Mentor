from flask import Flask, render_template, request, redirect, session, url_for, flash
import pandas as pd
import os
import json
import re  # <--- MOVED TO THE VERY TOP
from utils.analysis import analyze_data, detect_patterns
from utils.chatbot import financial_chatbot
import markdown
from flask_session import Session

app = Flask(__name__)
app.secret_key = "super_secret_hackathon_key"

# Configure Server-Side Sessions
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # Ensure folder exists
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

users = {}  # In-memory storage

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("name")
        
        # If the user exists, log them in
        if name in users:
            session["user"] = name
            return redirect(url_for("dashboard"))
        
        # If the user DOES NOT exist, flash a message and send them to register
        else:
            flash("You are not registered. Please register first.", "error")
            return redirect(url_for("register"))
            
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
    # 1. Check if they have a session cookie at all
    if "user" not in session:
        return redirect(url_for("login"))
    
    user = users.get(session["user"])

    # 2. Check if the user actually exists
    if user is None:
        session.clear()
        flash("Session expired. Please register or log in again.", "error")
        return redirect(url_for("register"))

    # Initialize custom_rules if it doesn't exist
    if "custom_rules" not in session:
        session["custom_rules"] = {}

    # Ensure a chat history list exists
    if "chat_history" not in session:
        session["chat_history"] = []

    summary = session.get("summary", {})
    patterns = session.get("patterns", [])

    # ==========================================
    # FILE UPLOAD & AUTO-ANALYSIS TRIGGER
    # ==========================================
    if request.method == "POST":
        file = request.files.get("file")
        if file and file.filename.endswith('.csv'):
            path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(path)
            
            session["current_file"] = file.filename
            
            df = pd.read_csv(path)
            
            # Run the Python Math
            summary = analyze_data(df, session["custom_rules"])
            patterns = detect_patterns(df, summary, session["custom_rules"]) 

            session["summary"] = summary
            session["patterns"] = patterns

            # Clear old chat history so the new file gets a fresh analysis
            session["chat_history"] = []
            
           # Force the AI to write the deep analysis report immediately
            auto_query = "I just uploaded my bank statement. Please provide a deep, personalized financial analysis of my recent statement based on the exact math and patterns."
            
            # Convert DataFrame to a string so Gemini can read the rows!
            csv_string = df.to_csv(index=False)
            
            # Add csv_string to the end!
            raw_response = financial_chatbot(auto_query, user, summary, patterns, session["chat_history"], csv_string)
            
            
            # Erase any hidden tags just in case
            raw_response = re.sub(r'\[UPDATE_CATEGORY.*?\]', '', raw_response)
            
            html_response = markdown.markdown(raw_response.strip())
            
            # Append the AI's deep analysis as the first message!
            session["chat_history"].append({"role": "model", "text": raw_response.strip(), "html": html_response})
            session.modified = True

    # ==========================================
    # NORMAL CHAT PROCESSING
    # ==========================================
    query = request.args.get("query")
    if query:
        # We need the dataframe to pass the raw data
        csv_string = ""
        if "current_file" in session:
            path = os.path.join(app.config["UPLOAD_FOLDER"], session["current_file"])
            if os.path.exists(path):
                temp_df = pd.read_csv(path)
                csv_string = temp_df.to_csv(index=False)

        # Add csv_string to the end!
        raw_response = financial_chatbot(query, user, summary, patterns, session["chat_history"], csv_string)
        
        # Secret Tag Interceptor
        match = re.search(r'\[UPDATE_CATEGORY:\s*(.+?)\s*->\s*(.+?)\]', raw_response)
        if match:
            old_name = match.group(1).strip()
            new_name = match.group(2).strip()
            session["custom_rules"][old_name] = new_name
            session.modified = True
            raw_response = raw_response.replace(match.group(0), "")
            
            if "current_file" in session:
                path = os.path.join(app.config["UPLOAD_FOLDER"], session["current_file"])
                if os.path.exists(path):
                    df = pd.read_csv(path)
                    summary = analyze_data(df, session["custom_rules"])
                    patterns = detect_patterns(df, summary, session["custom_rules"])
                    session["summary"] = summary
                    session["patterns"] = patterns

        html_response = markdown.markdown(raw_response.strip())

        session["chat_history"].append({"role": "user", "text": query})
        session["chat_history"].append({"role": "model", "text": raw_response.strip(), "html": html_response})
        session.modified = True

    return render_template(
        "dashboard.html",
        user=user,
        summary=summary,
        patterns=patterns,
        chat_history=session.get("chat_history", []) 
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/clear_chat")
def clear_chat():
    session.pop("chat_history", None)
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(debug=True)