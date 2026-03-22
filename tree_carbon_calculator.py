import streamlit as st
from streamlit_lottie import st_lottie
import requests
import pandas as pd
import math
from PIL import Image
import io

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Tree Carbon Calculator", page_icon="🌳", layout="centered")

# ------------------ CSS STYLING ------------------
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #2d5016 0%, #4a7023 50%, #6b8e23 100%);
    }
    h1, h2, h3, p, label, .stMarkdown {
        color: #f0fff0 !important;
    }
    .stButton > button {
        background-color: #556b2f !important;
        color: white !important;
        border: 2px solid #8fbc8f !important;
        border-radius: 10px;
    }
    .stButton > button:hover {
        background-color: #6b8e23 !important;
    }
    .result-box {
        background-color: rgba(85, 107, 47, 0.8);
        padding: 20px;
        border-radius: 15px;
        border: 3px solid #8fbc8f;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ------------------ LOTTIE ANIMATION ------------------
def load_lottie_url(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None

lottie_tree = load_lottie_url("https://lottie.host/4db68bbd-31f6-4cd8-84eb-189571e03aed/7XY6GgSLcq.json")

# ------------------ TREE DATA ------------------
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

# ------------------ HEADER ------------------
st.markdown("<h1 style='text-align: center;'>Tree Carbon Calculator</h1>", unsafe_allow_html=True)

if lottie_tree:
    st_lottie(lottie_tree, height=200, key="tree")

st.markdown("---")

# ------------------ IMAGE UPLOAD & PLANT.ID API ------------------
PLANT_ID_KEY = "YOUR_PLANT_ID_API_KEY"  # <-- replace with your Plant.id API key
uploaded_file = st.file_uploader("Upload Tree Image", type=["jpg","jpeg","png"])

detected_tree = None

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Tree", use_column_width=True)
    
    # Resize image to speed up API
    image = Image.open(uploaded_file)
    image = image.resize((512, 512))
    buf = io.BytesIO()
    image.save(buf, format="JPEG")
    buf.seek(0)
    
    with st.spinner("Detecting tree, please wait..."):
        try:
            response = requests.post(
                "https://api.plant.id/v2/identify",
                files={"images": buf},
                headers={"Api-Key": PLANT_ID_KEY},
                timeout=20  # seconds
            )
            result = response.json()
            # Extract the first suggestion from Plant.id API
            detected_tree = result['suggestions'][0]['plant_name'] if 'suggestions' in result and len(result['suggestions'])>0 else None
        except Exception as e:
            st.error(f"Tree detection failed: {e}")
            detected_tree = None

    if detected_tree:
        st.success(f"Detected Tree Type: {detected_tree}")
    else:
        st.warning("Tree could not be detected. Please select manually.")

# ------------------ INPUTS ------------------
col1, col2 = st.columns(2)

with col1:
    if detected_tree:
        tree_type = detected_tree
        st.text_input("Tree Type", value=tree_type, disabled=True)
    else:
        tree_type = st.selectbox("Select Tree Type", list(INDIAN_TREES.keys()))
    
    num_trees = st.number_input("Number of Trees", min_value=1, value=8)
    tree_age = st.number_input("Tree Age (years)", min_value=1, value=5)

with col2:
    years = st.number_input("Number of Years", min_value=1, value=5)
    height = st.number_input("Average Tree Height (meters)", min_value=0.5, value=5.0)
    diameter = st.number_input("Trunk Diameter (meters)", min_value=0.05, value=0.3)

# ------------------ CALCULATION ------------------
if st.button("Calculate Carbon Absorption", use_container_width=True):

    base_rate = INDIAN_TREES.get(tree_type, 10)  # fallback in case tree not in list

    # Volume (cylinder approximation)
    radius = diameter / 2
    volume = math.pi * (radius ** 2) * height

    # Age factor
    if tree_age <= 5:
        age_factor = 0.5
    elif tree_age <= 15:
        age_factor = 1.0
    else:
        age_factor = 1.5

    dynamic_rate = base_rate * volume * age_factor
    total_co2_kg = num_trees * dynamic_rate * years
    total_co2_tons = total_co2_kg / 1000

    st.markdown(f"""
    <div class="result-box">
        <h2>Total CO2 Absorbed</h2>
        <h1 style="font-size: 48px; color: #9acd32;">{total_co2_tons:.3f} TONS</h1>
        <p>({total_co2_kg:.2f} kg)</p>
    </div>
    """, unsafe_allow_html=True)

    df = pd.DataFrame({
        "Parameter": [
            "Tree Type",
            "Number of Trees",
            "Tree Age",
            "Height (m)",
            "Diameter (m)",
            "Volume",
            "CO2/tree/year (dynamic kg)"
        ],
        "Value": [
            tree_type,
            num_trees,
            tree_age,
            height,
            diameter,
            round(volume,3),
            round(dynamic_rate,2)
        ]
    })

    st.table(df)

# ------------------ TREE CO2 REFERENCE ------------------
with st.expander("View All Tree CO2 Base Rates"):
    st.dataframe(pd.DataFrame({
        "Tree": INDIAN_TREES.keys(),
        "Base CO2 (kg/year)": INDIAN_TREES.values()
    }))
