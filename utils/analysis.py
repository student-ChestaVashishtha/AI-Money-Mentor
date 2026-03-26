def categorize(desc, amount):
    desc = str(desc).lower()
    
    if "zomato" in desc or "swiggy" in desc:
        return "Food"
    elif "amazon" in desc or "flipkart" in desc:
        return "Shopping"
    elif "rent" in desc:
        return "Housing"
    elif "atm" in desc:
        return "Cash"
    
    if amount < 2000:
        return "Grocery"
    
    return "Other"


def analyze_data(df):
    df["Category"] = df.apply(
        lambda x: categorize(x["Description"], abs(x["Amount"])), axis=1
    )
    
    return df.groupby("Category")["Amount"].sum().abs()


def detect_patterns(summary):
    patterns = []
    
    if summary.get("Shopping", 0) > 5000:
        patterns.append("⚠️ Frequent shopping detected")
    
    if summary.get("Food", 0) > 3000:
        patterns.append("⚠️ High food spending")
    
    if summary.get("Cash", 0) > 5000:
        patterns.append("⚠️ High cash usage")
    
    return patterns