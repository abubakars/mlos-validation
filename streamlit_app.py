import streamlit as st
import pandas as pd

# --- Load CSVs from GitHub raw links ---
ACCESS_URL = "https://github.com/abubakars/mlos-validation/raw/main/access.csv"
MLOS_URL = "https://github.com/abubakars/mlos-validation/raw/main/Niger%20MLoS%2012.1_.csv"

@st.cache_data
def load_data():
    access_df = pd.read_csv(ACCESS_URL)
    mlos_df = pd.read_csv(MLOS_URL)
    return access_df, mlos_df

# --- Load Data ---
access_df, mlos_df = load_data()

st.title("🔐 MLoS Access Portal")

# --- Debugging: Show columns if needed ---
# st.write("Access CSV columns:", list(access_df.columns))
# st.write("MLOS CSV columns:", list(mlos_df.columns))

# --- Login Section ---
email = st.text_input("Enter your email").strip()

if st.button("Login"):
    # Normalize all email column names
    email_cols = [c for c in access_df.columns if c.lower() in ["email", "email_address", "user_email"]]
    if not email_cols:
        st.error("❌ 'Email' column not found in access.csv. Please check the file.")
    else:
        email_col = email_cols[0]
        user = access_df[access_df[email_col].str.lower() == email.lower()]

        if not user.empty:
            user_lga = user.iloc[0]["LGA"]
            st.success(f"✅ Login successful! Access granted for LGA: {user_lga}")

            # Filter MLOS data for user LGA
            lga_data = mlos_df[mlos_df["lga_name"].str.lower() == user_lga.lower()]

            if not lga_data.empty:
                st.subheader(f"📍 LGA Summary: {user_lga}")
                st.info(f"Total settlements in {user_lga}: **{len(lga_data)}**")

                # --- Ward Filter ---
                wards = sorted(lga_data["ward_name"].dropna().unique())
                selected_ward = st.selectbox("Filter by Ward (optional):", ["All"] + wards)
                if selected_ward != "All":
                    lga_data = lga_data[lga_data["ward_name"] == selected_ward]

                # --- Settlement Search ---
                search_query = st.text_input("Search for a Settlement:")
                if search_query:
                    lga_data = lga_data[lga_data["settlement_name"].str.contains(search_query, case=False, na=False)]

                st.dataframe(lga_data)

                # --- Settlement Details Box ---
                selected_settlement = st.selectbox(
                    "Select a settlement to view details:",
                    ["None"] + list(lga_data["settlement_name"].dropna().unique())
                )

                if selected_settlement != "None":
                    settlement_details = lga_data[lga_data["settlement_name"] == selected_settlement].iloc[0]
                    st.subheader(f"🏠 Settlement Details: {selected_settlement}")
                    st.json(settlement_details.to_dict())

            else:
                st.warning("⚠️ No MLoS data found for your LGA.")
        else:
            st.error("❌ Invalid email. Please try again.")
