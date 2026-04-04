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

# --- 2. THE STYLING ENGINE (Architect's Secret) ---
def style_pipe(row):
    """Applies soft background colors based on status for high readability."""
    status = row['STATUS']
    if status == 'SOLD':
        return ['background-color: #d4edda; color: #155724'] * len(row) # Soft Green
    elif status == 'PENDING':
        return ['background-color: #fff3cd; color: #856404'] * len(row) # Soft Yellow
    elif status == 'LOST':
        return ['background-color: #f8d7da; color: #721c24'] * len(row) # Soft Red
    elif status == 'NEW':
        return ['background-color: #e2e3e5; color: #383d41'] * len(row) # Soft Grey
    return [''] * len(row)

# --- 3. PAGE: MAIN MENU ---
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

# --- 4. PAGE: CRM (THE COLOR HUB) ---
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
        st.error(f"Syncing with Google... {e}")
        df = pd.DataFrame(columns=COLUMNS)

    # --- PART A: PIPELINE DASHBOARD (LOST Leads Excluded) ---
    if not df.empty:
        temp_df = df.copy()
        temp_df['QUOTE'] = pd.to_numeric(temp_df['QUOTE'], errors='coerce').fillna(0)
        
        # ARCHITECT'S RULE: Pipeline value only counts ACTIVE deals (Not LOST)
        active_pipeline = temp_df[temp_df['STATUS'] != 'LOST']
        pipeline_val = active_pipeline['QUOTE'].sum()
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Leads", len(temp_df))
        m2.metric("Pipeline Value", f"${pipeline_val:,.2f}", help="Excludes LOST leads")
        
        sold_val = temp_df[temp_df['STATUS'] == 'SOLD']['QUOTE'].sum()
        m3.metric("Total SOLD", f"${sold_val:,.2f}")
        
        lost_count = len(temp_df[temp_df['STATUS'] == 'LOST'])
        m4.metric("Lost Opportunities", lost_count)

    st.markdown("---")

    # --- PART B: THE INPUT FORM ---
    with st.expander("➕ Capture New Event Lead"):
        with st.form("new_lead_form", clear_on_submit=True):
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                c_status = st.selectbox("STATUS", STATUS_OPTIONS)
                c_quote = st.number_input("QUOTE ($)", min_value=0.0, step=100.0)
                c_contact = st.text_input("CONTACT NAME")
                c_email = st.text_input("EMAIL")
            with f_col2:
                c_phone = st.text_input("PHONE")
                c_date = st.date_input("EVENT DATE", datetime.now())
                c_loc = st.text_input("LOCATION")
                c_notes = st.text_area("NOTES")
            
            if st.form_submit_button("🚀 Secure & Sync"):
                new_row = pd.DataFrame([{
                    "Submitted": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "STATUS": c_status,
                    "QUOTE": str(c_quote),
                    "CONTACT": c_contact,
                    "EMAIL": c_email,
                    "PHONE": c_phone,
                    "EVENT DATE": str(c_date),
                    "LOCATION": c_loc,
                    "NOTES": c_notes
                }])
                updated_df = pd.concat([df, new_row], ignore_index=True)
                conn.update(worksheet="2026", data=updated_df)
                st.success("🔥 Data Secured!")
                st.rerun()

    # --- PART C: THE COLOR-CODED SALES BOARD ---
    st.write("### 🗄️ Active Sales Pipeline")
    
    # We apply the styling to the view
    styled_df = df.style.apply(style_pipe, axis=1)
    
    # Show the styled table (Note: Styled tables are for VIEWING)
    st.dataframe(styled_df, use_container_width=True)
    
    st.markdown("---")
    
    # PART D: THE EDITING AREA
    with st.expander("📝 Edit Pipeline / Update Status"):
        st.info("Update status or details here and click Sync.")
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "STATUS": st.column_config.SelectboxColumn("STATUS", options=STATUS_OPTIONS, required=True),
                "QUOTE": st.column_config.NumberColumn("QUOTE ($)", format="$%d"),
                "Submitted": st.column_config.TextColumn("Submitted", disabled=True)
            },
            key="crm_editor_v4"
        )
        
        if not edited_df.equals(df):
            if st.button("💾 Sync Changes to Google Sheets", type="primary", key='btn_crm_sync'):
                conn.update(worksheet="2026", data=edited_df)
                st.success("Pipeline Updated!")
                st.rerun()
