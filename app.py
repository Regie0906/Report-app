import streamlit as st
import pandas as pd

st.set_page_config(page_title="Student Council Finance Tracker", layout="wide")

# -------------------------
# COUNCIL / ORGANIZATION LIST
# -------------------------
councils = [
    "ICSSC - Institute of Computer Studies Student Council",
    "SSC - Supreme Student Council",
    "JPCS - Junior Philippine Computer Society",
    "ITSO - IT Society Organization",
    "Other Organization"
]

# -------------------------
# SESSION STORAGE
# -------------------------
if "reports" not in st.session_state:
    st.session_state.reports = {}

if "transactions" not in st.session_state:
    st.session_state.transactions = pd.DataFrame(
        columns=["Council", "Date", "Type", "Category", "Description", "Amount"]
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

    council_selected = st.selectbox("Select Council / Organization", councils)

    month = st.selectbox(
        "Select Month",
        [
            "January","February","March","April","May","June",
            "July","August","September","October","November","December"
        ]
    )

    # starting balance with comma support
    starting_balance_input = st.text_input(
        "Starting Balance (Cash on Hand at Beginning of Month)",
        "0"
    )

    try:
        starting_balance = float(starting_balance_input.replace(",", ""))
    except:
        starting_balance = 0.0

    st.subheader("Add Transaction")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        date = st.date_input("Date")

    with col2:
        t_type = st.selectbox("Type", ["Income", "Expense"])

    with col3:
        category = st.text_input("Category")

    with col4:
        amount_input = st.text_input("Amount (₱)", "0")

    desc = st.text_input("Description")

    # Convert comma number
    try:
        amount = float(amount_input.replace(",", ""))
    except:
        amount = 0

    if st.button("Add Transaction"):

        new = pd.DataFrame(
            [[council_selected, date, t_type, category, desc, amount]],
            columns=st.session_state.transactions.columns
        )

        st.session_state.transactions = pd.concat(
            [st.session_state.transactions, new],
            ignore_index=True
        )

        st.success("Transaction added")

    # -------------------------
    # FILTER BY COUNCIL
    # -------------------------
    df = st.session_state.transactions[
        st.session_state.transactions["Council"] == council_selected
    ]

    st.subheader("Ledger Table")

    edited_df = st.data_editor(df, num_rows="dynamic")

    # Update stored dataframe
    st.session_state.transactions.update(edited_df)

    # -------------------------
    # CALCULATIONS
    # -------------------------
    total_income = edited_df[edited_df["Type"]=="Income"]["Amount"].sum()
    total_expense = edited_df[edited_df["Type"]=="Expense"]["Amount"].sum()
    cash_on_hand = starting_balance + total_income - total_expense

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Income", f"₱ {total_income:,.2f}")
    col2.metric("Total Expense", f"₱ {total_expense:,.2f}")
    col3.metric("Remaining Balance", f"₱ {cash_on_hand:,.2f}")
    col4.metric("Cash on Hand", f"₱ {cash_on_hand:,.2f}")

    if st.button("Save Monthly Report"):
        key = f"{council_selected}_{month}"
        st.session_state.reports[key] = edited_df.copy()
        st.success(f"{month} report saved for {council_selected}")

# -------------------------
# FINANCIAL STATEMENTS
# -------------------------
elif menu == "Financial Statements":

    st.title("📊 Financial Statements")

    council_selected = st.selectbox("Select Council", councils)

    df = st.session_state.transactions[
        st.session_state.transactions["Council"] == council_selected
    ]

    month_selected = st.selectbox(
        "Select Month",
        [
            "January","February","March","April","May","June",
            "July","August","September","October","November","December"
        ]
    )

    year_selected = st.number_input("Year", value=2026)

    total_income = df[df["Type"]=="Income"]["Amount"].sum()
    total_expense = df[df["Type"]=="Expense"]["Amount"].sum()

    net_income = total_income - total_expense

    # -------------------------
    # STATEMENT OF COMPREHENSIVE INCOME
    # -------------------------
    if total_income > 0:

        st.subheader("Statement of Comprehensive Income")

        income_items = df[df["Type"]=="Income"].groupby("Category")["Amount"].sum()
        expense_items = df[df["Type"]=="Expense"].groupby("Category")["Amount"].sum()

        st.text(f"""
{council_selected}
STATEMENT OF COMPREHENSIVE INCOME
For the Month Ended {month_selected} {year_selected}

Service Revenue                ₱ {total_income:,.2f}
Operating Expenses             ₱ {total_expense:,.2f}

Net Income                     ₱ {net_income:,.2f}
""")

    # -------------------------
    # COUNCIL EQUITY
    # -------------------------
    st.subheader("Statement of Council's Equity")

    beginning_equity_input = st.text_input(
        "Beginning Equity",
        "25,689.02"
    )

    try:
        beginning_equity = float(beginning_equity_input.replace(",", ""))
    except:
        beginning_equity = 0

    ending_equity = beginning_equity + net_income

    st.text(f"""
{council_selected}
STATEMENT OF COUNCIL'S EQUITY

Beginning Equity     ₱ {beginning_equity:,.2f}
Net Income           ₱ {net_income:,.2f}

Ending Equity        ₱ {ending_equity:,.2f}
""")

# -------------------------
# SAVED REPORTS
# -------------------------
elif menu == "Saved Reports":

    st.title("📁 Saved Monthly Reports")

    if st.session_state.reports:

        for key in st.session_state.reports:

            st.subheader(key)
            st.dataframe(st.session_state.reports[key])

    else:
        st.info("No saved reports yet.")

# -------------------------
# ABOUT
# -------------------------
elif menu == "About":

    st.title("About This App")

    st.write("""
Student Council Finance Tracker

Features:
• Monthly Ledger Recording
• Automatic Income & Expense Calculation
• Financial Statements Generation
• Multi-Council Tracking
• Editable Transactions

Currency Format: ₱ Philippine Peso
""")
