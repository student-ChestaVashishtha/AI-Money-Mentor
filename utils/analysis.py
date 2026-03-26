import pandas as pd

def categorize(desc, amount):
    desc = str(desc).lower()
    
    if any(word in desc for word in ["zomato", "swiggy", "food", "restaurant"]):
        return "Food"
    elif any(word in desc for word in ["amazon", "flipkart", "myntra"]):
        return "Shopping"
    elif "rent" in desc:
        return "Housing"
    elif "atm" in desc or "cash" in desc:
        return "Cash"
    elif any(word in desc for word in ["uber", "ola", "irctc"]):
        return "Transport"
    
    if amount < 2000:
        return "Grocery"
    
    return "Other"

def analyze_data(df):
    # Fallback if CSV format is unexpected
    if "Description" not in df.columns or "Amount" not in df.columns:
        return {"Error": 0}
        
    df["Category"] = df.apply(
        lambda x: categorize(x["Description"], abs(x["Amount"])), axis=1
    )
    
    # Convert to a standard dictionary
    summary_dict = df.groupby("Category")["Amount"].sum().abs().to_dict()
    return summary_dict

def detect_patterns(summary):
    patterns = []
    
    if summary.get("Shopping", 0) > 5000:
        patterns.append("⚠️ Frequent shopping detected. Consider a 30-day wait rule.")
    
    if summary.get("Food", 0) > 3000:
        patterns.append("⚠️ High food delivery spending. Meal prepping could save you ₹2k+ a month.")
    
    if summary.get("Cash", 0) > 5000:
        patterns.append("⚠️ High untracked cash usage. Try shifting to UPI for better tracking.")
        
    if not patterns and summary:
         patterns.append("✅ Great job! Your spending looks balanced and healthy.")
    
    return patterns