import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import numpy_financial as npf
import re

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="🏨 Rental Analyzer UI", layout="wide")
st.title("🏠 Rental Property Investment Analyzer")
st.subheader("Made By: Jacob Klingman.")

# --- ADDRESS LOOKUP TAB ---
with st.expander("📍 One-Line Address Lookup"):
    full_address_input = st.text_input("Enter Full Address", placeholder="123 Main St, Dallas, TX 75201")
    if full_address_input:
        st.markdown(f"**📍 You entered:** {full_address_input}")
        maps_url = f"https://www.google.com/maps/search/{full_address_input.replace(' ', '+')}"

        zip_rent_map = {
            "58104": 1300, "58103": 1100, "58102": 1200, "58047": 2300,
            "58105": 1100, "58109": 950, "58125": 1000, "58122": 950,
            "58124": 900, "58123": 900,
        }
        zip_match = re.search(r"(\d{5})", full_address_input)
        if zip_match:
            zip_code = zip_match.group(1)
            avg_rent = zip_rent_map.get(zip_code)
            if avg_rent:
                st.info(f"💰 Estimated average rent for ZIP {zip_code}: ${avg_rent:,.0f}")
            else:
                st.warning(f"No rent data available for ZIP {zip_code}.")
        st.markdown(f"[🗘️ View on Google Maps]({maps_url})")

# --- HELPER FUNCTIONS ---
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
    df = pd.DataFrame(schedule)
    dollar_cols = ["Payment", "Principal", "Interest", "Balance"]
    df[dollar_cols] = df[dollar_cols].applymap(lambda x: f"${x:,.2f}")
    return df

def calculate_cashflows(purchase_price, down_payment, loan_amount, loan_term_years, interest_rate,
                        monthly_expenses, current_rent, vacancy_rate, mgmt_fee_percent, maintenance_percent,
                        tax_annual, insurance_annual, hoa_monthly, rent_growth_percent, inflation_percent,
                        years=5, include_mortgage=True, include_expenses=True):
    months = years * 12
    schedule = amortization_schedule(loan_amount, interest_rate, loan_term_years) if include_mortgage else pd.DataFrame()
    cash_flows = []
    rents = []
    for month in range(1, months + 1):
        rent = current_rent * ((1 + rent_growth_percent / 100 / 12) ** month)
        rents.append(rent)
        vacancy_loss = rent * (vacancy_rate / 100)
        mgmt_fee = rent * (mgmt_fee_percent / 100)
        maintenance = rent * (maintenance_percent / 100)
        monthly_tax = tax_annual / 12
        monthly_insurance = insurance_annual / 12

        expenses = sum([
            monthly_expenses, vacancy_loss, mgmt_fee,
            maintenance, monthly_tax, monthly_insurance, hoa_monthly
        ])
        mortgage_payment = mortgage_payment_calc(loan_amount, interest_rate, loan_term_years) if include_mortgage else 0
        total_expenses = expenses + mortgage_payment if include_expenses else 0
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

def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# --- USER INPUTS ---
mode = st.radio("Calculation Mode", ["Basic (Non-Rental)", "Basic (With Rent)", "Advanced"], horizontal=True)
st.subheader("📄 Property Inputs")
col1, col2, col3 = st.columns(3)
with col1:
    purchase_price = st.number_input("Purchase Price ($)", 50000, 2000000, 300000)
with col2:
    down_payment_percent = st.number_input("Down Payment (% of Purchase Price)", 0.0, 100.0, 20.0)
    down_payment = purchase_price * (down_payment_percent / 100)
with col3:
    loan_term_years = st.number_input("Loan Term (years)", 5, 40, 30)
col4, col5 = st.columns(2)
with col4:
    interest_rate = st.number_input("Interest Rate (%)", 0.0, 10.0, 6.5)

# --- DEFAULTS ---
current_rent = tax_annual = insurance_annual = vacancy_rate = monthly_expenses = 0
mgmt_fee_percent = maintenance_percent = hoa_monthly = rent_growth_percent = inflation_percent = discount_rate = 0

if mode in ["Basic (With Rent)", "Advanced"]:
    st.subheader("💵 Rental Income")
    col6, col7 = st.columns(2)
    with col6:
        current_rent = st.number_input("Monthly Rent ($)", 0, 20000, 2200)
    with col7:
        tax_annual = st.number_input("Annual Property Tax ($)", 0, 20000, 3500)
        insurance_annual = st.number_input("Annual Insurance ($)", 0, 10000, 1200)

    optional_zip = st.text_input("Optional: Enter ZIP Code for Rent Comparison")
    zip_rent_map = {
        "58104": 1300, "58103": 800, "58102": 995, "58047": 2300,
        "58105": 1100, "58109": 950, "58125": 1000, "58122": 950,
        "58124": 900, "58123": 900,
    }
    avg_rent = zip_rent_map.get(optional_zip.strip(), None)
    if optional_zip and avg_rent:
        st.subheader("🏨 Rent Quality Check")
        diff = current_rent - avg_rent
        if abs(diff) <= 0.1 * avg_rent:
            st.success(f"✅ Rent of ${current_rent:,.0f} is close to average (${avg_rent:,.0f}) for ZIP {optional_zip}.")
        elif current_rent > avg_rent:
            st.warning(f"⚠️ Rent of ${current_rent:,.0f} is above average (${avg_rent:,.0f}) for ZIP {optional_zip}.")
        else:
            st.error(f"🔻 Rent of ${current_rent:,.0f} is below average (${avg_rent:,.0f}) for ZIP {optional_zip}.")

if mode == "Advanced":
    st.subheader("⚙️ Advanced Settings")
    col8, col9, col10 = st.columns(3)
    with col8:
        vacancy_rate = st.number_input("Vacancy Rate (%)", 0.0, 100.0, 5.0)
    with col9:
        mgmt_fee_percent = st.number_input("Management Fee (%)", 0.0, 20.0, 8.0)
    with col10:
        maintenance_percent = st.number_input("Maintenance (% of Rent)", 0.0, 20.0, 5.0)
    col11, col12, col13 = st.columns(3)
    with col11:
        monthly_expenses = st.number_input("Other Monthly Expenses ($)", 0, 5000, 200)
    with col12:
        hoa_monthly = st.number_input("Monthly HOA Fees ($)", 0, 1000, 150)
    with col13:
        discount_rate = st.number_input("Discount Rate for NPV (%)", 0.0, 20.0, 8.0)
    col14, col15 = st.columns(2)
    with col14:
        rent_growth_percent = st.number_input("Rent Growth Rate (% per year)", 0.0, 10.0, 2.5)
    with col15:
        inflation_percent = st.number_input("Inflation Rate (% per year)", 0.0, 10.0, 2.0)

# --- CALCULATE & OUTPUT ---
loan_amount = purchase_price - down_payment



if mode == "Basic (Non-Rental)":
    st.subheader("📘 Mortgage & Homebuyer Summary")

    # Calculate loan amount and monthly payments
    loan_amount = purchase_price - down_payment
    tax_annual = st.number_input("Annual Property Tax ($)", 0, 20000, 3000)
    monthly_property_tax = tax_annual / 12
    monthly_mortgage = mortgage_payment_calc(loan_amount, interest_rate, loan_term_years)
    total_monthly_payment = monthly_mortgage + monthly_property_tax

    # Optional: Gross monthly income for affordability check
    gross_income = st.number_input("Your Gross Monthly Income ($)", 0, 50000, 8000)
    housing_ratio = (total_monthly_payment / gross_income * 100) if gross_income else 0

    st.markdown("### 💰 Monthly Payment Breakdown")
    st.write(f"**🏦 Mortgage Payment:** ${monthly_mortgage:,.2f}")
    st.write(f"**🏛️ Property Tax:** ${monthly_property_tax:,.2f}")
    st.success(f"**💰 Total Monthly Payment:** ${total_monthly_payment:,.2f}")

    st.markdown("### 🧾 Loan Summary")
    st.write(f"**Purchase Price:** ${purchase_price:,.0f}")
    st.write(f"**Down Payment ({down_payment_percent:.1f}%):** ${down_payment:,.0f}")
    st.write(f"**Loan Amount:** ${loan_amount:,.0f}")
    st.write(f"**Interest Rate:** {interest_rate:.2f}%")
    st.write(f"**Loan Term:** {loan_term_years} years")

    st.markdown("### 💼 Upfront Cost Estimate")
    closing_cost_percent = st.slider("Estimated Closing Costs (% of Purchase Price)", 1.0, 5.0, 3.0)
    closing_costs = purchase_price * (closing_cost_percent / 100)
    total_upfront = down_payment + closing_costs
    st.write(f"**Estimated Closing Costs:** ${closing_costs:,.0f}")
    st.success(f"**Total Cash Needed at Purchase:** ${total_upfront:,.0f}")

    if gross_income:
        st.markdown("### 🧮 Affordability Check")
        st.write(f"**Housing Cost Ratio:** {housing_ratio:.1f}% of income")
        if housing_ratio < 30:
            st.success("✅ Within typical affordability range (under 30%).")
        elif housing_ratio < 40:
            st.warning("⚠️ Borderline affordability (30–40%).")
        else:
            st.error("❌ Monthly payment may be unaffordable (above 40%).")
projection_years = st.slider("Projection Duration (Years)", 1, 30, 5)
if st.button("🔍 Calculate") and mode in ["Basic (With Rent)", "Advanced"]:
    results = calculate_cashflows(
    purchase_price, down_payment, loan_amount, loan_term_years, interest_rate,
    monthly_expenses, current_rent, vacancy_rate, mgmt_fee_percent, maintenance_percent,
    tax_annual, insurance_annual, hoa_monthly, rent_growth_percent, inflation_percent,
        years=projection_years
    )
    cash_flows = results["cash_flows"]
    rents = results["rents"]
    schedule = results["schedule"]
    
    st.subheader("📊 Monthly Cash Flow")
    st.plotly_chart(plot_line_chart(list(range(1, len(cash_flows)+1)), cash_flows, "Monthly Cash Flow", "Cash Flow ($)", "#1f77b4"), use_container_width=True)
    
    st.subheader("📉 Rent Projection")
    st.plotly_chart(plot_line_chart(list(range(1, len(rents)+1)), rents, "Projected Rent Income", "Rent ($)", "#2ca02c"), use_container_width=True)
    
    if mode in ["Basic (With Rent)", "Advanced"] and len(cash_flows) >= 12:
     st.subheader("🗕️ Year-by-Year Financial Table")
     monthly_cf = np.array(cash_flows)
     rent_array = np.array(rents)
     years_list = list(range(1, int(len(cash_flows)/12) + 1))
     df_yearly = pd.DataFrame({
     "Year": years_list,
     "Total Rent": [rent_array[i*12:(i+1)*12].sum() for i in range(len(years_list))],
     "Cash Flow": [monthly_cf[i*12:(i+1)*12].sum() for i in range(len(years_list))]
     })
    st.dataframe(df_yearly, use_container_width=True)
    
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
