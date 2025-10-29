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

# --- Login Section ---
email = st.text_input("Enter your email")

if st.button("Login"):
    if "email" not in access_df.columns:
        st.error("❌ 'Email' column not found in access.csv.")
    else:
        # Check if email exists
        user = access_df[access_df["email"].str.lower() == email.lower()]

        if user.empty:
            st.error("❌ Invalid email. Please try again.")
        else:
            st.success("✅ Login successful!")

            # Get LGA name from access file
            user_lga = user.iloc[0]["lga"] if "lga" in user.columns else None

            if not user_lga:
                st.warning("⚠️ No LGA column found in access.csv.")
            else:
                st.subheader(f"Welcome! Showing settlements for **{user_lga}**")

                # Filter MLoS data by user's LGA
                df = mlos_df[mlos_df["lga_name"].str.lower() == user_lga.lower()]

                # Show only needed columns
                show_cols = ["lga_name", "ward_name", "settlement_name", "primary_settlement_name"]
                available = [c for c in show_cols if c in df.columns]
                df = df[available]

                # --- Ward filter ---
                wards = sorted(df["ward_name"].dropna().unique()) if "ward_name" in df else []
                ward = st.selectbox("Filter by Ward", ["All"] + wards)
                if ward != "All":
                    df = df[df["ward_name"] == ward]

                # --- Search box ---
                search = st.text_input("Search for Settlement")
                if search:
                    df = df[df["settlement_name"].str.contains(search, case=False, na=False)]

                # --- Show total settlements ---
                st.write(f"Total settlements in this view: {len(df)}")

                # --- Display table ---
                st.dataframe(df, use_container_width=True)
