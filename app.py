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
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
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

# -------------------------
# LOGIN PAGE
# -------------------------
if not st.session_state.logged_in:
    st.title("🔐 Council Finance Login")
    selected_council = st.selectbox("Select Council / Organization", list(COUNCIL_CREDENTIALS.keys()))
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
        st.rerun()

    menu = st.sidebar.radio("Navigation", ["Monthly Ledger", "Balance Sheet", "About"])

    full_df = load_data()
    user_df = full_df[full_df["Council"] == st.session_state.current_user].copy()
    user_df["Amount"] = pd.to_numeric(user_df["Amount"], errors='coerce').fillna(0)

    if menu == "Monthly Ledger":
        st.title(f"📒 Ledger: {st.session_state.current_user}")
        
        # Selection and Editable Start
        col_m, col_y, col_s = st.columns([1, 1, 1])
        with col_m:
            month_selected = st.selectbox("Select Month", range(1, 13), 
                                          index=datetime.now().month - 1,
                                          format_func=lambda x: datetime(2026, x, 1).strftime('%B'))
        with col_y:
            year_selected = st.number_input("Year", value=2026)
        
        with col_s:
            # MANUAL STARTING BALANCE INPUT
            start_input = st.text_input("Enter Starting Balance (₱)", "0")
            try:
                # Remove commas and convert to float
                starting_balance = float(start_input.replace(",", ""))
            except:
                starting_balance = 0.0

        # --- CALCULATIONS ---
        this_month_df = user_df[(user_df["Date"].dt.month == month_selected) & 
                                (user_df["Date"].dt.year == year_selected)]
        
        curr_inc = this_month_df[this_month_df["Type"] == "Income"]["Amount"].sum()
        curr_don = this_month_df[this_month_df["Type"] == "Donation"]["Amount"].sum()
        curr_exp = this_month_df[this_month_df["Type"] == "Expense"]["Amount"].sum()
        
        # Remaining balance calculation
        remaining_balance = starting_balance + curr_inc + curr_don - curr_exp

        # Display Metrics (Formatted with .2f for automated cents)
        st.subheader(f"Financial Activity for {datetime(2026, month_selected, 1).strftime('%B %Y')}")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("STARTING BALANCE", f"₱ {starting_balance:,.2f}")
        m2.metric("EXPENSE", f"₱ {curr_exp:,.2f}")
        m3.metric("DONATION", f"₱ {curr_don:,.2f}")
        m4.metric("REMAINING BALANCE", f"₱ {remaining_balance:,.2f}")

        st.divider()

        # --- INPUT SECTION ---
        with st.expander("➕ Add New Transaction"):
            c1, c2, c3 = st.columns(3)
            with c1: t_date = st.date_input("Date")
            with c2: t_type = st.selectbox("Type", ["Income", "Expense", "Donation"])
            with c3: category = st.text_input("Category")
            
            desc = st.text_input("Description")
            amt_str = st.text_input("Amount (₱)", "0")

            if st.button("Add Entry"):
                try:
                    # Automatically ensures numeric storage
                    amt_val = float(amt_str.replace(",", ""))
                    new_row = pd.DataFrame([{
                        "Council": st.session_state.current_user,
                        "Date": t_date,
                        "Type": t_type,
                        "Category": category,
                        "Description": desc,
                        "Amount": amt_val
                    }])
                    updated_full = pd.concat([load_data(), new_row], ignore_index=True)
                    save_data(updated_full)
                    st.success(f"Recorded: ₱ {amt_val:,.2f}")
                    st.rerun()
                except: st.error("Please enter a valid amount.")

        st.divider()

        # --- HISTORY & DELETE SECTION ---
        st.subheader("Monthly Transaction History")
        if not this_month_df.empty:
            # Display history with automated cents formatting
            formatted_history = this_month_df[["Date", "Type", "Category", "Description", "Amount"]].copy()
            st.dataframe(formatted_history, use_container_width=True)
            
            with st.expander("🗑️ Delete a Transaction"):
                delete_options = this_month_df.index.tolist()
                to_delete = st.selectbox("Select Index to Delete", options=delete_options,
                                         format_func=lambda x: f"Idx {x}: {this_month_df.loc[x, 'Description']} (₱{this_month_df.loc[x, 'Amount']:,.2f})")
                if st.button("Confirm Delete", type="primary"):
                    full_df_latest = load_data()
                    full_df_latest = full_df_latest.drop(to_delete)
                    save_data(full_df_latest)
                    st.warning("Transaction deleted.")
                    st.rerun()
        else:
            st.info("No records found for the selected month.")

    elif menu == "Balance Sheet":
        st.title("📊 Financial Position Summary")
        all_inc = user_df[user_df["Type"] == "Income"]["Amount"].sum()
        all_don = user_df[user_df["Type"] == "Donation"]["Amount"].sum()
        all_exp = user_df[user_df["Type"] == "Expense"]["Amount"].sum()
        final_bal = all_inc + all_don - all_exp

        st.code(f"""
{st.session_state.current_user}
--------------------------------------------------
TOTAL INCOME:                    ₱ {all_inc:,.2f}
TOTAL DONATIONS:                 ₱ {all_don:,.2f}
TOTAL EXPENSES:                  ₱ {all_exp:,.2f}
--------------------------------------------------
REMAINING BALANCE:               ₱ {final_bal:,.2f}
--------------------------------------------------
        """)

    elif menu == "About":
        st.title("About")
        st.info("System optimized for PHP currency with automated .00 decimal formatting.")
