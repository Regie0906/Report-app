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
