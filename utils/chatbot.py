from google import genai
import os

# Initialize the client. 
# NOTE: It's best practice to remove the hardcoded API key and use environment variables.
# If you set an environment variable named GEMINI_API_KEY, you can just use `client = genai.Client()`
client = genai.Client(api_key=os.getenv("API_KEY"))

def financial_chatbot(query, user, summary):
    try:
        prompt = f"""
        You are an empathetic but highly practical financial advisor.

        User Context:
        Name: {user['name']}
        Age: {user['age']}
        Salary: ₹{user['salary']}
        Profession: {user['profession']}
        Investment Interest: {user['investment']}

        Spending Data:
        {summary}

        User Question:
        {query}

        Give practical advice with reasoning.
        """

        # The new method for calling the model
        # The updated method
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt
        )

        return response.text

    except Exception as e:
        print("Gemini Error:", e)
        return "⚠️ AI service unavailable. Try again."