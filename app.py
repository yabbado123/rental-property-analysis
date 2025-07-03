import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import numpy_financial as npf
from fpdf import FPDF



# ── DARK / LIGHT MODE TOGGLE =====================================================
is_dark = st.toggle("🌗 Dark Mode", value=True)

if is_dark:
    st.markdown("""
    <style>

    /* ========== GLOBAL ========== */
    html, body, [data-testid="stApp"] {
        background-color: #0E1117 !important;
        color: white !important;
    }
    * { color: white !important; }   /* force‑white text everywhere */

    /* ========== GENERIC INPUTS ========== */
    input, textarea, select {
        background-color: #262730 !important;
        color: white !important;
        border: 1px solid #444 !important;
        border-radius: 6px !important;
    }
    input[type="number"]::-webkit-inner-spin-button,
    input[type="number"]::-webkit-outer-spin-button {      /* Chrome spinners */
        background: #262730 !important;
        color: white !important;
        border: none !important;
    }
    input[type="number"] { -moz-appearance: textfield; }   /* Firefox spinner */

    /* ========== BASEWEB WRAPPERS (Streamlit widgets) ========== */
    /* Number, text, password etc. */
    div[data-baseweb="input"]            ,
    /* TextArea */
    div[data-baseweb="textarea"]         ,
    /* Select trigger (closed state) */
    div[data-baseweb="select"]           {
        background-color: #262730 !important;
        color: white           !important;
        border: 1px solid #444 !important;
        border-radius: 6px      !important;
    }

    /* Actual <input> or <textarea> inside those wrappers */
    div[data-baseweb="input"]    input ,
    div[data-baseweb="textarea"] textarea ,
    div[data-baseweb="select"]   input  {
        background-color: #262730 !important;
        color: white !important;
    }

    /* Dropdown list box & items */
    ul[role="listbox"]                     { background:#262730 !important; }
    ul[role="listbox"] > li               { background:#262730 !important; }
    ul[role="listbox"] > li:hover         { background:#444    !important; }

    /* Dropdown / number‑input SVG icons (chevron, + / – buttons) */
    div[data-baseweb="select"] svg ,
    div[data-baseweb="input"]  svg         { fill: white !important; }

    /* ========== BUTTONS ========== */
    .stButton > button ,
    .stDownloadButton > button {
        background:#262730 !important;
        color:white          !important;
        border:none          !important;
        border-radius:6px    !important;
    }

    /* ========== CHART & TABLE BACKGROUNDS ========== */
    .plot-container                    ,
    .js-plotly-plot .svg-container     ,
    .stPlotlyChart                     ,
    table , th , td                    {
        background-color:#0E1117 !important;
    }

    </style>
    """, unsafe_allow_html=True)

else:
    # --- light mode =========================================================
    st.markdown("""
    <style>
    html, body, [data-testid="stApp"] {
        background-color:#f5f5f5;
        color:#111;
    }
    /* light wrappers */
    div[data-baseweb="input"],
    div[data-baseweb="textarea"],
    div[data-baseweb="select"],
    input, textarea, select {
        background:#ffffff !important;
        color:#111     !important;
        border:1px solid #ccc !important;
        border-radius:6px     !important;
    }
    </style>
    """, unsafe_allow_html=True)






# -------- Configuration & Styles --------
left, center, right = st.columns([2.25, 2, 0.8])
with center:
    st.image("logo.png", width=160)
st.set_page_config(page_title="🏡 Smart Rental Analyzer", layout="wide")
st.markdown("<p style='text-align:center; font-size:14px; color:gray;'>Created by Jacob Klingman</p>", unsafe_allow_html=True)

st.markdown("### 📬 Contact Me")
st.markdown(""" 
**📧 Email:** [smart-rental-analyzer@outlook.com](mailto:smart-rental-analyzer@outlook.com)  
""")




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
        'S.R.A': ['✅','✅','✅','✅','✅','✅','✅','✅','✅','🚧','🚧'],
        'BiggerPockets': ['✅','✅','❌','❌','❌','❌','❌','✅','❌','✅','❌'],
        'Stessa':          ['❌','✅','❌','❌','❌','❌','❌','✅','❌','✅','❌'],
        'Roofstock':       ['✅','✅','❌','❌','❌','❌','❌','✅','✅','✅','❌'],
        'DealCheck':       ['✅','✅','❌','❌','✅','❌','❌','✅','❌','🚧','❌'],
        'Mashvisor':       ['✅','✅','❌','❌','❌','✅','❌','✅','❌','✅','❌✗'],
        'Rentometer':      ['✅','❌','❌','❌','❌','❌','❌','❌','❌','✅','❌'],
        'Zilculator':      ['✅','✅','✅','❌','✅','❌','❌','✅','❌','❌','❌']
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
    st.markdown("Evaluate your deal with just a few inputs and see your score on a 0–100 scale.")

    col1, col2 = st.columns(2)
    with col1:
        purchase_price = st.number_input("Purchase Price ($)", value=250000)
        monthly_rent = st.number_input("Monthly Rent ($)", value=2200)
    with col2:
        monthly_expenses = st.number_input("Monthly Expenses ($)", value=1400)
        down_payment_pct = st.slider("Down Payment (%)", 0, 100, 20)

    annual_cashflow = (monthly_rent - monthly_expenses) * 12
    down_payment = purchase_price * down_payment_pct / 100
    roi = (annual_cashflow / down_payment) * 100 if down_payment else 0
    cap_rate = (annual_cashflow / purchase_price) * 100 if purchase_price else 0

    # --- Deal Score Calculation ---
    roi_score = min(roi / 20 * 30, 30)
    cashflow_score = min((monthly_rent - monthly_expenses) / 300 * 30, 30)
    cap_score = min(cap_rate / 10 * 20, 20)
    bonus_score = 10 if roi > 10 and (monthly_rent - monthly_expenses) > 250 else 0
    deal_score = roi_score + cashflow_score + cap_score + bonus_score

    if st.button("🔍 Analyze Deal"):
        st.metric("📊 Deal Score (0–100)", f"{deal_score:.1f}")

        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Annual Cash Flow", f"${annual_cashflow:,.0f}")
        col2.metric("📉 Cap Rate", f"{cap_rate:.1f}%")
        col3.metric("📈 ROI (Cash-on-Cash)", f"{roi:.1f}%")

        st.markdown("### 💵 Investment Details")
        col4, col5 = st.columns(2)
        col4.metric("🏦 Down Payment", f"${down_payment:,.0f}")
        col5.metric("📆 Monthly Cash Flow", f"${monthly_rent - monthly_expenses:,.0f}")

        if deal_score >= 85:
            st.success("🏆 Excellent deal!")
        elif deal_score >= 70:
            st.info("👍 Solid deal")
        elif deal_score >= 50:
            st.warning("⚠️ Needs work")
        else:
            st.error("🚫 Risky deal")

        st.markdown("### 📊 Deal Score Breakdown")
        score_data = {
            "Category": ["ROI", "Monthly Cash Flow", "Cap Rate", "Bonus"],
            "Score (out of 100)": [
                f"{roi_score:.1f}/30",
                f"{cashflow_score:.1f}/30",
                f"{cap_score:.1f}/20",
                f"{bonus_score}/10"
            ],
            "Improvement Tips": [
                "Increase annual cash flow or reduce down payment",
                "Raise rent or reduce expenses",
                "Improve purchase-to-income ratio",
                "Ensure ROI > 10% and monthly cash flow > $250"
            ]
        }
        st.table(pd.DataFrame(score_data))

# -------- Break-Even Calculator --------
elif page == "💡 Break-Even Calculator":
    st.header("💡 Break-Even Calculator")
    st.markdown("Calculate the rent you need to break even after covering mortgage and expenses.")

    col1, col2 = st.columns(2)
    with col1:
        purchase_price = st.number_input("Purchase Price ($)", value=250000)
        down_payment_pct = st.slider("Down Payment (%)", 0, 100, 20)
        interest_rate = st.number_input("Loan Interest Rate (%)", value=6.5)
        loan_term = st.selectbox("Loan Term (Years)", [15, 30], index=1)
    with col2:
        taxes_insurance = st.number_input("Taxes + Insurance + HOA ($/mo)", value=300)
        maintenance_pct = st.slider("Maintenance (% of Rent)", 0, 20, 10)
        management_pct = st.slider("Management (% of Rent)", 0, 20, 8)
        vacancy_rate = st.slider("Vacancy Rate (%)", 0, 20, 5)

    loan_amount = purchase_price * (1 - down_payment_pct / 100)
    monthly_interest = interest_rate / 100 / 12
    months = loan_term * 12
    mortgage_payment = npf.pmt(monthly_interest, months, -loan_amount) if loan_amount > 0 else 0

    # Estimate break-even rent
    def calc_break_even_rent():
        for rent in range(500, 5000, 10):
            maintenance = rent * (maintenance_pct / 100)
            management = rent * (management_pct / 100)
            vacancy_loss = rent * (vacancy_rate / 100)
            expenses = taxes_insurance + maintenance + management + vacancy_loss
            cash_flow = rent - (mortgage_payment + expenses)
            if cash_flow >= 0:
                return rent
        return None

    breakeven_rent = calc_break_even_rent()
    if breakeven_rent:
        st.success(f"✅ Estimated Break-Even Rent: ${breakeven_rent:,.0f}/mo")
        st.metric("Mortgage Payment", f"${mortgage_payment:,.0f}/mo")

        # Chart: Rent vs. Cash Flow
        rent_range = np.arange(breakeven_rent - 800, breakeven_rent + 800, 50)
        cash_flows = []
        for r in rent_range:
            maintenance = r * (maintenance_pct / 100)
            management = r * (management_pct / 100)
            vacancy_loss = r * (vacancy_rate / 100)
            expenses = taxes_insurance + maintenance + management + vacancy_loss
            cash_flow = r - (mortgage_payment + expenses)
            cash_flows.append(cash_flow)
        df_cf = pd.DataFrame({"Rent": rent_range, "Cash Flow": cash_flows})
        st.line_chart(df_cf.set_index("Rent"))

        # Export option
        df_cf_export = df_cf.copy()
        df_cf_export.loc[len(df_cf_export)] = ["Generated by Smart Rental Analyzer"] + [""] * (len(df_cf_export.columns)-1)
        csv_data = df_cf_export.to_csv(index=False).encode('utf-8')

        st.download_button(
            label="⬇️ Download Cash Flow Table (CSV)",
            data=csv_data,
            file_name="break_even_cash_flow.csv",
            mime="text/csv"
        )

    else:
        st.error("❌ No break-even rent found in range. Try adjusting your inputs.")
# -------- ROI & Projections --------
elif page == "📘 ROI & Projections":
    st.header("📘 ROI & Multi-Year Projections")
    st.markdown("Forecast your returns over time with appreciation, rent growth, and debt paydown.")

    col1, col2 = st.columns(2)
    with col1:
        purchase_price = st.number_input("Purchase Price ($)", value=250000)
        down_payment_pct = st.slider("Down Payment (%)", 0, 100, 20)
        interest_rate = st.number_input("Loan Interest Rate (%)", value=6.5)
        loan_term = st.selectbox("Loan Term (Years)", [15, 30], index=1)
        years = st.slider("Years to Project", 1, 30, 5)
    with col2:
        monthly_rent = st.number_input("Starting Monthly Rent ($)", value=2200)
        expenses = st.number_input("Monthly Operating Expenses ($)", value=800)
        rent_growth = st.slider("Rent Growth (%/yr)", 0, 10, 3)
        expense_growth = st.slider("Expense Growth (%/yr)", 0, 10, 2)
        appreciation = st.slider("Property Appreciation (%/yr)", 0, 10, 3)

    # Loan Calculations
    down_payment = purchase_price * down_payment_pct / 100
    loan_amount = purchase_price - down_payment
    monthly_interest = interest_rate / 100 / 12
    total_months = loan_term * 12
    mortgage_payment = npf.pmt(monthly_interest, total_months, -loan_amount)

    # Projection Calculations
    schedule = []
    balance = loan_amount
    rent = monthly_rent
    op_exp = expenses
    value = purchase_price
    total_cashflow = 0
    roi_rows = []

    for year in range(1, years + 1):
        annual_cf = (rent - op_exp - mortgage_payment) * 12
        interest_paid = 0
        principal_paid = 0
        for _ in range(12):
            interest = balance * monthly_interest
            principal = mortgage_payment - interest
            balance -= principal
            interest_paid += interest
            principal_paid += principal

        equity = value - balance
        roi = ((annual_cf + equity) / down_payment) * 100
        roi_rows.append([year, f"${rent*12:,.0f}", f"${op_exp*12:,.0f}", f"${annual_cf:,.0f}", f"${equity:,.0f}", f"{roi:.1f}%"])

        rent *= (1 + rent_growth / 100)
        op_exp *= (1 + expense_growth / 100)
        value *= (1 + appreciation / 100)
        total_cashflow += annual_cf

    df_proj = pd.DataFrame(roi_rows, columns=["Year", "Annual Rent", "Annual Expenses", "Cash Flow", "Equity", "ROI"])
    st.dataframe(df_proj, use_container_width=True)

    st.subheader("📈 ROI Over Time")
    roi_vals = [float(r[-1].replace('%','')) for r in roi_rows]
    st.line_chart(pd.DataFrame({"ROI %": roi_vals}, index=list(range(1, years+1))))

    # Download CSV
# Inside ROI & Projections page
    df_roi_export = df_proj.copy()
    df_roi_export.loc[len(df_roi_export)] = ["Generated by Smart Rental Analyzer"] + [""] * (len(df_roi_export.columns)-1)
    csv_roi = df_roi_export.to_csv(index=False).encode('utf-8')

    st.download_button("⬇️ Download ROI Projection Table (CSV)", csv_roi, file_name="roi_projection.csv", mime="text/csv")




# -------- Property Comparison (Pro) --------
elif page == "💎 Property Comparison (Pro)":
    st.header("💎 Multi-Property Comparison")
    st.write("**Pro Feature**")

    count = st.radio("Number of Properties", [2, 3, 4, 5], horizontal=True)
    cols = st.columns(count)
    props = []

    for i in range(count):
        with cols[i]:
            lbl = f"Property {chr(65 + i)}"
            price = st.number_input(f"Purchase Price ({lbl})", value=300000, key=f"pc_price_{i}")
            dp_pct = st.number_input(f"Down Payment % ({lbl})", value=20.0, key=f"pc_dp_{i}")
            rent = st.number_input(f"Monthly Rent ({lbl})", value=2200, key=f"pc_rent_{i}")
            exp = st.number_input(f"Monthly Expenses ({lbl})", value=300, key=f"pc_exp_{i}")
            appreciation = st.slider(f"Appreciation Rate % ({lbl})", 0, 10, 3, key=f"pc_app_{i}")
            interest = st.number_input(f"Interest Rate % ({lbl})", value=6.5, key=f"pc_int_{i}")
            term = st.selectbox(f"Loan Term ({lbl})", [15, 30], index=1, key=f"pc_term_{i}")

            dp = price * dp_pct / 100
            loan = price - dp
            months = term * 12
            rate = interest / 100 / 12
            payment = npf.pmt(rate, months, -loan) if loan > 0 else 0
            annual_cf = (rent - exp - payment) * 12
            cap = (annual_cf / price) * 100 if price else 0
            roi = (annual_cf / dp) * 100 if dp else 0
            proj_val = price * ((1 + appreciation / 100) ** 5)
            equity = proj_val - loan

            props.append({"lbl": lbl, "Price": f"${price:,.0f}", "Rent": f"${rent:,.0f}", "Annual Cash Flow": f"${annual_cf:,.0f}", "Cap Rate": f"{cap:.1f}%", "ROI": f"{roi:.1f}%", "5-Yr Equity": f"${equity:,.0f}", "roi_val": roi})

    if st.button("Compare"):
        st.markdown("### 📊 Comparison Table")
        df_props = pd.DataFrame([{k: v for k, v in p.items() if k != "roi_val"} for p in props])
        st.dataframe(df_props, use_container_width=True)

        try:
            best_idx = max(range(len(props)), key=lambda i: props[i]['roi_val'])
            best_property = props[best_idx]['lbl']
            st.success(f"🏆 Best ROI: {best_property}")
        except:
            st.warning("Unable to determine best ROI.")

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.set_font("Arial", style="B", size=14)
        pdf.cell(0, 10, "Property Comparison Report", ln=True, align='C')
        for metric in ["Price", "Rent", "Annual Cash Flow", "Cap Rate", "ROI", "5-Yr Equity"]:
            line = metric + ": " + ", ".join([f"{p['lbl']} {p[metric]}" for p in props])
            pdf.multi_cell(0, 8, line)
        b = pdf.output(dest='S').encode('latin1')
        st.download_button("⬇️ Download PDF", data=b, file_name="comparison.pdf", mime="application/pdf")
# -------- Advanced Analytics (Pro) --------
elif page == "🧪 Advanced Analytics (Pro)":
    st.header("🧪 Advanced Analytics & Forecasting")
    st.markdown("Explore long-term performance with charts, forecasts, and scenario analysis.")

    # Scenario Selection
    scenario = st.radio("Choose a Scenario", ["Conservative", "Base", "Aggressive", "Custom"])
    if scenario == "Conservative":
        rent_growth = 1.5
        appreciation = 2.0
        expense_growth = 3.0
    elif scenario == "Aggressive":
        rent_growth = 4.0
        appreciation = 5.0
        expense_growth = 1.5
    elif scenario == "Base":
        rent_growth = 2.5
        appreciation = 3.0
        expense_growth = 2.0
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            rent_growth = st.number_input("Rent Growth (% per year)", value=2.5)
        with col2:
            appreciation = st.number_input("Property Appreciation (% per year)", value=3.0)
        with col3:
            expense_growth = st.number_input("Expense Growth (% per year)", value=2.0)

    st.subheader("📈 5-Year Projection")
    purchase_price = 250000
    rent = 2200
    expenses = 800
    loan_amount = 200000
    interest = 0.065 / 12
    months = 30 * 12
    mortgage_payment = npf.pmt(interest, months, -loan_amount)

    years = list(range(1, 6))
    cashflow_list = []
    equity_list = []
    roi_list = []
    balance = loan_amount
    value = purchase_price

    for year in years:
        annual_cf = (rent - expenses - mortgage_payment) * 12
        for _ in range(12):
            interest_paid = balance * interest
            principal_paid = mortgage_payment - interest_paid
            balance -= principal_paid
        equity = value - balance
        roi = ((annual_cf + equity) / (purchase_price - loan_amount)) * 100

        cashflow_list.append(annual_cf)
        equity_list.append(equity)
        roi_list.append(roi)

        rent *= (1 + rent_growth / 100)
        expenses *= (1 + expense_growth / 100)
        value *= (1 + appreciation / 100)

    # Multi-line Chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years, y=cashflow_list, mode='lines+markers', name='Cash Flow'))
    fig.add_trace(go.Scatter(x=years, y=equity_list, mode='lines+markers', name='Equity'))
    fig.add_trace(go.Scatter(x=years, y=roi_list, mode='lines+markers', name='ROI %'))
    fig.update_layout(title="5-Year Projection: Cash Flow, Equity, ROI", xaxis_title="Year", yaxis_title="USD / %")
    st.plotly_chart(fig, use_container_width=True)

    # 2. Rent Sensitivity
    st.subheader("📊 Rent Sensitivity Table")
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        min_rent = st.number_input("Minimum Rent ($)", value=1800)
        max_rent = st.number_input("Maximum Rent ($)", value=2800)
    with col_r2:
        rent_step = st.number_input("Rent Step ($)", value=100)
        base_expense = st.number_input("Fixed Expenses ($)", value=1800)

    rent_vals = np.arange(min_rent, max_rent + rent_step, rent_step)
    cash_flows = rent_vals - base_expense
    df_sens = pd.DataFrame({'Rent': rent_vals, 'Cash Flow': cash_flows})
    st.dataframe(df_sens)
    df_sens_export = df_sens.copy()
    df_sens_export.loc[len(df_sens_export)] = ["Generated by Smart Rental Analyzer"] + [""] * (len(df_sens_export.columns)-1)
    csv_sens = df_sens_export.to_csv(index=False).encode('utf-8')

    st.download_button("⬇️ Download Rent Sensitivity (CSV)", data=csv_sens, file_name="rent_sensitivity.csv", mime="text/csv")


    # 3. Stress Test Table
    st.subheader("📉 Vacancy & Expense Stress Test")

    with st.expander("Customize Stress Test Inputs", expanded=True):
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            stress_rent = st.number_input("Monthly Rent ($)", value=2400)
        with col_b:
            base_op_exp = st.number_input("Base Operating Expenses ($)", value=800)
        with col_c:
            mortgage_toggle = st.checkbox("Include Mortgage", value=True)

        if mortgage_toggle:
            loan_amt = st.number_input("Loan Amount ($)", value=200000)
            rate = st.number_input("Interest Rate (%)", value=6.5) / 100 / 12
            term = st.selectbox("Loan Term (Years)", [15, 30], index=1)
            months = term * 12
            mortgage_payment = npf.pmt(rate, months, -loan_amt)
        else:
            mortgage_payment = 0

    vacancies = [0.0, 0.05, 0.1, 0.15]
    maint_pct = [0.05, 0.1, 0.15]
    stress_data = []
    for v in vacancies:
        row = []
        for m in maint_pct:
            effective_income = stress_rent * (1 - v)
            maintenance = stress_rent * m
            total_exp = base_op_exp + maintenance + mortgage_payment
            net = effective_income - total_exp
            row.append(round(net, 2))
        stress_data.append(row)

    stress_df = pd.DataFrame(stress_data, columns=[f"{int(p*100)}% Maint" for p in maint_pct], index=[f"{int(v*100)}% Vac" for v in vacancies])
    st.dataframe(stress_df)

    # Export CSV
    df_stress_export = stress_df.copy()
    df_stress_export.loc[len(df_stress_export)] = ["Generated by Smart Rental Analyzer"] + [""] * (len(df_stress_export.columns)-1)
    csv_stress = df_stress_export.to_csv(index=False).encode('utf-8')

    st.download_button("⬇️ Download Stress Test (CSV)", data=csv_stress, file_name="stress_test.csv", mime="text/csv")



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
