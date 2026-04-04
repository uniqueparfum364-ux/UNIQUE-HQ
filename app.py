import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. ARCHITECTURAL SETUP ---
st.set_page_config(layout="wide", page_title="Unique Parfum HQ", page_icon="👃")

# Injecting DM Sans & Luxury UI Styles
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stMetric { background-color: #ffffff; border: 0.5px solid #e2e8f0; padding: 15px; border-radius: 12px; }
    </style>
""", unsafe_allow_html=True)

# Connection Setup
conn = st.connection("gsheets", type=GSheetsConnection)

# The 4 Essential Statuses
STATUS_OPTIONS = ["NEW", "PENDING", "SOLD", "LOST"]
COLUMNS = ["Submitted", "STATUS", "QUOTE", "CONTACT", "EMAIL", "PHONE", "EVENT DATE", "LOCATION", "NOTES"]

if 'view' not in st.session_state:
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
            st.rerun() # FIX: Instant navigation
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
        st.rerun() # FIX: Added rerun for instant switching
    
    st.markdown("---")

    # LOAD LIVE DATA
    try:
        # Optimized TTL to 1m for performance
        df = conn.read(worksheet="2026", ttl="1m")
        df = df.dropna(how="all")
        
        # Ensure all columns exist
        for c in COLUMNS:
            if c not in df.columns:
                df[c] = ""
        
        # --- FIX: THE DATA SANITIZER (The "Anti-Crash" Logic) ---
        # Forces columns into the correct types for st.data_editor
        df['QUOTE'] = pd.to_numeric(df['QUOTE'], errors='coerce').fillna(0.0)
        df['EVENT DATE'] = pd.to_datetime(df['EVENT DATE'], errors='coerce').dt.date
        df['STATUS'] = df['STATUS'].fillna("NEW").astype(str)
        
        df = df[COLUMNS]
    except Exception as e:
        st.error(f"Connecting to Google Sheets... {e}")
        df = pd.DataFrame(columns=COLUMNS)

    # --- PART A: PIPELINE DASHBOARD (LOST = $0) ---
    if not df.empty:
        temp_df = df.copy()
        # Pipeline excludes LOST deals
        active_pipeline = temp_df[temp_df['STATUS'] != 'LOST']
        pipeline_val = active_pipeline['QUOTE'].sum()
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Active Leads", len(active_pipeline))
        m2.metric("Pipeline Value", f"${pipeline_val:,.2f}")
        m3.metric("Total SOLD", f"${temp_df[temp_df['STATUS'] == 'SOLD']['QUOTE'].sum():,.2f}")
        m4.metric("LOST Deals", len(temp_df[temp_df['STATUS'] == 'LOST']))

    st.markdown("---")

    # --- PART B: THE UNIFIED WORKSPACE ---
    st.write("### 🗄️ Active Sales Pipeline")
    
    # Store original for sync comparison
    df_original = df.copy()

    # Visual "Heat" column logic
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
        key="unified_crm_editor_v7"
    )

    # --- PART C: THE SYNC LOGIC ---
    edited_clean = edited_df.drop(columns=["HEAT"])

    if not edited_clean.equals(df_original):
        if st.button("💾 Sync Changes to Google Sheets", type="primary", key='btn_crm_sync', use_container_width=True):
            
            # Clean up new rows: Default to NEW status
            edited_clean['STATUS'] = edited_clean['STATUS'].replace("", "NEW").fillna("NEW")
            
            # Auto-timestamp new entries
            edited_clean.loc[edited_clean['Submitted'] == "", 'Submitted'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            # Convert dates back to strings for Google storage
            edited_clean['EVENT DATE'] = edited_clean['EVENT DATE'].astype(str)
            
            conn.update(worksheet="2026", data=edited_clean)
            st.success("🔥 Data synced to Google Sheets!")
            st.rerun()
