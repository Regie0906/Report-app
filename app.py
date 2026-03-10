import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Student Council Finance Tracker", layout="wide")

# -------------------------
# DATABASE / CONFIG
# -------------------------
DB_FILE = "finance_data.csv"

COUNCIL_CREDENTIALS = {
    "ICSSC - Institute of Computer Studies Student Council": "ics123",
    "SSC - Supreme Student Council": "ssc123",
    "JPCS - Junior Philippine Computer Society": "jpcs123",
    "ITSO - IT Society Organization": "itso123",
    "Other Organization": "admin123"
}

councils = list(COUNCIL_CREDENTIALS.keys())

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Council", "Date", "Type", "Category", "Description", "Amount"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# -------------------------
# SESSION STORAGE
# -------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "transactions" not in st.session_state:
    st.session_state.transactions = load_data()

# -------------------------
# LOGIN PAGE
# -------------------------
if not st.session_state.logged_in:
    st.title("🔐 Council Finance Login")
    selected_council = st.selectbox("Select Council / Organization", councils)
    password = st.text_input("Enter Password", type="password")
    if st.button("Login"):
        if password == COUNCIL_CREDENTIALS.get(selected_council):
            st.session_state.logged_in = True
            st.session_state.current_user = selected_council
            st.rerun()
        else:
            st.error("Incorrect password.")
else:
    # -------------------------
    # AUTHENTICATED APP
    # -------------------------
    st.sidebar.title(f"👤 {st.session_state.current_user}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()

    menu = st.sidebar.radio("Navigation", ["Monthly Ledger", "Financial Statements", "About"])

    # Filter data for current user
    full_df = st.session_state.transactions
    user_df = full_df[full_df["Council"] == st.session_state.current_user].copy()
    user_df["Amount"] = pd.to_numeric(user_df["Amount"], errors='coerce').fillna(0)

    if menu == "Monthly Ledger":
        st.title(f"📒 Ledger: {st.session_state.current_user}")
        
        with st.expander("➕ Add New Transaction"):
            c1, c2, c3 = st.columns(3)
            with c1: date = st.date_input("Date")
            with c2: t_type = st.selectbox("Type", ["Income", "Expense"])
            with c3: category = st.text_input("Category (e.g., Supplies, Donation)")
            
            desc = st.text_input("Description")
            amt_in = st.text_input("Amount (PHP)", "0")

            if st.button("Save Transaction"):
                try:
                    new_row = pd.DataFrame([{
                        "Council": st.session_state.current_user,
                        "Date": str(date),
                        "Type": t_type,
                        "Category": category,
                        "Description": desc,
                        "Amount": float(amt_in.replace(",", ""))
                    }])
                    st.session_state.transactions = pd.concat([st.session_state.transactions, new_row], ignore_index=True)
                    save_data(st.session_state.transactions)
                    st.success("Saved!")
                    st.rerun()
                except: st.error("Invalid Amount")

        st.subheader("Records")
        edited_df = st.data_editor(user_df, num_rows="dynamic", use_container_width=True)
        if st.button("Sync Changes"):
            others = full_df[full_df["Council"] != st.session_state.current_user]
            st.session_state.transactions = pd.concat([others, edited_df], ignore_index=True)
            save_data(st.session_state.transactions)
            st.rerun()

    elif menu == "Financial Statements":
        st.title("📊 Financial Reports")
        report_type = st.tabs(["Income Statement", "Balance Sheet"])

        # Calculations for Reports
        total_income = user_df[user_df["Type"] == "Income"]["Amount"].sum()
        total_expense = user_df[user_df["Type"] == "Expense"]["Amount"].sum()
        net_income = total_income - total_expense

        with report_type[0]:
            st.subheader("Statement of Comprehensive Income")
            st.code(f"""
{st.session_state.current_user}
For the period ended 2025

Total Revenue:          PHP {total_income:,.2f}
Total Expenses:         PHP {total_expense:,.2f}
------------------------------------------
NET INCOME:             PHP {net_income:,.2f}
            """)

        with report_type[1]:
            st.subheader("Statement of Financial Position")
            
            # Manual inputs for balance sheet items not in ledger
            col_a, col_b = st.columns(2)
            with col_a:
                cash_coop = st.number_input("Cash on Coop (Note 2)", value=21000.0)
                supplies = st.number_input("Supplies (Note 3)", value=1000.0)
                equip_cost = st.number_input("Equipment Cost (Note 4)", value=10000.0)
            with col_b:
                useful_life = st.number_input("Useful Life (Years)", value=10)
                donations = st.number_input("Donations (Note 9)", value=0.0)

            # Logic for Note 5: Depreciation
            acc_dep = (equip_cost / useful_life) if useful_life > 0 else 0
            net_equip = equip_cost - acc_dep
            
            # Note 1: Cash on Hand (Assuming ledger tracks cash)
            cash_on_hand = net_income # Simplified: Net income represents cash flow here
            
            total_assets = cash_on_hand + cash_coop + supplies + net_equip
            total_equity = total_assets # Accounting Equation A = L + E

            st.code(f"""
{st.session_state.current_user}
STATEMENT OF FINANCIAL POSITION
As of August 2025

ASSETS
Current Assets
    Cash on Hand (Note 1)              PHP {cash_on_hand:,.2f}
    Cash on Coop (Note 2)                  {cash_coop:,.2f}
    Supplies (Note 3)                      {supplies:,.2f}
Total Current Assets                   PHP {(cash_on_hand + cash_coop + supplies):,.2f}

Noncurrent Assets
    Equipment (Note 4)                     {equip_cost:,.2f}
    Acc. Depreciation (Note 5)            ({acc_dep:,.2f})
Total Noncurrent Assets                    {net_equip:,.2f}
---------------------------------------------------------
TOTAL ASSETS                           PHP {total_assets:,.2f}

LIABILITIES AND EQUITY
Liabilities
    Accounts Payable (Note 6)              0.00
    Unearned Income (Note 7)               0.00
Total Liabilities                          0.00

Equity
    SSC Capital (Note 8)                   {total_equity - donations:,.2f}
    Donations (Note 9)                     {donations:,.2f}
Total Equity                               {total_equity:,.2f}
---------------------------------------------------------
TOTAL LIABILITIES AND EQUITY           PHP {total_assets:,.2f}
            """)

            with st.expander("View Notes to Financial Statements"):
                st.write(f"**Note 5:** Cost (PHP {equip_cost:,.2f}) / Life ({useful_life}) = PHP {acc_dep:,.2f}")
                st.write(f"**Note 8:** Calculated as Total Net Assets.")

    elif menu == "About":
        st.title("About")
        st.info("Custom Finance System for SSC. Uses Philippine Peso (PHP) formatting.")
