
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- Login ---
users = {"Reelence": "9886669814"}
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    with st.form("login_form"):
        st.title("🔐 Login to Reelence Biomass Simulator")
        username = st.text_input("User ID")
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if username in users and users[username] == password:
                st.session_state.logged_in = True
                st.experimental_rerun()
            else:
                st.error("❌ Invalid credentials.")

if not st.session_state.logged_in:
    login()
    st.stop()

# --- Page Setup ---
st.set_page_config(page_title="Reelence Biomass Simulator", layout="wide")
st.sidebar.title("⚙️ Settings")
pitch_mode = st.sidebar.checkbox("🎤 Client Pitch Mode (Hide Inputs)")

# --- Tab Layout ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🏭 Factory Setup", "📦 Supply Chain", "🚨 Risk Simulator",
    "📚 References", "📈 Breakeven", "🌿 Carbon Credit", "🔥 GCV Simulator"
])

# --- Tab 1: Factory Setup ---
with tab1:
    st.header("🏭 Factory Setup Estimator – Kawardha")
    template = st.selectbox("📋 Choose Setup Scenario", ["Custom", "Basic", "Premium"])
    if template == "Basic":
        tpd = 2
    elif template == "Premium":
        tpd = 5
    elif not pitch_mode:
        tpd = st.slider("Tons Per Day (TPD)", 1, 10, 2)
    else:
        tpd = 2
        st.info(f"🎤 Showing default TPD: {tpd} (Pitch Mode)")

    values = {
        "Land": 600 * 10000,
        "Machinery": 950000 * tpd,
        "Warehouse": 1600 * 3000,
        "Electricity": 1200000,
        "Labor (Advance)": 15000 * 12 * 5,
        "Transport": 500000,
        "Installation": 400000,
        "Admin": 100000,
        "Working Capital": 300000 * tpd,
        "Contingency": 0.1 * (950000 * tpd + 1600 * 3000 + 15000 * 12 * 5)
    }
    total = sum(values.values())
    st.metric("💰 Total Setup Cost", f"₹{int(total):,}")
    df = pd.DataFrame(list(values.items()), columns=["Category", "Cost (₹)"])
    st.dataframe(df, use_container_width=True)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Factory Setup Cost CSV", data=csv, file_name="factory_setup_cost.csv", mime="text/csv")

# --- Tab 2: Supply Chain ---
with tab2:
    st.header("📦 Supply Chain Estimator")
    st.components.v1.html(
        '<iframe width="100%" height="450" src="https://www.google.com/maps?q=Kawardha,Chhattisgarh&output=embed"></iframe>',
        height=450
    )
    if not pitch_mode:
        dist = st.slider("Distance (km)", 10, 500, 120)
        tons = st.slider("Transport Tons", 1, 50, 10)
        rate = st.number_input("Rate (₹/ton/km)", value=6.5)
    else:
        dist, tons, rate = 120, 10, 6.5
        st.info("📍 Using preset values in Pitch Mode")
    cost = dist * tons * rate
    st.metric("🚛 Estimated Transport Cost", f"₹{int(cost):,}")

# --- Tab 3: Risk Simulator ---
with tab3:
    st.header("🚨 Risk Simulator")
    risks = {
        "⚡ Power Outage": (50000, "Install DG backup"),
        "⚙ Machine Breakdown": (80000, "Get AMC coverage"),
        "🛢 Fuel Price Surge": (30000, "Bulk diesel procurement"),
        "📦 Material Delay": (40000, "Buffer raw material stock"),
        "👷 Labor Strike": (35000, "Maintain contract labor")
    }
    total_loss = 0
    actions = []
    risk_status = {}
    for risk, (cost, fix) in risks.items():
        if not pitch_mode:
            checked = st.checkbox(risk)
        else:
            checked = False
        risk_status[risk] = checked
        if checked:
            total_loss += cost
            actions.append(fix)
    st.metric("💸 Simulated Total Loss", f"₹{total_loss:,}")
    if total_loss > 0:
        risk_df = pd.DataFrame({
            "Risk": [r for r in risks if risk_status[r]],
            "Loss (₹)": [risks[r][0] for r in risks if risk_status[r]],
            "Mitigation": [risks[r][1] for r in risks if risk_status[r]]
        })
        st.dataframe(risk_df)
        csv_risk = risk_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Risk Report CSV", data=csv_risk, file_name="risk_report.csv", mime="text/csv")
    if actions:
        st.subheader("✅ Suggested Fixes")
        for a in actions:
            st.info(a)

# --- Tab 4: References ---
with tab4:
    st.header("📚 References & Justification")
    st.markdown("""
    - **Land**: ₹600/sqft – Local registry data  
    - **Machinery**: ₹9.5L/TPD – Indiamart vendors  
    - **Warehouse**: ₹1600/sqft – CPWD prefab rate  
    - **Electricity**: ₹12L – 100 KVA transformer (CSEB)  
    - **Labor**: ₹15,000/month – Skill India rate  
    - **Diesel Cost**: ₹6.5/km/ton – Regional logistics average  
    - **Contingency**: 10% of total capex (industry standard)
    """)

# --- Tab 5: Breakeven Forecast ---
with tab5:
    st.header("📈 Breakeven Forecast")
    if not pitch_mode:
        monthly_profit = st.number_input("Expected Monthly Profit (₹)", value=75000)
    else:
        monthly_profit = 75000
        st.info("📊 Using ₹75,000/month for Pitch Mode")
    months = int(total / monthly_profit) if monthly_profit else 0
    st.metric("Estimated Breakeven (Months)", months)
    forecast_df = pd.DataFrame({
        "Month": list(range(1, 13)),
        "Cumulative Profit": [monthly_profit * i for i in range(1, 13)]
    })
    st.line_chart(forecast_df.set_index("Month"))

# --- Tab 6: Carbon Credit Estimator ---
with tab6:
    st.header("🌿 Carbon Credit Estimator")
    if not pitch_mode:
        tons_per_month = st.slider("Monthly Production (Tons)", 10, 100, 30)
        credit_rate = st.number_input("Credit Rate ₹/ton CO₂", value=700)
    else:
        tons_per_month = 30
        credit_rate = 700
        st.info("🌍 Using preset values for CO₂ savings")
    co2_per_ton = 1.8
    co2_saved = tons_per_month * co2_per_ton
    credit_value = co2_saved * credit_rate
    st.metric("🌍 CO₂ Saved", f"{co2_saved:.2f} tons")
    st.metric("💰 Carbon Credit Earned", f"₹{int(credit_value):,}")
    st.subheader("🏛 Subsidy or Certification Suggestion")
    st.info("✅ You may be eligible for MNRE’s Biomass Program or state-level energy grants.")
    carbon_txt = f"CO₂ Saved: {co2_saved:.2f} tons\nCredit Value: ₹{int(credit_value):,}"
    st.download_button("📄 Download CO₂ Savings Summary", carbon_txt, file_name="carbon_summary.txt", mime="text/plain")

# --- Tab 7: GCV Simulator ---
with tab7:
    st.header("🔥 Advanced GCV-Based Biomass Pellet Simulator")
    biomass_options = {
        "Wood Chips": 3500,
        "Rice Husk": 3000,
        "Bagasse": 2800,
        "Groundnut Shell": 3600,
        "Cotton Stalk": 3700,
        "Manure Pellet": 2500,
        "Sugarcane Bagasse": 2300,
        "Rice Husk": 3100,
        "Wood Pellets": 4000,
        "Bamboo": 4200,
        "Coconut Shell": 4800,
        "Mustard Husk": 3000,
        "Groundnut Shell": 4000,
        "Torrefied Biomass": 4200
    }
    col1, col2 = st.columns(2)
    with col1:
        selected_biomass = st.selectbox("Select Biomass Type", list(biomass_options.keys()))
        default_gcv = biomass_options[selected_biomass]
    with col2:
        gcv_input = st.number_input("Enter GCV (kcal/kg)", value=default_gcv)
    base_rate = 4.5  # ₹ per kcal/kg
    market_price_per_ton = gcv_input * base_rate
    st.metric("💸 Estimated Market Price", f"₹{int(market_price_per_ton):,} / ton")
    cost_per_ton = st.number_input("Production Cost per Ton (₹)", value=5000)
    profit_per_ton = market_price_per_ton - cost_per_ton
    st.metric("💰 Estimated Profit per Ton", f"₹{int(profit_per_ton):,}")
    gcv_values = list(range(2500, 4001, 100))
    price_values = [g * base_rate for g in gcv_values]
    chart_data = pd.DataFrame({"GCV (kcal/kg)": gcv_values, "Estimated Price (₹/ton)": price_values})
    st.line_chart(chart_data.set_index("GCV (kcal/kg)"))


# --- Tab 8: Enhanced GCV-Based Biomass Simulator ---


import streamlit as st
import pandas as pd
import random
import matplotlib.pyplot as plt

# st.set_page_config(page_title="Advanced Biomass Pellet Simulator", layout="centered")

# Simulated live price
live_price_today = random.randint(8500, 11500)

# Exhaustive Biomass Type Data
biomass_data = {
    "Sugarcane Bagasse": {"GCV": 2300, "Price": 7500},
    "Rice Husk": {"GCV": 3100, "Price": 8700},
    "Wood Pellets": {"GCV": 4000, "Price": 10000},
    "Bamboo": {"GCV": 4200, "Price": 10500},
    "Coconut Shell": {"GCV": 4800, "Price": 11200},
    "Mustard Husk": {"GCV": 3000, "Price": 8600},
    "Groundnut Shell": {"GCV": 4000, "Price": 9800},
    "Torrefied Biomass": {"GCV": 4200, "Price": 10836}
}
biomass_types = list(biomass_data.keys())

# Simulated chart values
gcv_values = [v["GCV"] for v in biomass_data.values()]
prices = [v["Price"] + random.randint(-300, 300) for v in biomass_data.values()]

# Sidebar Inputs
st.sidebar.title("🧮 Input Parameters")
lang = st.sidebar.radio("Language / भाषा", ("English", "हिंदी"))
st.sidebar.success(f"📢 Live Price Today: ₹{live_price_today}/ton")

template = st.sidebar.selectbox("Choose a Scenario", ("Custom", "Basic", "Semi-Automated", "Premium Export", "Torrefied Biomass"))
if template == "Basic":
    tons, gcv, rm_cost, labor_cost, elec_cost, maint_cost, credit = 20, 2300, 75000, 60000, 25000, 15000, 500
elif template == "Semi-Automated":
    tons, gcv, rm_cost, labor_cost, elec_cost, maint_cost, credit = 30, 3100, 90000, 50000, 30000, 20000, 700
elif template == "Premium Export":
    tons, gcv, rm_cost, labor_cost, elec_cost, maint_cost, credit = 50, 4200, 110000, 70000, 35000, 25000, 1000
elif template == "Torrefied Biomass":
    tons, gcv, rm_cost, labor_cost, elec_cost, maint_cost, credit = 40, 4200, 100000, 55000, 32000, 22000, 1000
else:
    mode = st.sidebar.radio("GCV Input Mode", ("Select Biomass Type", "Enter GCV Manually"))
    if mode == "Select Biomass Type":
        selected_biomass = st.sidebar.selectbox("Biomass Type", biomass_types)
        gcv = biomass_data[selected_biomass]["GCV"]
        price = biomass_data[selected_biomass]["Price"]
    else:
        gcv = st.sidebar.number_input("Enter GCV (kcal/kg)", min_value=1500, max_value=6000, value=4000)
        price = gcv * 0.0025 * 1000

    tons = st.sidebar.slider("Tons Produced per Month", 10, 100, 25)
    rm_cost = st.sidebar.number_input("Raw Material Cost/month (₹)", value=80000)
    labor_cost = st.sidebar.number_input("Labor Cost/month (₹)", value=60000)
    elec_cost = st.sidebar.number_input("Electricity Cost/month (₹)", value=25000)
    maint_cost = st.sidebar.number_input("Maintenance Cost/month (₹)", value=15000)
    credit = st.sidebar.number_input("Carbon Credit per Ton (₹)", value=700)

# Calculations
price = gcv * 0.0025 * 1000
total_cost = rm_cost + labor_cost + elec_cost + maint_cost
revenue = tons * price
carbon_credit = tons * credit
total_revenue = revenue + carbon_credit
profit_without_credit = revenue - total_cost
profit_with_credit = total_revenue - total_cost
breakeven_tons = round(total_cost / price, 2)
roi = (profit_with_credit / total_cost) * 100 if total_cost else 0
earning_per_kcal = price / gcv if gcv else 0

# Title
st.title("🌿 Advanced GCV-Based Biomass Pellet Simulator")

# Summary Box
st.success(f"📌 GCV: {gcv} kcal/kg → Estimated Price: ₹{int(price):,}/ton")

# Results Table with Extra Metrics
results = {
    "Total Cost (₹)": [total_cost],
    "Revenue (₹)": [revenue],
    "Carbon Credit (₹)": [carbon_credit],
    "Total Revenue (₹)": [total_revenue],
    "Profit without Credit (₹)": [profit_without_credit],
    "Profit with Credit (₹)": [profit_with_credit],
    "Breakeven Tons": [breakeven_tons],
    "ROI (%)": [round(roi, 2)],
    "Earning per kcal (₹)": [round(earning_per_kcal, 3)]
}
df = pd.DataFrame(results)
st.markdown("### 📊 Simulation Results")
st.dataframe(df, use_container_width=True)

# Export
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download Results as CSV", data=csv, file_name="biomass_simulation_results.csv", mime='text/csv')

# GCV Table
st.markdown("### 📘 Biomass GCV & Price Table")
gcv_table = pd.DataFrame([
    {"Biomass Type": k, "GCV (kcal/kg)": v["GCV"], "Market Price (₹/ton)": v["Price"]}
    for k, v in biomass_data.items()
])
st.table(gcv_table)

# Chart
st.markdown("### 📈 Simulated Market Price Trend")
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(gcv_values, prices, marker='o')
ax.set_xlabel("GCV (kcal/kg)")
ax.set_ylabel("Price (₹/ton)")
ax.set_title("Market Price vs GCV")
ax.grid(True)
st.pyplot(fig)

st.caption("Reelence technologies - Biomass Business Blueprint")
