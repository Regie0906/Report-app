import streamlit as st
import pandas as pd

st.set_page_config(page_title="Student Council Finance Tracker", layout="wide")

# SESSION STORAGE
if "reports" not in st.session_state:
    st.session_state.reports = {}

if "transactions" not in st.session_state:
    st.session_state.transactions = pd.DataFrame(
        columns=["Date","Type","Category","Description","Amount"]
    )

# SIDEBAR NAVIGATION
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
        "Starting Balance",
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

    income = df[df["Type"]=="Income"]["Amount"].sum()
    expense = df[df["Type"]=="Expense"]["Amount"].sum()

    balance = starting_balance + income - expense

    col1,col2,col3 = st.columns(3)

    col1.metric("Total Income",income)
    col2.metric("Total Expense",expense)
    col3.metric("Remaining Balance",balance)

    if st.button("Save Monthly Report"):

        st.session_state.reports[month] = df.copy()

        st.success(f"{month} report saved")

# -------------------------
# FINANCIAL STATEMENTS
# -------------------------

elif menu == "Financial Statements":

    st.title("📊 Financial Statements")

    df = st.session_state.transactions

    income = df[df["Type"]=="Income"]["Amount"].sum()
    expense = df[df["Type"]=="Expense"]["Amount"].sum()

    net_income = income - expense

    tabs = st.tabs([
        "Statement of Comprehensive Income",
        "Statement of Council Equity",
        "Statement of Financial Position"
    ])

    with tabs[0]:

        st.subheader("Statement of Comprehensive Income")

        report = pd.DataFrame({
            "Description":[
                "Service Revenue",
                "Operating Expenses",
                "Net Income"
            ],
            "Amount":[
                income,
                expense,
                net_income
            ]
        })

        st.table(report)

    with tabs[1]:

        beginning_equity = st.number_input(
            "Beginning Equity",
            min_value=0.0
        )

        ending_equity = beginning_equity + net_income

        equity = pd.DataFrame({
            "Description":[
                "Beginning Equity",
                "Add Net Income",
                "Ending Equity"
            ],
            "Amount":[
                beginning_equity,
                net_income,
                ending_equity
            ]
        })

        st.table(equity)

    with tabs[2]:

        assets = st.number_input("Assets",min_value=0.0)
        liabilities = st.number_input("Liabilities",min_value=0.0)

        equity = assets - liabilities

        st.metric("Assets",assets)
        st.metric("Liabilities",liabilities)
        st.metric("Equity",equity)

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

        st.dataframe(st.session_state.reports[month])

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
    This app records income and expenses and automatically generates financial statements.

    **Target Users:**
    Student councils and organizations managing finances.

    **Inputs Collected:**
    - Transaction date
    - Income or expense
    - Category
    - Description
    - Amount

    **Outputs Displayed:**
    - Financial ledger
    - Statement of Comprehensive Income
    - Statement of Council's Equity
    - Statement of Financial Position
    """)
