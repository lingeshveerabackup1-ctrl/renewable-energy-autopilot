import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Renewable Energy Autopilot",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Renewable Energy Autopilot")
st.write(
    "A software system that intelligently manages renewable energy, "
    "battery storage, electrical loads, and grid power."
)

# -----------------------------
# SIDEBAR SETTINGS
# -----------------------------

st.sidebar.header("⚙️ System Settings")

battery_capacity = st.sidebar.number_input(
    "Battery Capacity (kWh)",
    min_value=1.0,
    max_value=10000.0,
    value=100.0,
    step=10.0
)

battery_reserve = st.sidebar.slider(
    "Minimum Battery Reserve (%)",
    min_value=0,
    max_value=100,
    value=20
)

reserve_energy = battery_capacity * battery_reserve / 100

# -----------------------------
# OPTIMIZATION FUNCTION
# -----------------------------

def optimize(solar, wind, load, battery, grid_price):

    renewable = solar + wind

    battery_before = battery

    grid_import = 0.0
    grid_export = 0.0
    battery_charge = 0.0
    battery_discharge = 0.0

    # Renewable energy is more than the load
    if renewable >= load:

        surplus = renewable - load

        available_storage = battery_capacity - battery

        battery_charge = min(surplus, available_storage)

        battery = battery + battery_charge

        remaining_surplus = surplus - battery_charge

        grid_export = remaining_surplus

    # Renewable energy is less than the load
    else:

        deficit = load - renewable

        available_battery = max(0, battery - reserve_energy)

        battery_discharge = min(deficit, available_battery)

        battery = battery - battery_discharge

        remaining_deficit = deficit - battery_discharge

        grid_import = remaining_deficit

    grid_cost = grid_import * grid_price

    co2_avoided = renewable * 0.7

    return {
        "renewable": renewable,
        "battery_before": battery_before,
        "battery_after": battery,
        "battery_charge": battery_charge,
        "battery_discharge": battery_discharge,
        "grid_import": grid_import,
        "grid_export": grid_export,
        "grid_cost": grid_cost,
        "co2_avoided": co2_avoided
    }


# -----------------------------
# TABS
# -----------------------------

tab1, tab2, tab3 = st.tabs([
    "🔴 Live Control",
    "📊 24-Hour Simulation",
    "🧠 How It Works"
])


# =========================================================
# LIVE CONTROL
# =========================================================

with tab1:

    st.header("🔴 Live Energy Management")

    col1, col2, col3 = st.columns(3)

    with col1:
        solar = st.number_input(
            "☀️ Solar Generation (kW)",
            min_value=0.0,
            value=20.0,
            step=1.0
        )

        wind = st.number_input(
            "🌬️ Wind Generation (kW)",
            min_value=0.0,
            value=10.0,
            step=1.0
        )

    with col2:
        load = st.number_input(
            "🏠 Current Load (kW)",
            min_value=0.0,
            value=25.0,
            step=1.0
        )

        battery = st.number_input(
            "🔋 Current Battery Energy (kWh)",
            min_value=0.0,
            max_value=float(battery_capacity),
            value=min(50.0, float(battery_capacity)),
            step=1.0
        )

    with col3:
        grid_price = st.number_input(
            "💰 Grid Price (₹/kWh)",
            min_value=0.0,
            value=7.0,
            step=0.5
        )

    result = optimize(
        solar,
        wind,
        load,
        battery,
        grid_price
    )

    st.divider()

    st.subheader("⚡ Energy Decision")

    renewable = result["renewable"]

    if renewable > load:

        if result["battery_charge"] > 0:
            decision = "🔋 Charge the battery using surplus renewable energy."

        if result["grid_export"] > 0:
            decision += " Export the remaining surplus to the grid."

    elif result["grid_import"] > 0:

        decision = "⚡ Import the remaining required energy from the grid."

    else:

        decision = "🔋 Supply the load using battery energy."

    st.success(decision)

    # Metrics

    m1, m2, m3, m4 = st.columns(4)

    m1.metric(
        "Renewable Generation",
        f"{result['renewable']:.2f} kW"
    )

    m2.metric(
        "Battery Level",
        f"{result['battery_after']:.2f} kWh"
    )

    m3.metric(
        "Grid Import",
        f"{result['grid_import']:.2f} kW"
    )

    m4.metric(
        "Grid Export",
        f"{result['grid_export']:.2f} kW"
    )

    st.divider()

    st.subheader("📋 Energy Flow")

    data = pd.DataFrame({
        "Parameter": [
            "Solar Generation",
            "Wind Generation",
            "Total Renewable",
            "Electrical Load",
            "Battery Before",
            "Battery Charge",
            "Battery Discharge",
            "Battery After",
            "Grid Import",
            "Grid Export",
            "Grid Cost",
            "CO₂ Avoided"
        ],
        "Value": [
            f"{solar:.2f} kW",
            f"{wind:.2f} kW",
            f"{result['renewable']:.2f} kW",
            f"{load:.2f} kW",
            f"{result['battery_before']:.2f} kWh",
            f"{result['battery_charge']:.2f} kWh",
            f"{result['battery_discharge']:.2f} kWh",
            f"{result['battery_after']:.2f} kWh",
            f"{result['grid_import']:.2f} kW",
            f"{result['grid_export']:.2f} kW",
            f"₹{result['grid_cost']:.2f}",
            f"{result['co2_avoided']:.2f} kg"
        ]
    })

    st.dataframe(
        data,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# 24 HOUR SIMULATION
# =========================================================

with tab2:

    st.header("📊 24-Hour Energy Simulation")

    hours = np.arange(0, 24)

    # Simulated solar generation
    solar_profile = np.maximum(
        0,
        60 * np.sin((hours - 6) * np.pi / 12)
    )

    # Simulated wind generation
    np.random.seed(42)

    wind_profile = np.maximum(
        5,
        15 + np.random.normal(0, 3, 24)
    )

    # Simulated building load
    load_profile = (
        25
        + 8 * np.sin((hours - 7) * np.pi / 12)
        + 5 * ((hours >= 18) & (hours <= 22))
    )

    load_profile = np.maximum(load_profile, 10)

    # Simulated electricity price
    price_profile = np.where(
        (hours >= 18) & (hours <= 22),
        10,
        6
    )

    battery_level = min(
        50,
        float(battery_capacity)
    )

    records = []

    for i in range(24):

        result = optimize(
            solar_profile[i],
            wind_profile[i],
            load_profile[i],
            battery_level,
            price_profile[i]
        )

        battery_level = result["battery_after"]

        records.append({
            "Hour": i,
            "Solar (kW)": solar_profile[i],
            "Wind (kW)": wind_profile[i],
            "Load (kW)": load_profile[i],
            "Battery (kWh)": battery_level,
            "Grid Import (kW)": result["grid_import"],
            "Grid Export (kW)": result["grid_export"],
            "Grid Price (₹/kWh)": price_profile[i]
        })

    df = pd.DataFrame(records)

    st.subheader("☀️ Renewable Generation vs Load")

    chart_data = df.set_index("Hour")[
        ["Solar (kW)", "Wind (kW)", "Load (kW)"]
    ]

    st.line_chart(chart_data)

    st.subheader("🔋 Battery Level")

    st.line_chart(
        df.set_index("Hour")[["Battery (kWh)"]]
    )

    st.subheader("⚡ Grid Interaction")

    st.line_chart(
        df.set_index("Hour")[
            ["Grid Import (kW)", "Grid Export (kW)"]
        ]
    )

    st.subheader("📋 Complete Simulation Data")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    total_import = df["Grid Import (kW)"].sum()
    total_export = df["Grid Export (kW)"].sum()

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Total Grid Import",
        f"{total_import:.2f} kWh"
    )

    c2.metric(
        "Total Grid Export",
        f"{total_export:.2f} kWh"
    )

    c3.metric(
        "Final Battery",
        f"{battery_level:.2f} kWh"
    )


# =========================================================
# HOW IT WORKS
# =========================================================

with tab3:

    st.header("🧠 How Renewable Energy Autopilot Works")

    st.write(
        "The software continuously compares renewable energy generation "
        "with the electrical demand."
    )

    st.subheader("1️⃣ Measure Energy")

    st.write(
        "The system receives solar generation, wind generation, "
        "electrical load, battery level and electricity price."
    )

    st.subheader("2️⃣ Calculate Energy Balance")

    st.write(
        "Total renewable energy = Solar + Wind"
    )

    st.write(
        "The system then compares renewable generation with the current load."
    )

    st.subheader("3️⃣ If Renewable Energy Is Greater Than Load")

    st.write(
        "The surplus energy is first used to charge the battery."
    )

    st.write(
        "If the battery is full, the remaining energy can be exported "
        "to the electrical grid."
    )

    st.subheader("4️⃣ If Renewable Energy Is Less Than Load")

    st.write(
        "The system first uses available battery energy."
    )

    st.write(
        "The battery is not discharged below the selected reserve level."
    )

    st.write(
        "If more energy is required, the remaining demand is supplied "
        "by the grid."
    )

    st.subheader("5️⃣ Future Intelligence")

    st.write(
        "The prototype can later be upgraded with:"
    )

    st.markdown("""
    - Real-time weather data
    - Solar power forecasting
    - Wind power forecasting
    - Load forecasting
    - Electricity price forecasting
    - AI-based optimization
    - Battery State of Charge (SOC)
    - Battery State of Health (SOH)
    - Historical energy database
    - ESP32/IoT sensor integration
    - MQTT communication
    - Automatic control of electrical loads
    """)

    st.warning(
        "⚠️ This prototype is software-only. "
        "It does not directly switch or control real electrical mains equipment."
    )

st.divider()

st.caption(
    "Renewable Energy Autopilot | Software prototype for intelligent "
    "renewable-energy management"
)
