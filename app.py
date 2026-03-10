import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Student Council Finance Tracker", layout="wide")

# -------------------------
# SESSION STORAGE INITIALIZATION
# -------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "reports" not in st.session_state:
    st.session_state.reports = {}
if "manual_start_val" not in st.session_state:
    st.session_state.manual_start_val = 0.0
if "transactions" not in st.session_state:
    st.session_state.transactions = pd.DataFrame(
        columns=["Council", "Date", "Type", "Category", "Description", "Amount"]
    )

COUNCILS = [
    "ICSSC - Institute of Computer Studies Student Council",
    "SSC - Supreme Student Council",
    "JPCS - Junior Philippine Computer Society",
    "ITSO - IT Society Organization",
    "Other Organization"
]

# -------------------------
# LOGIN PAGE
# -------------------------
if not st.session_state.logged_in:
    st.title("🔐 Council Finance Login")
    selected_council = st.selectbox("Select Council / Organization", ["-- Choose One --"] + COUNCILS)
    
    if st.button("Login"):
        if selected_council != "-- Choose One --":
            st.session_state.logged_in = True
            st.session_state.current_user = selected_council
            st.rerun()
        else:
            st.warning("Please select a council before logging in.")
else:
    # -------------------------
    # AUTHENTICATED APP
    # -------------------------
    st.sidebar.title(f"👤 {st.session_state.current_user}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()

    menu = st.sidebar.radio("Navigation", ["Monthly Ledger", "Balance Sheet", "Saved Reports", "About"])

    full_df = st.session_state.transactions
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
            st_bal = st.number_input("Starting Balance (₱)", value=float(st.session_state.manual_start_val))
            st.session_state.manual_start_val = st_bal

        st.session_state.current_period = f"{datetime(2026, month_selected, 1).strftime('%B')} {year_selected}"

        # Filtering data
        user_df["Date"] = pd.to_datetime(user_df["Date"], errors='coerce')
        this_month_df = user_df[(user_df["Date"].dt.month == month_selected) & (user_df["Date"].dt.year == year_selected)]
        
        curr_inc = this_month_df[this_month_df["Type"] == "Income"]["Amount"].sum()
        curr_don_f = this_month_df[this_month_df["Type"] == "Donation (From)"]["Amount"].sum()
        curr_don_t = this_month_df[this_month_df["Type"] == "Donation (To)"]["Amount"].sum()
        curr_exp = this_month_df[this_month_df["Type"] == "Expense"]["Amount"].sum()
        rem_bal = st_bal + curr_inc + curr_don_f - curr_exp - curr_don_t

        st.subheader(f"Financial Activity for {st.session_state.current_period}")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("STARTING BALANCE", f"₱ {st_bal:,.2f}")
        m2.metric("EXPENSES", f"₱ {(curr_exp + curr_don_t):,.2f}")
        m3.metric("INCOME/DONATIONS", f"₱ {(curr_inc + curr_don_f):,.2f}")
        m4.metric("REMAINING BALANCE", f"₱ {rem_bal:,.2f}")

        st.divider()

        st.subheader("➕ Add New Transaction")
        with st.container(border=True):
            c1, c2, c3 = st.columns(3)
            with c1: t_date = st.date_input("Date")
            with c2: t_type = st.selectbox("Type", ["Income", "Expense", "Donation (From)", "Donation (To)"])
            with c3: category = st.text_input("Category")
            desc = st.text_input("Description")
            amt_val = st.number_input("Amount (₱)", min_value=0.0, step=100.0)

            if st.button("Add Entry"):
                new_row = pd.DataFrame([{
                    "Council": st.session_state.current_user,
                    "Date": t_date, "Type": t_type, "Category": category, 
                    "Description": desc, "Amount": amt_val
                }])
                st.session_state.transactions = pd.concat([st.session_state.transactions, new_row], ignore_index=True)
                st.success("Entry Saved!")
                st.rerun()

        st.subheader("📊 Ledger Table")
        edited_ledger = st.data_editor(user_df, num_rows="dynamic", use_container_width=True, key="main_ledger")
        if st.button("Save Changes to Ledger"):
            other_councils = full_df[full_df["Council"] != st.session_state.current_user]
            edited_ledger["Council"] = st.session_state.current_user
            st.session_state.transactions = pd.concat([other_councils, edited_ledger], ignore_index=True)
            st.success("Ledger Updated!")
            st.rerun()

    elif menu == "Balance Sheet":
        st.title("Financial Summary & Trends")
        st_bal_sheet = st.session_state.manual_start_val
        current_period = st.session_state.get('current_period', "Current Month")
        
        all_inc = user_df[user_df["Type"] == "Income"]["Amount"].sum()
        all_don_f = user_df[user_df["Type"] == "Donation (From)"]["Amount"].sum()
        all_don_t = user_df[user_df["Type"] == "Donation (To)"]["Amount"].sum()
        all_exp = user_df[user_df["Type"] == "Expense"]["Amount"].sum()
        final_bal = st_bal_sheet + all_inc + all_don_f - all_exp - all_don_t

        col_left, col_right = st.columns([1, 1])
        with col_left:
            st.subheader("Balance Summary")
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

        with col_right:
            st.subheader("Balance Trend Line")
            if not user_df.empty:
                chart_df = user_df.copy().sort_values("Date")
                chart_df['Impact'] = chart_df.apply(
                    lambda x: x['Amount'] if x['Type'] in ["Income", "Donation (From)"] 
                    else -x['Amount'], axis=1
                )
                chart_df['Current Balance'] = st_bal_sheet + chart_df['Impact'].cumsum()
                st.line_chart(chart_df.set_index('Date')['Current Balance'])
            else:
                st.info("No data for trend chart.")

        if st.button("💾 Finalize & Save Report"):
            archive_key = f"{st.session_state.current_user}_{current_period}_{datetime.now().strftime('%H%M%S')}"
            st.session_state.reports[archive_key] = user_df.copy()
            st.session_state.transactions = full_df[full_df["Council"] != st.session_state.current_user]
            st.session_state.manual_start_val = final_bal
            st.success(f"Report finalized! ₱{final_bal:,.2f} carried forward.")
            st.rerun()

    elif menu == "Saved Reports":
        st.title("📁 Your Archived Reports")
        st.info("You can edit archived reports here just like the Monthly Ledger.")
        
        user_reports = {k: v for k, v in st.session_state.reports.items() if k.startswith(st.session_state.current_user)}
        
        if user_reports:
            for key, data in user_reports.items():
                label = key.split('_')[1]
                with st.expander(f"Archived Report: {label}"):
                    # Same function as ledger table: dynamic editing
                    edited_archived_df = st.data_editor(data, num_rows="dynamic", use_container_width=True, key=f"editor_{key}")
                    
                    col_edit, col_del = st.columns([1, 1])
                    with col_edit:
                        if st.button("Update Archived Report", key=f"btn_save_{key}"):
                            st.session_state.reports[key] = edited_archived_df
                            st.success("Archive updated successfully!")
                            st.rerun()
                    with col_del:
                        if st.button("🗑️ Delete This Report", key=f"btn_del_{key}"):
                            del st.session_state.reports[key]
                            st.warning("Report deleted.")
                            st.rerun()
        else:
            st.info("No saved reports found.")

    elif menu == "About":
        st.title("About")
        st.info("Finance Tracker with Dynamic Ledger & Editable Archives.")
