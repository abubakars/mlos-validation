import streamlit as st
import pandas as pd

# --- Load CSVs from GitHub raw links ---
ACCESS_URL = "https://github.com/abubakars/mlos-validation/raw/main/access.csv"
MLOS_URL = "https://github.com/abubakars/mlos-validation/raw/main/Niger%20MLoS%2012.1_.csv"

# --- Load and clean data ---
@st.cache_data
def load_data():
    # Read both CSVs
    access_df = pd.read_csv(ACCESS_URL)
    mlos_df = pd.read_csv(MLOS_URL)

    # Standardize column names
    access_df.columns = access_df.columns.str.strip().str.lower()
    mlos_df.columns = mlos_df.columns.str.strip().str.lower()

    # Clean values for consistent matching
    if "email" in access_df.columns:
        access_df["email"] = access_df["email"].astype(str).str.strip().str.lower()
    if "lga" in access_df.columns:
        access_df["lga"] = access_df["lga"].astype(str).str.strip().str.lower()
    if "lga_name" in mlos_df.columns:
        mlos_df["lga_name"] = mlos_df["lga_name"].astype(str).str.strip().str.lower()
    if "ward_name" in mlos_df.columns:
        mlos_df["ward_name"] = mlos_df["ward_name"].astype(str).str.strip().str.lower()

    return access_df, mlos_df

# --- Load data ---
access_df, mlos_df = load_data()

# --- App title ---
st.title("🔐 MLoS Access Portal")

# --- Email input ---
email = st.text_input("Enter your registered email").strip().lower()

# --- Login button ---
if st.button("Login"):
    if email:
        # Check if email exists in access file
        if email in access_df["email"].values:
            user = access_df[access_df["email"] == email]
            user_lga = user.iloc[0]["lga"]

            st.success(f"✅ Login successful! Access granted for LGA: {user_lga.title()}")

            # Filter MLoS data for that LGA
            lga_data = mlos_df[mlos_df["lga_name"] == user_lga]

            if not lga_data.empty:
                # Count total settlements
                total_settlements = len(lga_data)
                st.info(f"📍 Total number of settlements in **{user_lga.title()}**: {total_settlements}")

                # --- Ward filter ---
                wards = sorted(lga_data["ward_name"].dropna().unique())
                selected_ward = st.selectbox("Filter by Ward", ["All Wards"] + wards)

                if selected_ward != "All Wards":
                    ward_data = lga_data[lga_data["ward_name"] == selected_ward]
                    st.info(f"📍 Showing settlements in **{selected_ward.title()} Ward** — {len(ward_data)} records")
                    st.dataframe(ward_data)
                else:
                    st.dataframe(lga_data)

            else:
                st.warning("⚠️ No MLoS data found for your LGA.")
        else:
            st.error("❌ Invalid email. Please try again.")
    else:
        st.warning("⚠️ Please enter your email before logging in.")
