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

access_df, mlos_df = load_data()

# --- Login Section ---
st.title("🔐 MLoS Access Portal")

email = st.text_input("Enter your email")
phone = st.text_input("Enter your phone number")

if st.button("Login"):
    user = access_df[
        (access_df["Email"].str.lower() == email.lower()) &
        (access_df["Phone"].astype(str) == str(phone))
    ]
    
    if not user.empty:
        user_lga = user.iloc[0]["LGA"]
        st.success(f"✅ Login successful! Access granted for LGA: {user_lga}")
        
        # Filter MLoS data for user's LGA
        lga_data = mlos_df[mlos_df["lga_name"].str.lower() == user_lga.lower()]
        if not lga_data.empty:
            st.dataframe(lga_data)
        else:
            st.warning("No MLoS data found for your LGA.")
    else:
        st.error("❌ Invalid email or phone number. Please try again.")
