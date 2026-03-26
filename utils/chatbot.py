from openai import OpenAI

client = OpenAI(api_key="YOUR_API_KEY")

def financial_chatbot(query, user, summary):

    prompt = f"""
    You are a financial advisor.

    User:
    Name: {user['name']}
    Age: {user['age']}
    Salary: ₹{user['salary']}
    Profession: {user['profession']}
    Investment Interest: {user['investment']}

    Spending:
    {summary}

    Question:
    {query}

    Give practical advice with reasoning.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a financial expert."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content