import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. ARCHITECTURAL SETUP ---
st.set_page_config(layout="wide", page_title="Unique Parfum HQ", page_icon="👃")

# CSS Injection for DM Sans and Luxury Styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stMetric { background-color: #ffffff; border: 0.5px solid #e2e8f0; padding: 15px; border-radius: 12px; }
    .status-chip { padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 500; display: inline-flex; align-items: center; gap: 6px; }
    </style>
""", unsafe_allow_html=True)

# Connection & Configuration
conn = st.connection("gsheets", type=GSheetsConnection)
STATUS_STYLES = {
    "NEW":     {"bg": "#F1EFE8", "color": "#5F5E5A", "dot": "⚪"},
    "PENDING": {"bg": "#FAEEDA", "color": "#854F0B", "dot": "🟡"},
    "SOLD":    {"bg": "#EAF3DE", "color": "#3B6D11", "dot": "🟢"},
    "LOST":    {"bg": "#FCEBEB", "color": "#A32D2D", "dot": "🔴"},
}
COLUMNS = ["Submitted", "STATUS", "QUOTE", "CONTACT", "EMAIL", "PHONE", "EVENT DATE", "LOCATION", "NOTES"]

# Initialize States
if 'view' not in st.session_state: st.session_state.view = "list"
if 'selected_lead_idx' not in st.session_state: st.session_state.selected_lead_idx = None

# --- 2. DATA LOADING ---
try:
    df = conn.read(worksheet="2026", ttl="1m")
    df = df.dropna(how="all")
    for c in COLUMNS:
        if c not in df.columns: df[c] = ""
    # Data Sanitization
    df['QUOTE'] = pd.to_numeric(df['QUOTE'], errors='coerce').fillna(0.0)
except:
    df = pd.DataFrame(columns=COLUMNS)

# --- 3. TOP NAV & METRICS ---
st.title("👃 Unique Parfum")
active_df = df[df['STATUS'] != 'LOST']
m1, m2, m3, m4 = st.columns(4)
m1.metric("Active Leads", len(active_df))
m2.metric("Pipeline Value", f"${active_df['QUOTE'].sum():,.0f}")
m3.metric("Closed Won", f"${df[df['STATUS'] == 'SOLD']['QUOTE'].sum():,.0f}")
m4.metric("Lost Deals", len(df[df['STATUS'] == 'LOST']))

st.markdown("---")

# --- 4. THE UNIFIED WORKSPACE ---

# VIEW: LIST (The Main Board)
if st.session_state.view == "list":
    col_a, col_b = st.columns([5, 1])
    col_a.subheader("Active Sales Pipeline")
    if col_b.button("+ New Lead", type="primary", use_container_width=True):
        st.session_state.view = "form"
        st.rerun()

    # FIX: Comparison logic
    df_original = df.copy()
    
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "STATUS": st.column_config.SelectboxColumn("STATUS", options=list(STATUS_STYLES.keys()), required=True),
            "QUOTE": st.column_config.NumberColumn("QUOTE ($)", format="$%d"),
            "Submitted": st.column_config.TextColumn("Submitted", disabled=True),
            "EVENT DATE": st.column_config.DateColumn("EVENT DATE")
        },
        key="luxury_crm_editor"
    )

    if not edited_df.equals(df_original):
        if st.button("💾 Sync Changes to Google", type="primary", use_container_width=True):
            # Cleanup & Sync
            edited_df['STATUS'] = edited_df['STATUS'].replace("", "NEW").fillna("NEW")
            edited_df.loc[edited_df['Submitted'] == "", 'Submitted'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            conn.update(worksheet="2026", data=edited_df)
            st.success("Synced successfully!")
            st.rerun()

# VIEW: FORM (Adding New Lead)
elif st.session_state.view == "form":
    if st.button("← Back to Board"):
        st.session_state.view = "list"
        st.rerun()
        
    with st.form("new_lead_luxury"):
        st.subheader("Create New Entry")
        f1, f2 = st.columns(2)
        contact = f1.text_input("Contact Name")
        email = f1.text_input("Email")
        phone = f2.text_input("Phone")
        status = f2.selectbox("Initial Status", list(STATUS_STYLES.keys()))
        quote = st.number_input("Estimated Quote ($)", min_value=0.0)
        loc = st.text_input("Location")
        date = st.date_input("Event Date")
        notes = st.text_area("Notes")
        
        if st.form_submit_button("Create Lead"):
            new_row = pd.DataFrame([{
                "Submitted": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "STATUS": status, "QUOTE": quote, "CONTACT": contact,
                "EMAIL": email, "PHONE": phone, "EVENT DATE": str(date),
                "LOCATION": loc, "NOTES": notes
            }])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(worksheet="2026", data=updated_df)
            st.session_state.view = "list"
            st.rerun()
