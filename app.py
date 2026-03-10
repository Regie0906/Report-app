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

    # Always reload fresh data from CSV to ensure carry-over is accurate
    full_df = load_data()
    # Filter for logged in council
    user_df = full_df[full_df["Council"] == st.session_state.current_user].sort_values("Date")
    user_df["Amount"] = pd.to_numeric(user_df["Amount"], errors='coerce').fillna(0)

    if menu == "Monthly Ledger":
        st.title(f"📒 Ledger: {st.session_state.current_user}")
        
        # Month/Year Selection
        col_m, col_y = st.columns(2)
        with col_m:
            month_selected = st.selectbox("Select Month", range(1, 13), 
                                          index=datetime.now().month - 1,
                                          format_func=lambda x: datetime(2025, x, 1).strftime('%B'))
        with col_y:
            year_selected = st.number_input("Year", value=2025)

        # STARTING BALANCE CALCULATION
        # Sum of everything BEFORE the first day of the selected month
        first_day_current = datetime(year_selected, month_selected, 1)
        prior_data = user_df[user_df["Date"] < pd.Timestamp(first_day_current)]
        
        prior_inc = prior_data[prior_data["Type"].isin(["Income", "Donation"])]["Amount"].sum()
        prior_exp = prior_data[prior_data["Type"] == "Expense"]["Amount"].sum()
        starting_balance = prior_inc - prior_exp # This starts at 0 if no prior data exists

        # CURRENT MONTH DATA
        this_month_df = user_df[(user_df["Date"].dt.month == month_selected) & 
                                (user_df["Date"].dt.year == year_selected)]
        
        curr_inc = this_month_df[this_month_df["Type"] == "Income"]["Amount"].sum()
        curr_don = this_month_df[this_month_df["Type"] == "Donation"]["Amount"].sum()
        curr_exp = this_month_df[this_month_df["Type"] == "Expense"]["Amount"].sum()
        
        remaining_balance = starting_balance + curr_inc + curr_don - curr_exp

        # Display Summary
        st.subheader("Summary for this Month")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("STARTING BALANCE", f"PHP {starting_balance:,.2f}")
        m2.metric("EXPENSE", f"PHP {curr_exp:,.2f}")
        m3.metric("DONATION", f"PHP {curr_don:,.2f}")
        m4.metric("REMAINING BALANCE", f"PHP {remaining_balance:,.2f}")

        st.divider()

        # Add New Transaction
        with st.expander("➕ Add New Transaction (From/To)"):
            c1, c2, c3 = st.columns(3)
            with c1: t_date = st.date_input("Date")
            with c2: t_type = st.selectbox("Type", ["Income", "Expense", "Donation"])
            with c3: category = st.text_input("From / To")
            
            desc = st.text_input("Description")
            amt_in = st.text_input("Amount (PHP)", "0")

            if st.button("Add Entry"):
                try:
                    new_row = pd.DataFrame([{
                        "Council": st.session_state.current_user,
                        "Date": t_date,
                        "Type": t_type,
                        "Category": category,
                        "Description": desc,
                        "Amount": float(amt_in.replace(",", ""))
                    }])
                    updated_full = pd.concat([full_df, new_row], ignore_index=True)
                    save_data(updated_full)
                    st.success("Transaction recorded!")
                    st.rerun()
                except: st.error("Invalid amount entered.")

        st.subheader("Monthly Records")
        st.dataframe(this_month_df[["Date", "Type", "Category", "Description", "Amount"]], use_container_width=True)

    elif menu == "Balance Sheet":
        st.title("📊 Statement of Financial Position")
        
        # Calculate overall totals for the cumulative report
        all_inc = user_df[user_df["Type"] == "Income"]["Amount"].sum()
        all_don = user_df[user_df["Type"] == "Donation"]["Amount"].sum()
        all_exp = user_df[user_df["Type"] == "Expense"]["Amount"].sum()
        final_balance = all_inc + all_don - all_exp

        st.code(f"""
{st.session_state.current_user}
---------------------------------------------------------
OVERALL FINANCIAL SUMMARY
---------------------------------------------------------
STARTING BALANCE (Initial):    PHP 0.00
(+) TOTAL INCOME:              PHP {all_inc:,.2f}
(+) TOTAL DONATIONS:           PHP {all_don:,.2f}
(-) TOTAL EXPENSES:            PHP {all_exp:,.2f}
---------------------------------------------------------
REMAINING BALANCE:             PHP {final_balance:,.2f}
---------------------------------------------------------
        """)

    elif menu == "About":
        st.title("About System")
        st.write("Automatic month-to-month carry-over system enabled.")
