import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. ARCHITECTURAL SETUP ---
st.set_page_config(layout="wide", page_title="Unique Parfum HQ", page_icon="👃")

# Define the "Golden Columns" for your sales team
COLUMNS = ["Submitted", "Contact", "Email", "Phone", "Event Date", "Location", "Notes", "Quote", "Status"]

if 'lead_data' not in st.session_state:
    try:
        st.session_state.lead_data = pd.read_csv("leads.csv")
    except:
        # Start with a clean, structured table if file is missing
        st.session_state.lead_data = pd.DataFrame(columns=COLUMNS)

if 'page' not in st.session_state:
    st.session_state.page = "home"

# --- 2. PAGE: MAIN MENU ---
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

# --- 3. PAGE: ELEVATED CRM ---
elif st.session_state.page == "crm":
    st.title("👥 Sales & Lead Hub")
    if st.button("← Back to Menu"):
        st.session_state.page = "home"
    
    st.markdown("---")

    # --- PART A: EXECUTIVE METRICS (The 'Money' View) ---
    # Sales guys love seeing the total value of their work
    total_leads = len(st.session_state.lead_data)
    # Convert 'Quote' to numeric safely for calculation
    pipeline_val = pd.to_numeric(st.session_state.lead_data['Quote'], errors='coerce').sum()
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Active Leads", total_leads)
    m2.metric("Total Pipeline Value", f"${pipeline_val:,.2f}")
    m3.metric("High Priority", len(st.session_state.lead_data[st.session_state.lead_data['Status'] == 'Hot']))

    st.markdown("---")

    # --- PART B: SMART INPUT FORM (Optimized for Mobile/Market use) ---
    with st.expander("➕ Capture New Event Lead"):
        with st.form("new_lead_form", clear_on_submit=True):
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                c_name = st.text_input("Contact Person")
                c_email = st.text_input("Email Address")
                c_phone = st.text_input("Phone Number")
                c_loc = st.selectbox("Event Location", ["Sydney CBD", "Sydney Greater", "Gold Coast", "Other"])
            
            with f_col2:
                c_date = st.date_input("Event Date", datetime.now())
                c_quote = st.number_input("Estimated Quote ($)", min_value=0.0, step=50.0)
                c_status = st.select_slider("Lead Status", options=["New", "Contacted", "Quoted", "Hot", "Paid"])
                c_notes = st.text_area("Notes (Scent prefs, etc.)")
            
            if st.form_submit_button("Secure Lead"):
                new_row = pd.DataFrame({
                    "Submitted": [datetime.now().strftime("%Y-%m-%d %H:%M")],
                    "Contact": [c_name],
                    "Email": [c_email],
                    "Phone": [c_phone],
                    "Event Date": [str(c_date)],
                    "Location": [c_loc],
                    "Notes": [c_notes],
                    "Quote": [c_quote],
                    "Status": [c_status]
                })
                st.session_state.lead_data = pd.concat([st.session_state.lead_data, new_row], ignore_index=True)
                st.success(f"Lead for {c_name} saved to pipeline!")

    # --- PART C: THE MASTER TABLE (Clean & Functional) ---
    st.write("### 🗄️ Active Sales Pipeline")
    
    # We use column_config to make it look expensive and professional
    edited_df = st.data_editor(
        st.session_state.lead_data,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "Quote": st.column_config.NumberColumn("Quote ($)", format="$%d"),
            "Status": st.column_config.SelectboxColumn("Status", options=["New", "Contacted", "Quoted", "Hot", "Paid"]),
            "Email": st.column_config.TextColumn("Email"),
            "Submitted": st.column_config.TextColumn("Submitted", disabled=True) # Lock the timestamp
        }
    )
    st.session_state.lead_data = edited_df
