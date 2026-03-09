import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="Financial Report Tracker", layout="wide")

# Sidebar Navigation
page = st.sidebar.radio("Navigation", ["Home", "Add Transaction", "Financial Report", "About"])

# Storage
if "transactions" not in st.session_state:
    st.session_state.transactions = []

# HOME PAGE
if page == "Home":

    st.title("💰 Financial Report Tracker")

    name = st.text_input("Enter your Name")

    st.write("This app helps you track income and expenses and generate a financial report.")

    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135706.png", width=150)

    if st.button("Start"):
        st.success(f"Welcome {name}! Start tracking your finances.")

# ADD TRANSACTION PAGE
elif page == "Add Transaction":

    st.header("Add Financial Transaction")

    transaction_type = st.selectbox(
        "Transaction Type",
        ["Income", "Expense"]
    )

    category = st.selectbox(
        "Category",
        ["Salary", "Allowance", "Food", "Transportation", "Bills", "Entertainment"]
    )

    amount = st.number_input("Amount", min_value=0)

    date = st.date_input("Transaction Date", datetime.date.today())

    payment_method = st.radio(
        "Payment Method",
        ["Cash", "Bank", "GCash", "Card"]
    )

    importance = st.slider("Transaction Importance", 1, 10)

    notes = st.text_area("Notes")

    receipt = st.file_uploader("Upload Receipt (optional)")

    confirm = st.checkbox("Confirm Transaction")

    if st.button("Save Transaction") and confirm:

        st.session_state.transactions.append({
            "Type": transaction_type,
            "Category": category,
            "Amount": amount,
            "Date": date,
            "Payment": payment_method
        })

        st.success("Transaction saved successfully!")

# FINANCIAL REPORT PAGE
elif page == "Financial Report":

    st.title("📊 Financial Report")

    df = pd.DataFrame(st.session_state.transactions)

    if not df.empty:

        income = df[df["Type"] == "Income"]["Amount"].sum()
        expense = df[df["Type"] == "Expense"]["Amount"].sum()
        balance = income - expense

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Income", income)
        col2.metric("Total Expenses", expense)
        col3.metric("Balance", balance)

        st.subheader("Transaction Table")
        st.dataframe(df)

        st.subheader("Expense Chart")
        st.bar_chart(df.groupby("Category")["Amount"].sum())

        progress = st.progress(70)

        st.caption("Financial tracking progress")

        with st.expander("Financial Advice"):
            st.write("""
            • Track expenses daily  
            • Set a monthly savings goal  
            • Avoid unnecessary spending
            """)

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download Financial Report",
            csv,
            "financial_report.csv",
            "text/csv"
        )

    else:
        st.warning("No transactions recorded yet.")

# ABOUT PAGE
elif page == "About":

    st.title("About This App")

    st.write("""
    **App Name:** Financial Report Tracker

    **What the App Does:**  
    This app allows users to record financial transactions and generate a report showing income, expenses, and balance.

    **Target Users:**  
    Students or individuals who want to monitor their financial activity.

    **Inputs Collected:**  
    - Transaction type  
    - Category  
    - Amount  
    - Date  
    - Payment method  
    - Notes  

    **Outputs Displayed:**  
    - Financial summary  
    - Transaction table  
    - Expense charts  
    - Downloadable financial report
    """)
