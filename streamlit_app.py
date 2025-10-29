import streamlit as st
import pandas as pd

# --- App Configuration ---
st.set_page_config(page_title="Access Data Viewer", layout="wide")

# --- Session State for Login ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- Login Section ---
def login():
    st.title("🔐 Login to Access Data")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        # Replace with your credentials or authentication logic
        if username == "admin" and password == "1234":
            st.session_state.logged_in = True
            st.success("✅ Login successful!")
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

# --- Main App Content ---
def main_app():
    st.title("📍 MLoS Data Viewer")
    
    try:
        df = pd.read_csv("access.csv")
    except FileNotFoundError:
        st.error("❌ File 'access.csv' not found. Please check the file path.")
        return
    
    # Columns to show
    show_cols = ["lga_name", "ward_name", "settlement_name", "primary_settlement_name"]
    df = df[show_cols]
    
    # --- Filters ---
    st.sidebar.header("🔎 Filter Options")

    lgas = sorted(df["lga_name"].dropna().unique())
    selected_lga = st.sidebar.selectbox("Select LGA", ["All"] + list(lgas))
    
    if selected_lga != "All":
        df = df[df["lga_name"] == selected_lga]
    
    wards = sorted(df["ward_name"].dropna().unique())
    selected_ward = st.sidebar.selectbox("Select Ward", ["All"] + list(wards))
    
    if selected_ward != "All":
        df = df[df["ward_name"] == selected_ward]

    # --- Search Bar ---
    search_term = st.sidebar.text_input("Search Settlement Name")
    if search_term:
        df = df[df["settlement_name"].str.contains(search_term, case=False, na=False)]
    
    # --- Display Data ---
    st.dataframe(df, use_container_width=True)
    
    # --- Logout Button ---
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# --- App Logic ---
if not st.session_state.logged_in:
    login()
else:
    main_app()
