import streamlit as st
import pandas as pd

# ✅ App settings
st.set_page_config(layout="wide", page_title="Chartered Secretary Extracts")

# Load Excel
@st.cache_data
def load_excel():
    return pd.read_excel("Updated_Chartered_Secretary.xlsx", sheet_name=None)

sheets = load_excel()

st.title("📘 Chartered Secretary Knowledge Hub")

# Icons for each tab
tabs = st.tabs(["📄 Articles", "⚖️ Judgements", "🧾 Updates", "🏛️ ROC & RD Adjudication"])

# Pagination helper
def paginate(df, key_prefix, page_size=10):
    total_pages = (len(df) - 1) // page_size + 1
    current_page = st.session_state.get(f"{key_prefix}_page", 1)

    # Display content
    start_idx = (current_page - 1) * page_size
    end_idx = start_idx + page_size
    df_page = df.iloc[start_idx:end_idx]

    for _, row in df_page.iterrows():
        yield row

    # Pagination controls
    st.divider()
    cols = st.columns(min(total_pages, 10) + 2)
    for i in range(min(total_pages, 10)):
        if cols[i].button(str(i + 1), key=f"{key_prefix}_btn_{i}"):
            st.session_state[f"{key_prefix}_page"] = i + 1
    if total_pages > 10:
        cols[-2].markdown("...")
        if cols[-1].button("Next ➡️", key=f"{key_prefix}_next"):
            if current_page < total_pages:
                st.session_state[f"{key_prefix}_page"] = current_page + 1

# ---------- TAB 1: ARTICLES ----------
with tabs[0]:
    df = sheets["Articles"].drop(columns=["Page"])

    col1, col2, col3 = st.columns(3)
    with col1:
        selected_author = st.selectbox("Filter by Author", ["All"] + sorted(df["Auther"].dropna().unique()))
    with col2:
        selected_section = st.selectbox("Filter by Section", ["All"] + sorted(df["Section"].dropna().astype(str).unique()))
    with col3:
        selected_ref = st.selectbox("Filter by Reference", ["All"] + sorted(df["Ref"].dropna().unique()))

    if selected_author != "All":
        df = df[df["Auther"] == selected_author]
    if selected_section != "All":
        df = df[df["Section"].astype(str) == selected_section]
    if selected_ref != "All":
        df = df[df["Ref"] == selected_ref]

    for row in paginate(df, "articles"):
        st.markdown(f"""
        <div style='margin-bottom:15px;'>
        <b>Title:</b> {row['Title']}<br>
        <b>Author:</b> {row['Auther']} &nbsp;&nbsp;&nbsp;
        <b>Section:</b> {row['Section']} &nbsp;&nbsp;&nbsp;
        <b>Reference:</b> {row['Ref']} &nbsp;&nbsp;&nbsp;
        <a href='{row['Link']}' target='_blank'>📄 Open PDF</a>
        </div>
        <hr>
        """, unsafe_allow_html=True)

# ---------- TAB 2: JUDGEMENTS ----------
with tabs[1]:
    df = sheets["Judgements"].drop(columns=["Page"])

    col1, col2 = st.columns(2)
    with col1:
        selected_type = st.selectbox("Filter by Type", ["All"] + sorted(df["Type"].dropna().unique()))
    with col2:
        selected_section = st.selectbox("Filter by Section", ["All"] + sorted(df["Section"].dropna().astype(str).unique()))

    if selected_type != "All":
        df = df[df["Type"] == selected_type]
    if selected_section != "All":
        df = df[df["Section"].astype(str) == selected_section]

    for row in paginate(df, "judgements"):
        st.markdown(f"""
        <div style='margin-bottom:15px;'>
        <b>Title:</b> {row['Title']}<br>
        <b>Type:</b> {row['Type']} &nbsp;&nbsp;&nbsp;
        <b>Section:</b> {row['Section']}<br>
        <b>Summary:</b> {row['Summary']}<br>
        <a href='{row['Link']}' target='_blank'>📄 Open PDF</a>
        </div>
        <hr>
        """, unsafe_allow_html=True)

# ---------- TAB 3: UPDATES ----------
with tabs[2]:
    df = sheets["Updates"].drop(columns=["Page"])

    selected_type = st.selectbox("Filter by Type", ["All"] + sorted(df["Type"].dropna().unique()))
    if selected_type != "All":
        df = df[df["Type"] == selected_type]

    for row in paginate(df, "updates"):
        st.markdown(f"""
        <div style='margin-bottom:15px;'>
        <b>Title:</b> {row['Title']}<br>
        <b>Type:</b> {row['Type']} &nbsp;&nbsp;&nbsp;
        <a href='{row['Link']}' target='_blank'>📄 Open PDF</a>
        </div>
        <hr>
        """, unsafe_allow_html=True)

# ---------- TAB 4: ROC & RD ADJUDICATION ----------
with tabs[3]:
    df = sheets["ROC & RD ADJUDICATION"].drop(columns=["Page"])

    col1, col2 = st.columns([1, 3])
    with col1:
        section_filter = st.selectbox("Filter by Section", ["All"] + sorted(df["Section"].dropna().astype(str).unique()))
    with col2:
        authority_filter = st.selectbox("Filter by Authority", ["All"] + sorted(df["Authority"].dropna().unique()))

    if section_filter != "All":
        df = df[df["Section"].astype(str) == section_filter]
    if authority_filter != "All":
        df = df[df["Authority"] == authority_filter]

    for row in paginate(df, "roc"):
        st.markdown(f"""
        <div style='margin-bottom:20px;'>
        <b>Month:</b> {row['Month']} &nbsp;&nbsp;&nbsp;
        <b>Title:</b> {row['Title']}<br>
        <b>Section:</b> {row['Section']} &nbsp;&nbsp;&nbsp;
        <b>Authority:</b> {row['Authority']}<br>
        <b>Judgement:</b> <span style='display:inline-block; max-width:90%; text-align:justify;'>{row['Judgement']}</span><br>
        <a href='{row['Link']}' target='_blank'>📄 Open PDF</a>
        </div>
        <hr>
        """, unsafe_allow_html=True)
