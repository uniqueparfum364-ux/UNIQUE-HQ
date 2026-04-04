import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. ARCHITECTURAL SETUP ---
st.set_page_config(layout="wide", page_title="Unique Parfum HQ", page_icon="👃")

# Create the Secure Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# The 4 Essential Statuses
STATUS_OPTIONS = ["NEW", "PENDING", "SOLD", "LOST"]
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
        st.rerun() # FIX: Added rerun for instant page switching
    
    st.markdown("---")

    # LOAD LIVE DATA (FIX: Optimized TTL to 1 minute to prevent rate limits)
    try:
        # ttl="1m" keeps it snappy but reduces API calls
        df = conn.read(worksheet="2026", ttl="1m") 
        df = df.dropna(how="all")
        
        # FIX: Warning for missing columns (Schema Drift Check)
        missing_cols = [c for c in COLUMNS if c not in df.columns]
        if missing_cols:
            st.warning(f"⚠️ Sheet schema drift! Missing columns: {', '.join(missing_cols)}")
            for c in missing_cols:
                df[c] = ""
        
        df = df[COLUMNS]
    except Exception as e:
        st.error(f"Connecting to Google Sheets... {e}")
        df = pd.DataFrame(columns=COLUMNS)

    # --- PART A: PIPELINE DASHBOARD ---
    if not df.empty:
        temp_df = df.copy()
        temp_df['QUOTE'] = pd.to_numeric(temp_df['QUOTE'], errors='coerce').fillna(0)
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
    
    # FIX: Store original for comparison BEFORE adding the HEAT column
    df_original = df.copy()

    # Visual "Heat" column logic
    def get_heat(status):
        if status == "SOLD": return "🟢"
        if status == "PENDING": return "🟡"
        if status == "LOST": return "🔴"
        return "⚪"

    df.insert(0, "HEAT", df["STATUS"].apply(get_heat))

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
        key="unified_crm_editor_v5"
    )

    # --- PART C: THE REFINED SYNC LOGIC ---
    # FIX: Clean comparison by dropping HEAT from the edited version
    edited_clean = edited_df.drop(columns=["HEAT"])

    if not edited_clean.equals(df_original):
        if st.button("💾 Sync Changes to Google Sheets", type="primary", key='btn_crm_sync', use_container_width=True):
            
            # FIX: Auto-fill empty STATUS for new rows
            edited_clean['STATUS'] = edited_clean['STATUS'].replace("", "NEW").fillna("NEW")
            
            # Ensure new rows get timestamps
            edited_clean.loc[edited_clean['Submitted'] == "", 'Submitted'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            # Update the Sheet
            conn.update(worksheet="2026", data=edited_clean)
            st.success("🔥 Changes synced! Refreshing data...")
            st.rerun()
