import streamlit as st
import pandas as pd

st.set_page_config(page_title="Student Council Finance Tracker", layout="wide")

# -------------------------
# SESSION STORAGE
# -------------------------
if "reports" not in st.session_state:
    st.session_state.reports = {}

if "transactions" not in st.session_state:
    st.session_state.transactions = pd.DataFrame(
        columns=["Date","Type","Category","Description","Amount"]
    )

# -------------------------
# SIDEBAR NAVIGATION
# -------------------------
menu = st.sidebar.radio(
    "Navigation",
    [
        "Monthly Ledger",
        "Financial Statements",
        "Saved Reports",
        "About"
    ]
)

# -------------------------
# MONTHLY LEDGER
# -------------------------
if menu == "Monthly Ledger":

    st.title("📒 Student Council Monthly Finance Ledger")

    month = st.selectbox(
        "Select Month",
        [
            "January","February","March","April",
            "May","June","July","August",
            "September","October","November","December"
        ]
    )

    starting_balance = st.number_input(
        "Starting Balance (Cash on Hand at Beginning of Month)",
        min_value=0.0
    )

    st.subheader("Add Transaction")

    col1,col2,col3,col4 = st.columns(4)

    with col1:
        date = st.date_input("Date")

    with col2:
        t_type = st.selectbox("Type",["Income","Expense"])

    with col3:
        category = st.text_input("Category")

    with col4:
        amount = st.number_input("Amount",min_value=0.0)

    desc = st.text_input("Description")

    if st.button("Add Transaction"):

        new = pd.DataFrame(
            [[date,t_type,category,desc,amount]],
            columns=st.session_state.transactions.columns
        )

        st.session_state.transactions = pd.concat(
            [st.session_state.transactions,new],
            ignore_index=True
        )

        st.success("Transaction added")

    st.subheader("Ledger Table")

    st.session_state.transactions = st.data_editor(
        st.session_state.transactions,
        num_rows="dynamic"
    )

    df = st.session_state.transactions

    # Calculate totals
    income = df[df["Type"]=="Income"]["Amount"].sum()
    expense = df[df["Type"]=="Expense"]["Amount"].sum()

    # Cash on Hand = Starting Balance + Income - Expenses
    cash_on_hand = starting_balance + income - expense

    # Display metrics
    col1,col2,col3,col4 = st.columns(4)

    col1.metric("Total Income", f"₱ {income:,.2f}")
    col2.metric("Total Expense", f"₱ {expense:,.2f}")
    col3.metric("Remaining Balance", f"₱ {cash_on_hand:,.2f}")
    col4.metric("Cash on Hand", f"₱ {cash_on_hand:,.2f}")

    if st.button("Save Monthly Report"):
        st.session_state.reports[month] = df.copy()
        st.success(f"{month} report saved")

# -------------------------
# FINANCIAL STATEMENTS
# -------------------------
elif menu == "Financial Statements":

    st.title("📊 Financial Statements")

    df = st.session_state.transactions

    # Totals
    total_income = df[df["Type"]=="Income"]["Amount"].sum()
    total_expense = df[df["Type"]=="Expense"]["Amount"].sum()
    net_income = total_income - total_expense

    month_selected = st.selectbox(
        "Select Month for Statement",
        [
            "January","February","March","April",
            "May","June","July","August",
            "September","October","November","December"
        ]
    )

    year_selected = st.number_input("Year", min_value=2000, max_value=2100, value=2025, step=1)

    st.subheader("Statement of Comprehensive Income")

    # Group incomes and expenses by category
    income_items = df[df["Type"]=="Income"].groupby("Category")["Amount"].sum().reset_index()
    expense_items = df[df["Type"]=="Expense"].groupby("Category")["Amount"].sum().reset_index()

    # Format main statement
    statement = f"""
SUPREME STUDENT COUNCIL
STATEMENT OF COMPREHENSIVE INCOME
For the Month Ended {month_selected} 31, {year_selected}


Service Revenue (Note 1)           ₱ {income_items['Amount'].sum():,.2f}
Add: Other Income (Note 2)         ₱ 0.00
Less: Operating Expenses (Note 3)  ₱ {expense_items['Amount'].sum():,.2f}
Net Income                        ₱ {net_income:,.2f}

Note 1: Net Sales
"""

    # List income items
    if not income_items.empty:
        for idx, row in income_items.iterrows():
            statement += f"\t{row['Category']:<20} ₱ {row['Amount']:,.2f}\n"
    else:
        statement += "\tNone recorded\t₱ 0.00\n"
    statement += f"Total Net Sales\t\t\t₱ {income_items['Amount'].sum():,.2f}\n\n"

    # Other Income (placeholder)
    statement += "Note 2: Other Income\n"
    statement += "\tNone recorded\t\t₱ 0.00\n"
    statement += "Total Other Income\t\t₱ 0.00\n\n"

    # Operating Expenses
    statement += "Note 3: Operating Expenses\n"
    if not expense_items.empty:
        for idx, row in expense_items.iterrows():
            statement += f"\t{row['Category']:<20} ₱ {row['Amount']:,.2f}\n"
    else:
        statement += "\tNone recorded\t₱ 0.00\n"
    statement += f"Total Operating Expenses\t₱ {expense_items['Amount'].sum():,.2f}\n"

    st.text(statement)

# -------------------------
# SAVED REPORTS
# -------------------------
elif menu == "Saved Reports":

    st.title("💾 Saved Monthly Reports")

    if st.session_state.reports:

        month = st.selectbox(
            "Select Report",
            list(st.session_state.reports.keys())
        )

        report_df = st.session_state.reports[month].copy()
        report_df["Amount"] = report_df["Amount"].apply(lambda x: f"₱ {x:,.2f}")

        st.dataframe(report_df)

    else:
        st.info("No reports saved yet.")

# -------------------------
# ABOUT PAGE
# -------------------------
elif menu == "About":

    st.title("About This App")

    st.write("""
**App Name:** Student Council Finance Report Tracker

**What the App Does:**
This application allows student councils to track their financial transactions,
compute balances automatically, and generate financial statements.

**Target Users:**
Student organizations and councils managing financial reports.

**Inputs Collected:**
- Transaction date
- Income or expense type
- Category
- Description
- Amount

**Outputs Displayed:**
- Financial ledger
- Statement of Comprehensive Income
- Cash on Hand
- Saved monthly financial reports
""")
