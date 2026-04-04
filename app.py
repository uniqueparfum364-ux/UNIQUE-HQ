import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. ARCHITECTURAL SETUP ---
st.set_page_config(layout="wide", page_title="Unique Parfum HQ", page_icon="👃")

# Create the Secure Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# The 4 Essential Statuses with Visual Markers
STATUS_MAP = {
    "NEW": "⚪ NEW",
    "PENDING": "🟡 PENDING",
    "SOLD": "🟢 SOLD",
    "LOST": "🔴 LOST"
}
STATUS_OPTIONS = list(STATUS_MAP.keys())
COLUMNS = ["Submitted", "STATUS", "QUOTE", "CONTACT", "EMAIL", "PHONE", "EVENT DATE", "LOCATION", "NOTES"]

if 'page' not in st.session_state:
    st.session_state.page = "home"

# --- 2. PAGE: MAIN MENU ---
if st.session_state.page == "home":
    st.title("📺 Unique Parfum: Pilot Room")
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("### 👥 Sales CRM")
        if st.button('Enter Sales Hub', key='btn_nav_crm', use_container_width=True):
            st.session_state.page = "crm"
    with col2:
        st.info("### 🧾 Auto-Invoices")
        st.button('Coming Soon', key='btn_menu_inv', use_container_width=True, disabled=True)
    with col3:
        st.info("### 🤖 AI Agents")
        st.button('Coming Soon', key='btn_menu_agent', use_container_width=True, disabled=True)

# --- 3. PAGE: UNIFIED CRM ---
elif st.session_state.page == "crm":
    st.title("👥 Sales & Lead Hub")
    if st.button("← Back to Menu", key='btn_crm_back'):
        st.session_state.page = "home"
    
    st.markdown("---")

    # LOAD LIVE DATA
    try:
        df = conn.read(worksheet="2026", ttl="0s")
        df = df.dropna(how="all")
        for c in COLUMNS:
            if c not in df.columns:
                df[c] = ""
        df = df[COLUMNS]
    except Exception as e:
        st.error(f"Connecting to Google Sheets... {e}")
        df = pd.DataFrame(columns=COLUMNS)

    # --- PART A: PIPELINE DASHBOARD (LOST = $0) ---
    if not df.empty:
        temp_df = df.copy()
        temp_df['QUOTE'] = pd.to_numeric(temp_df['QUOTE'], errors='coerce').fillna(0)
        
        # Pipeline logic: Only count NEW, PENDING, and SOLD
        active_pipeline = temp_df[temp_df['STATUS'] != 'LOST']
        pipeline_val = active_pipeline['QUOTE'].sum()
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Active Leads", len(active_pipeline))
        m2.metric("Pipeline Value", f"${pipeline_val:,.2f}", help="LOST deals are excluded from this total")
        
        sold_val = temp_df[temp_df['STATUS'] == 'SOLD']['QUOTE'].sum()
        m3.metric("Total SOLD", f"${sold_val:,.2f}")
        
        lost_count = len(temp_df[temp_df['STATUS'] == 'LOST'])
        m4.metric("LOST Deals", lost_count)

    st.markdown("---")

    # --- PART B: THE UNIFIED WORKSPACE ---
    st.write("### 🗄️ Active Sales Pipeline")
    st.write("💡 *Click any cell to edit. Add new rows at the bottom. Hit 'Sync' to save to Google.*")

    # Add a visual "Heat" column based on Status for the display
    def get_heat(status):
        if status == "SOLD": return "🟢"
        if status == "PENDING": return "🟡"
        if status == "LOST": return "🔴"
        return "⚪"

    df.insert(0, "HEAT", df["STATUS"].apply(get_heat))

    # THE ONE AND ONLY DATA EDITOR
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "HEAT": st.column_config.TextColumn("HEAT", disabled=True, width="small"),
            "STATUS": st.column_config.SelectboxColumn("STATUS", options=STATUS_OPTIONS, required=True),
            "QUOTE": st.column_config.NumberColumn("QUOTE ($)", format="$%d"),
            "Submitted": st.column_config.TextColumn("Submitted", disabled=True),
            "EVENT DATE": st.column_config.DateColumn("EVENT DATE")
        },
        key="unified_crm_editor"
    )

    # --- PART C: THE SYNC BUTTON ---
    # We remove the HEAT column before saving back to Google
    if not edited_df.equals(df):
        if st.button("💾 Sync Changes to Google Sheets", type="primary", key='btn_crm_sync', use_container_width=True):
            save_df = edited_df.drop(columns=["HEAT"])
            # Ensure New Rows get a timestamp
            save_df.loc[save_df['Submitted'] == "", 'Submitted'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            conn.update(worksheet="2026", data=save_df)
            st.success("🔥 All changes synced successfully!")
            st.rerun()
