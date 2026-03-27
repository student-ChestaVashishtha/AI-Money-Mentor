from google import genai
from google.genai import types # We need this for formatting the history
import os

# Initialize the client. 
# NOTE: It's best practice to remove the hardcoded API key and use environment variables.
# If you set an environment variable named GEMINI_API_KEY, you can just use `client = genai.Client()`
client = genai.Client(api_key=os.getenv("API_KEY"))

def financial_chatbot(query, user, summary, chat_history):
    try:
        prompt = f"""
        You are an empathetic but highly practical financial advisor.

        User Context:
        Name: {user['name']}
        Age: {user['age']}
        Salary: ₹{user['salary']} per month
        Profession: {user['profession']}
        Investment Interest: {user['investment']}

        Spending Data (Monthly):
        {summary}

        CRITICAL RULES & FORMATTING:
        1. STRICT CURRENCY: You MUST use the Indian Rupee symbol (₹) for all monetary amounts. NEVER use dollars ($).
        2. STRICT TIMEFRAME: The user's salary and all spending data provided are STRICTLY MONTHLY figures. 
        3. STRICT TEMPLATE: You MUST format your response using the exact Markdown template below. Keep paragraphs short.
        4. STRICT TEMPLATE: You MUST format your response using the exact Markdown template below.
        5. CATEGORY UPDATES: If the user explicitly asks to categorize a merchant into a new or specific category (e.g., "Yes, put Jio in Bills" or "Make a new category for Amazon called Shopping"), you MUST include a secret tag at the very end of your response in this exact format:
        [UPDATE_CATEGORY: MerchantName -> NewCategoryName]
        Example: [UPDATE_CATEGORY: Jio -> Monthly Bills]
        ### The Short Answer
        [Give a direct, 1-2 sentence answer]

        ### The Reality Check
        [Explain the financial reasoning based purely on their provided monthly ₹ data.]

        ### Next Steps
        * [Actionable step 1]
        * [Actionable step 2]
        * [Actionable step 3]

        ### Recommended Questions
        * [Follow up question 1]
        * [Follow up question 2]
        * [Follow up question 3]
        """

        # 2. Rebuild the conversation history for Gemini
        formatted_contents = []
        for msg in chat_history:
            formatted_contents.append(
                types.Content(role=msg["role"], parts=[types.Part.from_text(text=msg["text"])])
            )
        
        # 3. Add the brand new question from the user
        formatted_contents.append(
            types.Content(role="user", parts=[types.Part.from_text(text=query)])
        )

        # 4. Generate the response using the history and the system instructions
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=formatted_contents,
            config=types.GenerateContentConfig(
                system_instruction=prompt,
                temperature=0.7 # Makes the AI slightly more conversational
            )
        )

        return response.text  

    except Exception as e:
        print("Gemini Error:", e)
        return "⚠️ AI service unavailable. Try again."