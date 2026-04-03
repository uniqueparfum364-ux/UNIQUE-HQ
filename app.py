import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. ARCHITECTURAL SETUP ---
st.set_page_config(layout="wide", page_title="Unique Parfum HQ", page_icon="👃")

# Create the Secure Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# The Exact Columns for your Sales Team
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
        if st.button('Enter Sales Hub', key='main_crm_btn', use_container_width=True):
            st.session_state.page = "crm"
    with col2:
        st.info("### 🧾 Auto-Invoices")
        st.button('Coming Soon', key='inv_btn', use_container_width=True, disabled=True)
    with col3:
        st.info("### 🤖 AI Agents")
        st.button('Coming Soon', key='agent_btn', use_container_width=True, disabled=True)

# --- 3. PAGE: CRM (THE SALES HUB) ---
elif st.session_state.page == "crm":
    st.title("👥 Sales & Lead Hub")
    if st.button("← Back to Menu"):
        st.session_state.page = "home"
    
    st.markdown("---")

    # LOAD LIVE DATA FROM THE '2026' WORKSHEET
    try:
        # We tell it exactly which tab to look at
        df = conn.read(worksheet="2026", ttl="0s")
        df = df.dropna(how="all") # Clean up any empty rows
        for c in COLUMNS:
            if c not in df.columns:
                df[c] = ""
        df = df[COLUMNS]
    except Exception as e:
        st.error(f"Connecting to Google Sheets... {e}")
        df = pd.DataFrame(columns=COLUMNS)

    # --- PART A: PIPELINE DASHBOARD ---
    if not df.empty:
        temp_df = df.copy()
        temp_df['QUOTE'] = pd.to_numeric(temp_df['QUOTE'], errors='coerce').fillna(0)
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Leads", len(temp_df))
        m2.metric("Pipeline Value", f"${temp_df['QUOTE'].sum():,.2f}")
        m3.metric("Hot Deals", len(temp_df[temp_df['STATUS'] == 'HOT']))

    st.markdown("---")

    # --- PART B: THE INPUT FORM (AUTO-SAVING) ---
    with st.expander("➕ Capture New Event Lead"):
        with st.form("new_lead_form", clear_on_submit=True):
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                c_status = st.selectbox("STATUS", ["NEW", "CONTACTED", "QUOTED", "HOT", "PAID"])
                c_quote = st.number_input("QUOTE ($)", min_value=0.0, step=100.0)
                c_contact = st.text_input("CONTACT NAME")
                c_email = st.text_input("EMAIL")
            with f_col2:
                c_phone = st.text_input("PHONE")
                c_date = st.date_input("EVENT DATE", datetime.now())
                c_loc = st.text_input("LOCATION")
                c_notes = st.text_area("NOTES")
            
            if st.form_submit_button("🚀 Secure & Sync to Google"):
                new_row = {
                    "Submitted": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "STATUS": c_status,
                    "QUOTE": str(c_quote),
                    "CONTACT": c_contact,
                    "EMAIL": c_email,
                    "PHONE": c_phone,
                    "EVENT DATE": str(c_date),
                    "LOCATION": c_loc,
                    "NOTES": c_notes
                }
                
                # Push back specifically to the '2026' worksheet
                updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                conn.update(worksheet="2026", data=updated_df)
                st.success("🔥 Event Secured in Google Sheets!")
                st.rerun()

    # --- PART C: THE MASTER TABLE ---
    st.write("### 🗄️ Active Sales Pipeline")
    st.dataframe(df, use_container_width=True)
