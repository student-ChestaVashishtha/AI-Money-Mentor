## 🧠 FinSaarthi AI — Intelligent Financial Decision Engine

> **“Not a chatbot. A system that analyzes your financial behavior and tells you exactly what to do.”**

---

## 📌 Problem Statement

India has **14+ crore demat accounts**, but most retail investors:

* React emotionally instead of logically
* Don’t understand their spending patterns
* Miss critical financial signals
* Lack personalized financial planning

👉 Data exists.
❌ Decision-making intelligence does NOT.

---

## 💡 Solution

**FinSaarthi AI** is a **data-driven financial decision engine** that:

* Analyzes real financial statements
* Detects behavioral patterns
* Classifies users into financial scenarios
* Generates **strict, actionable financial advice using AI**

---

## 🔥 Core Innovation: Multi-Agent Architecture

Unlike typical finance apps:

❌ Not just tracking
❌ Not just chatbot

FinSaarthi AI moves beyond standard prompting by utilizing a specialized agentic workflow. Data flows through dedicated agents, each handling one stage of the reasoning pipeline:

1. 🧾 **Transaction Analyzer Agent:** Parses raw bank CSVs, auto-cleanses, normalizes, and structures messy real-world data.
2. 🗂️ **Categorization Agent (Smart Regex Engine):** Utilizes pattern recognition to classify income/expenses and isolates repeat merchants and subscriptions.
3. 🧠 **Scenario Agent (The Diagnostic Core):** Evaluates categorized data to detect behavioral patterns and assigns a definitive health status:
   * 🔴 **BURNER:** Expenses exceed income; low/negative savings.
   * 🟢 **SAVER:** Positive net savings; ready for wealth multiplication.
   * 🟡 **RISKY:** High EMI burden, volatile cash flow, or critical lack of insurance.
4. 🗺️ **Planning Agent (The Strategist):** Synthesizes the user's scenario and profile to generate a hyper-personalized roadmap with actionable monthly targets and risk mitigation steps.

---

## ⚙️ Tech Stack

| Layer | Technology |
| :--- | :--- |
| **AI Decision Engine** | Google Gemini 2.5 Flash API |
| **Backend & Orchestration** | Flask, Python |
| **Data Processing** | Pandas, Regex |
| **Session Management** | Flask-Session |
| **Frontend** | HTML, CSS, Bootstrap |

---

## ⚙️ How It Works

```text
User Profile + CSV Upload
        ↓
Transaction Categorization (Pandas)
        ↓
Behavioral Pattern Detection
        ↓
Scenario Detection Engine
        ↓
Context Injection into AI
        ↓
AI Financial Decision Engine
        ↓
Strict, Quantified Advice
```

---

## 📊 Features

### 🧾 Financial Statement Intelligence

* Upload real bank CSV
* Auto categorization (UPI, shopping, rent, etc.)
* Handles messy real-world data

---

### ⚠️ Behavioral Pattern Detection

* Overspending detection
* Cash leakage identification
* Habit-based financial insights

---

### 🧠 Scenario-Based Decision Engine

* Converts raw data → financial persona
* Drives AI decision-making logic

---

### 🤖 AI Financial Mentor (NOT a chatbot)

* Context-aware AI using:

  * User profile
  * Spending patterns
  * Scenario classification
  * Raw transaction data

👉 Produces:

* Financial diagnosis
* Cost leakage analysis
* Step-by-step action plan
* Future projections

---

### 🎯 Goal-Based Financial Planning

Supports:

💍 Marriage planning
🏠 Home loan decisions
🚀 Business planning
👶 Child future planning
🧓 Retirement planning

---

### 📈 Structured AI Output

Every response includes:

* 🧠 Financial Health Summary
* 🩺 Diagnosis
* 💸 Cost Leakage
* 🗺️ Action Plan
* 📈 Financial Impact
* 🔮 Future Projection

---

## 🔥 Example AI Output

> “You are currently a **BURNER**. Your expenses exceed income by ₹8,000/month.
> Cut shopping by ₹3,000 and food delivery by ₹2,000 to stabilize your finances within 2 months.”

---

## 📂 Project Structure

```bash
AI-Money-Mentor/
│
├── app.py
├── utils/
│   ├── analysis.py
│   ├── chatbot.py
│
├── templates/
├── static/
├── uploads/
```

---

## 📊 Sample Dataset

This project uses a synthetic financial dataset that mimics real-world bank statements (UPI transactions, bills, salary credits, etc.).

**uploads/sample_statement.csv**

Due to privacy concerns, no real user data is included. The dataset is fully anonymized and safe for public use.

### Data Format
**Columns**:
- Date
- Description
- Reference
- Amount
- Type (credit/debit)
- Balance

---

## 🚀 Setup

**1. Clone the Repository**
```bash
git clone [https://github.com/student-ChestaVashishtha/AI-Money-Mentor.git](https://github.com/student-ChestaVashishtha/AI-Money-Mentor.git)
cd AI-Money-Mentor
```

**2. Install Dependencies**
```bash
pip install -r requirements.txt
````

**3. Set Environment Variables**
Configure your Google Gemini API key:


# For Windows
```bash
set GEMINI_API_KEY=your_api_key
```

# For Mac/Linux
```bash
export GEMINI_API_KEY=your_api_key
```

**4. Run the Application**

```bash
python app.py
```

The application will be hosted locally at http://127.0.0.1:5000



---

## 📸 Demo

https://drive.google.com/file/d/1Ja-QeHqNbkjEAUdfmu9mh-J1JJAHB-R0/view?usp=sharing

---

## 🎯 Why This Project Wins

* ✅ Real-world financial complexity handled
* ✅ Behavioral finance + AI combined
* ✅ Scenario-driven decision system
* ✅ Not generic AI — **structured reasoning engine**

---

## ⚠️ Limitations

* Cash transactions are estimated
* Depends on CSV format
* Not a licensed financial advisor

---

## 🚀 Future Scope

* 🔗 Bank API integration (Plaid / ONDC / UPI)
* 📊 Portfolio tracking
* 🧠 Multi-agent financial system
* 📱 Mobile app
* 📈 Investment recommendation engine

---

## 🎤 Hackathon Pitch Line

> “We built an AI that doesn’t just analyze your money — it tells you exactly how to fix your financial life.”

---

## 👨‍💻 Author

**Chesta Vashishtha**
B.Tech (3rd Year)

---

