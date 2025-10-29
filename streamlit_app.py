import streamlit as st
import pandas as pd

# --- URLs for your CSV files ---
ACCESS_URL = "https://github.com/abubakars/mlos-validation/raw/main/access.csv"
MLOS_URL = "https://github.com/abubakars/mlos-validation/raw/main/Niger%20MLoS%2012.1_.csv"

# --- Load and clean data ---
@st.cache_data
def load_data():
    access_df = pd.read_csv(ACCESS_URL)
    mlos_df = pd.read_csv(MLOS_URL)

    # Clean column names
    access_df.columns = access_df.columns.str.strip().str.lower()
    mlos_df.columns = mlos_df.columns.str.strip().str.lower()

    # Clean up data
    access_df["email"] = access_df["email"].astype(str).str.strip().str.lower()
    access_df["lga"] = access_df["lga"].astype(str).str.strip().str.lower()

    mlos_df["lga_name"] = mlos_df["lga_name"].astype(str).str.strip().str.lower()
    if "ward_name" in mlos_df.columns:
        mlos_df["ward_name"] = mlos_df["ward_name"].astype(str).str.strip().str.lower()
    if "settlement_name" in mlos_df.columns:
        mlos_df["settlement_name"] = mlos_df["settlement_name"].astype(str).str.strip().str.lower()

    return access_df, mlos_df


# --- Load data ---
access_df, mlos_df = load_data()

# --- Initialize session state ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_lga" not in st.session_state:
    st.session_state.user_lga = None


# --- Login Page ---
if not st.session_state.logged_in:
    st.title("🔐 MLoS Access Portal")

    email = st.text_input("Enter your registered email").strip().lower()

    if st.button("Login"):
        if email:
            if email in access_df["email"].values:
                user = access_df[access_df["email"] == email]
                user_lga = user.iloc[0]["lga"]

                st.session_state.logged_in = True
                st.session_state.user_lga = user_lga

                st.success(f"✅ Login successful! Access granted for LGA: {user_lga.title()}")
                st.rerun()
            else:
                st.error("❌ Invalid email. Please try again.")
        else:
            st.warning("⚠️ Please enter your email before logging in.")


# --- Main Dashboard ---
else:
    user_lga = st.session_state.user_lga
    st.title(f"📍 MLoS Dashboard — {user_lga.title()} LGA")

    # Logout button
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_lga = None
        st.rerun()

    # Filter LGA data
    lga_data = mlos_df[mlos_df["lga_name"] == user_lga]

    if not lga_data.empty:
        total_settlements = len(lga_data)
        st.info(f"Total number of settlements in **{user_lga.title()}**: {total_settlements}")

        # --- Ward Filter ---
        wards = sorted(lga_data["ward_name"].dropna().unique())
        selected_ward = st.selectbox("Filter by Ward", ["All Wards"] + wards)

        if selected_ward != "All Wards":
            lga_data = lga_data[lga_data["ward_name"] == selected_ward]

        # --- Settlement Search ---
        settlement_list = sorted(lga_data["settlement_name"].dropna().unique())
        search_settlement = st.selectbox("🔍 Search Settlement", ["All Settlements"] + settlement_list)

        if search_settlement != "All Settlements":
            selected_data = lga_data[lga_data["settlement_name"] == search_settlement]

            if not selected_data.empty:
                st.subheader(f"🏠 Details for {search_settlement.title()}")
                st.dataframe(selected_data.transpose())
            else:
                st.warning("Settlement not found.")
        else:
            st.dataframe(lga_data)

    else:
        st.warning("⚠️ No MLoS data found for your LGA.")
