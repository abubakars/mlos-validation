import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# ---- Load your data ----
df = pd.read_excel("settlements.xlsx")

st.title("🏘️ Settlement Management Dashboard")

# ---- LGA Filter ----
lga_list = df["LGA"].unique()
selected_lga = st.selectbox("Select LGA", lga_list)

filtered_lga = df[df["LGA"] == selected_lga]

# ---- Ward Filter ----
ward_list = filtered_lga["Ward"].unique()
selected_ward = st.selectbox("Select Ward", ward_list)

filtered_ward = filtered_lga[filtered_lga["Ward"] == selected_ward]

# ---- Search by Settlement ----
search = st.text_input("🔍 Search Settlement Name")
if search:
    filtered_ward = filtered_ward[filtered_ward["Settlement"].str.contains(search, case=False, na=False)]

# ---- AgGrid Table ----
gb = GridOptionsBuilder.from_dataframe(filtered_ward)
gb.configure_selection("single", use_checkbox=True)
gb.configure_grid_options(domLayout="normal", enableBrowserTooltips=True)
grid_options = gb.build()

grid_response = AgGrid(
    filtered_ward,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    theme="streamlit",
    height=350,
)

selected_rows = grid_response["selected_rows"]

# ---- Settlement Detail Box ----
if selected_rows:
    selected = selected_rows[0]  # only one selected
    st.subheader(f"🏠 Settlement Details: {selected['Settlement']}")

    with st.form("edit_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_settlement = st.text_input("Settlement Name", selected["Settlement"])
            new_lga = st.text_input("LGA", selected["LGA"])
            new_ward = st.text_input("Ward", selected["Ward"])
        with col2:
            new_lat = st.number_input("Latitude", value=float(selected["Latitude"]))
            new_lon = st.number_input("Longitude", value=float(selected["Longitude"]))
            new_population = st.number_input("Population", value=int(selected.get("Population", 0)))

        submitted = st.form_submit_button("💾 Update Record")

        if submitted:
            # Update in DataFrame
            df.loc[df["Settlement"] == selected["Settlement"], ["Settlement", "LGA", "Ward", "Latitude", "Longitude", "Population"]] = [
                new_settlement, new_lga, new_ward, new_lat, new_lon, new_population
            ]
            df.to_excel("settlements_updated.xlsx", index=False)
            st.success("✅ Settlement details updated successfully!")
            st.rerun()
