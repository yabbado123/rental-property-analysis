import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import numpy_financial as npf
from fpdf import FPDF

# -------- Configuration & Styles --------
left, center, right = st.columns([2.25, 2, 0.8])
with center:
    st.image("logo.png", width=160)
st.set_page_config(page_title="🏡 Smart Rental Analyzer", layout="wide")
st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}
html, body {background-color: #f6f9fc; font-family: 'Inter', sans-serif;}
.stButton > button, .stDownloadButton > button {border-radius:8px; font-weight:600;}
</style>
""", unsafe_allow_html=True)

# -------- Top Navigation --------
st.markdown("<h1 style='text-align:center;'>🏡 Smart Rental Analyzer</h1>", unsafe_allow_html=True)
page = st.selectbox(
    "Navigate to:",
    [
        "🏠 Home",
        "📊 Quick Deal Analyzer",
        "💡 Break-Even Calculator",
        "📘 ROI & Projections",
        "💎 Property Comparison (Pro)",
        "🧪 Advanced Analytics (Pro)",
        "🏚 Rehab & Refi (Pro)",
        "📄 Download Reports",
        "📖 Glossary"
    ],
    index=0
)

# -------- Home Page --------

if page == "🏠 Home":
    st.markdown("---")
    cols = st.columns(3)
    cols[0].success("✅ Beginner Friendly")
    cols[1].info("📈 Advanced ROI Tools")
    cols[2].warning("💾 Export & Reports")
    st.markdown("---")
    st.markdown(
        "**Features:** Quick Deal Analyzer, ROI & Projections, Break-Even, CSV/PDF Exports, Premium Pro tools"
    )

    st.markdown("---")
    st.markdown("### 🆚 How We Stack Up Against Competitors")
    comp_data = {
        'Feature': [
            'Quick Deal Analyzer',
            'ROI & Multi-Year Projections',
            'Break-Even Calculator',
            'Deal Score / Rating',
            'Property Comparison',
            'Advanced Analytics Charts',
            'Rehab & Refi Tools',
            'CSV Export',
            'PDF Export',
            'Mobile Friendly',
            'AI Insights'
        ],
        'This app': ['✓','✓','✓','✓','✓','✓','✓','✓','✓','🚧','🚧'],
        'BiggerPockets': ['✓','✓','✗','✗','✗','✗','✗','✓','✗','✓','✗'],
        'Stessa':          ['✗','✓','✗','✗','✗','✗','✗','✓','✗','✓','✗'],
        'Roofstock':       ['✓','✓','✗','✗','✗','✗','✗','✓','✓','✓','✗'],
        'DealCheck':       ['✓','✓','✗','✗','✓','✗','✗','✓','✗','🚧','✗'],
        'Mashvisor':       ['✓','✓','✗','✗','✗','✓','✗','✓','✗','✓','✗'],
        'Rentometer':      ['✓','✗','✗','✗','✗','✗','✗','✗','✗','✓','✗'],
        'Zilculator':      ['✓','✓','✓','✗','✓','✗','✗','✓','✗','✗','✗']
    }
    df_comp = pd.DataFrame(comp_data)
    # Generate alternating row colors
    n_rows = df_comp.shape[0]
    row_colors = [("white" if i % 2 == 0 else "lightgrey") for i in range(n_rows)]
    # Create two columns: logo and table
    table_col, logo_col = st.columns([3,1], gap="small")

    with table_col:
        styled = df_comp.set_index('Feature').style.applymap(
            lambda v: 'color: green;' if v=='✓' else (
                      'color: red;' if v=='✗' else (
                      'color: orange;' if v in ['🚧','Partial'] else '')), 
            subset=df_comp.columns[1:]
        )
        html = styled.set_table_attributes('class="dataframe"').to_html()
        st.markdown(html, unsafe_allow_html=True)






elif page == "📊 Quick Deal Analyzer":
    st.header("📊 Quick Deal Analyzer")
    col1, col2 = st.columns(2)
    with col1:
        price = st.number_input("Purchase Price", value=300000)
        dp_pct = st.slider("Down Payment %", 0, 100, 20)
        ir = st.number_input("Interest Rate %", value=6.5)
    with col2:
        rent = st.number_input("Monthly Rent", value=2200)
        exp = st.number_input("Monthly Expenses", value=300)
        term = st.selectbox("Loan Term (yrs)", [15, 20, 30])
    if st.button("🔍 Analyze Deal"):
        dp = price * dp_pct / 100
        loan = price - dp
        m_pay = npf.pmt(ir/100/12, term * 12, -loan)
        net = rent - exp - m_pay
        st.metric("Monthly Mortgage", f"${m_pay:,.2f}")
        st.metric("Net Monthly Cash Flow", f"${net:,.2f}")
        # Deal Score / Investment Rating
        cap_rate = (rent * 12) / price if price > 0 else 0
        coc_return = (net * 12) / dp if dp > 0 else 0
        score = (cap_rate * 100 * 0.5) + (coc_return * 100 * 0.5)
        rating = (
            "Excellent" if score >= 20 else
            "Good" if score >= 10 else
            "Average" if score >= 5 else
            "Poor"
        )
        st.metric("Deal Score", f"{score:.1f}", delta=rating)
        # Explanation and Improvement Tips
        st.markdown("**How the Deal Score is Calculated:**")
        st.markdown(
            "- **Cap Rate (50%)**: (Annual Rent / Purchase Price) * 100.\n"
            "- **Cash-on-Cash Return (50%)**: (Annual Net Cash Flow / Down Payment) * 100.\n"
            "- The score is the average of these two metrics, scaled to 0–100."
        )
        st.markdown("**Tips to Improve Your Deal Score:**")
        st.markdown(
            "- Increase **Monthly Rent** or project higher rent growth.\n"
            "- Reduce **Monthly Expenses** through efficient management or lower operating costs.\n"
            "- Increase **Down Payment** to improve cash-on-cash return.\n"
            "- Negotiate a lower **Purchase Price** to boost both Cap Rate and Cash-on-Cash Return."
        )

# -------- Break-Even Calculator --------
elif page == "💡 Break-Even Calculator":
    st.header("⚖️ Break-Even Calculator")
    rev = st.number_input("Monthly Revenue", value=5000)
    fc = st.number_input("Fixed Costs", value=2000)
    vc_pct = st.slider("Variable Costs % of Revenue", 0, 100, 30)
    be_rev = fc / (1 - vc_pct / 100) if vc_pct < 100 else 0
    st.metric("Break-Even Revenue", f"${be_rev:,.2f}")

# -------- ROI & Projections --------
elif page == "📘 ROI & Projections":
    st.header("📘 ROI & Multi-Year Projection")
    price = st.number_input("Purchase Price", value=300000, key="roi_price")
    rent = st.number_input("Monthly Rent", value=2200, key="roi_rent")
    exp = st.number_input("Monthly Expenses", value=300, key="roi_exp")
    ir = st.number_input("Discount Rate %", value=6.5, key="roi_ir")
    years = st.slider("Projection Years", 1, 30, 10)
    if st.button("🧮 Calculate ROI"):
        cf = [-price] + [rent - exp for _ in range(years)]
        npv = npf.npv(ir / 100, cf)
        irr = npf.irr(cf)
        dfp = pd.DataFrame({'Year': range(0, years + 1), 'Cash Flow': cf})
        st.line_chart(dfp.set_index('Year'))
        st.metric("NPV", f"${npv:,.2f}")
        st.metric("IRR", f"{irr * 100:.2f}%")

# -------- Property Comparison (Pro) --------
elif page == "💎 Property Comparison (Pro)":
    st.header("📈 Multi-Property Comparison")
    st.write("**Pro Feature**")
    count = st.radio("Number of Properties", [2, 3], horizontal=True)
    cols = st.columns(count)
    props = []
    for i in range(count):
        with cols[i]:
            lbl = f"Property {chr(65 + i)}"
            price = st.number_input(f"Purchase Price ({lbl})", value=300000, key=f"pc_price_{i}")
            dp_pct = st.number_input(f"Down Payment % ({lbl})", value=20.0, key=f"pc_dp_{i}")
            rent = st.number_input(f"Monthly Rent ({lbl})", value=2200, key=f"pc_rent_{i}")
            exp = st.number_input(f"Monthly Expenses ({lbl})", value=300, key=f"pc_exp_{i}")
            props.append({"lbl": lbl, "price": price, "dp": price * dp_pct / 100, "rent": rent, "exp": exp})
    if st.button("Compare"):
        metrics = {"Metric": ["Price", "Down", "Rent", "Exp"]}
        for p in props:
            metrics[p['lbl']] = [f"${p['price']:,}", f"${p['dp']:,}", f"${p['rent']:,}", f"${p['exp']:,}"]
        dfc = pd.DataFrame(metrics)
        st.table(dfc)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.set_font("Arial", style="B", size=14)
        pdf.cell(0, 10, "Property Comparison Report", ln=True, align='C')
        for idx, m in enumerate(metrics["Metric"]):
            line = m + ": " + ", ".join([f"{p['lbl']} {metrics[p['lbl']][idx]}" for p in props])
            pdf.multi_cell(0, 8, line)
        b = pdf.output(dest='S').encode('latin1')
        st.download_button("⬇️ Download PDF", data=b, file_name="comparison.pdf", mime="application/pdf")

# -------- Advanced Analytics (Pro) --------
elif page == "🧪 Advanced Analytics (Pro)":
    st.header("🧪 Advanced Analytics & Forecasting")
    st.markdown("Explore long-term performance with charts, forecasts, and scenario analysis.")

    # 1. 5-Year Forecast: Cash Flow and Equity
    st.subheader("📈 5-Year Forecast")
    years = list(range(1, 6))
    cash_flow = [6000, 7200, 8500, 9000, 9600]  # Placeholder
    equity = [20000, 40000, 65000, 90000, 120000]  # Placeholder

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=years, y=cash_flow, mode='lines+markers', name='Cash Flow'))
    fig1.add_trace(go.Scatter(x=years, y=equity, mode='lines+markers', name='Equity'))
    fig1.update_layout(title="Cash Flow & Equity Growth", xaxis_title="Year", yaxis_title="USD")
    st.plotly_chart(fig1, use_container_width=True)

    # 2. Sensitivity: Rent vs. Cash Flow
    st.subheader("📊 Rent Sensitivity")
    base_expense = 1800
    rent_vals = np.arange(1800, 2800, 100)
    cash_flows = rent_vals - base_expense
    df_sens = pd.DataFrame({'Rent': rent_vals, 'Cash Flow': cash_flows})
    st.line_chart(df_sens.set_index('Rent'))

    # 3. Stress Test Table
    st.markdown("""
    **Stress Test Legend**  
    - **Vacancy %**: How often your unit is unoccupied over a year.  
    - **Maintenance %**: What percent of rent you reserve for ongoing repairs and upkeep.
    """)
    st.subheader("📉 Vacancy & Expense Stress Test")
    vacancies = [0.0, 0.05, 0.1, 0.15]
    maint_pct = [0.05, 0.1, 0.15]
    rent = 2400
    base_operating = 800
    stress_data = []
    for v in vacancies:
        row = []
        for m in maint_pct:
            effective_income = rent * (1 - v)
            expenses = base_operating + (rent * m)
            net = effective_income - expenses
            row.append(round(net, 2))
        stress_data.append(row)
    stress_df = pd.DataFrame(stress_data, columns=[f"{int(p*100)}% Maint" for p in maint_pct], index=[f"{int(v*100)}% Vac" for v in vacancies])
    st.dataframe(stress_df)

# -------- Rehab & Refi (Pro) --------
elif page == "🏚 Rehab & Refi (Pro)":
    st.header("🏚 Renovation & Refinance Tools")
    st.write("**Pro Feature**: Rehab ROI & refinance projections.")

    # 🛠️ Renovation / Rehab ROI Calculator
    with st.expander("🛠️ Renovation / Rehab ROI Calculator", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            purchase_price = st.number_input("Purchase Price ($)", min_value=0, value=300000)
            down_pct = st.slider("Down Payment %", 0, 100, 20)
            down_payment = purchase_price * down_pct/100
            rehab_cost = st.number_input("Rehab Cost ($)", min_value=0, value=25000, step=1000)
        with col2:
            loan_amount = st.number_input("Outstanding Loan Balance ($)", min_value=0, value=int(purchase_price-down_payment))
            arv = st.number_input("After-Repair Value (ARV) ($)", min_value=0, value=int(purchase_price*1.1), step=1000)
            rehab_months = st.slider("Months Until Rehab Complete", 1, 24, 6)

        total_invested = down_payment + rehab_cost
        equity_after = arv - loan_amount
        post_rehab_roi = ((equity_after - total_invested) / total_invested) * 100 if total_invested else 0

        st.metric("💸 Total Invested", f"${total_invested:,.0f}")
        st.metric("🏡 Equity After Rehab", f"${equity_after:,.0f}")
        st.metric("📈 Post-Rehab ROI", f"{post_rehab_roi:.1f}%")

    # 🔄 Refinance Scenario Explorer
    with st.expander("🔄 Refinance Scenario Explorer", expanded=False):
        col3, col4 = st.columns(2)
        with col3:
            refi_after = st.slider("Refinance After (Months)", 1, 360, 12)
            new_rate = st.number_input("New Interest Rate (%)", 0.0, 15.0, 5.0)
        with col4:
            new_term = st.selectbox("New Loan Term (Years)", [15, 20, 30], index=2)
            cash_out = st.number_input("Cash-Out Amount ($)", min_value=0, value=0, step=1000)

        new_principal = loan_amount + cash_out
        new_payment = npf.pmt(new_rate/100/12, new_term*12, -new_principal)

        st.metric("🧾 New Monthly Payment", f"${new_payment:,.2f}")
        st.metric("💳 New Loan Amount", f"${new_principal:,.0f}")
        st.metric("💵 Cash Pulled Out", f"${cash_out:,.0f}")
elif page == "📄 Download Reports":
    st.header("📄 Export Data")
    if 'dfp' in locals():
        st.download_button("Download Projection CSV", dfp.to_csv(index=False), "projection.csv")
    if st.button("Generate PDF Report"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 12)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Smart Rental Analyzer Report", ln=True, align='C')
        pdf.output("report.pdf")
        st.success("report.pdf created")

# -------- Glossary --------
if page == "📖 Glossary":
    st.header("📖 Real Estate & Investment Glossary")
    glossary = {
        "Appraisal": "A professional estimate of a property's market value.",
        "Cap Rate (Capitalization Rate)": "The annual Net Operating Income divided by the purchase price, showing the property's yield ignoring financing.",
        "Cash Flow": "Money left over each month after all expenses and debt payments.",
        "Cash on Cash Return": "Annual cash flow divided by your actual cash invested (down payment), showing your cash yield.",
        "Closing Costs": "Fees paid at the final step of a real estate transaction (e.g., title, lender fees, taxes).",
        "Comps (Comparables)": "Recently sold similar properties used to determine a property's value.",
        "Depreciation": "A tax deduction that spreads out the cost of a property over its useful life.",
        "Equity": "The portion of the property you truly own: Market Value - Loan Balance.",
        "Escrow": "A neutral third-party account holding funds/documents during a transaction.",
        "Gross Rent Multiplier (GRM)": "Ratio of property price to gross annual rent; used for quick valuation.",
        "Hard Money Loan": "Short-term, high-interest loan secured by real estate, often used by flippers.",
        "HOA (Homeowners Association)": "Organization managing a community and collecting fees for upkeep.",
        "Inflation Rate": "Annual increase in expenses and costs.",
        "Internal Rate of Return (IRR)": "The annualized return earned on an investment over time, accounting for timing of cash flows.",
        "Leverage": "Using borrowed money to increase the potential return of an investment.",
        "Loan-to-Value (LTV)": "Ratio of loan amount to property value. High LTV means more risk for lenders.",
        "Maintenance": "Percentage of rent set aside for upkeep and repairs.",
        "Management Fee": "Percentage of rent paid to a property manager.",
        "Net Operating Income (NOI)": "Income from rent minus operating expenses (taxes, insurance, maintenance), excluding mortgage costs.",
        "Net Present Value (NPV)": "The total value today of future cash flows minus the initial investment, used to evaluate profitability.",
        "Operating Expenses": "Costs to run the property (e.g., insurance, taxes, maintenance, management).",
        "Payback Period": "Time it takes to recoup your initial investment (down payment) from cash flows.",
        "PMI (Private Mortgage Insurance)": "Insurance added to monthly payments when your down payment is <20%.",
        "Principal": "The base amount of your loan, not including interest.",
        "Rehab": "Renovating a property to improve value or condition.",
        "Rent Growth Rate": "Expected annual increase in rent charged.",
        "ROI (Return on Investment)": "Percentage gain or loss on your investment over time, including cash flow and equity gains.",
        "Title": "Legal documentation showing who owns a property.",
        "Vacancy Rate": "Percentage of time the property is expected to be unoccupied."
    }
    for term in sorted(glossary.keys()):
        st.markdown(f"**{term}**: {glossary[term]}")
