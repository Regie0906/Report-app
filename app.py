import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Student Council Finance Tracker", layout="wide")


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "reports" not in st.session_state:
    st.session_state.reports = {}
if "transactions" not in st.session_state:
    # Ensure Date is datetime type from the start
    st.session_state.transactions = pd.DataFrame(
        columns=["Council", "Date", "Type", "Category", "Description", "Amount"]
    )

COUNCILS = [
    "ICSSC - Institute of Computer Studies Student Council",
    "SSC - Supreme Student Council",
    "PCSSC - Pasig Central Student Council",
    "MCSSC - Mandaluyong Central Student Council",
    "Other Organization"
]

def calculate_balance(df):
    """Calculates net balance from a dataframe of transactions"""
    inc = df[df["Type"].isin(["Income", "Donation (From)"])]["Amount"].sum()
    exp = df[df["Type"].isin(["Expense", "Donation (To)"])]["Amount"].sum()
    return inc - exp

if not st.session_state.logged_in:
    st.title("Council Finance Login")
    selected_council = st.selectbox("Select Council / Organization", ["-- Choose One --"] + COUNCILS)
    
    if st.button("Login"):
        if selected_council != "-- Choose One --":
            st.session_state.logged_in = True
            st.session_state.current_user = selected_council
            st.rerun()
        else:
            st.warning("Please select a council before logging in.")
else:

    st.sidebar.title(f"👤 {st.session_state.current_user}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()

    menu = st.sidebar.radio("Navigation", ["Financial Report", "Balance Sheet", "Saved Reports", "About"])

    # Source of Data
    full_df = st.session_state.transactions.copy()
    full_df["Date"] = pd.to_datetime(full_df["Date"])
    user_df = full_df[full_df["Council"] == st.session_state.current_user].copy()
    user_df["Amount"] = pd.to_numeric(user_df["Amount"], errors='coerce').fillna(0)

    if menu == "Financial Report":
        st.title(f"Financial Report: {st.session_state.current_user}")
        
        col_m, col_y = st.columns(2)
        with col_m:
            month_selected = st.selectbox("Select Month", range(1, 13), 
                                          index=datetime.now().month - 1,
                                          format_func=lambda x: datetime(2026, x, 1).strftime('%B'))
        with col_y:
            year_selected = st.number_input("Year", value=2026)

        st.session_state.current_period = f"{datetime(2026, month_selected, 1).strftime('%B')} {year_selected}"

        
        first_day_of_month = datetime(year_selected, month_selected, 1)
        past_df = user_df[user_df["Date"] < first_day_of_month]
        auto_start_bal = calculate_balance(past_df)

        this_month_df = user_df[(user_df["Date"].dt.month == month_selected) & (user_df["Date"].dt.year == year_selected)]

        curr_exp = this_month_df[this_month_df["Type"] == "Expense"]["Amount"].sum()
        curr_inc = this_month_df[this_month_df["Type"] == "Income"]["Amount"].sum()
        curr_don_f = this_month_df[this_month_df["Type"] == "Donation (From)"]["Amount"].sum()
        curr_don_t = this_month_df[this_month_df["Type"] == "Donation (To)"]["Amount"].sum()
        
        
        rem_bal = auto_start_bal + curr_inc + curr_don_f - curr_exp - curr_don_t

        st.subheader(f"Report for the Month of {st.session_state.current_period}")
        m1, m2, m3 = st.columns(3)
        m1.metric("TOTAL EXPENSES", f"₱ {(curr_exp + curr_don_t):,.2f}", delta_color="inverse")
        m2.metric("TOTAL INCOME", f"₱ {(curr_inc + curr_don_f):,.2f}")
        m3.metric("ENDING BALANCE", f"₱ {rem_bal:,.2f}")

        st.divider()

        st.subheader("➕ Add New Transaction")
        with st.container(border=True):
            c1, c2, c3 = st.columns(3)
            with c1: t_date = st.date_input("Date")
            with c2: t_type = st.selectbox("Type", ["Expense", "Income", "Donation (From)", "Donation (To)"])
            with c3: category = st.text_input("Category")
            desc = st.text_input("Description")
            amt_val = st.number_input("Amount (₱)", min_value=0.0, step=100.0)

            if st.button("Add Entry"):
                new_row = pd.DataFrame([{
                    "Council": st.session_state.current_user,
                    "Date": pd.to_datetime(t_date), 
                    "Type": t_type, 
                    "Category": category, 
                    "Description": desc, 
                    "Amount": amt_val
                }])
                st.session_state.transactions = pd.concat([st.session_state.transactions, new_row], ignore_index=True)
                st.success("Entry Saved!")
                st.rerun()

        st.subheader("History")

        edited_ledger = st.data_editor(user_df, num_rows="dynamic", use_container_width=True, key="main_ledger")
        if st.button("Save Changes"):
            other_councils = full_df[full_df["Council"] != st.session_state.current_user]
            edited_ledger["Council"] = st.session_state.current_user
            st.session_state.transactions = pd.concat([other_councils, edited_ledger], ignore_index=True)
            st.success("Ledger Updated!")
            st.rerun()

    elif menu == "Balance Sheet":
        st.title("Financial Records")

        
        all_exp = user_df[user_df["Type"] == "Expense"]["Amount"].sum()
        all_inc = user_df[user_df["Type"] == "Income"]["Amount"].sum()
        all_don_f = user_df[user_df["Type"] == "Donation (From)"]["Amount"].sum()
        all_don_t = user_df[user_df["Type"] == "Donation (To)"]["Amount"].sum()
        
        final_bal = all_inc + all_don_f - all_exp - all_don_t

        col_left, col_right = st.columns([1, 1])
        with col_left:
            st.subheader("Summary")
            st.code(f"""
{st.session_state.current_user}
AS OF: {datetime.now().strftime('%B %d, %Y')}
--------------------------------------------------
(-) TOTAL EXPENSES:              ₱ {all_exp:,.2f}
(+) TOTAL INCOME:                ₱ {all_inc:,.2f}
(+) DONATIONS (RECEIVED):        ₱ {all_don_f:,.2f}
(-) DONATIONS (GIVEN OUT):       ₱ {all_don_t:,.2f}
--------------------------------------------------
CASH ON HAND:                    ₱ {final_bal:,.2f}
--------------------------------------------------
            """)

        with col_right:
            st.subheader("Financial Flow")
            if not user_df.empty:
                chart_df = user_df.copy().sort_values("Date")
                chart_df['Impact'] = chart_df.apply(
                    lambda x: x['Amount'] if x['Type'] in ["Income", "Donation (From)"] 
                    else -x['Amount'], axis=1
                )
                chart_df['Running Balance'] = chart_df['Impact'].cumsum()
                st.line_chart(chart_df.set_index('Date')['Running Balance'])
            else:
                st.info("No data to display.")

    elif menu == "Saved Reports":
        st.title("📁 Your Saved Reports")

        user_reports = {k: v for k, v in st.session_state.reports.items() if k.startswith(st.session_state.current_user)}
        if user_reports:
            for key, data in user_reports.items():
                label = key.split('_')[1]
                with st.expander(f"Archived Report: {label}"):
                    st.dataframe(data, use_container_width=True)
        else:
            st.info("No saved reports found.")

    elif menu == "About":

        st.title("About")
        st.info("Finance Tracker: Automated Ledger and Cumulative Balance logic.")

        
        st.markdown("""
        ### Student Council Financial Reports Tracker

        The **Student Council Financial Reports Tracker** is a digital tool designed to help student councils and organizations efficiently record, monitor, and manage their financial activities. This application simplifies the process of tracking income, expenses, and financial balances while automatically generating organized financial reports.

        ### Key Features
        • Record monthly income and expenses  
        • Automatic calculation of balances and totals  
        • Editable transaction ledger  
        • Financial statement generation  
        • Multi-organization tracking  
        • Organized monthly financial reports  

        ### Purpose
        This application was developed to support **student leaders, treasurers, and council officers** in managing their finances more efficiently and responsibly. It promotes proper financial documentation, transparency, and accountability within student organizations.

        ### Developer
        This application was created as a financial management tool to assist student councils in preparing clear and accurate financial reports for their activities and projects.
        """)
