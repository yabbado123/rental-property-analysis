
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import numpy_financial as npf
import re

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="🏨 Rental Analyzer", layout="centered", initial_sidebar_state="collapsed")
st.title("🏠 Rental Property Investment Analyzer")
st.caption("Created by Jacob Klingman")

# --- STYLES ---
st.markdown("""
<style>
section.main > div {
    padding-top: 1rem;
    padding-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

# --- ADDRESS LOOKUP ---
with st.expander("📍 Property Address Lookup (Optional)"):
    full_address_input = st.text_input("Enter Full Address", placeholder="123 Main St, Dallas, TX 75201")
    if full_address_input:
        st.markdown(f"**You entered:** {full_address_input}")
        maps_url = f"https://www.google.com/maps/search/{full_address_input.replace(' ', '+')}"
        zip_match = re.search(r"(\d{5})", full_address_input)
        if zip_match:
            zip_code = zip_match.group(1)
            zip_rent_map = {
                "58104": 1300, "58103": 1100, "58102": 1200, "58047": 2300,
                "58105": 1100, "58109": 950, "58125": 1000, "58122": 950,
                "58124": 900, "58123": 900,
            }
            avg_rent = zip_rent_map.get(zip_code)
            if avg_rent:
                st.info(f"Estimated average rent for ZIP {zip_code}: ${avg_rent:,.0f}")
            else:
                st.warning(f"No rent data available for ZIP {zip_code}.")
        st.markdown(f"[🔗 View on Google Maps]({maps_url})")

# --- FUNCTIONS ---
def mortgage_payment_calc(loan_amount, annual_interest_rate, loan_term_years):
    monthly_rate = annual_interest_rate / 100 / 12
    n_payments = loan_term_years * 12
    if monthly_rate == 0:
        return loan_amount / n_payments
    return loan_amount * (monthly_rate * (1 + monthly_rate) ** n_payments) / ((1 + monthly_rate) ** n_payments - 1)

def amortization_schedule(loan_amount, annual_interest_rate, loan_term_years):
    monthly_rate = annual_interest_rate / 100 / 12
    n_payments = loan_term_years * 12
    payment = mortgage_payment_calc(loan_amount, annual_interest_rate, loan_term_years)
    schedule = []
    balance = loan_amount
    for month in range(1, n_payments + 1):
        interest = balance * monthly_rate
        principal = payment - interest
        balance = max(balance - principal, 0)
        schedule.append({
            "Month": month,
            "Payment": round(payment, 2),
            "Principal": round(principal, 2),
            "Interest": round(interest, 2),
            "Balance": round(balance, 2)
        })
    return pd.DataFrame(schedule)

def calculate_cashflows(purchase_price, down_payment, loan_amount, loan_term_years, interest_rate,
                        monthly_expenses, current_rent, vacancy_rate, mgmt_fee_percent, maintenance_percent,
                        tax_annual, insurance_annual, hoa_monthly, rent_growth_percent, inflation_percent,
                        years=5):
    months = years * 12
    schedule = amortization_schedule(loan_amount, interest_rate, loan_term_years)
    cash_flows, rents = [], []
    for month in range(1, months + 1):
        rent = current_rent * ((1 + rent_growth_percent / 100 / 12) ** month)
        rents.append(rent)
        vacancy_loss = rent * (vacancy_rate / 100)
        mgmt_fee = rent * (mgmt_fee_percent / 100)
        maintenance = rent * (maintenance_percent / 100)
        monthly_tax = tax_annual / 12
        monthly_insurance = insurance_annual / 12
        mortgage_payment = mortgage_payment_calc(loan_amount, interest_rate, loan_term_years)
        total_expenses = sum([monthly_expenses, vacancy_loss, mgmt_fee, maintenance, monthly_tax, monthly_insurance, hoa_monthly, mortgage_payment])
        net_cash_flow = rent - total_expenses
        cash_flows.append(net_cash_flow)
    return {"cash_flows": cash_flows, "rents": rents, "schedule": schedule}

def calculate_irr(cash_flows, down_payment):
    try:
        irr = npf.irr([-down_payment] + list(cash_flows))
        return None if irr is None or np.isnan(irr) else irr * 100
    except:
        return None

def calculate_npv(cash_flows, down_payment, discount_rate):
    try:
        return npf.npv(discount_rate / 100 / 12, [-down_payment] + list(cash_flows))
    except:
        return None

def plot_line_chart(x, y, title, yaxis_title, color):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line=dict(color=color, width=3)))
    fig.update_layout(title=title, xaxis_title='Months', yaxis_title=yaxis_title, template='plotly_white')
    return fig


# --- MODE SELECTION ---
mode = st.radio("Calculation Mode", ["Basic (Non-Rental)", "Basic (With Rent)", "Advanced"], horizontal=True)

st.markdown("### 🧾 Property & Loan Information")
st.divider()

col1, col2 = st.columns(2)
with col1:
    purchase_price = st.number_input("Purchase Price ($)", 50000, 2000000, 300000)
    down_payment_percent = st.number_input("Down Payment (% of Purchase Price)", 0.0, 100.0, 20.0,
                                           help="How much money you're putting down.")
    loan_term_years = st.number_input("Loan Term (Years)", 5, 40, 30)
with col2:
    interest_rate = st.number_input("Interest Rate (%)", 0.0, 15.0, 6.5,
                                    help="Annual interest rate on the mortgage.")
    gross_income = st.number_input("Gross Monthly Income ($)", 0, 50000, 8000,
                                   help="For affordability check (optional).")

down_payment = purchase_price * (down_payment_percent / 100)
loan_amount = purchase_price - down_payment
monthly_mortgage = mortgage_payment_calc(loan_amount, interest_rate, loan_term_years)



# --- RENTAL & ADVANCED MODES ---
if mode in ["Basic (With Rent)", "Advanced"]:
    st.markdown("### 💵 Rental Income & Expenses")
    current_rent = st.number_input("Monthly Rent ($)", 0, 20000, 2200)
    tax_annual = st.number_input("Annual Property Tax ($)", 0, 20000, 3500)
    insurance_annual = st.number_input("Annual Insurance ($)", 0, 10000, 1200)

    optional_zip = st.text_input("Optional: ZIP Code for Rent Comparison")
    if optional_zip:
        zip_rent_map = {
            "58104": 1300, "58103": 800, "58102": 995, "58047": 2300,
            "58105": 1100, "58109": 950, "58125": 1000, "58122": 950,
            "58124": 900, "58123": 900,
        }
        avg_rent = zip_rent_map.get(optional_zip.strip(), None)
        if avg_rent:
            diff = current_rent - avg_rent
            if abs(diff) <= 0.1 * avg_rent:
                st.success(f"✅ Rent ${current_rent:,.0f} is close to average (${avg_rent:,.0f})")
            elif current_rent > avg_rent:
                st.warning(f"⚠️ Rent is above average (${avg_rent:,.0f})")
            else:
                st.error(f"🔻 Rent is below average (${avg_rent:,.0f})")

# --- ADVANCED INPUTS ---
monthly_expenses = vacancy_rate = mgmt_fee_percent = maintenance_percent = hoa_monthly = rent_growth_percent = inflation_percent = discount_rate = 0

if mode == "Advanced":
    with st.expander("⚙️ Advanced Expense Settings", expanded=False):
        col3, col4 = st.columns(2)
        with col3:
            vacancy_rate = st.number_input("Vacancy Rate (%)", 0.0, 100.0, 5.0, help="Expected vacancy rate.")
            mgmt_fee_percent = st.number_input("Management Fee (%)", 0.0, 20.0, 8.0)
            maintenance_percent = st.number_input("Maintenance (% of Rent)", 0.0, 20.0, 5.0)
        with col4:
            monthly_expenses = st.number_input("Other Monthly Expenses ($)", 0, 5000, 200)
            hoa_monthly = st.number_input("Monthly HOA Fees ($)", 0, 1000, 150)
            discount_rate = st.number_input("Discount Rate for NPV (%)", 0.0, 20.0, 8.0)
        col5, col6 = st.columns(2)
        with col5:
            rent_growth_percent = st.number_input("Rent Growth Rate (%/yr)", 0.0, 10.0, 2.5)
        with col6:
            inflation_percent = st.number_input("Inflation Rate (%/yr)", 0.0, 10.0, 2.0)


# --- PROJECTION PERIOD ---
projection_years = st.slider("Projection Duration (Years)", 1, 30, 5)

# --- CALCULATE BUTTON ---
if st.button("🔍 Calculate"):
    monthly_property_tax = tax_annual / 12 if 'tax_annual' in locals() else 0
    loan_amount = purchase_price - down_payment
    monthly_mortgage = mortgage_payment_calc(loan_amount, interest_rate, loan_term_years)

    if mode == "Basic (Non-Rental)":
        total_monthly_payment = monthly_mortgage + monthly_property_tax
        st.markdown("### 💼 Non-Rental Payment Summary")
        st.write(f"**🏦 Mortgage Payment:** ${monthly_mortgage:,.2f}")
        st.write(f"**🏛️ Property Tax:** ${monthly_property_tax:,.2f}")
        st.success(f"**💰 Total Monthly Payment:** ${total_monthly_payment:,.2f}")

        if gross_income:
            housing_ratio = (total_monthly_payment / gross_income * 100)
            st.info(f"Housing Cost Ratio: {housing_ratio:.1f}% of income")
            if housing_ratio < 30:
                st.success("✅ Affordable")
            elif housing_ratio < 40:
                st.warning("⚠️ Borderline")
            else:
                st.error("❌ May be unaffordable")

    else:
        results = calculate_cashflows(
            purchase_price, down_payment, loan_amount, loan_term_years, interest_rate,
            monthly_expenses, current_rent, vacancy_rate, mgmt_fee_percent, maintenance_percent,
            tax_annual, insurance_annual, hoa_monthly, rent_growth_percent, inflation_percent,
            years=projection_years
        )
        cash_flows = results["cash_flows"]
        rents = results["rents"]
        schedule = results["schedule"]

        st.markdown("### 📈 Monthly Cash Flow Projection")
        st.plotly_chart(plot_line_chart(list(range(1, len(cash_flows)+1)), cash_flows, "Monthly Cash Flow", "Cash Flow ($)", "#1f77b4"), use_container_width=True)

        st.markdown("### 📉 Rent Projection")
        st.plotly_chart(plot_line_chart(list(range(1, len(rents)+1)), rents, "Projected Rent Income", "Rent ($)", "#2ca02c"), use_container_width=True)

        # Year-by-Year Table
        if len(cash_flows) >= 12:
            st.markdown("### 📅 Year-by-Year Summary")
            monthly_cf = np.array(cash_flows)
            rent_array = np.array(rents)
            years_list = list(range(1, int(len(cash_flows)/12) + 1))
            df_yearly = pd.DataFrame({
                "Year": years_list,
                "Total Rent": [rent_array[i*12:(i+1)*12].sum() for i in range(len(years_list))],
                "Cash Flow": [monthly_cf[i*12:(i+1)*12].sum() for i in range(len(years_list))]
            })
            st.dataframe(df_yearly, use_container_width=True)

        # Quick Summary
        st.markdown("### 📌 Quick Summary")
        col_qs1, col_qs2, col_qs3 = st.columns(3)
        with col_qs1:
            st.metric("💰 Monthly Mortgage", f"${monthly_mortgage:,.2f}")
        with col_qs2:
            st.metric("📆 Year 1 Cash Flow", f"${monthly_cf[:12].sum():,.2f}")
        with col_qs3:
            irr = calculate_irr(cash_flows, down_payment)
            st.metric("📈 IRR", f"{irr:.2f}%" if irr else "N/A")

        col_qs4, col_qs5 = st.columns(2)
        with col_qs4:
            npv = calculate_npv(cash_flows, down_payment, discount_rate)
            st.metric("🏦 NPV", f"${npv:,.0f}" if npv else "N/A")
        with col_qs5:
            total_cf = sum(cash_flows)
            st.metric("📊 Total Net Cash Flow", f"${total_cf:,.0f}")


# --- Non-Rental Monthly Payment Calculator (Separate Button) ---
if mode == "Basic (Non-Rental)":
    st.markdown("### 💵 Monthly Payment Estimate")

    with st.form("non_rental_form"):
        tax_annual_input = st.number_input("Annual Property Tax ($)", 0, 20000, 3000, key="tax_non_rental")
        submitted_non_rental = st.form_submit_button("📘 Calculate Monthly Payment")

    if submitted_non_rental:
        monthly_property_tax = tax_annual_input / 12
        loan_amount = purchase_price - down_payment
        monthly_mortgage = mortgage_payment_calc(loan_amount, interest_rate, loan_term_years)
        total_monthly_payment = monthly_mortgage + monthly_property_tax

        st.markdown("### 💼 Payment Breakdown")
        st.write(f"**🏦 Mortgage Payment:** ${monthly_mortgage:,.2f}")
        st.write(f"**🏛️ Property Tax:** ${monthly_property_tax:,.2f}")
        st.success(f"**💰 Total Monthly Payment:** ${total_monthly_payment:,.2f}")

        if gross_income:
            housing_ratio = (total_monthly_payment / gross_income * 100)
            st.info(f"Housing Cost Ratio: {housing_ratio:.1f}% of income")
            if housing_ratio < 30:
                st.success("✅ Affordable")
            elif housing_ratio < 40:
                st.warning("⚠️ Borderline")
            else:
                st.error("❌ May be unaffordable")


        # --- Mortgage Payoff Chart ---
        st.markdown("### 📊 Mortgage Payoff Chart")

        schedule_df = amortization_schedule(loan_amount, interest_rate, loan_term_years)
        months = schedule_df["Month"]
        principal = schedule_df["Principal"]
        interest = schedule_df["Interest"]
        balance = schedule_df["Balance"]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=months,
            y=principal,
            name="Principal",
            marker_color="green"
        ))
        fig.add_trace(go.Bar(
            x=months,
            y=interest,
            name="Interest",
            marker_color="red"
        ))
        fig.add_trace(go.Scatter(
            x=months,
            y=balance,
            name="Remaining Balance",
            line=dict(color="blue", width=3),
            yaxis="y2"
        ))

        fig.update_layout(
            title="Mortgage Payment Breakdown Over Time",
            xaxis_title="Month",
            yaxis=dict(title="Monthly Payment"),
            yaxis2=dict(
                title="Remaining Balance",
                overlaying="y",
                side="right",
                showgrid=False
            ),
            barmode="stack",
            legend=dict(x=0.01, y=0.99),
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

        # --- FHA Loan & Debt-to-Income Check ---
        st.markdown("### 🧮 Debt-to-Income & FHA Eligibility")

        monthly_property_tax = tax_annual_input / 12
        monthly_insurance = st.number_input("Estimated Monthly Home Insurance ($)", 0, 2000, 100)
        pmi = 0
        if down_payment_percent < 20:
            pmi = 0.008 * loan_amount / 12  # Est. PMI at 0.8% annually
            st.info(f"Estimated PMI Added: ${pmi:,.2f}/mo")

        fha_max_dti = 0.43  # 43%
        total_payment = monthly_mortgage + monthly_property_tax + monthly_insurance + pmi
        dti_ratio = (total_payment / gross_income) if gross_income else 0

        st.write(f"**Estimated Total Monthly Payment (PITI + PMI):** ${total_payment:,.2f}")
        st.write(f"**Debt-to-Income Ratio:** {dti_ratio * 100:.1f}%")

        if dti_ratio < 0.31:
            st.success("✅ Well below FHA limit (31% front-end)")
        elif dti_ratio < fha_max_dti:
            st.warning("⚠️ Acceptable, but close to FHA limit (43%)")
        else:
            st.error("❌ May exceed FHA affordability guidelines")


# --- INLINE TOOLTIP HELPER ---
def info_label(label, tooltip):
    return f"<span style='font-weight:bold'>{label}</span> <span title='{tooltip}' style='cursor: help'>ℹ️</span>"

# --- EXAMPLE USE OF TOOLTIPS ON OUTPUTS ---
if mode == "Basic (Non-Rental)" and 'submitted_non_rental' in locals() and submitted_non_rental:

    st.markdown("### 🧾 Key Terms (With Tooltips)")

    st.markdown(info_label("PMI", "Private Mortgage Insurance — required if down payment is under 20%"), unsafe_allow_html=True)
    st.markdown(info_label("DTI", "Debt-to-Income Ratio — percent of your gross income going toward monthly debt obligations"), unsafe_allow_html=True)
    st.markdown(info_label("PITI", "Principal, Interest, Taxes, and Insurance — full monthly housing cost"), unsafe_allow_html=True)

if mode in ["Basic (With Rent)", "Advanced"] and st.session_state.get("Calculate"):

    st.markdown("### 📘 Glossary for Investment Metrics")

    glossary_terms = {
        "IRR": "Internal Rate of Return — annualized return accounting for timing of cash flows.",
        "NPV": "Net Present Value — value of future profits in today's dollars minus your investment.",
        "Cash Flow": "Net income each month after expenses and debt payments.",
        "Cap Rate": "Capitalization Rate — Net Operating Income ÷ Purchase Price.",
        "Vacancy Rate": "Estimated % of time property is unoccupied.",
        "Management Fee": "Percent of rent paid to property managers.",
        "Rent Growth Rate": "Expected yearly increase in rent.",
        "Maintenance": "Estimated monthly cost for upkeep as % of rent.",
        "Operating Expenses": "Total monthly property costs excluding mortgage.",
    }

    for term, tip in glossary_terms.items():
        st.markdown(info_label(term, tip), unsafe_allow_html=True)


# --- Break-Even Calculator ---
        st.markdown("### 🔄 Break-Even Point")

        cumulative_cf = np.cumsum(cash_flows)
        breakeven_month = next((i+1 for i, val in enumerate(cumulative_cf) if val >= down_payment), None)

        if breakeven_month:
            breakeven_years = breakeven_month / 12
            st.success(f"💸 Break-even reached in {breakeven_month} months ({breakeven_years:.1f} years)")
        else:
            st.warning("⚠️ Property does not break even within the selected projection period.")

# --- Equity Growth Projection ---
        st.markdown("### 📈 Equity Growth Over Time")

        appreciation_rate = st.number_input("Property Appreciation Rate (% per year)", 0.0, 15.0, 3.0,
                                            help="Expected annual increase in property value.")
        equity_list = []
        balance_list = schedule["Balance"]
        for i in range(len(balance_list)):
            year_fraction = i / 12
            est_home_value = purchase_price * ((1 + appreciation_rate / 100) ** year_fraction)
            equity = est_home_value - balance_list[i]
            equity_list.append(equity)

        months = list(range(1, len(balance_list)+1))
        st.plotly_chart(
            plot_line_chart(months, equity_list, "Projected Home Equity Over Time", "Equity ($)", "#ff7f0e"),
            use_container_width=True
        )

    
with st.expander("📖 Legend: Key Terms Explained", expanded=False):
        st.markdown("""
    Appraisal - A professional estimate of a properties market value.

    Cap Rate (Capitalization Rate) -  The annual Net Operating Income divided by the purchase price, showing the property's yield ignoring financing.

    Cash Flow -	Money left over each month after all expenses and debt payments.

    Cash on Cash Return -	Annual cash flow divided by your actual cash invested (down payment), showing your cash yield.

    Closing Costs -	Fees paid at the final step of a real estate transaction (e.g., title, lender fees, taxes).

    Comps (Comparables) - Recently sold similar properties used to determine a property's value.

    Depreciation - A tax deduction that spreads out the cost of a property over its useful life.

    Equity - The portion of the property you truly own: Market Value - Loan Balance.

    Escrow - A neutral third-party account holding funds/documents during a transaction.

    Gross Rent Multiplier (GRM)	- Ratio of property price to gross annual rent; used for quick valuation.

    Hard Money Loan	Short-term - high-interest loan secured by real estate, often used by flippers.

    HOA (Homeowners Association) -	Organization managing a community and collecting fees for upkeep.

    Inflation Rate - Annual increase in expenses and costs.

    Internal Rate of Return (IRR) - The annualized return earned on an investment over time, accounting for timing of cash flows.

    Leverage - Using borrowed money to increase the potential return of an investment.

    Loan-to-Value (LTV)	- Ratio of loan amount to property value. High LTV means more risk for lenders.

    Maintenance - Percentage of rent set aside for upkeep and repairs.

    Management Fee - Percentage of rent paid to a property manager.

    Net Operating Income (NOI) - Income from rent minus operating expenses (taxes, insurance, maintenance), excluding mortgage costs.

    Net Present Value (NPV) - The total value today of future cash flows minus the initial investment, used to evaluate profitability.

    Operating Expenses - Costs to run the property (e.g., insurance, taxes, maintenance, management).

    Payback Period - Time it takes to recoup your initial investment (down payment) from cash flows.

    Principal - The base amount of your loan, not including interest.

    Private Mortgage Insurance (PMI) - Insurance added to monthly payments when your down payment is <20%.

    Rehab - Renovating a property to improve value or condition.

    Rent Growth Rate - Expected annual increase in rent charged.

    ROI (Return on Investment) - Percentage gain or loss on your investment over time, including cash flow and equity gains.

    Title - Legal documentation showing who owns a property.

    Vacancy Rate - Percentage of time the property is expected to be unoccupied.

        """)
