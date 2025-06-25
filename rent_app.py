import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from PIL import Image

# Load and display logo (uncomment if you want to use)
# logo = Image.open(r"C:\Users\jacob\OneDrive\Desktop\rent_app\logo.jpg")
# st.image(logo, width=150)

st.markdown("#### Created by **Jacob K..**")

# --- Calculation and Helper Functions ---

def mortgage_payment_calc(loan_amount, annual_interest_rate, loan_term_years):
    monthly_rate = annual_interest_rate / 100 / 12
    n_payments = loan_term_years * 12
    if monthly_rate == 0:
        return loan_amount / n_payments
    payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** n_payments) / ((1 + monthly_rate) ** n_payments -1)
    return payment

def amortization_schedule(loan_amount, annual_interest_rate, loan_term_years):
    monthly_rate = annual_interest_rate / 100 / 12
    n_payments = loan_term_years * 12
    payment = mortgage_payment_calc(loan_amount, annual_interest_rate, loan_term_years)
    schedule = []
    balance = loan_amount
    for month in range(1, n_payments +1):
        interest = balance * monthly_rate
        principal = payment - interest
        balance = max(balance - principal, 0)
        schedule.append({"Month": month, "Payment": payment, "Principal": principal, "Interest": interest, "Balance": balance})
    return pd.DataFrame(schedule)

def calculate_cashflows(
    purchase_price,
    down_payment,
    loan_amount,
    loan_term_years,
    interest_rate,
    monthly_expenses,
    current_rent,
    vacancy_rate,
    mgmt_fee_percent,
    maintenance_percent,
    tax_annual,
    insurance_annual,
    hoa_monthly,
    rent_growth_percent,
    inflation_percent,
    years=5,
    include_mortgage=True,
    include_expenses=True
):
    n_months = years * 12
    monthly_interest_rate = interest_rate / 100 / 12
    mortgage_pmt = mortgage_payment_calc(loan_amount, interest_rate, loan_term_years) if include_mortgage else 0

    rent = np.zeros(n_months)
    expenses = np.zeros(n_months)
    vacancy_losses = np.zeros(n_months)
    mgmt_fees = np.zeros(n_months)
    maintenance = np.zeros(n_months)
    total_expenses = np.zeros(n_months)
    mortgage_payments = np.zeros(n_months)
    cash_flows = np.zeros(n_months)
    cumulative_cash_flows = np.zeros(n_months)
    equity = np.zeros(n_months)
    balances = np.zeros(n_months)
    roi_over_time = np.zeros(n_months)

    monthly_tax = tax_annual / 12
    monthly_insurance = insurance_annual / 12

    amort = amortization_schedule(loan_amount, interest_rate, loan_term_years)
    amort = amort.set_index("Month")

    rent_growth_rate = rent_growth_percent / 100 / 12
    inflation_rate = inflation_percent / 100 / 12

    for month in range(n_months):
        rent[month] = current_rent * ((1 + rent_growth_rate) ** month)
        vacancy_losses[month] = rent[month] * (vacancy_rate / 100)
        mgmt_fees[month] = (rent[month] - vacancy_losses[month]) * (mgmt_fee_percent / 100)
        maintenance[month] = (rent[month] - vacancy_losses[month]) * (maintenance_percent / 100)

        expenses[month] = monthly_expenses * ((1 + inflation_rate) ** month)
        expenses[month] += monthly_tax * ((1 + inflation_rate) ** month)
        expenses[month] += monthly_insurance * ((1 + inflation_rate) ** month)
        expenses[month] += hoa_monthly * ((1 + inflation_rate) ** month)

        total_expenses[month] = expenses[month] + vacancy_losses[month] + mgmt_fees[month] + maintenance[month]
        mortgage_payments[month] = mortgage_pmt if (include_mortgage and month < loan_term_years*12) else 0

        cash_flows[month] = rent[month] - total_expenses[month] - mortgage_payments[month]

        balances[month] = amort.loc[month +1]["Balance"] if (month + 1) in amort.index else 0
        equity[month] = purchase_price - balances[month]
        cumulative_cash_flows[month] = cash_flows[:month+1].sum()

        cash_invested = down_payment
        roi_over_time[month] = (cumulative_cash_flows[month] / cash_invested) * 100 if cash_invested > 0 else 0

    noi_annual = (rent * (1 - vacancy_rate/100) - expenses).mean() * 12
    cap_rate = (noi_annual / purchase_price) * 100

    annual_cash_flow = cash_flows.mean() * 12
    coc_return = (annual_cash_flow / down_payment) * 100 if down_payment > 0 else 0

    payback_months = next((i+1 for i, val in enumerate(cumulative_cash_flows) if val >= down_payment), None)

    return {
        "rent": rent,
        "vacancy_losses": vacancy_losses,
        "mgmt_fees": mgmt_fees,
        "maintenance": maintenance,
        "expenses": expenses,
        "total_expenses": total_expenses,
        "mortgage_payments": mortgage_payments,
        "cash_flows": cash_flows,
        "cumulative_cash_flows": cumulative_cash_flows,
        "balances": balances,
        "equity": equity,
        "roi_over_time": roi_over_time,
        "cap_rate": cap_rate,
        "coc_return": coc_return,
        "annual_cash_flow": annual_cash_flow,
        "payback_months": payback_months,
        "months": n_months,
        "loan_term_months": loan_term_years * 12
    }

# --- Plotting Functions ---
def plot_line_chart(x, y, title, yaxis_title, color):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line=dict(color=color, width=3)))
    fig.update_layout(title=title, xaxis_title='Months', yaxis_title=yaxis_title, template='plotly_white')
    return fig

def plot_area_chart(x, y, title, yaxis_title, color):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', fill='tozeroy', line=dict(color=color, width=3)))
    fig.update_layout(title=title, xaxis_title='Months', yaxis_title=yaxis_title, template='plotly_white')
    return fig

def plot_bar_chart(x, y, title, yaxis_title, colors):
    fig = go.Figure()
    if isinstance(colors, list):
        fig.add_trace(go.Bar(x=x, y=y, marker_color=colors))
    else:
        fig.add_trace(go.Bar(x=x, y=y, marker_color=colors))
    fig.update_layout(title=title, xaxis_title='Months' if len(x) > 2 else '', yaxis_title=yaxis_title, template='plotly_white')
    return fig

def plot_pie_chart(labels, sizes, colors, title):
    fig = go.Figure()
    fig.add_trace(go.Pie(labels=labels, values=sizes, marker_colors=colors, textinfo='label+percent', hole=0.3))
    fig.update_layout(title=title)
    return fig

# --- EXPORT FUNCTION ---
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# --- STREAMLIT UI ---

st.set_page_config(page_title="Advanced Rental Property Analyzer", layout="wide")
st.title("🏘️ Rental Property Analyzer")

# Layout: Simple and Advanced inputs side by side
col_simple, col_advanced = st.columns(2)

with col_simple:
    st.header("Basic Property Input")

    purchase_price = st.number_input("Purchase Price ($)", value=180000.0, step=1000.0, format="%.2f", key="purchase_price")
    down_payment_percent = st.number_input("Down Payment (%)", value=20.0, step=1.0, max_value=100.0, key="down_payment_percent")
    loan_term_years = st.number_input("Loan Term (years)", value=30, step=1, min_value=1, key="loan_term_years")
    interest_rate = st.number_input("Interest Rate (%)", value=6.43, step=0.01, key="interest_rate")
    current_rent = st.number_input("Current Monthly Rent ($)", value=1600.0, step=10.0, key="current_rent")
    years_projection = st.slider("Years to Project", min_value=1, max_value=30, value=5, step=1, key="years_projection")

    # Calculate loan amount and mortgage payment for breakdown
    loan_amount = purchase_price * (1 - down_payment_percent / 100)
    monthly_mortgage_payment = mortgage_payment_calc(loan_amount, interest_rate, loan_term_years)

    # Typical averages
    vacancy_rate = 5.0
    monthly_expenses = 350.0
    tax_annual = 2400.0
    insurance_annual = 1200.0
    hoa_monthly = 0.0
    mgmt_fee_percent = 8.0
    maintenance_percent = 5.0
    rent_growth_percent = 2.5
    inflation_percent = 2.0

    # Calculate breakdown values
    monthly_tax = tax_annual / 12
    monthly_insurance = insurance_annual / 12
    vacancy_loss = current_rent * vacancy_rate / 100
    management_fee = (current_rent - vacancy_loss) * mgmt_fee_percent / 100
    maintenance_cost = (current_rent - vacancy_loss) * maintenance_percent / 100
    other_expenses = monthly_expenses

    total_monthly_payment = (
        monthly_mortgage_payment
        + monthly_tax
        + monthly_insurance
        + hoa_monthly
        + maintenance_cost
        + vacancy_loss
        + management_fee
        + other_expenses
    )

    with st.expander("📊 Estimated Monthly Payment Breakdown", expanded=True):
        st.write(f"**Mortgage Payment:** ${monthly_mortgage_payment:,.2f}")
        st.write(f"**Property Tax:** ${monthly_tax:,.2f}")
        st.write(f"**Insurance:** ${monthly_insurance:,.2f}")
        st.write(f"**HOA Fees:** ${hoa_monthly:,.2f}")
        st.write(f"**Maintenance:** ${maintenance_cost:,.2f}")
        st.write(f"**Vacancy Loss:** ${vacancy_loss:,.2f}")
        st.write(f"**Management Fees:** ${management_fee:,.2f}")
        st.write(f"**Other Expenses:** ${other_expenses:,.2f}")
        st.markdown(f"---\n### Total Estimated Monthly Payment: **${total_monthly_payment:,.2f}**")

    if st.button("Calculate Basic Analysis"):

        down_payment = purchase_price * (down_payment_percent / 100)

        results = calculate_cashflows(
            purchase_price=purchase_price,
            down_payment=down_payment,
            loan_amount=loan_amount,
            loan_term_years=loan_term_years,
            interest_rate=interest_rate,
            monthly_expenses=monthly_expenses,
            current_rent=current_rent,
            vacancy_rate=vacancy_rate,
            mgmt_fee_percent=mgmt_fee_percent,
            maintenance_percent=maintenance_percent,
            tax_annual=tax_annual,
            insurance_annual=insurance_annual,
            hoa_monthly=hoa_monthly,
            rent_growth_percent=rent_growth_percent,
            inflation_percent=inflation_percent,
            years=years_projection,
            include_mortgage=True,
            include_expenses=True,
        )

        st.header("Basic Financial Summary")
        is_profitable = results['annual_cash_flow'] > 0 and results['coc_return'] > 0
        if is_profitable:
            st.success("✅ This property is projected to be **Profitable** based on current inputs.")
        else:
            st.error("❌ This property is projected to be **Not Profitable** based on current inputs.")

        col1, col2, col3 = st.columns(3)
        col1.metric("Cap Rate", f"{results['cap_rate']:.2f}%")
        col2.metric("Cash on Cash Return", f"{results['coc_return']:.2f}%")
        payback_text = f"{results['payback_months']//12} years {results['payback_months']%12} months" if results['payback_months'] else "Not within projection"
        col3.metric("Payback Period", payback_text)

with col_advanced:
    st.header("Advanced Inputs")

    # Allow user to override typical averages for more precise calc
    vacancy_rate_adv = st.number_input("Vacancy Rate (%)", value=5.0, step=0.1, max_value=100.0, key="vacancy_rate_adv")
    monthly_expenses_adv = st.number_input("Monthly Expenses ($)", value=350.0, step=10.0, key="monthly_expenses_adv")
    tax_annual_adv = st.number_input("Annual Property Taxes ($)", value=2400.0, step=100.0, key="tax_annual_adv")
    insurance_annual_adv = st.number_input("Annual Insurance ($)", value=1200.0, step=50.0, key="insurance_annual_adv")
    hoa_monthly_adv = st.number_input("HOA Fees Monthly ($)", value=0.0, step=10.0, key="hoa_monthly_adv")
    mgmt_fee_percent_adv = st.number_input("Management Fee (%)", value=8.0, step=0.1, max_value=100.0, key="mgmt_fee_percent_adv")
    maintenance_percent_adv = st.number_input("Maintenance (%)", value=5.0, step=0.1, max_value=100.0, key="maintenance_percent_adv")
    rent_growth_percent_adv = st.number_input("Rent Growth Rate (%)", value=2.5, step=0.1, key="rent_growth_percent_adv")
    inflation_percent_adv = st.number_input("Inflation Rate (%)", value=2.0, step=0.1, key="inflation_percent_adv")

    if st.button("Calculate Advanced Analysis"):

        down_payment = purchase_price * (down_payment_percent / 100)

        results_adv = calculate_cashflows(
            purchase_price=purchase_price,
            down_payment=down_payment,
            loan_amount=loan_amount,
            loan_term_years=loan_term_years,
            interest_rate=interest_rate,
            monthly_expenses=monthly_expenses_adv,
            current_rent=current_rent,
            vacancy_rate=vacancy_rate_adv,
            mgmt_fee_percent=mgmt_fee_percent_adv,
            maintenance_percent=maintenance_percent_adv,
            tax_annual=tax_annual_adv,
            insurance_annual=insurance_annual_adv,
            hoa_monthly=hoa_monthly_adv,
            rent_growth_percent=rent_growth_percent_adv,
            inflation_percent=inflation_percent_adv,
            years=years_projection,
            include_mortgage=True,
            include_expenses=True,
        )

        st.header("Advanced Financial Summary")
        is_profitable = results_adv['annual_cash_flow'] > 0 and results_adv['coc_return'] > 0
        if is_profitable:
            st.success("✅ This property is projected to be **Profitable** based on advanced inputs.")
        else:
            st.error("❌ This property is projected to be **Not Profitable** based on advanced inputs.")

        col1, col2, col3 = st.columns(3)
        col1.metric("Cap Rate", f"{results_adv['cap_rate']:.2f}%")
        col2.metric("Cash on Cash Return", f"{results_adv['coc_return']:.2f}%")
        payback_text = f"{results_adv['payback_months']//12} years {results_adv['payback_months']%12} months" if results_adv['payback_months'] else "Not within projection"
        col3.metric("Payback Period", payback_text)

        with st.expander("🔍 Advanced Rental Property Analyzer Details", expanded=False):

            months = np.arange(1, results_adv["months"] + 1)
            tabs = st.tabs(["Cash Flow Over Time", "ROI Over Time", "Loan Amortization", "Expense Breakdown", "Summary & Export"])

            with tabs[0]:
                chart_type = st.selectbox("Select Chart Type for Cash Flow", ["Line Chart", "Area Chart", "Bar Chart"], key="cf_chart_type")
                if chart_type == "Line Chart":
                    fig = plot_line_chart(months, results_adv["cash_flows"], "Monthly Cash Flow", "Cash Flow ($)", "#2ca02c")
                elif chart_type == "Area Chart":
                    fig = plot_area_chart(months, results_adv["cash_flows"], "Monthly Cash Flow", "Cash Flow ($)", "#2ca02c")
                else:
                    fig = plot_bar_chart(months, results_adv["cash_flows"], "Monthly Cash Flow", "Cash Flow ($)", "#2ca02c")
                st.plotly_chart(fig, use_container_width=True)
                st.markdown(f"**Average Monthly Cash Flow:** ${results_adv['annual_cash_flow'] / 12:.2f}")

            with tabs[1]:
                chart_type = st.selectbox("Select Chart Type for ROI", ["Line Chart", "Area Chart", "Bar Chart"], key="roi_chart_type")
                if chart_type == "Line Chart":
                    fig = plot_line_chart(months, results_adv["roi_over_time"], "ROI Over Time", "ROI (%)", "#ff7f0e")
                elif chart_type == "Area Chart":
                    fig = plot_area_chart(months, results_adv["roi_over_time"], "ROI Over Time", "ROI (%)", "#ff7f0e")
                else:
                    fig = plot_bar_chart(months, results_adv["roi_over_time"], "ROI Over Time", "ROI (%)", "#ff7f0e")
                st.plotly_chart(fig, use_container_width=True)

            with tabs[2]:
                amort_df = amortization_schedule(loan_amount, interest_rate, loan_term_years)
                st.dataframe(amort_df.style.format({
                    "Payment": "${:,.2f}",
                    "Principal": "${:,.2f}",
                    "Interest": "${:,.2f}",
                    "Balance": "${:,.2f}"
                }))
                st.markdown(f"*Loan Term: {loan_term_years} years | Interest Rate: {interest_rate}%*")

            with tabs[3]:
                labels = ["Vacancy Losses", "Management Fees", "Maintenance", "Property Expenses (taxes, insurance, HOA)"]
                sizes = [
                    results_adv["vacancy_losses"].mean(),
                    results_adv["mgmt_fees"].mean(),
                    results_adv["maintenance"].mean(),
                    results_adv["expenses"].mean()
                ]
                colors = ["#d62728", "#1f77b4", "#9467bd", "#8c564b"]
                fig = plot_pie_chart(labels, sizes, colors, "Average Monthly Expense Breakdown")
                st.plotly_chart(fig, use_container_width=True)

            with tabs[4]:
                st.markdown("### Summary")
                st.write(f"**Purchase Price:** ${purchase_price:,.2f}")
                st.write(f"**Down Payment:** ${down_payment:,.2f} ({down_payment_percent}%)")
                st.write(f"**Loan Amount:** ${loan_amount:,.2f}")
                st.write(f"**Loan Term:** {loan_term_years} years")
                st.write(f"**Interest Rate:** {interest_rate}%")
                st.write(f"**Monthly Rent:** ${current_rent:,.2f}")
                st.write(f"**Vacancy Rate:** {vacancy_rate_adv}%")
                st.write(f"**Monthly Expenses:** ${monthly_expenses_adv:,.2f} + Taxes, Insurance, HOA")

                st.markdown("---")

                export_data = pd.DataFrame({
                    "Month": months,
                    "Rent": results_adv["rent"],
                    "Vacancy Losses": results_adv["vacancy_losses"],
                    "Management Fees": results_adv["mgmt_fees"],
                    "Maintenance": results_adv["maintenance"],
                    "Expenses": results_adv["expenses"],
                    "Total Expenses": results_adv["total_expenses"],
                    "Mortgage Payments": results_adv["mortgage_payments"],
                    "Cash Flow": results_adv["cash_flows"],
                    "Cumulative Cash Flow": results_adv["cumulative_cash_flows"],
                    "Equity": results_adv["equity"],
                    "ROI (%)": results_adv["roi_over_time"]
                })

                csv = convert_df_to_csv(export_data)
                st.download_button(
                    label="Download Full Projection Data as CSV",
                    data=csv,
                    file_name='rental_property_projection.csv',
                    mime='text/csv',
                )

# Legend Section
with st.expander("📖 Legend: Key Terms Explained", expanded=False):
    st.markdown("""
    **Cap Rate:** The annual Net Operating Income divided by the purchase price, showing the property's yield ignoring financing.

    **Net Operating Income (NOI):** Income from rent minus operating expenses (taxes, insurance, maintenance), excluding mortgage costs.

    **Cash on Cash Return:** Annual cash flow divided by your actual cash invested (down payment), showing your cash yield.

    **ROI (Return on Investment):** Percentage gain or loss on your investment over time, including cash flow and equity gains.

    **Payback Period:** Time it takes to recoup your initial investment (down payment) from cash flows.

    **Vacancy Rate:** Percentage of time the property is expected to be unoccupied.

    **Management Fee:** Percentage of rent paid to a property manager.

    **Maintenance:** Percentage of rent set aside for upkeep and repairs.

    **Inflation Rate:** Annual increase in expenses and costs.

    **Rent Growth Rate:** Expected annual increase in rent charged.
    """)

