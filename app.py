import streamlit as st
import pandas as pd

st.set_page_config(page_title="Student Council Finance Tracker", layout="wide")

# -------------------------
# DATABASE / CONFIG
# -------------------------
# Define passwords for each council
COUNCIL_CREDENTIALS = {
    "ICSSC - Institute of Computer Studies Student Council": "ics123",
    "SSC - Supreme Student Council": "ssc123",
    "JPCS - Junior Philippine Computer Society": "jpcs123",
    "ITSO - IT Society Organization": "itso123",
    "Other Organization": "admin123"
}

councils = list(COUNCIL_CREDENTIALS.keys())

# -------------------------
# SESSION STORAGE INITIALIZATION
# -------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "reports" not in st.session_state:
    st.session_state.reports = {}
if "transactions" not in st.session_state:
    st.session_state.transactions = pd.DataFrame(
        columns=["Council", "Date", "Type", "Category", "Description", "Amount"]
    )

# -------------------------
# LOGIN SECTION
# -------------------------
def login_page():
    st.title("🔐 Council Finance Login")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        selected_council = st.selectbox("Select Council / Organization", councils)
        password = st.text_input("Enter Password", type="password")
        
        if st.button("Login"):
            if password == COUNCIL_CREDENTIALS.get(selected_council):
                st.session_state.logged_in = True
                st.session_state.current_user = selected_council
                st.success(f"Welcome, {selected_council}!")
                st.rerun()
            else:
                st.error("Incorrect password. Please try again.")

# -------------------------
# MAIN APP LOGIC
# -------------------------
if not st.session_state.logged_in:
    login_page()
else:
    # Sidebar logout and info
    st.sidebar.title(f"👤 {st.session_state.current_user}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()

    menu = st.sidebar.radio(
        "Navigation",
        ["Monthly Ledger", "Financial Statements", "Saved Reports", "About"]
    )

    # -------------------------
    # MONTHLY LEDGER
    # -------------------------
    if menu == "Monthly Ledger":
        st.title(f"📒 {st.session_state.current_user} Ledger")
        
        month = st.selectbox(
            "Select Month",
            ["January","February","March","April","May","June",
             "July","August","September","October","November","December"]
        )

        starting_balance_input = st.text_input("Starting Balance (Beginning of Month)", "0")
        try:
            starting_balance = float(starting_balance_input.replace(",", ""))
        except ValueError:
            starting_balance = 0.0

        st.subheader("Add New Transaction")
        col1, col2, col3, col4 = st.columns(4)
        with col1: date = st.date_input("Date")
        with col2: t_type = st.selectbox("Type", ["Income", "Expense"])
        with col3: category = st.text_input("Category")
        with col4: amount_input = st.text_input("Amount (₱)", "0")
        
        desc = st.text_input("Description")

        try:
            amount = float(amount_input.replace(",", ""))
        except:
            amount = 0.0

        if st.button("Add Transaction"):
            new_row = pd.DataFrame([{
                "Council": st.session_state.current_user, # Locked to logged in user
                "Date": date,
                "Type": t_type,
                "Category": category,
                "Description": desc,
                "Amount": amount
            }])
            st.session_state.transactions = pd.concat([st.session_state.transactions, new_row], ignore_index=True)
            st.success("Transaction added!")
            st.rerun()

        st.divider()
        
        # Filter data ONLY for the logged-in council
        full_df = st.session_state.transactions
        filtered_df = full_df[full_df["Council"] == st.session_state.current_user].copy()

        st.subheader("Ledger Table")
        edited_df = st.data_editor(filtered_df, num_rows="dynamic", use_container_width=True)

        if st.button("Save Table Changes"):
            other_councils = full_df[full_df["Council"] != st.session_state.current_user]
            st.session_state.transactions = pd.concat([other_councils, edited_df], ignore_index=True)
            st.success("Changes saved!")
            st.rerun()

        # Calculations
        edited_df["Amount"] = pd.to_numeric(edited_df["Amount"], errors='coerce').fillna(0)
        total_income = edited_df[edited_df["Type"] == "Income"]["Amount"].sum()
        total_expense = edited_df[edited_df["Type"] == "Expense"]["Amount"].sum()
        ending_balance = starting_balance + total_income - total_expense

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Income", f"₱ {total_income:,.2f}")
        c2.metric("Total Expense", f"₱ {total_expense:,.2f}")
        c3.metric("Ending Balance", f"₱ {ending_balance:,.2f}")

        if st.button("Save Monthly Report"):
            key = f"{st.session_state.current_user}_{month}"
            st.session_state.reports[key] = edited_df.copy()
            st.success(f"Report for {month} archived.")

    # -------------------------
    # FINANCIAL STATEMENTS
    # -------------------------
    elif menu == "Financial Statements":
        st.title(f"📊 {st.session_state.current_user} Statements")
        
        df = st.session_state.transactions[
            st.session_state.transactions["Council"] == st.session_state.current_user
        ].copy()

        month_selected = st.selectbox("Select Month", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
        year_selected = st.number_input("Year", value=2026)

        df["Amount"] = pd.to_numeric(df["Amount"], errors='coerce').fillna(0)
        total_income = df[df["Type"] == "Income"]["Amount"].sum()
        total_expense = df[df["Type"] == "Expense"]["Amount"].sum()
        net_income = total_income - total_expense

        st.code(f"""
{st.session_state.current_user}
STATEMENT OF COMPREHENSIVE INCOME
For the Month Ended {month_selected} {year_selected}

Revenue:            ₱ {total_income:,.2f}
Expenses:           ₱ {total_expense:,.2f}
-------------------------------------
NET INCOME:         ₱ {net_income:,.2f}
        """)

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


    # -------------------------
    # SAVED REPORTS
    # -------------------------
    elif menu == "Saved Reports":
        st.title("📁 Your Archived Reports")
        user_reports = {k: v for k, v in st.session_state.reports.items() if k.startswith(st.session_state.current_user)}
        
        if user_reports:
            for key, data in user_reports.items():
                with st.expander(f"Report: {key.replace(st.session_state.current_user + '_', '')}"):
                    st.dataframe(data, use_container_width=True)
        else:
            st.info("No reports saved for this council yet.")

    # -------------------------
    # ABOUT
    # -------------------------
    elif menu == "About":
        st.title("About")
        st.write("Secure Finance Tracking System for Student Organizations.")
