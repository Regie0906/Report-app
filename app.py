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
# SESSION STORAGE INITIALIZATION
# -------------------------
if "reports" not in st.session_state:
    st.session_state.reports = {}

if "transactions" not in st.session_state:
    # We define the structure once here
    st.session_state.transactions = pd.DataFrame(
        columns=["Council", "Date", "Type", "Category", "Description", "Amount"]
    )

# -------------------------
# SIDEBAR NAVIGATION
# -------------------------
menu = st.sidebar.radio(
    "Navigation",
    ["Monthly Ledger", "Financial Statements", "Saved Reports", "About"]
)

# -------------------------
# MONTHLY LEDGER
# -------------------------
if menu == "Monthly Ledger":
    st.title("📒 Student Council Monthly Finance Ledger")

    council_selected = st.selectbox("Select Council / Organization", councils)
    month = st.selectbox(
        "Select Month",
        ["January","February","March","April","May","June",
         "July","August","September","October","November","December"]
    )

    # Starting balance logic
    starting_balance_input = st.text_input("Starting Balance (Beginning of Month)", "0")
    try:
        starting_balance = float(starting_balance_input.replace(",", ""))
    except ValueError:
        starting_balance = 0.0

    st.divider()
    st.subheader("Add New Transaction")
    
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

    try:
        amount = float(amount_input.replace(",", ""))
    except ValueError:
        amount = 0.0

    if st.button("Add Transaction"):
        # Explicitly create a new row with matching columns
        new_row = pd.DataFrame([{
            "Council": council_selected,
            "Date": date,
            "Type": t_type,
            "Category": category,
            "Description": desc,
            "Amount": amount
        }])
        
        st.session_state.transactions = pd.concat(
            [st.session_state.transactions, new_row], 
            ignore_index=True
        )
        st.success("Transaction added!")
        st.rerun()

    st.divider()
    st.subheader(f"Ledger for {council_selected}")

    # -------------------------
    # DATA FILTERING & EDITING
    # -------------------------
    # This prevents the KeyError by ensuring we filter safely
    full_df = st.session_state.transactions
    
    # Filter only the rows for the selected council
    filtered_df = full_df[full_df["Council"] == council_selected].copy()

    # Editable Table
    edited_df = st.data_editor(
        filtered_df, 
        num_rows="dynamic", 
        use_container_width=True,
        key="main_editor"
    )

    # Sync back to session state if the user edited the table
    if st.button("Save Table Changes"):
        # Keep rows from other councils, replace current council rows with edited ones
        other_councils = full_df[full_df["Council"] != council_selected]
        st.session_state.transactions = pd.concat([other_councils, edited_df], ignore_index=True)
        st.success("Changes saved to database!")
        st.rerun()

    # -------------------------
    # CALCULATIONS
    # -------------------------
    # Ensure amount is treated as a number for math
    edited_df["Amount"] = pd.to_numeric(edited_df["Amount"], errors='coerce').fillna(0)
    
    total_income = edited_df[edited_df["Type"] == "Income"]["Amount"].sum()
    total_expense = edited_df[edited_df["Type"] == "Expense"]["Amount"].sum()
    net_total = total_income - total_expense
    ending_balance = starting_balance + net_total

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Income", f"₱ {total_income:,.2f}")
    col2.metric("Total Expense", f"₱ {total_expense:,.2f}")
    col3.metric("Ending Balance", f"₱ {ending_balance:,.2f}", delta=f"{net_total:,.2f}")

    if st.button("Save Monthly Report"):
        key = f"{council_selected}_{month}"
        st.session_state.reports[key] = edited_df.copy()
        st.success(f"Report archived for {month}")

# -------------------------
# FINANCIAL STATEMENTS
# -------------------------
elif menu == "Financial Statements":
    st.title("📊 Financial Statements")
    council_selected = st.selectbox("Select Council", councils)
    
    # Filter global transactions for this council
    df = st.session_state.transactions[
        st.session_state.transactions["Council"] == council_selected
    ].copy()

    month_selected = st.selectbox("Select Month", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
    year_selected = st.number_input("Year", value=2026)

    # Calculations
    df["Amount"] = pd.to_numeric(df["Amount"], errors='coerce').fillna(0)
    total_income = df[df["Type"] == "Income"]["Amount"].sum()
    total_expense = df[df["Type"] == "Expense"]["Amount"].sum()
    net_income = total_income - total_expense

    st.divider()

    # Statement of Income
    st.subheader("Statement of Comprehensive Income")
    st.code(f"""
{council_selected}
STATEMENT OF COMPREHENSIVE INCOME
For the Month Ended {month_selected} {year_selected}

Total Revenue:              ₱ {total_income:,.2f}
Total Operating Expenses:   ₱ {total_expense:,.2f}
------------------------------------------
NET INCOME / (LOSS):        ₱ {net_income:,.2f}
    """)

    # Statement of Equity
    st.subheader("Statement of Council's Equity")
    beg_equity_in = st.text_input("Beginning Equity", "0")
    try:
        beg_equity = float(beg_equity_in.replace(",", ""))
    except ValueError:
        beg_equity = 0.0
    
    end_equity = beg_equity + net_income

    st.code(f"""
{council_selected}
STATEMENT OF COUNCIL'S EQUITY

Beginning Balance:          ₱ {beg_equity:,.2f}
Add: Net Income:            ₱ {net_income:,.2f}
------------------------------------------
ENDING EQUITY:              ₱ {end_equity:,.2f}
    """)

# -------------------------
# SAVED REPORTS
# -------------------------
elif menu == "Saved Reports":
    st.title("📁 Archived Reports")
    if st.session_state.reports:
        for key, data in st.session_state.reports.items():
            with st.expander(f"Report: {key}"):
                st.dataframe(data, use_container_width=True)
    else:
        st.info("No reports saved yet.")

# -------------------------
# ABOUT
# -------------------------
elif menu == "About":
    st.title("About This App")
    st.info("This is a specialized finance tracker for school organizations. It manages multi-tenant data using Streamlit Session State.")
