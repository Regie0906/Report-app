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
        columns=["Date", "Type", "Category", "Description", "Amount"]
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
            "January", "February", "March", "April",
            "May", "June", "July", "August",
            "September", "October", "November", "December"
        ]
    )

    starting_balance = st.number_input(
        "Starting Balance (Cash on Hand at Beginning of Month)",
        min_value=0.0
    )

    st.subheader("Add Transaction")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        date = st.date_input("Date")
    with col2:
        t_type = st.selectbox("Type", ["Income", "Expense"])
    with col3:
        category = st.text_input("Category")
    with col4:
        amount = st.number_input("Amount", min_value=0.0)
    desc = st.text_input("Description")

    if st.button("Add Transaction"):
        new = pd.DataFrame(
            [[date, t_type, category, desc, amount]],
            columns=st.session_state.transactions.columns
        )
        st.session_state.transactions = pd.concat(
            [st.session_state.transactions, new],
            ignore_index=True
        )
        st.success("Transaction added")

    st.subheader("Ledger Table")
    st.session_state.transactions = st.data_editor(
        st.session_state.transactions, num_rows="dynamic"
    )

    df = st.session_state.transactions

    # Calculate totals
    total_income = df[df["Type"] == "Income"]["Amount"].sum()
    total_expense = df[df["Type"] == "Expense"]["Amount"].sum()
    cash_on_hand = starting_balance + total_income - total_expense

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Income", f"₱ {total_income:,.2f}")
    col2.metric("Total Expense", f"₱ {total_expense:,.2f}")
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

    # Month and Year
    month_selected = st.selectbox(
        "Select Month for Statement",
        [
            "January", "February", "March", "April",
            "May", "June", "July", "August",
            "September", "October", "November", "December"
        ]
    )
    year_selected = st.number_input("Year", min_value=2000, max_value=2100, value=2026, step=1)

    # Calculate totals
    total_income = df[df["Type"] == "Income"]["Amount"].sum()
    total_expense = df[df["Type"] == "Expense"]["Amount"].sum()
    net_income = total_income - total_expense
    cash_on_hand = total_income - total_expense + st.session_state.transactions["Amount"].iloc[0] if not df.empty else 0

    # -------------------------
    # Statement of Comprehensive Income
    # -------------------------
    if total_income > 0:
        st.subheader("Statement of Comprehensive Income")

        income_items = df[df["Type"] == "Income"].groupby("Category")["Amount"].sum().reset_index()
        expense_items = df[df["Type"] == "Expense"].groupby("Category")["Amount"].sum().reset_index()

        statement_income = f"""
SUPREME STUDENT COUNCIL
STATEMENT OF COMPREHENSIVE INCOME
For the Month Ended {month_selected} 31, {year_selected}

Service Revenue (Note 1)           ₱ {total_income:,.2f}
Add: Other Income (Note 2)         ₱ 0.00
Less: Operating Expenses (Note 3)  ₱ {total_expense:,.2f}
Net Income                        ₱ {net_income:,.2f}

Note 1: Net Sales
"""
        if not income_items.empty:
            for idx, row in income_items.iterrows():
                statement_income += f"\t{row['Category']:<25} ₱ {row['Amount']:,.2f}\n"
        else:
            statement_income += "\tNone recorded              ₱ 0.00\n"
        statement_income += f"Total Net Sales                ₱ {total_income:,.2f}\n\n"

        statement_income += "Note 2: Other Income\n\tNone recorded              ₱ 0.00\nTotal Other Income            ₱ 0.00\n\n"

        statement_income += "Note 3: Operating Expenses\n"
        if not expense_items.empty:
            for idx, row in expense_items.iterrows():
                statement_income += f"\t{row['Category']:<25} ₱ {row['Amount']:,.2f}\n"
        else:
            statement_income += "\tNone recorded              ₱ 0.00\n"
        statement_income += f"Total Operating Expenses      ₱ {total_expense:,.2f}\n"

        st.text(statement_income)

    # -------------------------
    # Statement of Council’s Equity
    # -------------------------
    st.subheader("Statement of Council’s Equity")
    beginning_equity = st.number_input(
        "ICSSC’s Equity, Beginning", min_value=0.0, value=25689.02
    )
    ending_equity = beginning_equity + total_income - total_expense
    statement_equity = f"""
INSTITUTE OF COMPUTER STUDIES - STUDENT COUNCIL
STATEMENT OF COUNCIL’S EQUITY
As of TechConnect {year_selected}

ICSSC’s Equity, Beginning                ₱ {beginning_equity:>12,.2f}
    Less:   Expenses                      ₱ {total_expense:>12,.2f}
ICSSC’s Equity, Ending                   ₱ {ending_equity:>12,.2f}
"""
    st.text(statement_equity)

    # -------------------------
    # Statement of Financial Position
    # -------------------------
    st.subheader("Statement of Financial Position")
    cash_coop = 0.0
    supplies = 3890.50
    equipment = 10250.00
    accumulated_dep = 2050.00
    accounts_payable = 0.0
    unearned_income = 0.0
    donations = 0.0

    total_current_assets = cash_on_hand + cash_coop + supplies
    total_noncurrent_assets = equipment - accumulated_dep
    total_assets = total_current_assets + total_noncurrent_assets
    total_equity = total_assets

    statement_position = f"""
INSTITUTE OF COMPUTER STUDIES - STUDENT COUNCIL
STATEMENT OF FINANCIAL POSITION
As of {month_selected} {year_selected}

ASSETS
Current Assets
    Cash on Hand (Note 1)               ₱ {cash_on_hand:>12,.2f}
    Cash on Coop (Note 2)               ₱ {cash_coop:>12,.2f}
    Supplies (Note 3)                   ₱ {supplies:>12,.2f}
Total Current Assets                     ₱ {total_current_assets:>12,.2f}
Noncurrent Assets
    Equipment (Note 4)                  ₱ {equipment:>12,.2f}
    Accumulated Depreciation (Note 5)   ₱ ({accumulated_dep:>10,.2f})
Total Noncurrent Assets                 ₱ {total_noncurrent_assets:>12,.2f}
TOTAL ASSETS                            ₱ {total_assets:>12,.2f}

LIABILITIES AND EQUITY
Liabilities
    Accounts Payable (Note 6)           ₱ {accounts_payable:>12,.2f}
    Unearned Income (Note 7)            ₱ {unearned_income:>12,.2f}
Total Liabilities                        ₱ {accounts_payable + unearned_income:>12,.2f}
Equity
    ICSSC, Capital (Note 8)             ₱ {total_assets:>12,.2f}
    Donations (Note 9)                   ₱ {donations:>12,.2f}
Total Equity                             ₱ {total_equity:>12,.2f}
TOTAL LIABILITIES AND EQUITY            ₱ {total_assets:>12,.2f}
"""
    st.text(statement_position)


