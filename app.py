import streamlit as st
import pandas as pd

# --- 1. GLOBAL SETTINGS ---
st.set_page_config(layout="wide", page_title="Unique Parfum HQ")

# --- 2. THE "BRAIN" (MEMORY SETUP) ---
# This part checks if we already have a list of leads in our temporary memory.
# If not, it loads the ones from your 'leads.csv' file.
if 'lead_data' not in st.session_state:
    try:
        # Load the starting list from your GitHub file
        st.session_state.lead_data = pd.read_csv("leads.csv")
    except:
        # If the file is missing, start with an empty table
        st.session_state.lead_data = pd.DataFrame(columns=["Name", "Email", "Source", "Status"])

if 'page' not in st.session_state:
    st.session_state.page = "home"

# --- 3. PAGE: MAIN MENU ---
if st.session_state.page == "home":
    st.title("📺 Unique Parfum: Pilot Room")
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("👥 CRM")
        if st.button('Open CRM', key='main_crm_btn', use_container_width=True):
            st.session_state.page = "crm"

    with col2:
        st.subheader("🧾 Auto-Invoices")
        st.button('Coming Soon', key='inv_btn', use_container_width=True, disabled=True)

    with col3:
        st.subheader("🤖 AI Agents")
        st.button('Coming Soon', key='agent_btn', use_container_width=True, disabled=True)

# --- 4. PAGE: CRM ---
elif st.session_state.page == "crm":
    st.title("👥 Customer Relationship Management")
    if st.button("← Back to Menu", key='back_home'):
        st.session_state.page = "home"
    
    st.markdown("---")

    # PART A: THE INPUT FORM (Now it actually works!)
    with st.expander("➕ Add a New Lead"):
        with st.form("new_lead_form", clear_on_submit=True):
            new_name = st.text_input("Customer Name")
            new_email = st.text_input("Customer Email")
            new_source = st.selectbox("Source", ["ADX Sydney", "Gold Coast", "Wedding Giveaway", "Market"])
            
            submit = st.form_submit_button("Save to List")
            
            if submit:
                # 1. Create a "Row" for the new person
                new_row = pd.DataFrame({
                    "Name": [new_name],
                    "Email": [new_email],
                    "Source": [new_source],
                    "Status": ["New"]
                })
                # 2. Add that row to our temporary memory
                st.session_state.lead_data = pd.concat([st.session_state.lead_data, new_row], ignore_index=True)
                st.success(f"✅ {new_name} added to the list below!")

    st.markdown("---")

    # PART B: THE DATABASE VIEW
    st.write("### Current Active Leads")
    # We now show the data from our "Memory" (session_state)
    st.dataframe(st.session_state.lead_data, use_container_width=True)
    
    # PART C: THE AI BRAIN
    st.write("### 🧠 AI Analysis")
    if st.button("Run AI Sales Audit", key='ai_audit_btn'):
        st.balloons()
        wedding_count = len(st.session_state.lead_data[st.session_state.lead_data['Source'] == 'Wedding Giveaway'])
        st.success(f"AI Found **{wedding_count}** potential wedding bookings!")
