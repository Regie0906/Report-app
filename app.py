import streamlit as st
import pandas as pd
import os
from datetime import datetime

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

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df["Date"] = pd.to_datetime(df["Date"])
        return df
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
    selected_council = st.selectbox("Select Council", list(COUNCIL_CREDENTIALS.keys()))
    password = st.text_input("Password", type="password")
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
        st.rerun()

    menu = st.sidebar.radio("Navigation", ["Monthly Ledger", "Balance Sheet", "About"])

    # Load and Filter Data
    full_df = load_data()
    user_df = full_df[full_df["Council"] == st.session_state.current_user].sort_values("Date")

    if menu == "Monthly Ledger":
        st.title(f"📒 Ledger: {st.session_state.current_user}")
        
        # 1. Select Month for viewing/entry
        col_m, col_y = st.columns(2)
        with col_m: 
            month_selected = st.selectbox("Select Month", range(1, 13), format_func=lambda x: datetime(2025, x, 1).strftime('%B'))
        with col_y: 
            year_selected = st.number_input("Year", value=2025)

        # 2. Add New Transaction
        with st.expander("➕ Add New Entry"):
            c1, c2, c3 = st.columns(3)
            with c1: t_date = st.date_input("Transaction Date")
            with c2: t_type = st.selectbox("Type", ["Income", "Expense", "Donation"])
            with c3: category = st.text_input("From / To (Category)")
            
            desc = st.text_input("Description / Details")
            amt_in = st.text_input("Amount (PHP)", "0")

            if st.button("Save Entry"):
                try:
                    new_row = pd.DataFrame([{
                        "Council": st.session_state.current_user,
                        "Date": t_date,
                        "Type": t_type,
                        "Category": category,
                        "Description": desc,
                        "Amount": float(amt_in.replace(",", ""))
                    }])
                    full_df = pd.concat([full_df, new_row], ignore_index=True)
                    save_data(full_df)
                    st.success("Entry Saved!")
                    st.rerun()
                except: st.error("Please enter a valid amount.")

        st.divider()

        # 3. Monthly Calculations
        # STARTING BALANCE (All transactions before this month)
        first_day_current = datetime(year_selected, month_selected, 1)
        prior_df = user_df[user_df["Date"] < pd.Timestamp(first_day_current)]
        starting_balance = prior_df[prior_df["Type"].isin(["Income", "Donation"])]["Amount"].sum() - prior_df[prior_df["Type"] == "Expense"]["Amount"].sum()

        # Current Month Data
        this_month_df = user_df[(user_df["Date"].dt.month == month_selected) & (user_df["Date"].dt.year == year_selected)]
        
        expenses = this_month_df[this_month_df["Type"] == "Expense"]["Amount"].sum()
        donations = this_month_df[this_month_df["Type"] == "Donation"]["Amount"].sum()
        incomes = this_month_df[this_month_df["Type"] == "Income"]["Amount"].sum()
        
        remaining_balance = starting_balance + incomes + donations - expenses

        # Display Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("STARTING BALANCE", f"PHP {starting_balance:,.2f}")
        m2.metric("TOTAL EXPENSES", f"PHP {expenses:,.2f}")
        m3.metric("TOTAL DONATIONS", f"PHP {donations:,.2f}")
        m4.metric("REMAINING BALANCE", f"PHP {remaining_balance:,.2f}")

        st.subheader(f"Transactions for {datetime(2025, month_selected, 1).strftime('%B %Y')}")
        st.dataframe(this_month_df[["Date", "Type", "Category", "Description", "Amount"]], use_container_width=True)

    elif menu == "Balance Sheet":
        st.title("⚖️ Statement of Financial Position")
        
        # Get Latest Data for the Report
        total_donations = user_df[user_df["Type"] == "Donation"]["Amount"].sum()
        total_expense = user_df[user_df["Type"] == "Expense"]["Amount"].sum()
        total_income = user_df[user_df["Type"] == "Income"]["Amount"].sum()
        current_remaining = total_income + total_donations - total_expense

        st.code(f"""
{st.session_state.current_user}
FINANCIAL SUMMARY REPORT
---------------------------------------------------------
STARTING BALANCE (Initial):    PHP 0.00
(+) TOTAL INCOME:              PHP {total_income:,.2f}
(+) TOTAL DONATIONS:           PHP {total_donations:,.2f}
(-) TOTAL EXPENSES:            PHP {total_expense:,.2f}
---------------------------------------------------------
REMAINING BALANCE:             PHP {current_remaining:,.2f}
---------------------------------------------------------
*Note: The Remaining Balance will serve as the 
Starting Balance for the following period.
        """)

    elif menu == "About":
        st.title("System Info")
        st.write("Finance Tracker v3.0 - Auto-balancing Enabled.")
