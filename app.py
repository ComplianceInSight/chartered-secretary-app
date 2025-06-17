import streamlit as st
import pandas as pd

# App title
st.set_page_config(page_title="Chartered Secretary Reader", layout="wide")
st.title("📘 Chartered Secretary Article Finder")

# Load Excel
excel_file = "Updated_Chartered_Secretary.xlsx"
xls = pd.read_excel(excel_file, sheet_name=None)

# Create tabs for each sheet
tabs = st.tabs(list(xls.keys()))

for tab, (sheet_name, df) in zip(tabs, xls.items()):
    with tab:
        st.subheader(f"📂 {sheet_name}")
        
        # Search box
        search = st.text_input(f"Search in {sheet_name}", key=sheet_name)
        filtered_df = df.copy()
        if search:
            filtered_df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]

        # Show table with PDF links
        for index, row in filtered_df.iterrows():
            col1, col2, col3 = st.columns([4, 2, 2])
            with col1:
                st.markdown(f"**{row.get('Title', 'Untitled')}**")
            with col2:
                st.write(f"📄 Page: {int(row.get('Page', 1))}")
            with col3:
                if pd.notna(row.get("Link")):
                    st.markdown(f"[🔗 Open PDF]({row['Link']})", unsafe_allow_html=True)
                else:
                    st.write("No link")
