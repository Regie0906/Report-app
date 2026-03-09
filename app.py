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
        "Starting Balance (Cash on Hand at Beginning of Month)",
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

    # Calculate totals
    income = df[df["Type"]=="Income"]["Amount"].sum()
    expense = df[df["Type"]=="Expense"]["Amount"].sum()

    # Cash on Hand = Starting Balance + Income - Expenses
    cash_on_hand = starting_balance + income - expense

    # Display metrics
    col1,col2,col3,col4 = st.columns(4)

    col1.metric("Total Income", f"₱ {income:,.2f}")
    col2.metric("Total Expense", f"₱ {expense:,.2f}")
    col3.metric("Remaining Balance", f"₱ {cash_on_hand:,.2f}")
    col4.metric("Cash on Hand", f"₱ {cash_on_hand:,.2f}")

    if st.button("Save Monthly Report"):

        st.session_state.reports[month] = df.copy()

        st.success(f"{month} report saved")
