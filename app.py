from flask import Flask, render_template, request, redirect, session, url_for, flash
import pandas as pd
import os
import json
from utils.analysis import analyze_data, detect_patterns
from utils.chatbot import financial_chatbot
import markdown
from flask_session import Session

app = Flask(__name__)
app.secret_key = "super_secret_hackathon_key"

# 2. Add these two lines to configure Server-Side Sessions
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

    # 2. CRITICAL FIX: Check if the user actually exists in the database/dictionary
    # If the server restarted and wiped the dictionary, clear their dead session cookie.
    if user is None:
        session.clear()
        flash("Session expired. Please register or log in again.", "error")
        return redirect(url_for("register"))

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
            patterns = detect_patterns(df, summary) # Pass both the raw data and the summary!

            # Store in session so it persists during chat queries
            session["summary"] = summary
            session["patterns"] = patterns

    # Ensure a chat history list exists for this user's session
    if "chat_history" not in session:
        session["chat_history"] = []

    query = request.args.get("query")
    if query:
        # Pass the session history to the chatbot
        raw_response = financial_chatbot(query, user, summary, session["chat_history"])
        html_response = markdown.markdown(raw_response)

        # Append both the user's question and the AI's answer to the session
        session["chat_history"].append({"role": "user", "text": query})
        session["chat_history"].append({"role": "model", "text": raw_response, "html": html_response})
        
        # Tell Flask that we modified the list so it saves the cookie
        session.modified = True

    return render_template(
        "dashboard.html",
        user=user,
        summary=summary,
        patterns=patterns,
        # Pass the chat history instead of the single response
        chat_history=session.get("chat_history", []) 
    )
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/clear_chat")
def clear_chat():
    # Only clear the chat history, keep the user logged in and keep their CSV data
    session.pop("chat_history", None)
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(debug=True)