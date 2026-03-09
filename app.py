import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="Financial Report Tracker", layout="wide")

# Sidebar Navigation
page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Add Transaction",
        "Financial Reports",
        "Upload Receipts",
        "About"
    ]
)

# Storage
if "transactions" not in st.session_state:
    st.session_state.transactions = []

# HOME PAGE
if page == "Home":

    st.title("💰 Financial Report Tracker")

    name = st.text_input("Enter Organization / User Name")

    st.write("Track finances, generate financial statements, and store receipts.")

    st.image("https://cdn-icons-png.flaticon.com/512/2331/2331941.png", width=150)

    if st.button("Start Tracking"):
        st.success(f"Welcome {name}! You can now manage your financial records.")

# ADD TRANSACTION
elif page == "Add Transaction":

    st.header("Add Financial Transaction")

    transaction_type = st.selectbox(
        "Transaction Type",
        ["Income", "Expense", "Asset", "Liability"]
    )

    category = st.selectbox(
        "Category",
        [
            "Membership Fee",
            "Event Fund",
            "Food",
            "Supplies",
            "Transportation",
            "Equipment"
        ]
    )

    amount = st.number_input("Amount", min_value=0)

    event = st.text_input("Event / Activity Name")

    date = st.date_input("Transaction Date", datetime.date.today())

    payment_method = st.radio(
        "Payment Method",
        ["Cash", "Bank", "GCash", "Card"]
    )

    importance = st.slider("Transaction Importance", 1, 10)

    notes = st.text_area("Notes")

    confirm = st.checkbox("Confirm this transaction")

    if st.button("Save Transaction") and confirm:

        st.session_state.transactions.append({
            "Type": transaction_type,
            "Category": category,
            "Amount": amount,
            "Event": event,
            "Date": date
        })

        st.success("Transaction saved successfully!")

# FINANCIAL REPORTS
elif page == "Financial Reports":

    st.title("📊 Financial Statements")

    df = pd.DataFrame(st.session_state.transactions)

    if not df.empty:

        income = df[df["Type"] == "Income"]["Amount"].sum()
        expense = df[df["Type"] == "Expense"]["Amount"].sum()
        assets = df[df["Type"] == "Asset"]["Amount"].sum()
        liabilities = df[df["Type"] == "Liability"]["Amount"].sum()

        net_income = income - expense
        equity = assets - liabilities

        tabs = st.tabs([
            "Statement of Comprehensive Income",
            "Statement of Council’s Equity",
            "Statement of Financial Position"
        ])

        # STATEMENT OF COMPREHENSIVE INCOME
        with tabs[0]:

            st.subheader("Statement of Comprehensive Income")

            data = {
                "Description": ["Total Income", "Total Expenses", "Net Income"],
                "Amount": [income, expense, net_income]
            }

            income_df = pd.DataFrame(data)

            st.table(income_df)

            st.bar_chart(income_df.set_index("Description"))

        # STATEMENT OF COUNCIL EQUITY
        with tabs[1]:

            st.subheader("Statement of Council’s Equity")

            equity_data = {
                "Description": [
                    "Beginning Equity",
                    "Add: Net Income",
                    "Ending Equity"
                ],
                "Amount": [
                    equity,
                    net_income,
                    equity + net_income
                ]
            }

            equity_df = pd.DataFrame(equity_data)

            st.table(equity_df)

        # STATEMENT OF FINANCIAL POSITION
        with tabs[2]:

            st.subheader("Statement of Financial Position")

            position_data = {
                "Category": ["Assets", "Liabilities", "Equity"],
                "Amount": [assets, liabilities, equity]
            }

            position_df = pd.DataFrame(position_data)

            st.table(position_df)

            st.metric("Assets", assets)
            st.metric("Liabilities", liabilities)
            st.metric("Equity", equity)

        st.subheader("Transaction Records")

        st.dataframe(df)

    else:
        st.warning("No transactions recorded yet.")

# RECEIPT UPLOAD SECTION
elif page == "Upload Receipts":

    st.title("📂 Upload Receipts")

    month = st.selectbox(
        "Select Month",
        [
            "January","February","March","April",
            "May","June","July","August",
            "September","October","November","December"
        ]
    )

    event = st.text_input("Event Name")

    receipt_files = st.file_uploader(
        "Upload Receipts",
        accept_multiple_files=True
    )

    if receipt_files:

        for file in receipt_files:
            st.write("Uploaded:", file.name)

        st.success("Receipts uploaded successfully!")

    st.caption("Upload receipts for documentation and auditing purposes.")

# ABOUT PAGE
elif page == "About":

    st.title("About This App")

    st.write("""
    **App Name:** Financial Report Tracker

    **Use Case:**  
    This application records financial transactions and automatically generates financial statements.

    **Target Users:**  
    Student councils, organizations, and individuals who need financial reports.

    **Inputs Collected:**  
    - Transaction type  
    - Category  
    - Amount  
    - Event or activity  
    - Transaction date  
    - Receipt uploads  

    **Outputs Displayed:**  
    - Statement of Comprehensive Income  
    - Statement of Council’s Equity  
    - Statement of Financial Position  
    - Transaction records and charts  
    """)
