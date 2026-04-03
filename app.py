import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. ARCHITECTURAL SETUP ---
st.set_page_config(layout="wide", page_title="Unique Parfum HQ", page_icon="👃")

# Create the Secure Connection to your Google Sheet
conn = st.connection("gsheets", type=GSheetsConnection)

# Your 4 Pillar Statuses & Column Order
STATUS_OPTIONS = ["NEW", "PENDING", "SOLD", "LOST"]
COLUMNS = ["Submitted", "STATUS", "QUOTE", "CONTACT", "EMAIL", "PHONE", "EVENT DATE", "LOCATION", "NOTES"]

if 'page' not in st.session_state:
    st.session_state.page = "home"

# --- 2. PAGE: MAIN MENU (SMART TV STYLE) ---
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
        # Added unique key 'btn_menu_inv' to prevent error
        st.button('Coming Soon', key='btn_menu_inv', use_container_width=True, disabled=True)

    with col3:
        st.info("### 🤖 AI Agents")
        # Added unique key 'btn_menu_agent' to prevent error
        st.button('Coming Soon', key='btn_menu_agent', use_container_width=True, disabled=True)

# --- 3. PAGE: ELEVATED CRM ---
elif st.session_state.page == "crm":
    st.title("👥 Sales & Lead Hub")
    if st.button("← Back to Menu", key='btn_crm_back'):
        st.session_state.page = "home"
    
    st.markdown("---")

    # LOAD LIVE DATA FROM '2026' TAB
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

    # --- PART A: PIPELINE DASHBOARD ---
    if not df.empty:
        temp_df = df.copy()
        temp_df['QUOTE'] = pd.to_numeric(temp_df['QUOTE'], errors='coerce').fillna(0)
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Leads", len(temp_df))
        m2.metric("Pipeline Value", f"${temp_df['QUOTE'].sum():,.2f}")
        sold_val = temp_df[temp_df['STATUS'] == 'SOLD']['QUOTE'].sum()
        m3.metric("Total SOLD", f"${sold_val:,.2f}")
        m4.metric("Pending Deals", len(temp_df[temp_df['STATUS'] == 'PENDING']))

    st.markdown("---")

    # --- PART B: THE INPUT FORM (NEW/PENDING/SOLD/LOST) ---
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
                st.success("🔥 Data Secured in Google Sheets!")
                st.rerun()

    # --- PART C: THE MASTER TABLE (EDITABLE) ---
    st.write("### 🗄️ Active Sales Pipeline")
    
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "STATUS": st.column_config.SelectboxColumn("STATUS", options=STATUS_OPTIONS, required=True),
            "QUOTE": st.column_config.NumberColumn("QUOTE ($)", format="$%d"),
            "Submitted": st.column_config.TextColumn("Submitted", disabled=True)
        },
        key="crm_editor_v3"
    )
    
    # Save button appears only if you change something in the table
    if not edited_df.equals(df):
        if st.button("💾 Sync Changes to Google Sheets", type="primary", key='btn_crm_sync'):
            conn.update(worksheet="2026", data=edited_df)
            st.success("Pipeline Updated!")
            st.rerun()
