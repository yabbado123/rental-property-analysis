

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import numpy_financial as npf
import re

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="🏘️ Rental Analyzer UI", layout="wide")
st.title("🏠 Rental Property Investment Analyzer")
st.subheader("Made By: Jacob Klingman.")

# --- ADDRESS LOOKUP TAB ---
with st.expander("📍 One-Line Address Lookup"):
    full_address_input = st.text_input("Enter Full Address", placeholder="123 Main St, Dallas, TX 75201")
    if full_address_input:
        st.markdown(f"**📍 You entered:** {full_address_input}")
        maps_url = f"https://www.google.com/maps/search/{full_address_input.replace(' ', '+')}"

        zip_rent_map = {
       
            "58104": 1300,
            "58103": 1100,
            "58102": 1200,
            "58047": 2300,
            "58105": 1100,
            "58109": 950,
            "58125": 1000,
            "58122": 950,
            "58124": 900,
            "58123": 900,
        }
        zip_match = re.search(r"(\d{5})", full_address_input)
        if zip_match:
            zip_code = zip_match.group(1)
            avg_rent = zip_rent_map.get(zip_code)
            if avg_rent:
                st.info(f"💰 Estimated average rent for ZIP {zip_code}: ${avg_rent:,.0f}")
            else:
                st.warning(f"No rent data available for ZIP {zip_code}.")
        st.markdown(f"[🗺️ View on Google Maps]({maps_url})")



    


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
        monthly_tax = tax_annual / 12
        monthly_insurance = insurance_annual / 12

        expenses = sum([
        monthly_expenses, vacancy_loss, mgmt_fee,
        maintenance, monthly_tax, monthly_insurance, hoa_monthly
      ])
    return {"cash_flows": cash_flows, "rents": rents, "schedule": schedule}

def calculate_irr(cash_flows, down_payment):
    try:
        irr = npf.irr([-down_payment] + list(cash_flows))
        if irr is None or np.isnan(irr):
            return None
        return irr * 100
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

def plot_area_chart(x, y, title, yaxis_title, color):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', fill='tozeroy', line=dict(color=color, width=3)))
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
with col5:
    years = st.number_input("Projection Period (years)", 1, 30, 5)

# --- DEFAULTS ---
current_rent = tax_annual = insurance_annual = vacancy_rate = monthly_expenses = 0
mgmt_fee_percent = maintenance_percent = hoa_monthly = rent_growth_percent = inflation_percent = discount_rate = 0

if mode in ["Basic (With Rent)", "Advanced"]:
        st.subheader("💵 Rental Income")
        col6, col7 = st.columns(2)
        with col6:
            current_rent = st.number_input("Monthly Rent ($)", 0, 20000, current_rent or 2200)
        with col7:
            tax_annual = st.number_input("Annual Property Tax ($)", 0, 20000, 3500)
            insurance_annual = st.number_input("Annual Insurance ($)", 0, 10000, 1200)

        # Optional rent comparison check
        zip_rent_map = {
            "58104": 1300,
            "58103": 800,
            "58102": 995,
            "58047": 2300,
            "58105": 1100,
            "58109": 950,
            "58125": 1000,
            "58122": 950,
            "58124": 900,
            "58123": 900,
        }

        optional_zip = st.text_input("Optional: Enter ZIP Code for Rent Comparison")
        avg_rent = zip_rent_map.get(optional_zip.strip(), None)
        if optional_zip and avg_rent:
            st.subheader("🏘️ Rent Quality Check")
            diff = current_rent - avg_rent
            if abs(diff) <= 0.1 * avg_rent:
                st.markdown(f"""
                    <div style='color:#0c4128;background:#d1e7dd;padding:10px;border-radius:5px;'>
                        ✅ Rent of ${current_rent:,.0f} is close to the average for ZIP {optional_zip}.<br>
                        Average rent: ${avg_rent:,.0f}
                    </div>
                """, unsafe_allow_html=True)
            elif current_rent > avg_rent:
                st.markdown(f"""
                    <div style='color:#664d03;background:#fff3cd;padding:10px;border-radius:5px;'>
                        ⚠️ Rent of ${current_rent:,.0f} is above average for ZIP {optional_zip}.<br>
                        Average rent: ${avg_rent:,.0f}
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div style='color:#842029;background:#f8d7da;padding:10px;border-radius:5px;'>
                        🔻 Rent of ${current_rent:,.0f} is below average for ZIP {optional_zip}.<br>
                        Average rent: ${avg_rent:,.0f}
                    </div>
                """, unsafe_allow_html=True)
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

# --- CALCULATIONS ---
loan_amount = purchase_price - down_payment
results = calculate_cashflows(
    purchase_price, down_payment, loan_amount, loan_term_years, interest_rate,
    monthly_expenses, current_rent, vacancy_rate, mgmt_fee_percent, maintenance_percent,
    tax_annual, insurance_annual, hoa_monthly, rent_growth_percent, inflation_percent,
    years=years
)
cash_flows = results["cash_flows"]
rents = results["rents"]
schedule = results["schedule"]
st.write("Down Payment:", down_payment)
irr = calculate_irr(cash_flows, down_payment)
npv = calculate_npv(cash_flows, down_payment, discount_rate)

if mode in ["Basic (With Rent)", "Advanced"]:
            with st.expander("📈 Break-Even Calculator"):
                cumulative_cash_flow = np.cumsum(cash_flows)
                break_even_month = next((i for i, total in enumerate(cumulative_cash_flow, start=1) if total >= down_payment), None)

                if break_even_month:
                    years_to_break_even = break_even_month / 12
                    st.success(f"Break-even in {years_to_break_even:.1f} years (Month {break_even_month})")
                    st.plotly_chart(
                        plot_line_chart(
                            list(range(1, len(cumulative_cash_flow)+1)),
                            cumulative_cash_flow,
                            "Cumulative Cash Flow",
                            "Cumulative $",
                            "#ff7f0e"
                        ),
                        use_container_width=True
                    )
                else:
                    st.warning("This investment does not break even within the selected projection period.")

                    # Estimate minimum rent to break even
                    estimated_rent_needed = current_rent
                    for rent_test in range(int(current_rent), int(current_rent * 2)):
                        test_results = calculate_cashflows(
                            purchase_price, down_payment, loan_amount, loan_term_years, interest_rate,
                            monthly_expenses, rent_test, vacancy_rate, mgmt_fee_percent, maintenance_percent,
                            tax_annual, insurance_annual, hoa_monthly, rent_growth_percent, inflation_percent,
                            years=years
                        )
                        cumulative_cf = np.cumsum(test_results["cash_flows"])
                        if len(cumulative_cf) > 0 and cumulative_cf[-1] >= down_payment:
                            estimated_rent_needed = rent_test
                            break

                    st.info(f"💡 Estimated rent needed to break even in {years} years: **${estimated_rent_needed:,.0f}/month**")



if not schedule.empty:
    st.subheader("📋 Mortgage Schedule")
    st.dataframe(schedule)
    csv = convert_df_to_csv(schedule)
    st.download_button("Download Schedule as CSV", csv, "amortization_schedule.csv", "text/csv")

 
def calculate_irr(cash_flows, down_payment):
    try:
        irr = npf.irr([-down_payment] + list(cash_flows))
        if irr is None or np.isnan(irr):
            return None
        return irr * 100
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

def plot_area_chart(x, y, title, yaxis_title, color):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', fill='tozeroy', line=dict(color=color, width=3)))
    fig.update_layout(title=title, xaxis_title='Months', yaxis_title=yaxis_title, template='plotly_white')
    return fig

def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

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
