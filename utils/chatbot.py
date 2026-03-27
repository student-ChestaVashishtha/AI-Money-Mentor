from google import genai
from google.genai import types 
import os

client = genai.Client(api_key=os.getenv("API_KEY"))

def financial_chatbot(query, user, summary, patterns, chat_history, csv_data=""):
    try:
        behavioral_insights = "\n".join(patterns) if patterns else "No specific patterns detected yet."

        prompt = f"""
        You are an elite, highly empathetic Financial Advisor.

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
        (Use this to answer specific questions about individual purchases)
        {csv_data}

        CRITICAL RULES FOR AI:
        1. DO NOT RECALCULATE TOTALS: You must trust the "EXACT MATH" provided in the insights for total income/expenses. 
        2. USE RAW DATA FOR SPECIFICS: If the user asks about specific transactions, search the RAW TRANSACTION HISTORY to give exact, accurate answers.
        3. STRICT CURRENCY: You MUST use the Indian Rupee symbol (₹).
        4. CATEGORY UPDATES: If the user explicitly asks to categorize a merchant, include this secret tag at the end: [UPDATE_CATEGORY: OldName -> NewCategory]

        FORMATTING RULES:
        - IF the user asks for a general analysis, review, or "how am I doing", you MUST use this strict template:
            ### 📊 The Reality Check
            [Summary based on EXACT MATH]
            ### 🔍 Where Your Money is Going
            [Analysis of categories]
            ### 🎯 Your Action Plan
            * [Step 1]
            * [Step 2]
        - IF the user asks a specific question, DO NOT use the template. Just answer their specific question directly.
        
        UNIVERSAL ENDING RULE (MANDATORY):
        No matter what the user asks, you MUST end EVERY SINGLE RESPONSE with exactly 3 highly relevant follow-up questions based on their data. 
        You MUST format it exactly like this:
        
        ### ❓ Recommended Questions
        * [Question 1]
        * [Question 2]
        * [Question 3]
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