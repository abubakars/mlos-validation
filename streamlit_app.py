import streamlit as st
import pandas as pd

# --- GitHub raw CSV links ---
ACCESS_URL = "https://raw.githubusercontent.com/abubakars/mlos-validation/main/access.csv"
MLOS_URL = "https://raw.githubusercontent.com/abubakars/mlos-validation/main/Niger%20MLoS%2012.1_.csv"

@st.cache_data
def load_data():
    # Try both comma and semicolon separators
    try:
        access_df = pd.read_csv(ACCESS_URL)
    except Exception:
        access_df = pd.read_csv(ACCESS_URL, sep=';')
    
    try:
        mlos_df = pd.read_csv(MLOS_URL)
    except Exception:
        mlos_df = pd.read_csv(MLOS_URL, sep=';')

    # Normalize column names (remove spaces, lowercase)
    access_df.columns = access_df.columns.str.strip().str.lower()
    mlos_df.columns = mlos_df.columns.str.strip().str.lower()

    return access_df, mlos_df

access_df, mlos_df = load_data()

# --- Show detected columns (for debugging) ---
st.sidebar.write("Access.csv columns:", list(access_df.columns))
st.sidebar.write("MLoS.csv columns:", list(mlos_df.columns))

# --- Login Section ---
st.title("🔐 MLoS Access Portal")

email = st.text_input("Enter your email")
phone = st.text_input("Enter your phone number")

if st.button("Login"):
    # Make sure expected columns exist
    required_cols = ["email", "phone", "lga"]
    if not all(col in access_df.columns for col in required_cols):
        st.error("❌ 'access.csv' must contain at least Email, Phone, and LGA columns.")
    else:
        # Normalize user inputs
        email = email.strip().lower()
        phone = phone.strip()

        # Verify user
        user = access_df[
            (access_df["email"].str.lower() == email) &
            (access_df["phone"].astype(str) == phone)
        ]

        if not user.empty:
            user_lga = user.iloc[0]["lga"]
            st.success(f"✅ Login successful! Access granted for LGA: {user_lga}")

            # Match on any common LGA column name
            possible_lga_cols = ["lga", "lga_name", "lga name"]
            lga_col = next((c for c in possible_lga_cols if c in mlos_df.columns), None)

            if lga_col:
                lga_data = mlos_df[mlos_df[lga_col].str.lower() == user_lga.lower()]
                if not lga_data.empty:
                    st.dataframe(lga_data)
                else:
                    st.warning(f"No MLoS data found for {user_lga}.")
            else:
                st.error("❌ No LGA column found in MLoS CSV.")
        else:
            st.error("❌ Invalid email or phone number. Please try again.")
