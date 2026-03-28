import pandas as pd
import re

# ==========================================
# 1. SMART CATEGORY DETECTION
# ==========================================
def categorize_transaction(desc):
    desc = str(desc).lower()

    if re.search(r'zomato|swiggy|blinkit|zepto|instamart|restaurant|cafe|food|grocery|mart', desc):
        return 'Food & Dining'

    if re.search(r'amazon|flipkart|myntra|meesho|ajio|shopping|mall|store', desc):
        return 'Shopping'

    if re.search(r'uber|ola|rapido|irctc|train|fuel|petrol|toll|fastag', desc):
        return 'Transport'

    if re.search(r'rent|electricity|power|water|gas|wifi|broadband|jio|airtel|bsnl|recharge', desc):
        return 'Housing & Utilities'

    if re.search(r'school|college|univ|fee|exam|tuition|academy', desc):
        return 'Education'

    if re.search(r'atm|cash|withdrawal|wdl', desc):
        return 'Cash Withdrawal'

    if re.search(r'netflix|spotify|prime|hotstar|movie|pvr', desc):
        return 'Entertainment'

    if re.search(r'hospital|clinic|pharmacy|doctor|apollo', desc):
        return 'Healthcare'

    if re.search(r'upi|gpay|paytm|phonepe|cred', desc):
        return 'UPI Transfers'

    return 'Miscellaneous'


def extract_merchant_name(desc):
    desc = str(desc).lower()
    match = re.search(r'upi/([^@/]+)', desc)
    if match:
        merchant = match.group(1).strip()
        if merchant.isdigit():
            return "Personal Transfer"
        return merchant.capitalize()
    return "Miscellaneous"


# ==========================================
# 2. FILTER LAST 3 MONTHS
# ==========================================
def filter_last_3_months(df):
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce', dayfirst=True)
        df = df.dropna(subset=['Date'])

        df['Month_Key'] = df['Date'].dt.strftime('%Y-%m')
        recent_months = sorted(df['Month_Key'].unique())[-3:]
        return df[df['Month_Key'].isin(recent_months)].copy()

    return df.copy()


# ==========================================
# 3. MAIN ANALYSIS
# ==========================================
def analyze_data(df):
    df.columns = df.columns.str.strip()
    df = filter_last_3_months(df)

    df['Amount'] = pd.to_numeric(
        df['Amount'].astype(str).str.replace(r'[^\d.-]', '', regex=True),
        errors='coerce'
    ).fillna(0)

    if 'Type' in df.columns:
        expenses = df[df['Type'].str.lower() == 'debit'].copy()
    else:
        expenses = df[df['Amount'] < 0].copy()
        expenses['Amount'] = expenses['Amount'].abs()

    expenses['Category'] = expenses['Description'].apply(categorize_transaction)

    summary = expenses.groupby('Category')['Amount'].sum()
    total = summary.sum()

    percentage_summary = {}
    if total > 0:
        for k, v in summary.items():
            percentage_summary[k] = round((v / total) * 100, 1)

    return dict(sorted(percentage_summary.items(), key=lambda x: x[1], reverse=True))


# ==========================================
# 4. ADVANCED PATTERN DETECTION
# ==========================================
def detect_patterns(df, summary):
    patterns = []

    df.columns = df.columns.str.strip()
    df = filter_last_3_months(df)

    df['Amount'] = pd.to_numeric(
        df['Amount'].astype(str).str.replace(r'[^\d.-]', '', regex=True),
        errors='coerce'
    ).fillna(0)

    if 'Type' in df.columns:
        expenses = df[df['Type'].str.lower() == 'debit'].copy()
        income = df[df['Type'].str.lower() == 'credit'].copy()
    else:
        expenses = df[df['Amount'] < 0].copy()
        expenses['Amount'] = expenses['Amount'].abs()
        income = df[df['Amount'] > 0].copy()

    # =========================
    # CORE FINANCIAL MATH
    # =========================
    total_income = income['Amount'].sum()
    total_expense = expenses['Amount'].sum()
    net = total_income - total_expense

    patterns.append(
        f"📊 EXACT MATH: Income ₹{total_income:,.0f} | Expense ₹{total_expense:,.0f} | Net ₹{net:,.0f}"
    )

    # =========================
    # SAVINGS RATE
    # =========================
    if total_income > 0:
        savings_rate = (net / total_income) * 100

        if savings_rate < 10:
            patterns.append(f"⚠️ Low savings rate: {savings_rate:.1f}%")
        elif savings_rate > 30:
            patterns.append(f"🌟 Excellent savings rate: {savings_rate:.1f}%")

    # =========================
    # COST LEAKAGE DETECTION
    # =========================
    for cat, pct in summary.items():
        if pct > 40:
            patterns.append(f"💸 Cost Leakage: {cat} is {pct}% of your expenses")

    # =========================
    # 50-30-20 RULE CHECK
    # =========================
    needs = summary.get('Housing & Utilities', 0)
    wants = summary.get('Food & Dining', 0) + summary.get('Entertainment', 0)

    if needs > 50:
        patterns.append("⚠️ Needs exceed 50% (financial stress risk)")

    if wants > 30:
        patterns.append("⚠️ Wants exceed 30% (lifestyle inflation)")

    # =========================
    # ANOMALY DETECTION
    # =========================
    avg = expenses['Amount'].mean()
    for amt in expenses['Amount']:
        if amt > 3 * avg:
            patterns.append(f"🚨 Unusual high expense detected: ₹{amt:,.0f}")

    # =========================
    # TOP CATEGORY
    # =========================
    if summary:
        top_cat = max(summary, key=summary.get)
        patterns.append(f"🔎 Highest spending category: {top_cat} ({summary[top_cat]}%)")

    # =========================
    # MERCHANT HABITS
    # =========================
    expenses['Merchant'] = expenses['Description'].apply(extract_merchant_name)

    merchant_stats = expenses.groupby('Merchant')['Amount'].agg(['count', 'sum'])

    for merchant, row in merchant_stats.iterrows():
        if merchant not in ["Miscellaneous", "Personal Transfer"]:
            if row['count'] >= 3 and row['sum'] > 1000:
                patterns.append(
                    f"🔁 Habit: {merchant} used {row['count']} times (₹{row['sum']:,.0f})"
                )

    return patterns