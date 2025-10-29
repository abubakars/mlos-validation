import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# --- URLs for your CSV files ---
ACCESS_URL = "https://github.com/abubakars/mlos-validation/raw/main/access.csv"
MLOS_URL = "https://github.com/abubakars/mlos-validation/raw/main/Niger%20MLoS%2012.1_.csv"

# --- Cache data loading ---
@st.cache_data
def load_data():
    access_df = pd.read_csv(ACCESS_URL)
    mlos_df = pd.read_csv(MLOS_URL)
    return access_df, mlos_df

access_df, mlos_df = load_data()

# --- App Title ---
st.title("🔐 MLoS Access & Data Portal")

# --- Login Section ---
email = st.text_input("Enter your email").strip().lower()

if st.button("Login"):
    if "Email" not in access_df.columns:
        st.error("❌ 'Email' column not found in access.csv. Please check the file.")
    else:
        user = access_df[access_df["Email"].str.lower() == email]
        if not user.empty:
            st.session_state["logged_in"] = True
            st.session_state["user_lga"] = user.iloc[0]["LGA"]
            st.success(f"✅ Welcome! Access granted for LGA: {st.session_state['user_lga']}")
        else:
            st.error("❌ Invalid email. Please try again.")

# --- If logged in ---
if st.session_state.get("logged_in", False):

    user_lga = st.session_state["user_lga"]
    lga_data = mlos_df[mlos_df["lga_name"].str.lower() == user_lga.lower()]

    if lga_data.empty:
        st.warning("No MLoS data found for your LGA.")
    else:
        # --- Summary info ---
        total_settlements = lga_data["settlement_name"].nunique()
        st.info(f"📍 Total Settlements in **{user_lga}**: {total_settlements}")

        # --- Ward filter ---
        wards = sorted(lga_data["ward_name"].dropna().unique())
        selected_ward = st.selectbox("Filter by Ward", ["All"] + wards)

        if selected_ward != "All":
            filtered_data = lga_data[lga_data["ward_name"] == selected_ward]
        else:
            filtered_data = lga_data.copy()

        # --- Search box ---
        search_query = st.text_input("🔍 Search Settlement Name")
        if search_query:
            filtered_data = filtered_data[
                filtered_data["settlement_name"].str.contains(search_query, case=False, na=False)
            ]

        # --- AgGrid setup for interactive table ---
        st.subheader("🧭 Settlement Data Table")

        gb = GridOptionsBuilder.from_dataframe(filtered_data)
        gb.configure_selection('single')  # single row selection
        gb.configure_grid_options(domLayout='normal')
        gb.configure_default_column(editable=True, resizable=True)
        grid_options = gb.build()

        grid_response = AgGrid(
            filtered_data,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.SELECTION_CHANGED | GridUpdateMode.VALUE_CHANGED,
            height=400,
            fit_columns_on_grid_load=True
        )

        selected_rows = grid_response["selected_rows"]

        # --- Show full details when row is selected ---
        if selected_rows:
            st.subheader("📋 Settlement Details")
            selected_row = pd.DataFrame(selected_rows).iloc[0]
            st.write(selected_row)

            st.success("✅ You can edit directly in the table above. Changes are temporary until saved.")

        # --- Save button (optional) ---
        if st.button("💾 Save Updated Data"):
            updated_df = grid_response["data"]
            csv_path = "updated_mlos.csv"
            updated_df.to_csv(csv_path, index=False)
            st.success("✅ Updates saved locally as 'updated_mlos.csv'.")
            st.download_button("Download Updated CSV", data=open(csv_path, "rb"), file_name="updated_mlos.csv")

