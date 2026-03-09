import streamlit as st
import pandas as pd
import os
from fpdf import FPDF

st.set_page_config(page_title="ICSSC Finance Tracker", layout="wide")

# SESSION STORAGE
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(
        columns=["Date","Type","Description","Amount"]
    )

# SIDEBAR
menu = st.sidebar.radio(
    "Navigation",
    [
        "Monthly Ledger",
        "Financial Statements",
        "Upload Receipts",
        "Export Report"
    ]
)

# -----------------------------
# MONTHLY LEDGER
# -----------------------------

if menu == "Monthly Ledger":

    st.title("📒 Student Council Monthly Finance Report")

    starting_balance = st.number_input(
        "Enter Starting Balance",
        min_value=0.0,
        value=0.0
    )

    st.subheader("Add Transaction")

    col1,col2,col3,col4 = st.columns(4)

    with col1:
        date = st.date_input("Date")

    with col2:
        t_type = st.selectbox(
            "Transaction Type",
            ["Income","Expense"]
        )

    with col3:
        desc = st.text_input("Product / Description")

    with col4:
        amount = st.number_input("Amount",min_value=0.0)

    if st.button("Add Transaction"):

        new = pd.DataFrame(
            [[date,t_type,desc,amount]],
            columns=st.session_state.data.columns
        )

        st.session_state.data = pd.concat(
            [st.session_state.data,new],
            ignore_index=True
        )

    st.subheader("Ledger")

    st.session_state.data = st.data_editor(
        st.session_state.data,
        num_rows="dynamic"
    )

    df = st.session_state.data

    income = df[df["Type"]=="Income"]["Amount"].sum()
    expenses = df[df["Type"]=="Expense"]["Amount"].sum()

    balance = starting_balance + income - expenses

    st.divider()

    col1,col2,col3 = st.columns(3)

    col1.metric("Total Income",f"₱ {income:,.2f}")
    col2.metric("Total Expenses",f"₱ {expenses:,.2f}")
    col3.metric("Remaining Balance",f"₱ {balance:,.2f}")

# -----------------------------
# FINANCIAL STATEMENTS
# -----------------------------

elif menu == "Financial Statements":

    st.title("📊 Financial Statements")

    df = st.session_state.data

    income = df[df["Type"]=="Income"]["Amount"].sum()
    expenses = df[df["Type"]=="Expense"]["Amount"].sum()
    net_income = income - expenses

    tabs = st.tabs([
        "Statement of Comprehensive Income",
        "Statement of Council Equity",
        "Statement of Financial Position"
    ])

    # Comprehensive Income
    with tabs[0]:

        st.subheader("Statement of Comprehensive Income")

        report = pd.DataFrame({
            "Description":[
                "Service Revenue",
                "Other Income",
                "Operating Expenses",
                "Net Income"
            ],
            "Amount":[
                income,
                0,
                expenses,
                net_income
            ]
        })

        st.table(report)

    # Council Equity
    with tabs[1]:

        st.subheader("Statement of Council's Equity")

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

    # Financial Position
    with tabs[2]:

        st.subheader("Statement of Financial Position")

        assets = st.number_input("Assets",min_value=0.0)
        liabilities = st.number_input("Liabilities",min_value=0.0)

        equity = assets - liabilities

        st.metric("Assets",assets)
        st.metric("Liabilities",liabilities)
        st.metric("Equity",equity)

# -----------------------------
# RECEIPT UPLOAD
# -----------------------------

elif menu == "Upload Receipts":

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

    uploaded_files = st.file_uploader(
        "Upload Receipt Files",
        accept_multiple_files=True
    )

    if uploaded_files:

        folder = f"receipts/{month}_{event}"

        os.makedirs(folder,exist_ok=True)

        for file in uploaded_files:

            with open(
                os.path.join(folder,file.name),
                "wb"
            ) as f:
                f.write(file.getbuffer())

        st.success("Receipts saved successfully!")

# -----------------------------
# EXPORT PDF REPORT
# -----------------------------

elif menu == "Export Report":

    st.title("📄 Export Financial Report")

    if st.button("Generate PDF"):

        df = st.session_state.data

        pdf = FPDF()
        pdf.add_page()

        pdf.set_font("Arial","B",16)
        pdf.cell(0,10,"Student Council Financial Report",ln=True)

        pdf.set_font("Arial","",12)

        for i,row in df.iterrows():

            text = f"{row['Date']} | {row['Type']} | {row['Description']} | ₱{row['Amount']}"

            pdf.cell(0,8,text,ln=True)

        pdf.output("finance_report.pdf")

        with open("finance_report.pdf","rb") as f:

            st.download_button(
                "Download PDF",
                f,
                file_name="finance_report.pdf"
            )
