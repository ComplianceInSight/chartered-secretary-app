import streamlit as st
import pandas as pd

# Page config
st.set_page_config(page_title="Chartered Secretary App", layout="wide", page_icon="📘")

st.markdown("""
    <style>
    body { background-color: #f9f9f9; }
    .block-container { padding-top: 2rem; }
    .stTabs [data-baseweb="tab"] { font-size: 16px; font-weight: 600; }
    .stButton>button { background-color: #4CAF50; color: white; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <h1 style='color:#2C3E50;'>📘 Chartered Secretary Article & Judgement Explorer</h1>
""", unsafe_allow_html=True)

excel_file = "Updated_Chartered_Secretary.xlsx"
xls = pd.read_excel(excel_file, sheet_name=None)

# Use actual sheet names from Excel file
sheet_names = list(xls.keys())

field_map = {
    "Articles": ["Title", "Author", "Section", "Reference", "Link"],
    "Judgements": ["Title", "Type", "Section", "Summary", "Link"],
    "Updates": ["Title", "Type", "Details", "Link"],
    "ROC & RD Adjudication": ["Title", "Section", "Authority", "Judgement", "Link"],
}

filter_map = {
    "Articles": ["Author", "Section", "Reference"],
    "Judgements": ["Type", "Section"],
    "Updates": ["Type"],
    "ROC & RD Adjudication": ["Section", "Authority"]
}

# Create tabs for each sheet
tabs = st.tabs(sheet_names)

for tab, sheet_name in zip(tabs, sheet_names):
    with tab:
        df = xls[sheet_name].copy()
        display_fields = field_map.get(sheet_name, df.columns.tolist())
        filters = filter_map.get(sheet_name, [])

        st.subheader(f"🔍 {sheet_name}")

        for filt in filters:
            if filt in df.columns:
                options = sorted(df[filt].dropna().astype(str).unique())
                selected = st.selectbox(f"Filter by {filt}", ["All"] + options, key=f"filter_{filt}_{sheet_name}")
                if selected != "All":
                    df = df[df[filt].astype(str) == selected]

        search_term = st.text_input("🔎 Search", key=f"search_{sheet_name}")
        if search_term:
            df = df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]

        for _, row in df.iterrows():
            st.markdown("---")
            cols = st.columns(len(display_fields))
            for i, field in enumerate(display_fields):
                value = row.get(field, "-")
                if pd.isna(value): value = "-"
                if field == "Link" and value:
                    cols[i].markdown(f"[📄 Open PDF]({value})", unsafe_allow_html=True)
                else:
                    cols[i].markdown(f"**{field}**: {value}")

        if df.empty:
            st.warning("No records match your filters or search.")
