import streamlit as st
import requests
import pandas as pd
import math
from PIL import Image
import io

# Page config
st.set_page_config(page_title="Tree Carbon Calculator", page_icon="🌳", layout="centered")

# Dark Green + Olive Theme + Falling Leaves
st.markdown("""
<style>

/* Background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(-45deg, #1b4332, #2d6a4f, #344e41, #588157);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
}

@keyframes gradientBG {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* Falling Leaves */
.leaf {
    position: fixed;
    top: -10px;
    font-size: 20px;
    animation: fall linear infinite;
    z-index: 9999;
}

@keyframes fall {
    0% {transform: translateY(-10px) rotate(0deg); opacity: 0.8;}
    100% {transform: translateY(110vh) rotate(360deg); opacity: 0.1;}
}

/* Result box */
.result-box {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(10px);
    border-radius: 18px;
    padding: 25px;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.2);
}

/* Text */
h1, h2, h3, p, label {
    color: #f1faee !important;
}

</style>

<div class="leaf" style="left:5%; animation-duration: 9s;">🍃</div>
<div class="leaf" style="left:15%; animation-duration: 11s;">🍂</div>
<div class="leaf" style="left:25%; animation-duration: 8s;">🍃</div>
<div class="leaf" style="left:35%; animation-duration: 12s;">🍂</div>
<div class="leaf" style="left:45%; animation-duration: 10s;">🍃</div>
<div class="leaf" style="left:55%; animation-duration: 13s;">🍂</div>
<div class="leaf" style="left:65%; animation-duration: 9s;">🍃</div>
<div class="leaf" style="left:75%; animation-duration: 11s;">🍂</div>
<div class="leaf" style="left:85%; animation-duration: 10s;">🍃</div>

""", unsafe_allow_html=True)

# CO2 Rates
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

# Scientific mapping
SCIENTIFIC_TO_COMMON = {
    "Ficus religiosa": "Peepal",
    "Azadirachta indica": "Neem",
    "Ficus benghalensis": "Banyan",
    "Mangifera indica": "Mango",
    "Tectona grandis": "Teak",
    "Polyalthia longifolia": "Ashoka",
    "Syzygium cumini": "Jamun",
    "Tamarindus indica": "Tamarind",
    "Cocos nucifera": "Coconut",
    "Bambusa vulgaris": "Bamboo"
}

# PlantNet API
def analyze_tree_with_plantnet(image):

    api_key = "2b10em1Pf7T3bO7yv58v4865Bu"

    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")

    files = {
        "images": ("tree.jpg", buffered.getvalue(), "image/jpeg")
    }

    data = {"organs": "auto"}

    url = f"https://my-api.plantnet.org/v2/identify/all?api-key={api_key}"

    try:
        response = requests.post(url, files=files, data=data)

        if response.status_code != 200:
            st.error("PlantNet API Error")
            return None

        result = response.json()

        if "results" not in result or len(result["results"]) == 0:
            st.warning("No plant detected")
            return None

        scientific = result["results"][0]["species"]["scientificNameWithoutAuthor"]
        common = SCIENTIFIC_TO_COMMON.get(scientific, "Peepal")

        return {
            "tree_name": common,
            "age_years": 5,
            "height_meters": 5,
            "trunk_diameter_meters": 0.3
        }

    except Exception:
        st.error("Plant detection failed")
        return None

# UI
st.title("🌳 Tree Carbon Calculator")

uploaded_file = st.file_uploader("Upload Tree Image", type=["jpg", "png", "jpeg"])

ai_data = None

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, use_container_width=True)

    with st.spinner("Detecting tree..."):
        ai_data = analyze_tree_with_plantnet(image)

tree_type_default = "Peepal"
tree_age_default = 5
height_default = 5.0
diameter_default = 0.3

if ai_data:
    tree_type_default = ai_data.get("tree_name", tree_type_default)
    tree_age_default = ai_data.get("age_years", tree_age_default)
    height_default = ai_data.get("height_meters", height_default)
    diameter_default = ai_data.get("trunk_diameter_meters", diameter_default)

col1, col2 = st.columns(2)

with col1:
    tree_type = st.selectbox(
        "Tree Type",
        list(INDIAN_TREES.keys()),
        index=list(INDIAN_TREES.keys()).index(tree_type_default)
    )
    num_trees = st.number_input("Number of Trees", min_value=1, value=1)
    tree_age = st.number_input("Tree Age", value=int(tree_age_default))

with col2:
    years = st.number_input("Years", value=5)
    height = st.number_input("Height (m)", value=float(height_default))
    diameter = st.number_input("Diameter (m)", value=float(diameter_default))

if st.button("Calculate Carbon Absorption"):

    base_rate = INDIAN_TREES[tree_type]

    radius = diameter / 2
    volume = math.pi * (radius ** 2) * height

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
        <h1>{total_co2_tons:.3f} TONS</h1>
        <p>({total_co2_kg:.2f} kg)</p>
    </div>
    """, unsafe_allow_html=True)
