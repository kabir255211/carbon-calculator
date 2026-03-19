"""
TREE CARBON CONSUMPTION CALCULATOR (IMPROVED VERSION)
"""

import streamlit as st
from streamlit_lottie import st_lottie
import requests
import pandas as pd

# Page config
st.set_page_config(page_title="Tree Carbon Calculator", page_icon="🌳", layout="centered")

# CSS
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #2d5016 0%, #4a7023 50%, #6b8e23 100%); }
    h1, h2, h3, p, label, .stMarkdown { color: #f0fff0 !important; }
    .stButton > button { background-color: #556b2f !important; color: white !important; border: 2px solid #8fbc8f !important; border-radius: 10px; }
    .result-box { background-color: rgba(85, 107, 47, 0.8); padding: 20px; border-radius: 15px; border: 3px solid #8fbc8f; text-align: center; }
</style>
""", unsafe_allow_html=True)

# Lottie loader
def load_lottie_url(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
    except:
        return None

lottie_tree = load_lottie_url("https://lottie.host/4db68bbd-31f6-4cd8-84eb-189571e03aed/7XY6GgSLcq.json")

# Tree CO2 rates (kg/year when mature)
INDIAN_TREES = {
    "Peepal": 22.0,
    "Neem": 18.0,
    "Banyan": 25.0,
    "Mango": 15.0,
    "Teak": 12.0,
    "Ashoka": 10.0,
    "Jamun": 14.0,
    "Tamarind": 16.0,
    "Coconut": 8.0,
    "Bamboo": 35.0,
}

# Header
st.markdown("<h1 style='text-align: center;'>Tree Carbon Calculator 🌱</h1>", unsafe_allow_html=True)

# Animation
if lottie_tree:
    st_lottie(lottie_tree, height=200)

st.markdown("---")

# Inputs
col1, col2 = st.columns(2)
with col1:
    tree_type = st.selectbox("Select Tree Type", list(INDIAN_TREES.keys()))
    num_trees = st.number_input("Number of Trees", min_value=1, value=8)
with col2:
    years = st.number_input("Number of Years", min_value=1, value=5)
    area_acres = st.number_input("Area (Acres)", min_value=0.1, value=10.0)

# Calculate button
if st.button("Calculate Carbon Absorption", use_container_width=True):

    co2_rate = INDIAN_TREES[tree_type]

    # 🌳 AREA VALIDATION
    trees_per_acre = 50  # average spacing assumption
    max_trees = area_acres * trees_per_acre

    if num_trees > max_trees:
        st.warning(f"⚠️ Too many trees for this area! Max recommended: {int(max_trees)} trees")

    # 🌱 GROWTH-BASED CALCULATION
    total_co2_kg = 0
    yearly_data = []

    for year in range(1, years + 1):
        growth_factor = min(1, year / 5)  # tree matures in ~5 years
        yearly_absorption = co2_rate * growth_factor
        yearly_total = num_trees * yearly_absorption

        total_co2_kg += yearly_total

        yearly_data.append({
            "Year": year,
            "CO2 Absorbed (kg)": round(yearly_total, 2)
        })

    total_co2_tons = total_co2_kg / 1000

    # Result box
    st.markdown(f"""
    <div class="result-box">
        <h2>Total CO2 Absorbed</h2>
        <h1 style="font-size: 48px; color: #9acd32;">{total_co2_tons:.3f} TONS</h1>
        <p>({total_co2_kg:.2f} kg)</p>
    </div>
    """, unsafe_allow_html=True)

    # Year-wise table
    st.subheader("📊 Year-wise CO2 Absorption")
    st.dataframe(pd.DataFrame(yearly_data))

    # Summary table
    df = pd.DataFrame({
        "Parameter": ["Tree Type", "Number of Trees", "Years", "Area (Acres)", "CO2/tree/year (kg)"],
        "Value": [tree_type, num_trees, years, area_acres, co2_rate]
    })
    st.table(df)

# Tree rates
with st.expander("View All Tree CO2 Rates"):
    st.dataframe(pd.DataFrame({
        "Tree": INDIAN_TREES.keys(),
        "CO2 (kg/year)": INDIAN_TREES.values()
    }))

# ⚠️ Accuracy Note (VERY IMPORTANT)
st.markdown("""
---
⚠️ **Note:**  
This calculator uses estimated average CO₂ absorption rates.  
Actual absorption depends on tree age, climate, soil, and maintenance.  
A growth factor is applied to simulate realistic tree development over time.
""")
