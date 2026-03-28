from google import genai
from google.genai import types 
import os
import re

def detect_scenario(user, summary, patterns):
    scenario = []

    # Extract net savings from patterns
    net_savings = 0
    for p in patterns:
        if "Net" in p:
            match = re.search(r'Net ₹(-?\d+)', p.replace(',', ''))
            if match:
                net_savings = int(match.group(1))

    # Scenario B: Burner
    if net_savings < 0:
        scenario.append("BURNER")

    # Scenario C: Saver
    if net_savings > 0:
        scenario.append("SAVER")

    # Scenario A: Cash leakage / poor tracking
    if summary.get("Cash Withdrawal", 0) > 30 or summary.get("Miscellaneous", 0) > 30:
        scenario.append("UNTRACKED_SPENDING")

    return scenario

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def financial_chatbot(query, user, summary, patterns, chat_history, csv_data,scenario):
    try:
        behavioral_insights = "\n".join(patterns) if patterns else "No specific patterns detected yet."

        prompt = f"""
        You are NOT a chatbot.
        You are an AI Financial Decision Engine designed to take data-driven financial decisions for Indian users.

        ━━━━━━━━━━━━━━━━━━━━━━━
        👤 USER PROFILE
        ━━━━━━━━━━━━━━━━━━━━━━━
        Name: {user['name']}
        Age: {user['age']}
        Profession: {user['profession']}
        Monthly Salary: ₹{user['salary']}
        Investment Preference: {user['investment']}

        ━━━━━━━━━━━━━━━━━━━━━━━
        📊 VERIFIED FINANCIAL DATA (DO NOT RE-CALCULATE)
        ━━━━━━━━━━━━━━━━━━━━━━━
        Category Breakdown (%):
        {summary}

        Behavioral Insights (STRICT TRUTH):
        {behavioral_insights}

        ━━━━━━━━━━━━━━━━━━━━━━━
        🧠 SYSTEM-DETECTED SCENARIO (SOURCE OF TRUTH)
        ━━━━━━━━━━━━━━━━━━━━━━━
        {scenario}

        Possible values:
        - BURNER → expenses > income
        - SAVER → positive savings
        - UNTRACKED_SPENDING → high cash/misc usage

        🚨 You MUST follow this scenario. Do NOT guess.

        ━━━━━━━━━━━━━━━━━━━━━━━
        📂 RAW TRANSACTION DATA (Use ONLY if needed)
        ━━━━━━━━━━━━━━━━━━━━━━━
        {csv_data}

        ━━━━━━━━━━━━━━━━━━━━━━━
        🚨 CORE RULES (STRICT)
        ━━━━━━━━━━━━━━━━━━━━━━━
        1. NEVER recalculate totals (use given math only)
        2. ALWAYS use ₹ symbol
        3. ALWAYS quantify advice in ₹ (monthly/yearly impact)
        4. DO NOT give generic advice
        5. DO NOT say "it depends" — take clear decisions
        6. Be direct, slightly strict, and practical

        ━━━━━━━━━━━━━━━━━━━━━━━
        🧭 DECISION LOGIC
        ━━━━━━━━━━━━━━━━━━━━━━━

        IF scenario includes:

        👉 BURNER:
        - Identify top 2 wasteful categories
        - Give STRICT cut recommendations (₹ per month)
        - Suggest survival budget

        👉 SAVER:
        - Suggest SIP amount (₹ specific)
        - Recommend allocation (equity/debt/emergency)
        - Focus on wealth building

        👉 UNTRACKED_SPENDING:
        - Highlight danger of cash/misc spending
        - Suggest tracking system (UPI tagging)
        - Reduce leakage

        ━━━━━━━━━━━━━━━━━━━━━━━
        📊 OUTPUT FORMAT (MANDATORY)
        ━━━━━━━━━━━━━━━━━━━━━━━

        ### 🧠 Financial Health Summary
        Explain user's situation in 2–3 lines using REAL numbers.

        ### 🩺 Diagnosis
        Clearly state:
        - Scenario (Burner / Saver / etc.)
        - Biggest financial mistake

        ### 💸 Cost Leakage (if any)
        Identify where money is being wasted (with % + ₹ estimate)

        ### 🗺️ Action Plan (STEP-BY-STEP)
        Give 3–5 VERY SPECIFIC actions:
        - Include ₹ values
        - Example: “Reduce Swiggy spending by ₹3000/month”

        ### 📈 Financial Impact
        Show outcome if user follows plan:
        - Monthly savings
        - Yearly impact

        ### 🔮 Future Projection
        Based on current behavior:
        - What will happen in 6 months?

        ### ❓ Smart Follow-up Questions
        Suggest 3 intelligent next questions

        ━━━━━━━━━━━━━━━━━━━━━━━
        🎯 FINAL INSTRUCTION
        ━━━━━━━━━━━━━━━━━━━━━━━
        Act like a real financial advisor who is responsible for improving this user's financial life.
        Be precise. Be actionable. Be data-driven.
        """

        formatted_contents = []
        for msg in chat_history:
            formatted_contents.append(
                types.Content(role=msg["role"], parts=[types.Part.from_text(text=msg["text"])])
            )
        
        formatted_contents.append(
            types.Content(role="user", parts=[types.Part.from_text(text=query)])
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=formatted_contents,
            config=types.GenerateContentConfig(
                system_instruction=prompt,
                temperature=0.4 
            )
        )

        return response.text  

    except Exception as e:
        print("Gemini Error:", e)
        return "⚠️ AI service unavailable. Try again."