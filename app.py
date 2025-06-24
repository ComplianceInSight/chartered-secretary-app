import streamlit as st
import pandas as pd
import json
import os

# App settings
st.set_page_config(layout="wide", page_title="Chartered Secretary Extracts")

# Font Awesome
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
""", unsafe_allow_html=True)

BOOKMARK_FILE = "bookmarks.json"

# Load or initialize bookmarks
if os.path.exists(BOOKMARK_FILE):
    with open(BOOKMARK_FILE, "r") as f:
        st.session_state.bookmarks = json.load(f)
else:
    st.session_state.bookmarks = []

def save_bookmarks():
    with open(BOOKMARK_FILE, "w") as f:
        json.dump(st.session_state.bookmarks, f)

@st.cache_data
def load_excel():
    return pd.read_excel("Updated_Chartered_Secretary.xlsx", sheet_name=None)

sheets = load_excel()

search_query = st.text_input("🔍 Global Search across all content")

if search_query:
    st.markdown("---")
    st.subheader(f"🔎 Search Results for: '{search_query}'")

    def search_in_df(df, columns):
        mask = df[columns].astype(str).apply(lambda row: row.str.contains(search_query, case=False, na=False)).any(axis=1)
        return df[mask]

    def show_results(df, label, icon):
        if not df.empty:
            st.markdown(f"### {icon} {label} ({len(df)})")
            for _, row in df.iterrows():
                st.markdown(f"""
                <div style='padding:12px; border:1px solid #ccc; border-radius:8px; margin-bottom:15px;'>
                    <b>Title:</b> {row.get('Title', '')}<br>
                    <b>Section:</b> {row.get('Section', '')} &nbsp;&nbsp;&nbsp;
                    <a href='{row.get('Link', '')}' target='_blank'><i class='fa-solid fa-file-pdf'></i> Open PDF</a>
                </div>
                """, unsafe_allow_html=True)

    show_results(search_in_df(sheets["Articles"], ["Title", "Auther", "Section", "Ref"]), "Articles", "📄")
    show_results(search_in_df(sheets["Judgements"], ["Title", "Type", "Section", "Summary"]), "Judgements", "⚖️")
    show_results(search_in_df(sheets["Updates"], ["Title", "Type"]), "Updates", "🧾")
    show_results(search_in_df(sheets["ROC & RD ADJUDICATION"], ["Title", "Section", "Authority", "Judgement"]), "ROC & RD Adjudication", "🏛️")

    st.stop()

st.title("📘 Chartered Secretary Knowledge Hub")
tabs = st.tabs(["📄 Articles", "⚖️ Judgements", "🧾 Updates", "🏛️ ROC & RD Adjudication", "⭐ Bookmarks"])

def paginate(df, key_prefix, page_size=10):
    total_pages = (len(df) - 1) // page_size + 1
    current_page = st.session_state.get(f"{key_prefix}_page", 1)
    start_idx = (current_page - 1) * page_size
    end_idx = start_idx + page_size
    df_page = df.iloc[start_idx:end_idx]

    for _, row in df_page.iterrows():
        yield row

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

def render_item(row, content_type):
    title = row['Title']
    author = row.get('Auther', '-')
    section = row.get('Section', '-')
    ref = row.get('Ref', '-')
    link = row['Link']

    col_main, col_btn = st.columns([5, 1])
    with col_main:
        st.markdown(f"""
        <div style='padding:12px; border:1px solid #ccc; border-radius:8px;'>
            <div style='font-weight:500; font-size:1.05em; margin-bottom:8px;'>{title}</div>
            <div style='display:flex; flex-wrap:wrap; gap:15px; font-size:0.9em; margin-bottom:6px;'>
                <div>✍️ <b>{author}</b></div>
                <div>📑 <b>{section}</b></div>
                <div>🏷️ <b>{ref}</b></div>
            </div>
            <a href="{link}" target="_blank" style="text-decoration:none;">
                <i class="fa-solid fa-file-pdf"></i> Open PDF
            </a>
        </div>
        """, unsafe_allow_html=True)
    with col_btn:
        if st.button("🔖", key=f"bm_{content_type}_{title}"):
            if link not in [b['link'] for b in st.session_state.bookmarks]:
                st.session_state.bookmarks.append({"type": content_type, "title": title, "link": link})
                save_bookmarks()
                st.success("Bookmarked!")

with tabs[0]:
    df = sheets["Articles"].drop(columns=["Page"])
    author_counts = df["Auther"].value_counts().to_dict()
    author_options = ["All"] + [f"{a} ({c} Articles)" for a, c in sorted(author_counts.items())]

    col1, col2, col3 = st.columns(3)
    with col1:
        author_disp = st.selectbox("Author", author_options)
        author = author_disp.split(" (")[0] if author_disp != "All" else "All"
    with col2:
        section = st.selectbox("Section", ["All"] + sorted(df["Section"].dropna().astype(str).unique()))
    with col3:
        ref = st.selectbox("Reference", ["All"] + sorted(df["Ref"].dropna().unique()))

    if author != "All":
        df = df[df["Auther"] == author]
    if section != "All":
        df = df[df["Section"].astype(str) == section]
    if ref != "All":
        df = df[df["Ref"] == ref]

    st.markdown(f"### 🧾 Total Articles: {len(df)}")
    for row in paginate(df, "articles"):
        render_item(row, "Article")

with tabs[1]:
    df = sheets["Judgements"].drop(columns=["Page"])
    col1, col2 = st.columns(2)
    with col1:
        j_type = st.selectbox("Type", ["All"] + sorted(df["Type"].dropna().unique()))
    with col2:
        section = st.selectbox("Section", ["All"] + sorted(df["Section"].dropna().astype(str).unique()))

    if j_type != "All":
        df = df[df["Type"] == j_type]
    if section != "All":
        df = df[df["Section"].astype(str) == section]

    for row in paginate(df, "judgements"):
        render_item(row, "Judgement")

with tabs[2]:
    df = sheets["Updates"].drop(columns=["Page"])
    update_type = st.selectbox("Type", ["All"] + sorted(df["Type"].dropna().unique()))
    if update_type != "All":
        df = df[df["Type"] == update_type]
    for row in paginate(df, "updates"):
        render_item(row, "Update")

with tabs[3]:
    df = sheets["ROC & RD ADJUDICATION"].drop(columns=["Page"])
    col1, col2 = st.columns([1, 3])
    with col1:
        section = st.selectbox("Section", ["All"] + sorted(df["Section"].dropna().astype(str).unique()))
    with col2:
        authority = st.selectbox("Authority", ["All"] + sorted(df["Authority"].dropna().unique()))

    if section != "All":
        df = df[df["Section"].astype(str) == section]
    if authority != "All":
        df = df[df["Authority"] == authority]

    for row in paginate(df, "roc"):
        render_item(row, "ROC")

with tabs[4]:
    st.subheader("⭐ Bookmarked Items")
    for i, item in enumerate(st.session_state.bookmarks):
        st.markdown(f"""
        <div style='margin-bottom:10px;'>
        <b>[{item['type']}]</b> {item['title']}<br>
        <a href='{item['link']}' target='_blank'><i class='fa-solid fa-file-pdf'></i> Open PDF</a>
        </div>
        """, unsafe_allow_html=True)
        if st.button("❌ Remove", key=f"remove_{i}"):
            st.session_state.bookmarks.pop(i)
            save_bookmarks()
            st.rerun()
