import streamlit as st
import pandas as pd

st.title("📍 MLoS Access Portal")

# --- Load CSV files ---
access_url = "https://github.com/abubakars/mlos-validation/raw/main/access.csv"
mlos_url = "https://github.com/abubakars/mlos-validation/raw/main/Niger%20MLoS%2012.1_.csv"

# Read both files
access_df = pd.read_csv(access_url)
mlos_df = pd.read_csv(mlos_url)

# Clean up column names
access_df.columns = access_df.columns.str.strip().str.lower()
mlos_df.columns = mlos_df.columns.str.strip().str.lower()

# --- Initialize session state for login ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_lga" not in st.session_state:
    st.session_state.user_lga = None

# --- LOGIN SECTION ---
if not st.session_state.logged_in:
    email = st.text_input("Enter your email")
    if st.button("Login"):
        if "email" not in access_df.columns:
            st.error("❌ 'Email' column not found in access.csv.")
        else:
            user = access_df[access_df["email"].str.lower() == email.lower()]
            if user.empty:
                st.error("❌ Invalid email. Please try again.")
            else:
                st.session_state.logged_in = True
                st.session_state.user_lga = user.iloc[0]["lga"]
                st.success(f"✅ Login successful! Welcome to {st.session_state.user_lga} LGA.")
else:
    # --- MAIN APP AFTER LOGIN ---
    user_lga = st.session_state.user_lga
    st.subheader(f"Settlements for **{user_lga}**")

    # Filter MLoS data by user's LGA
    df = mlos_df[mlos_df["lga_name"].str.lower() == user_lga.lower()]

    # Keep only selected columns
    cols_to_show = ["lga_name", "ward_name", "settlement_name", "primary_settlement_name"]
    df = df[[c for c in cols_to_show if c in df.columns]]

    # --- Ward filter ---
    if "ward_name" in df.columns:
        wards = sorted(df["ward_name"].dropna().unique())
        ward = st.selectbox("Filter by Ward", ["All"] + wards)
        if ward != "All":
            df = df[df["ward_name"] == ward]

    # --- Search settlement ---
    search = st.text_input("Search for Settlement")
    if search:
        df = df[df["settlement_name"].str.contains(search, case=False, na=False)]

    # --- Show total settlements ---
    st.write(f"Total settlements: {len(df)}")

    # --- Display table ---
    st.dataframe(df, use_container_width=True)

    # --- Logout button ---
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_lga = None
        st.experimental_rerun()
