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
        try:
            return pd.read_csv(ARCHIVE_FILE)
        except:
            pass
    return pd.DataFrame(columns=["Council", "Archive_Date", "Period", "Starting_Bal", "Total_Inc", "Don_Rcv", "Total_Exp", "Don_Giv", "Remaining_Bal"])

def save_all_archives(df):
    df.to_csv(ARCHIVE_FILE, index=False)

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
# MAIN APP LOGIC
# -------------------------
if not st.session_state.logged_in:
    st.title("Council Finance Login")
    selected_council = st.selectbox("Select Council / Organization", COUNCILS)
    if st.button("Login"):
        st.session_state.logged_in = True
        st.session_state.current_user = selected_council
        st.rerun()
else:
    st.sidebar.title(f"👤 {st.session_state.current_user}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    menu = st.sidebar.radio("Navigation", ["Monthly Ledger", "Balance Sheet", "Archived Reports", "About"])
    
    full_df = load_data()
    user_df = full_df[full_df["Council"] == st.session_state.current_user].copy()

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
            st_bal = st.number_input("Starting Balance (₱)", value=float(st.session_state.manual_start_val))
            st.session_state.manual_start_val = st_bal

        st.session_state.current_period = f"{datetime(2026, month_selected, 1).strftime('%B')} {year_selected}"

        # 1. Calculation Section
        this_month_df = user_df[(user_df["Date"].dt.month == month_selected) & (user_df["Date"].dt.year == year_selected)].copy()
        inc_sum = this_month_df[this_month_df["Type"].isin(["Income", "Donation (From)"])]["Amount"].sum()
        exp_sum = this_month_df[this_month_df["Type"].isin(["Expense", "Donation (To)"])]["Amount"].sum()
        rem_bal = st_bal + inc_sum - exp_sum

        st.subheader(f"Activity for {st.session_state.current_period}")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("STARTING", f"₱{st_bal:,.2f}")
        m2.metric("EXPENSES", f"₱{exp_sum:,.2f}")
        m3.metric("INCOME", f"₱{inc_sum:,.2f}")
        m4.metric("REMAINING", f"₱{rem_bal:,.2f}")

        st.divider()

        # 2. Add Transaction Section
        with st.expander("➕ Add New Transaction"):
            c1, c2, c3 = st.columns(3)
            with c1: t_date = st.date_input("Date")
            with c2: t_type = st.selectbox("Type", ["Income", "Expense", "Donation (From)", "Donation (To)"])
            with c3: category = st.text_input("Category")
            desc = st.text_input("Description")
            amt_val = st.number_input("Amount (₱)", min_value=0.0)
            if st.button("Add Entry"):
                new_row = pd.DataFrame([{"Council": st.session_state.current_user, "Date": t_date, "Type": t_type, "Category": category, "Description": desc, "Amount": amt_val}])
                save_data(pd.concat([full_df, new_row], ignore_index=True))
                st.success("Transaction added!")
                st.rerun()

        # 3. Ledger/Table Section
        st.write("### Transaction History")
        st.caption("Click a row below to select it, then the delete button will appear.")

        ledger_selection = st.dataframe(
            this_month_df[["Date", "Type", "Category", "Description", "Amount"]],
            use_container_width=True,
            on_select="rerun",
            selection_mode="single_row"
        )

        if ledger_selection.selection.rows:
            selected_idx = this_month_df.index[ledger_selection.selection.rows[0]]
            if st.button("🗑️ Delete Selected Record", type="primary"):
                save_data(full_df.drop(selected_idx))
                st.rerun()

    elif menu == "Balance Sheet":
        st.title("Financial Summary")
        st_bal_sheet = st.session_state.get('manual_start_val', 0.0)
        current_period = st.session_state.get('current_period', "Current Month")
        
        inc = user_df[user_df["Type"] == "Income"]["Amount"].sum()
        don_f = user_df[user_df["Type"] == "Donation (From)"]["Amount"].sum()
        don_t = user_df[user_df["Type"] == "Donation (To)"]["Amount"].sum()
        exp = user_df[user_df["Type"] == "Expense"]["Amount"].sum()
        final_bal = st_bal_sheet + inc + don_f - exp - don_t

        st.code(f"PERIOD: {current_period}\nREMAINING BALANCE: ₱ {final_bal:,.2f}")

        if st.button("💾 Finalize & Save Report (Carry Over)"):
            archive_row = pd.DataFrame([{"Council": st.session_state.current_user, "Archive_Date": datetime.now().strftime("%Y-%m-%d"), "Period": current_period, "Starting_Bal": st_bal_sheet, "Total_Inc": inc, "Don_Rcv": don_f, "Total_Exp": exp, "Don_Giv": don_t, "Remaining_Bal": final_bal}])
            save_all_archives(pd.concat([load_archives(), archive_row], ignore_index=True))
            save_data(full_df[full_df["Council"] != st.session_state.current_user])
            st.session_state.manual_start_val = final_bal
            st.success("Report Saved and Balance Carried Over!")
            st.rerun()

    elif menu == "Archived Reports":
        st.title("📁 Saved Reports")
        all_archives = load_archives()
        user_archives = all_archives[all_archives["Council"] == st.session_state.current_user].copy()

        if not user_archives.empty:
            st.write("### Archive Management")
            st.caption("Click a row to select a report to delete.")
            
            archive_selection = st.dataframe(
                user_archives.drop(columns=["Council"]),
                use_container_width=True,
                on_select="rerun",
                selection_mode="single_row"
            )

            if archive_selection.selection.rows:
                arc_idx = user_archives.index[archive_selection.selection.rows[0]]
                report_name = user_archives.loc[arc_idx, 'Period']
                if st.button(f"🗑️ Delete Saved Report ({report_name})", type="primary"):
                    save_all_archives(all_archives.drop(arc_idx))
                    st.rerun()
        else:
            st.info("No saved reports.")

    elif menu == "About":
        st.title("About")
        st.info("Student Council Finance Tracker with Row Selection, Deletion, and Balance Carry-over.")
