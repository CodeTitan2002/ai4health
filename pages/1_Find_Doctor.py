# pages/1_Find_Doctor.py
import streamlit as st
import pandas as pd
from findDoc import find_doctors

st.set_page_config(page_title="Find Nearby Doctors", layout="centered")
st.title("🏥 Find a Doctor Near You")

# User Input
disease = st.text_input("Enter the diagnosed disease", placeholder="e.g., diabetes")
city = st.text_input("Enter your city", placeholder="e.g., Delhi")

if st.button("🔍 Search"):
    if not disease or not city:
        st.warning("Please enter both disease and city.")
    else:
        result = find_doctors(disease, city)
        st.markdown("---")
        if isinstance(result, str):
            st.error(result)
        else:
            st.success(f"✅ Found {len(result)} doctor(s) in {city.title()}:")
            st.dataframe(result, use_container_width=True)
