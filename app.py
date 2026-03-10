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
 if menu == "Monthly Ledger":
        st.title(f"Financial Report: {st.session_state.current_user}")
        
        col_m, col_y, col_s = st.columns([1, 1, 1])
        with col_m:
            month_selected = st.selectbox("Select Month", range(1, 13), 
                                          index=datetime.now().month - 1,
                                          format_func=lambda x: datetime(2026, x, 1).strftime('%B'))
        with col_y:
            year_selected = st.number_input("Year", value=2026)
        
        with col_s:
            st_bal = st.number_input("Starting Balance (₱)", value=float(st.session_state.manual_start_val))
            st.session_state.manual_start_val = st_bal

        st.session_state.current_period = f"{datetime(2026, month_selected, 1).strftime('%B')} {year_selected}"

        # Filtering current data
        this_month_df = user_df[(user_df["Date"].dt.month == month_selected) & 
                                (user_df["Date"].dt.year == year_selected)]
        
        curr_inc = this_month_df[this_month_df["Type"] == "Income"]["Amount"].sum()
        curr_don_from = this_month_df[this_month_df["Type"] == "Donation (From)"]["Amount"].sum()
        curr_don_to = this_month_df[this_month_df["Type"] == "Donation (To)"]["Amount"].sum()
        curr_exp = this_month_df[this_month_df["Type"] == "Expense"]["Amount"].sum()
        rem_bal = st_bal + curr_inc + curr_don_from - curr_exp - curr_don_to

        st.subheader(f"Financial Activity for {st.session_state.current_period}")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("STARTING BALANCE", f"₱ {st_bal:,.2f}")
        m2.metric("EXPENSES", f"₱ {(curr_exp + curr_don_to):,.2f}")
        m3.metric("INCOME/DONATIONS", f"₱ {(curr_inc + curr_don_from):,.2f}")
        m4.metric("REMAINING BALANCE", f"₱ {rem_bal:,.2f}")

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

  elif menu == "Balance Sheet":
        st.title("Financial Summary")
        st_bal_sheet = st.session_state.get('manual_start_val', 0.0)
        current_period = st.session_state.get('current_period', "Current Month")
        
        all_inc = user_df[user_df["Type"] == "Income"]["Amount"].sum()
        all_don_f = user_df[user_df["Type"] == "Donation (From)"]["Amount"].sum()
        all_don_t = user_df[user_df["Type"] == "Donation (To)"]["Amount"].sum()
        all_exp = user_df[user_df["Type"] == "Expense"]["Amount"].sum()
        final_bal = st_bal_sheet + all_inc + all_don_f - all_exp - all_don_t

        st.code(f"""
{st.session_state.current_user}
PERIOD: {current_period}
--------------------------------------------------
STARTING BALANCE:                ₱ {st_bal_sheet:,.2f}
--------------------------------------------------
(+) TOTAL INCOME:                ₱ {all_inc:,.2f}
(+) DONATIONS (RECEIVED):        ₱ {all_don_f:,.2f}
(-) TOTAL EXPENSES:              ₱ {all_exp:,.2f}
(-) DONATIONS (GIVEN OUT):       ₱ {all_don_t:,.2f}
--------------------------------------------------
REMAINING BALANCE:               ₱ {final_bal:,.2f}
--------------------------------------------------
        """)

        if st.button("💾 Finalize & Save Report (Carry Over Balance)"):
            archive_row = pd.DataFrame([{
                "Council": st.session_state.current_user,
                "Archive_Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Period": current_period,
                "Starting_Bal": st_bal_sheet,
                "Total_Inc": all_inc,
                "Don_Rcv": all_don_f,
                "Total_Exp": all_exp,
                "Don_Giv": all_don_t,
                "Remaining_Bal": final_bal
            }])
            save_all_archives(pd.concat([load_archives(), archive_row], ignore_index=True))
            
            # Reset current entries and carry over balance
            save_data(full_df[full_df["Council"] != st.session_state.current_user])
            st.session_state.manual_start_val = final_bal
            st.success(f"Report finalized! ₱{final_bal:,.2f} is now your Starting Balance.")
            st.rerun()

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

