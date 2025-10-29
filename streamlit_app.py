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

# --- Initialize session state ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_lga" not in st.session_state:
    st.session_state.user_lga = None
if "selected_settlement" not in st.session_state:
    st.session_state.selected_settlement = None

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

# --- MAIN APP ---
else:
    user_lga = st.session_state.user_lga
    st.subheader(f"Settlements for **{user_lga}**")

    # Filter MLoS data by user's LGA
    df = mlos_df[mlos_df["lga_name"].str.lower() == user_lga.lower()]

    # Columns to show in table
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

    # --- Settlement selection ---
    settlements = df["settlement_name"].dropna().unique().tolist()
    selected = st.selectbox("Select a Settlement to View/Edit", ["None"] + settlements)

    if selected != "None":
        st.session_state.selected_settlement = selected
        # Show sidebar info
        st.sidebar.header(f"🛠 Edit Settlement: {selected}")

        # Get full record
        record = mlos_df[
            (mlos_df["lga_name"].str.lower() == user_lga.lower()) &
            (mlos_df["settlement_name"].str.lower() == selected.lower())
        ].iloc[0]

        updated_data = {}
        for col in mlos_df.columns:
            value = record[col]
            new_val = st.sidebar.text_input(col, value)
            updated_data[col] = new_val

        if st.sidebar.button("💾 Save Changes"):
            for key, val in updated_data.items():
                mlos_df.loc[
                    (mlos_df["lga_name"].str.lower() == user_lga.lower()) &
                    (mlos_df["settlement_name"].str.lower() == selected.lower()),
                    key
                ] = val
            st.sidebar.success("✅ Settlement information updated successfully!")

    # --- Display table ---
    st.dataframe(df, use_container_width=True)

    # --- Logout ---
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_lga = None
        st.session_state.selected_settlement = None
        st.experimental_rerun()
