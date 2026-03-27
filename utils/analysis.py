import pandas as pd
import re

# ==========================================
# 1. FAST REGEX CATEGORIZATION (Replaces AI)
# ==========================================
# ==========================================
# 1. FAST REGEX CATEGORIZATION (Upgraded for India)
# ==========================================
def categorize_transaction(desc):
    """Instantly categorizes transactions using broad Indian keywords."""
    desc = str(desc).lower()
    
    # FOOD & GROCERY
    if re.search(r'zomato|swiggy|blinkit|zepto|instamart|pizza|food|restaurant|cafe|dairy|bakery|grocery|mart|supermarket|ration', desc): 
        return 'Food & Dining'
        
    # SHOPPING
    if re.search(r'amazon|flipkart|myntra|meesho|ajio|shopping|sneakers|clothes|apparel|store|mall', desc): 
        return 'Shopping'
        
    # TRANSPORT
    if re.search(r'uber|ola|rapido|irctc|train|commute|auto|petrol|fuel|hpcl|bpcl|indian oil|toll|fastag', desc): 
        return 'Transport'
        
    # HOUSING & UTILITIES (Added 'elec', 'power', broadband)
    if re.search(r'rent|electricity|elec|power|water|gas|wifi|broadband|jio|airtel|vi|bsnl|recharge|bill|uppcl|bescom', desc): 
        return 'Housing & Utilities'
        
    # EDUCATION (Added 'univ', 'college', 'fee')
    if re.search(r'school|univ|college|institute|physicswallah|unacademy|byju|academy|exam|tuition|nta|fee', desc): 
        return 'Education'
        
    # CASH
    if re.search(r'atm|cash|wdl|withdrawal', desc): 
        return 'Cash Withdrawal'
        
    # ENTERTAINMENT
    if re.search(r'netflix|spotify|prime|hotstar|movie|cinema|pvr|bookmyshow', desc): 
        return 'Entertainment'
        
    # HEALTHCARE
    if re.search(r'med|hospital|clinic|pharmacy|doctor|apollo|pharma', desc): 
        return 'Healthcare'
        
    # GENERIC UPI (If it doesn't match anything above, it falls here)
    if re.search(r'upi/|gpay|paytm|phonepe|bharatpe|cred', desc): 
        return 'UPI Transfers'
    
    return 'Miscellaneous'

def extract_merchant_name(desc):
    """Extracts specific merchant names for tracking habits."""
    desc = str(desc).lower()
    upi_match = re.search(r'upi/([^@/]+)', desc)
    if upi_match:
        merchant = upi_match.group(1).strip()
        merchant = merchant.replace('pv', '').replace('servi', '').replace('retail', '').replace('direct', '')
        if merchant.isdigit(): return "Personal Transfer"
        if len(merchant) > 2: return merchant.capitalize()
    return "Miscellaneous"


# ==========================================
# 2. HELPER: 3-MONTH FILTER
# ==========================================
def filter_last_3_months(df):
    """Filters the dataframe to ONLY include the 3 most recent months."""
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce', dayfirst=True)
        df_clean = df.dropna(subset=['Date']).copy()
        
        if not df_clean.empty:
            df_clean['Month_Key'] = df_clean['Date'].dt.strftime('%Y-%m')
            recent_months = sorted(df_clean['Month_Key'].unique())[-3:]
            return df_clean[df_clean['Month_Key'].isin(recent_months)].copy()
            
    return df.copy()


# ==========================================
# 3. DATA ANALYSIS (Builds Percentage Chart)
# ==========================================
def analyze_data(df, custom_rules=None):
    if custom_rules is None: custom_rules = {}

    df.columns = df.columns.str.strip()
    df_clean = filter_last_3_months(df)

    if df_clean['Amount'].dtype == object:
        df_clean['Amount'] = df_clean['Amount'].astype(str).str.replace(r'[^\d.-]', '', regex=True)
    df_clean['Amount'] = pd.to_numeric(df_clean['Amount'], errors='coerce').fillna(0)

    # Strictly grab Debits for the expense chart
    if 'Type' in df_clean.columns:
        expenses = df_clean[df_clean['Type'].astype(str).str.lower().str.strip() == 'debit'].copy()
    else:
        expenses = df_clean[df_clean['Amount'] < 0].copy()
        expenses['Amount'] = expenses['Amount'].abs()

    # Apply fast Regex Categories
    def apply_category(desc):
        desc_str = str(desc)
        # Check if user made a custom rule first
        for original_merchant, new_category in custom_rules.items():
            if original_merchant.lower() in desc_str.lower(): return new_category
        # Otherwise, use the fast regex
        return categorize_transaction(desc_str)

    expenses['Dynamic_Category'] = expenses['Description'].apply(apply_category)
    summary_df = expenses.groupby('Dynamic_Category')['Amount'].sum().reset_index()
    
    # Calculate PERCENTAGES for the chart
    total_expense = summary_df['Amount'].sum()
    percentage_summary = {}
    
    if total_expense > 0:
        for index, row in summary_df.iterrows():
            if row['Amount'] > 0:
                pct = round((row['Amount'] / total_expense) * 100, 1)
                percentage_summary[row['Dynamic_Category']] = pct
                
    return dict(sorted(percentage_summary.items(), key=lambda item: item[1], reverse=True))


# ==========================================
# 4. BEHAVIORAL PATTERN DETECTOR (MATH & INSIGHTS)
# ==========================================
def detect_patterns(df, summary, custom_rules=None):
    patterns = []
    df.columns = df.columns.str.strip()
    df_clean = filter_last_3_months(df)

    if df_clean['Amount'].dtype == object:
        df_clean['Amount'] = df_clean['Amount'].astype(str).str.replace(r'[^\d.-]', '', regex=True)
    df_clean['Amount'] = pd.to_numeric(df_clean['Amount'], errors='coerce').fillna(0)

    # 1. Scope Tracking
    if 'Date' in df_clean.columns:
        df_clean['MonthYear'] = df_clean['Date'].dt.strftime('%b %Y')
        unique_months = df_clean['MonthYear'].dropna().unique()
        num_months = len(unique_months)
        if num_months > 0:
            patterns.append(f"📅 Statement Scope: Focused analysis on your {num_months} most recent month(s) ({', '.join(unique_months)}).")
    else:
        unique_months = []
        num_months = 1

    # 2. Separate Income (Credit) and Expenses (Debit)
    if 'Type' in df_clean.columns:
        df_clean['Norm_Type'] = df_clean['Type'].astype(str).str.lower().str.strip()
        expenses = df_clean[df_clean['Norm_Type'] == 'debit'].copy()
        income = df_clean[df_clean['Norm_Type'] == 'credit'].copy()
    else:
        expenses = df_clean[df_clean['Amount'] < 0].copy()
        expenses['Amount'] = expenses['Amount'].abs()
        income = df_clean[df_clean['Amount'] > 0].copy()

    # 3. EXACT MATH CALCULATION
    total_income = income['Amount'].sum()
    total_expense = expenses['Amount'].sum()
    net_savings = total_income - total_expense
    
    patterns.append(f"📊 EXACT MATH: Total 3-Month Income = ₹{total_income:,.0f} | Total 3-Month Expense = ₹{total_expense:,.0f} | Net Savings = ₹{net_savings:,.0f}.")
    
    if net_savings < 0:
        patterns.append(f"🚨 Severe Deficit: You spent ₹{abs(net_savings):,.0f} more than you earned over this period.")
    else:
        patterns.append(f"🌟 Positive Cashflow: You successfully saved ₹{net_savings:,.0f} over this period.")

    # 4. Check for deficits per month
    deficit_months = []
    if len(unique_months) > 0 and 'MonthYear' in df_clean.columns:
        for month in unique_months:
            month_exp = expenses[expenses['MonthYear'] == month]['Amount'].sum()
            month_inc = income[income['MonthYear'] == month]['Amount'].sum()
            if month_exp > month_inc and month_exp > 0:
                deficit_months.append(month)
        if deficit_months:
            patterns.append(f"⚠️ Month-to-Month Alert: You exceeded your income specifically in: {', '.join(deficit_months)}.")

    # 5. Simple Merchant Tracking
    expenses['Merchant'] = expenses['Description'].apply(extract_merchant_name)
    merchant_stats = expenses.groupby('Merchant').agg(
        count=('Amount', 'size'),
        total_amount=('Amount', 'sum')
    ).reset_index()
    
    for index, stats in merchant_stats.iterrows():
        merchant = stats['Merchant']
        total = stats['total_amount']
        count = stats['count']
        
        if merchant in ["Cash Withdrawal", "Personal Transfer", "Miscellaneous"]: 
            continue
            
        if count >= 3 and total > 1000:
            patterns.append(f"🔁 Habit Detected: You transferred money to '{merchant}' {count} times (Total: ₹{total:,.0f}).")

    return patterns