import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. ARCHITECTURAL SETUP ---
st.set_page_config(layout="wide", page_title="Unique Parfum HQ", page_icon="👃")

# These are the exact columns you requested
COLUMNS = ["Submitted", "Email", "Phone", "Contact", "Event Date", "Location", "Notes", "Quote", "Status"]

# --- 2. DATA LOADING & SELF-HEALING ---
if 'lead_data' not in st.session_state:
    try:
        # Load the existing file
        existing_df = pd.read_csv("leads.csv")
        
        # SELF-HEALING: If the old file is missing your new columns, we add them now
        for col in COLUMNS:
            if col not in existing_df.columns:
                existing_df[col] = "" # Add the missing column as empty
        
        # Keep only the columns we want, in the right order
        st.session_state.lead_data = existing_df[COLUMNS]
        
    except:
        # If no file exists, start a fresh professional table
        st.session_state.lead_data = pd.DataFrame(columns=COLUMNS)

if 'page' not in st.session_state:
    st.session_state.page = "home"

# --- 3. PAGE: MAIN MENU ---
if st.session_state.page == "home":
    st.title("📺 Unique Parfum: Pilot Room")
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("### 👥 Sales CRM")
        st.write("Track leads, quotes, and event dates.")
        if st.button('Enter Sales Hub', key='main_crm_btn', use_container_width=True):
            st.session_state.page = "crm"

    with col2:
        st.info("### 🧾 Auto-Invoices")
        st.write("Generate PDFs for paid quotes.")
        st.button('System Locked', key='inv_btn', use_container_width=True, disabled=True)

    with col3:
        st.info("### 🤖 AI Agents")
        st.write("Draft follow-up emails automatically.")
        st.button('System Locked', key='agent_btn', use_container_width=True, disabled=True)

# --- 4. PAGE: ELEVATED CRM ---
elif st.session_state.page == "crm":
    st.title("👥 Sales & Lead Hub")
    if st.button("← Back to Menu"):
        st.session_state.page = "home"
    
    st.markdown("---")

    # --- PART A: EXECUTIVE METRICS ---
    # We use .fillna(0) to prevent errors if quotes are empty
    temp_df = st.session_state.lead_data.copy()
    temp_df['Quote'] = pd.to_numeric(temp_df['Quote'], errors='coerce').fillna(0)
    
    total_leads = len(temp_df)
    pipeline_val = temp_df['Quote'].sum()
    hot_leads = len(temp_df[temp_df['Status'] == 'Hot'])
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Active Leads", total_leads)
    m2.metric("Pipeline Value", f"${pipeline_val:,.2f}")
    m3.metric("Hot Deals", hot_leads)

    st.markdown("---")

    # --- PART B: SMART INPUT FORM ---
    with st.expander("➕ Capture New Event Lead"):
        with st.form("new_lead_form", clear_on_submit=True):
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                c_contact = st.text_input("Contact Person")
                c_email = st.text_input("Email Address")
                c_phone = st.text_input("Phone Number")
                c_loc = st.text_input("Location (Venue/City)")
            
            with f_col2:
                c_date = st.date_input("Event Date", datetime.now())
                c_quote = st.number_input("Quote Amount ($)", min_value=0.0, step=100.0)
                c_status = st.selectbox("Status", ["New", "Contacted", "Quoted", "Hot", "Paid"])
                c_notes = st.text_area("Specific Notes")
            
            if st.form_submit_button("Secure Lead"):
                new_row = pd.DataFrame({
                    "Submitted": [datetime.now().strftime("%Y-%m-%d %H:%M")],
                    "Contact": [c_contact],
                    "Email": [c_email],
                    "Phone": [c_phone],
                    "Event Date": [str(c_date)],
                    "Location": [c_loc],
                    "Notes": [c_notes],
                    "Quote": [c_quote],
                    "Status": [c_status]
                })
                st.session_state.lead_data = pd.concat([st.session_state.lead_data, new_row], ignore_index=True)
                st.rerun()

    # --- PART C: THE MASTER TABLE ---
    st.write("### 🗄️ Active Sales Pipeline")
    
    edited_df = st.data_editor(
        st.session_state.lead_data,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "Quote": st.column_config.NumberColumn("Quote ($)", format="$%d"),
            "Status": st.column_config.SelectboxColumn("Status", options=["New", "Contacted", "Quoted", "Hot", "Paid"]),
            "Submitted": st.column_config.TextColumn("Submitted", disabled=True)
        },
        key="lead_editor_v2"
    )
    st.session_state.lead_data = edited_df
