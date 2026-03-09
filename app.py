import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
from datetime import date

st.set_page_config(page_title="Student Council Finance Reports", layout="wide")

# SESSION DATA
if "transactions" not in st.session_state:
    st.session_state.transactions = pd.DataFrame(
        columns=["Date","Month","Type","Category","Description","Amount"]
    )

# SIDEBAR
menu = st.sidebar.selectbox(
    "Navigation",
    [
        "Monthly Ledger",
        "Financial Statements",
        "Expense Analytics",
        "Receipt Manager",
        "Save Report"
    ]
)

# -----------------------------
# MONTHLY LEDGER
# -----------------------------

if menu == "Monthly Ledger":

    st.title("📒 Student Council Monthly Finance Ledger")

    starting_balance = st.number_input(
        "Enter Starting Balance",
        min_value=0.0
    )

    st.subheader("Add Transaction")

    col1,col2,col3,col4 = st.columns(4)

    with col1:
        t_date = st.date_input("Date")

    with col2:
        month = st.selectbox(
            "Month",
            ["January","February","March","April","May","June",
             "July","August","September","October","November","December"]
        )

    with col3:
        t_type = st.selectbox(
            "Transaction Type",
            ["Income","Expense"]
        )

    with col4:
        amount = st.number_input("Amount",min_value=0.0)

    category = st.text_input("Category")
    desc = st.text_input("Description")

    if st.button("Add Transaction"):

        new = pd.DataFrame(
            [[t_date,month,t_type,category,desc,amount]],
            columns=st.session_state.transactions.columns
        )

        st.session_state.transactions = pd.concat(
            [st.session_state.transactions,new],
            ignore_index=True
        )

        st.success("Transaction added successfully")

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

    col1.metric("Total Income",f"₱ {income:,.2f}")
    col2.metric("Total Expenses",f"₱ {expense:,.2f}")
    col3.metric("Remaining Balance",f"₱ {balance:,.2f}")

# -----------------------------
# FINANCIAL STATEMENTS
# -----------------------------

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

    # SCI
    with tabs[0]:

        st.subheader("Statement of Comprehensive Income")

        sci = pd.DataFrame({
            "Description":[
                "Service Revenue",
                "Other Income",
                "Operating Expenses",
                "Net Income"
            ],
            "Amount":[income,0,expense,net_income]
        })

        st.table(sci)

    # COUNCIL EQUITY
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

    # FINANCIAL POSITION
    with tabs[2]:

        assets = st.number_input("Assets",min_value=0.0)
        liabilities = st.number_input("Liabilities",min_value=0.0)

        equity = assets - liabilities

        st.metric("Assets",assets)
        st.metric("Liabilities",liabilities)
        st.metric("Equity",equity)

# -----------------------------
# EXPENSE ANALYTICS
# -----------------------------

elif menu == "Expense Analytics":

    st.title("📊 Expense Analytics")

    df = st.session_state.transactions
    expense_df = df[df["Type"]=="Expense"]

    if not expense_df.empty:

        chart = expense_df.groupby("Category")["Amount"].sum()

        fig,ax = plt.subplots()

        ax.pie(
            chart,
            labels=chart.index,
            autopct="%1.1f%%"
        )

        ax.set_title("Expense Distribution")

        st.pyplot(fig)

    else:
        st.info("No expense data available")

# -----------------------------
# RECEIPT MANAGER
# -----------------------------

elif menu == "Receipt Manager":

    st.title("📂 Upload Receipts")

    month = st.selectbox(
        "Select Month",
        ["January","February","March","April","May","June",
         "July","August","September","October","November","December"]
    )

    event = st.text_input("Event Name")

    uploaded_files = st.file_uploader(
        "Upload Receipt Files",
        accept_multiple_files=True
    )

    if uploaded_files:

        folder = f"receipts/{month}_{event}"

        os.makedirs(folder,exist_ok=True)

        for file in uploaded_files:

            path = os.path.join(folder,file.name)

            with open(path,"wb") as f:
                f.write(file.getbuffer())

        st.success("Receipts saved successfully")

# -----------------------------
# SAVE REPORT
# -----------------------------

elif menu == "Save Report":

    st.title("💾 Save Monthly Report")

    month = st.selectbox(
        "Select Month to Save",
        ["January","February","March","April","May","June",
         "July","August","September","October","November","December"]
    )

    df = st.session_state.transactions

    if st.button("Save Report"):

        os.makedirs(f"reports/{month}",exist_ok=True)

        path = f"reports/{month}/finance_report.csv"

        df.to_csv(path,index=False)

        st.success(f"Report saved successfully in {path}")
