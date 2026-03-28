from google import genai
from google.genai import types 
import os

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def financial_chatbot(query, user, summary, patterns, chat_history, csv_data=""):
    try:
        behavioral_insights = "\n".join(patterns) if patterns else "No specific patterns detected yet."

        prompt = f"""
        You are an elite, highly empathetic Financial Advisor and Wealth Strategist.

        User Profile:
        Name: {user['name']}
        Age: {user['age']}
        Stated Monthly Salary: ₹{user['salary']} per month
        Profession: {user['profession']}
        Investment Interest: {user['investment']}

        --- VERIFIED FINANCIAL TOTALS ---
        Category Breakdown (Percentages):
        {summary}

        Behavioral & Mathematical Insights (CRITICAL):
        {behavioral_insights}

        --- RAW TRANSACTION HISTORY ---
        {csv_data}

        CRITICAL RULES FOR AI:
        1. DO NOT RECALCULATE TOTALS: Trust the "EXACT MATH" provided in the insights. 
        2. STRICT CURRENCY: Use the Indian Rupee symbol (₹).
        3. EXPERT KNOWLEDGE: If the user asks general questions (e.g., "How to make passive income", "What is an SIP?"), ignore their CSV data and provide expert, actionable advice tailored to a {user['profession']} in India. Quote philosophies from top investors if relevant.

        SCENARIO-BASED ROUTING (MANDATORY LOGIC):
        IF QUERY NEED TO ANSWER USING TRANSACTION THEN USE CSV DATA OTHERWISE USE SCENARIO BASED REPLY
        When the user asks for a "Plan", "Analysis", or "Advice" based on their data, you MUST diagnose their situation using the insights and apply the correct strategy:
        - FROM CATEGORY BREAKDOWN IF CASH WITHDRAW OR Miscellaneous CATEGORY PERCETAGE IS VERY LARGE THEN GIVE ADVICE USINF 
        FINANCIAL PLANNING RESOURCES LIKE Financial Planning Toolkit (ICSI) ALSO SUGGEST TO NOTE CATEGORY AT THE TIME OF UPI TRANSFER
        AND OTHER RELEVENT SUGGESTION TO TRACK THEIR EXPENSES SO THAT YOU CAN MAKE A PERSONALISED PLAN
        - SCENARIO A: DEBT/EMI HEAVY (If they have significant Loan/EMI categories)
          -> Strategy: Focus strictly on debt reduction (Avalanche vs. Snowball method). Warn them about interest rates.
        - SCENARIO B: THE BURNER (If Net Savings is NEGATIVE)
          -> Strategy: Focus entirely on "Plugging the Leak". Identify the top 2 wasteful categories and give strict daily budgets to recover the deficit.
        - SCENARIO C: THE SAVER (If Net Savings is POSITIVE)
          -> Strategy: Focus on wealth generation. Since they are saving money, advise them on SIPs, Index Funds, and Emergency Funds based on their {user['investment']} interest.
         

        FORMATTING RULES (For Personal Analysis Queries):
        ### 🩺 Your Financial Diagnosis
        [State their exact scenario (A, B, or C) and a 2-sentence reality check based on the EXACT MATH OR CAAN BE MORE THAN ONE SCENARIO.]
        
        ### 🗺️ Your Custom Financial Plan
        [Detail the specific strategy based on their scenario]
        
        ### ❓ Recommend THE Questions THAT USER CAN ASK
        * [Follow-up question 1]
        * [Follow-up question 2]
        * [Follow-up question 3]
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