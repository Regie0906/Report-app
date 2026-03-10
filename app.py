import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Student Council Finance Tracker", layout="wide")

# -------------------------
# DATABASE / CONFIG
# -------------------------
DB_FILE = "finance_data.csv"
ARCHIVE_FILE = "archived_reports.csv"

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

def load_archives():
    if os.path.exists(ARCHIVE_FILE):
        return pd.read_csv(ARCHIVE_FILE)
    return pd.DataFrame(columns=["Council", "Archive_Date", "Period", "Starting_Bal", "Total_Inc", "Don_Rcv", "Total_Exp", "Don_Giv", "Remaining_Bal"])

def save_archive(archive_row):
    df = load_archives()
    df = pd.concat([df, archive_row], ignore_index=True)
    df.to_csv(ARCHIVE_FILE, index=False)

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

    menu = st.sidebar.radio("Navigation", ["Monthly Ledger", "Balance Sheet", "Archived Reports", "About"])

    full_df = load_data()
    user_df = full_df[full_df["Council"] == st.session_state.current_user].copy()
    user_df["Amount"] = pd.to_numeric(user_df["Amount"], errors='coerce').fillna(0)

    if menu == "Monthly Ledger":
        st.title(f"📒 Ledger: {st.session_state.current_user}")
        
        col_m, col_y, col_s = st.columns([1, 1, 1])
        with col_m:
            month_selected = st.selectbox("Select Month", range(1, 13), 
                                          index=datetime.now().month - 1,
                                          format_func=lambda x: datetime(2026, x, 1).strftime('%B'))
        with col_y:
            year_selected = st.number_input("Year", value=2026)
        
        with col_s:
            start_input = st.text_input("Enter Starting Balance (₱)", "0")
            try:
                st_bal = float(start_input.replace(",", ""))
            except:
                st_bal = 0.0

        st.session_state.manual_start_val = st_bal
        st.session_state.current_period = f"{datetime(2026, month_selected, 1).strftime('%B')} {year_selected}"

        # Filter current month
        this_month_df = user_df[(user_df["Date"].dt.month == month_selected) & 
                                (user_
