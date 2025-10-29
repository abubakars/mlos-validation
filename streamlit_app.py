import streamlit as st
import pandas as pd

# --- App Configuration ---
st.set_page_config(page_title="Access Data Viewer", layout="wide")

# --- Session State for Login ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = None

# --- Login Section ---
def login():
    st.title("🔐 Email Login to Access Data")
    email_input = st.text_input("Enter your email address")

    if st.button("Login"):
        try:
            df = pd.read_csv("access.csv")
        except FileNotFoundError:
            st.error("❌ 'access.csv' not found in the app directory.")
            return

        # Normalize and validate email column
        df.columns = df.columns.str.strip().str.lower()
        if "email" not in df.columns:
            st.error("❌ 'Email' column not found in 'access.csv'. Please check your file.")
            return

        if email_input.strip().lower() in df["email"].str.lower().values:
            st.session_state.logged_in = True
            st.session_state.user_email = email_input.strip().lower()
            st.success("✅ Login successful!")
            st.rerun()
        else:
            st.error("❌ Email not found. Please check your entry or contact admin.")

# --- Main App Content ---
def main_app():
    st.title("📍 MLoS Data Viewer")

    try:
        df = pd.read_csv("access.csv")
    except FileNotFoundError:
        st.error("❌ 'access.csv' not found. Please check your file path.")
        return

    # Select only the required columns
    required_cols = ["lga_name", "ward_name", "settlement_name", "primary_settlement_name"]
    df.columns = df.columns.str.strip().str.lower()
    df = df[required_cols]

    # --- Sidebar Filters ---
    st.sidebar.header("🔎 Filter Options")

    lgas = sorted(df["lga_name"].dropna().unique())
    selected_lga = st.sidebar.selectbox("Select LGA", ["All"] + list(lgas))

    if selected_lga != "All":
        df = df[df["lga_name"] == selected_lga]

    wards = sorted(df["ward_name"].dropna().unique())
    selected_ward = st.sidebar.selectbox("Select Ward", ["All"] + list(wards))

    if selected_ward != "All":
        df = df[df["ward_name"] == selected_ward]

    # --- Search Settlements ---
    search_term = st.sidebar.text_input("Search Settlement")
    if search_term:
        df = df[df["settlement_name"].str.contains(search_term, case=False, na=False)]

    # --- Display Data ---
    st.dataframe(df, use_container_width=True)

    # --- Logout Button ---
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_email = None
        st.rerun()

# --- App Flow ---
if not st.session_state.logged_in:
    login()
else:
    main_app()
