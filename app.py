import streamlit as st
import pandas as pd

# --- 1. GLOBAL SETTINGS ---
st.set_page_config(layout="wide", page_title="Unique Parfum HQ")

# --- 2. THE "BRAIN" (MEMORY SETUP) ---
if 'lead_data' not in st.session_state:
    try:
        # Load the starting list from your GitHub file
        st.session_state.lead_data = pd.read_csv("leads.csv")
    except:
        # If the file is missing, start with a clean table
        st.session_state.lead_data = pd.DataFrame(columns=["Name", "Email", "Source", "Status"])

if 'page' not in st.session_state:
    st.session_state.page = "home"

# --- 3. PAGE: MAIN MENU (SMART TV) ---
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

# --- 4. PAGE: CRM (CUSTOMER HUB) ---
elif st.session_state.page == "crm":
    st.title("👥 Customer Relationship Management")
    if st.button("← Back to Menu", key='back_home'):
        st.session_state.page = "home"
    
    st.markdown("---")

    # PART A: THE INPUT FORM
    with st.expander("➕ Add a New Lead"):
        with st.form("new_lead_form", clear_on_submit=True):
            new_name = st.text_input("Customer Name")
            new_email = st.text_input("Customer Email")
            new_source = st.selectbox("Source", ["ADX Sydney", "Gold Coast", "Wedding Giveaway", "Market"])
            
            submit = st.form_submit_button("Save to List")
            
            if submit:
                new_row = pd.DataFrame({
                    "Name": [new_name],
                    "Email": [new_email],
                    "Source": [new_source],
                    "Status": ["New"]
                })
                st.session_state.lead_data = pd.concat([st.session_state.lead_data, new_row], ignore_index=True)
                st.success(f"✅ {new_name} added to the Pilot Room memory!")

    st.markdown("---")

    # PART B: THE DATABASE VIEW (Editable & Surgical Delete)
    st.write("### Current Active Leads")
    st.write("💡 *To remove a lead: Select the row and press **Delete** or **Backspace** on your keyboard.*")
    
    # We kept the editor so you can still fix typos or delete single rows
    edited_df = st.data_editor(
        st.session_state.lead_data, 
        use_container_width=True, 
        num_rows="dynamic", 
        key="lead_editor"
    )
    
    # Save the changes back to memory
    st.session_state.lead_data = edited_df

    st.markdown("---")
    
    # PART C: THE AI BRAIN
    st.write("### 🧠 AI Analysis")
    if st.button("Run AI Sales Audit", key='ai_audit_btn'):
        st.balloons()
        wedding_count = len(st.session_state.lead_data[st.session_state.lead_data['Source'] == 'Wedding Giveaway'])
        st.success(f"AI Found **{wedding_count}** high-value potential wedding bookings!")
