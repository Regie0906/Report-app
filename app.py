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

COUNCILS = [
    "ICSSC - Institute of Computer Studies Student Council",
    "SSC - Supreme Student Council",
    "JPCS - Junior Philippine Computer Society",
    "ITSO - IT Society Organization",
    "Other Organization"
]

def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
            if "Council" not in df.columns:
                return pd.DataFrame(columns=["Council", "Date", "Type", "Category", "Description", "Amount"])
            return df
        except:
            return pd.DataFrame(columns=["Council", "Date", "Type", "Category", "Description", "Amount"])
    return pd.DataFrame(columns=["Council", "Date", "Type", "Category", "Description", "Amount"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

def load_archives():
    if os.path.exists(ARCHIVE_FILE):
        return pd.read_csv(ARCHIVE_FILE)
    return pd.DataFrame(columns=["Council", "Archive_Date", "Period", "Starting_Bal", "Total_Inc", "Don_Rcv", "Total_Exp", "Don_Giv", "Remaining_Bal"])

# -------------------------
# SESSION STORAGE
# -------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "manual_start_val" not in st.session_state:
    st.session_state.manual_start_val = 0.0

# -------------------------
# LOGIN PAGE
# -------------------------
if not st.session_state.logged_in:
    st.title("Council Finance Login")
    selected_council = st.selectbox("Select Council / Organization", COUNCILS)
    if st.button("Login"):
        st.session_state.logged_in = True
        st.session_state.current_user = selected_council
        st.rerun()
else:
    # -------------------------
    # AUTHENTICATED APP
    # -------------------------
    st.sidebar.title(f"👤 {st.session_state.current_user}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()

    menu = st.sidebar.radio("Navigation", ["Monthly Ledger", "Balance Sheet", "Archived Reports", "About"])

    full_df = load_data()
    user_df = full_df[full_df["Council"] == st.session_state.current_user].copy()
    user_df["Amount"] = pd.to_numeric(user_df["Amount"], errors='coerce').fillna(0)

    if menu == "Monthly Ledger":
        st.title(f"Financial Report: {st.session_state.current_user}")
        
        col_m, col_y, col_s = st.columns([1, 1, 1])
        with col_m:
            month_selected = st.selectbox("Select Month", range(1, 13), 
                                          index=datetime.now().month - 1,
                                          format_func=lambda x: datetime(2026, x, 1).strftime('%B'))
        with col_y:
            year_selected = st.number_input("Year", value=2026)
        
        with col_s:
            # Auto-populated from carry-over, but still editable
            st_bal = st.number_input("Starting Balance (₱)", value=float(st.session_state.manual_start_val))
            st.session_state.manual_start_val = st_bal

        st.session_state.current_period = f"{datetime(2026, month_selected, 1).strftime('%B')} {year_selected}"

        this_month_df = user_df[(user_df["Date"].dt.month == month_selected) & 
                                (user_df["Date"].dt.year == year_selected)]
        
        curr_inc = this_month_df[this_month_df["Type"] == "Income"]["Amount"].sum()
        curr_don_from = this_month_df[this_month_df["Type"] == "Donation (From)"]["Amount"].sum()
        curr_don_to = this_month_df[this_month_df["Type"] == "Donation (To)"]["Amount"].sum()
        curr_exp = this_month_df[this_month_df["Type"] == "Expense"]["Amount"].sum()
        
        rem_bal = st_bal + curr_inc + curr_don_from - curr_exp - curr_don_to

        st.subheader(f"Financial Activity for {st.session_state.current_period}")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("STARTING BALANCE", f"₱ {st_bal:,.2f}")
        m2.metric("EXPENSES", f"₱ {(curr_exp + curr_don_to):,.2f}")
        m3.metric("DONATIONS RECEIVED", f"₱ {curr_don_from:,.2f}")
        m4.metric("REMAINING BALANCE", f"₱ {rem_bal:,.2f}")

        st.divider()

        # TRANSACTION MANAGEMENT
        st.subheader("Manage Records")
        if not this_month_df.empty:
            # Selection box to choose a specific item
            selected_item_idx = st.selectbox(
                "Select a record item to manage:", 
                options=this_month_df.index.tolist(),
                format_func=lambda x: f"{this_month_df.loc[x, 'Date'].strftime('%Y-%m-%d')} | {this_month_df.loc[x, 'Type']} | {this_month_df.loc[x, 'Description']} (₱{this_month_df.loc[x, 'Amount']:,.2f})"
            )
            
            act1, act2, _ = st.columns([1, 1, 2])
            with act1:
                if st.button("🗑️ Delete Selected"):
                    save_data(full_df.drop(selected_item_idx))
                    st.success("Record deleted.")
                    st.rerun()
            with act2:
                if st.button("📥 Archive Selected"):
                    # Individual archive logic could go here, for now it confirms index
                    st.info("Item flagged for archive. Use Balance Sheet for full period saving.")

            st.dataframe(this_month_df[["Date", "Type", "Category", "Description", "Amount"]], use_container_width=True)
        else:
            st.info("No records for this period.")

        with st.expander("➕ Add New Transaction"):
            c1, c2, c3 = st.columns(3)
            with c1: t_date = st.date_input("Date")
            with c2: t_type = st.selectbox("Type", ["Income", "Expense", "Donation (From)", "Donation (To)"])
            with c3: category = st.text_input("Category")
            desc = st.text_input("Description")
            amt_val = st.number_input("Amount (₱)", min_value=0.0, step=100.0)

            if st.button("Add Entry"):
                new_row = pd.DataFrame([{
                    "Council": st.session_state.current_user,
                    "Date": t_date,
                    "Type": t_type,
                    "Category": category,
                    "Description": desc,
                    "Amount": amt_val
                }])
                save_data(pd.concat([load_data(), new_row], ignore_index=True))
                st.success("Entry Saved!")
                st.rerun()

    elif menu == "Balance Sheet":
        st.title("Financial Summary")
        st_bal_sheet = st.session_state.get('manual_start_val', 0.0)
        current_period = st.session_state.get('current_period', "Current Month")
        
        all_inc = user_df[user_df["Type"] == "Income"]["Amount"].sum()
        all_don_f = user_df[user_df["Type"] == "Donation (From)"]["Amount"].sum()
        all_don_t = user_df[user_df["Type"] == "Donation (To)"]["Amount"].sum()
        all_exp = user_df[user_df["Type"] == "Expense"]["Amount"].sum()
        
        final_bal = st_bal_sheet + all_inc + all_don_f - all_exp - all_don_t

        st.code(f"""
{st.session_state.current_user}
PERIOD: {current_period}
--------------------------------------------------
STARTING BALANCE:                ₱ {st_bal_sheet:,.2f}
--------------------------------------------------
(+) TOTAL INCOME:                ₱ {all_inc:,.2f}
(+) DONATIONS (RECEIVED):        ₱ {all_don_f:,.2f}
(-) TOTAL EXPENSES:              ₱ {all_exp:,.2f}
(-) DONATIONS (GIVEN OUT):       ₱ {all_don_t:,.2f}
--------------------------------------------------
REMAINING BALANCE:               ₱ {final_bal:,.2f}
--------------------------------------------------
        """)

        if st.button("💾 Finalize & Save Report (Carry Over Balance)"):
            # 1. Archive the summary
            archive_row = pd.DataFrame([{
                "Council": st.session_state.current_user,
                "Archive_Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Period": current_period,
                "Starting_Bal": st_bal_sheet,
                "Total_Inc": all_inc,
                "Don_Rcv": all_don_f,
                "Total_Exp": all_exp,
                "Don_Giv": all_don_t,
                "Remaining_Bal": final_bal
            }])
            df_arch = load_archives()
            pd.concat([df_arch, archive_row], ignore_index=True).to_csv(ARCHIVE_FILE, index=False)
            
            # 2. CLEAR the current ledger for this council
            remaining_data = full_df[full_df["Council"] != st.session_state.current_user]
            save_data(remaining_data)
            
            # 3. SET Carry-over balance
            st.session_state.manual_start_val = final_bal
            
            st.success(f"Report finalized! {final_bal:,.2f} carried over as new Starting Balance.")
            st.balloons()

    elif menu == "Archived Reports":
        st.title("📁 Saved Reports")
        archives = load_archives()
        user_archives = archives[archives["Council"] == st.session_state.current_user]
        if not user_archives.empty:
            st.dataframe(user_archives.drop(columns=["Council"]), use_container_width=True)
        else:
            st.info("No archives found.")

    elif menu == "About":
        st.title("About")
        st.info("Finance System with Period Closing and Balance Carry-over.")
