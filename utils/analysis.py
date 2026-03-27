import pandas as pd
import re

def extract_dynamic_category(desc, custom_rules=None):
    if custom_rules is None:
        custom_rules = {}
        
    desc = str(desc).lower()
    
    # NEW: Check the user's custom rules first!
    # E.g., if custom_rules = {"jio": "Wifi & Internet"}
    for original_merchant, new_category in custom_rules.items():
        if original_merchant.lower() in desc:
            return new_category

    # ... [The rest of your extraction logic stays exactly the same] ...
    
    # Explicitly catch recharges
    if 'recharge' in desc or 'prepaid' in desc:
        return "Mobile/Wifi Recharge"
        
    # Look for specific major brands first to ensure clean names
    brands = {'amazon': 'Amazon', 'swiggy': 'Swiggy', 'zomato': 'Zomato', 'flipkart': 'Flipkart', 
              'netflix': 'Netflix', 'uber': 'Uber', 'ola': 'Ola', 'myntra': 'Myntra'}
    for key, value in brands.items():
        if key in desc:
            return value

    # Look for UPI handles (Captures unique local stores and specific companies)
    upi_match = re.search(r'upi/([^@/]+)', desc)
    if upi_match:
        merchant = upi_match.group(1).strip()
        merchant = merchant.replace('pv', '').replace('servi', '').replace('retail', '').replace('direct', '')
        if merchant.isdigit():
            return "Personal Transfer"
        if len(merchant) > 2:
            return merchant.capitalize()

    # Look for ATM/Cash
    if 'cash' in desc or 'atm' in desc or 'wdl' in desc:
        return "Cash Withdrawal"

    # Grab the most unique word ignoring generic bank jargon
    generic_terms = ['bank', 'ltd', 'limited', 'upi', 'neft', 'imps', 'payment', 'from', 'ph', 'ibl', 'hdfc', 'axis', 'sbi']
    words = re.findall(r'[a-z]+', desc)
    for word in words:
        if word not in generic_terms and len(word) > 3:
            return word.capitalize()

    return "Miscellaneous"


def analyze_data(df):
    """Generates the pie chart summary."""
    df.columns = df.columns.str.strip()
    df_clean = df.copy()

    if df_clean['Amount'].dtype == object:
        df_clean['Amount'] = df_clean['Amount'].astype(str).str.replace(r'[^\d.-]', '', regex=True)
    df_clean['Amount'] = pd.to_numeric(df_clean['Amount'], errors='coerce').fillna(0)

    if 'Type' in df_clean.columns:
        expenses = df_clean[df_clean['Type'].astype(str).str.lower().str.strip() == 'debit'].copy()
    else:
        expenses = df_clean[df_clean['Amount'] < 0].copy()
        expenses['Amount'] = expenses['Amount'].abs()

    expenses['Dynamic_Category'] = expenses['Description'].apply(extract_dynamic_category)
    summary_df = expenses.groupby('Dynamic_Category')['Amount'].sum().reset_index()
    clean_summary = {row['Dynamic_Category']: round(row['Amount'], 2) for index, row in summary_df.iterrows() if row['Amount'] > 0}
    
    return dict(sorted(clean_summary.items(), key=lambda item: item[1], reverse=True))


def detect_patterns(df, summary):
    patterns = []
    df_clean = df.copy()
    df_clean.columns = df_clean.columns.str.strip()

    # --- RULE 1: Detect How Many Months of Data ---
    if 'Date' in df_clean.columns:
        # Convert to datetime and extract the Month and Year (e.g., 'Feb 2026')
        df_clean['Date'] = pd.to_datetime(df_clean['Date'], errors='coerce', dayfirst=True)
        df_clean['MonthYear'] = df_clean['Date'].dt.strftime('%b %Y')
        
        # Count unique months
        unique_months = df_clean['MonthYear'].dropna().unique()
        num_months = len(unique_months)
        
        if num_months > 0:
            months_str = ", ".join(unique_months)
            patterns.append(f"📅 Statement Scope: Analyzed {num_months} month(s) of data ({months_str}).")
    else:
        patterns.append("📅 Statement Scope: Could not detect dates.")
        unique_months = []

    # Clean the 'Amount' column
    if df_clean['Amount'].dtype == object:
        df_clean['Amount'] = df_clean['Amount'].astype(str).str.replace(r'[^\d.-]', '', regex=True)
    df_clean['Amount'] = pd.to_numeric(df_clean['Amount'], errors='coerce').fillna(0)

    # Separate Income and Expenses
    if 'Type' in df_clean.columns:
        df_clean['Norm_Type'] = df_clean['Type'].astype(str).str.lower().str.strip()
        expenses = df_clean[df_clean['Norm_Type'] == 'debit'].copy()
        income = df_clean[df_clean['Norm_Type'] == 'credit'].copy()
    else:
        expenses = df_clean[df_clean['Amount'] < 0].copy()
        expenses['Amount'] = expenses['Amount'].abs()
        income = df_clean[df_clean['Amount'] > 0].copy()

    # --- RULE 2: How many months exceeded expenditure? ---
    deficit_count = 0
    if len(unique_months) > 0 and 'MonthYear' in df_clean.columns:
        for month in unique_months:
            month_exp = expenses[expenses['MonthYear'] == month]['Amount'].sum()
            month_inc = income[income['MonthYear'] == month]['Amount'].sum()
            
            # If they spent more than they made (and they actually had expenses)
            if month_exp > month_inc and month_exp > 0:
                deficit_count += 1
                
        if deficit_count > 0:
            patterns.append(f"🚨 Deficit Alert: You exceeded your income in {deficit_count} out of the {num_months} month(s) provided.")
    
    # Apply dynamic categorization to expenses for Rule 4
    expenses['Dynamic_Category'] = expenses['Description'].apply(extract_dynamic_category)

    # --- RULE 4: Asking Questions About Repeating Behaviors ---
    
    # Behavior A: Same Amount to the Same Merchant (Fixed Commitments/EMIs)
    # We group by BOTH the merchant name and the exact amount
    recurring_transactions = expenses.groupby(['Dynamic_Category', 'Amount']).size()
    recurring_transactions = recurring_transactions[recurring_transactions >= 2]
    
    for (merchant, amount), count in recurring_transactions.items():
        if amount > 100 and merchant not in ["Cash Withdrawal", "Miscellaneous", "Personal Transfer"]:
            patterns.append(f"❓ Clarification Needed: You paid exactly ₹{amount} to '{merchant}' {count} times. Is this a recurring subscription, EMI, or regular recharge?")

    # Behavior B: High Frequency to the Same Merchant (Habits)
    merchant_counts = expenses['Dynamic_Category'].value_counts()
    frequent_merchants = merchant_counts[merchant_counts >= 3]
    
    for merchant, count in frequent_merchants.items():
        # Check if we already asked about this merchant in Behavior A to avoid repeating ourselves
        already_asked = any(merchant in p for p in patterns if "Clarification Needed" in p)
        
        if not already_asked and merchant not in ["Cash Withdrawal", "Miscellaneous", "Personal Transfer"]:
            patterns.append(f"❓ Habit Check: You made {count} separate transactions to '{merchant}' recently. Do you want to set a strict budget for this specific place?")

    # Fallback if the user is a perfect saver
    if len(patterns) <= 1:
        patterns.append("✅ Your spending is exceptionally well-distributed with no major alarming patterns.")

    return patterns