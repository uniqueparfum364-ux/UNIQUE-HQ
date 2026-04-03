import streamlit as st
import pandas as pd

# --- 1. GLOBAL SETTINGS ---
# This sets the page to wide mode (Smart TV style)
st.set_page_config(layout="wide", page_title="Unique Parfum HQ")

# This "session_state" is the memory of your app. 
# It remembers which page you are on.
if 'page' not in st.session_state:
    st.session_state.page = "home"

# --- 2. PAGE: MAIN MENU (THE SMART TV) ---
if st.session_state.page == "home":
    st.title("📺 Unique Parfum: Pilot Room")
    st.write("Welcome to your secret command center.")
    st.markdown("---")

    # Creating 3 columns for our "App Tiles"
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("👥 CRM")
        st.write("Manage your Sydney & Gold Coast leads.")
        if st.button('Open CRM', key='main_crm_btn', use_container_width=True):
            st.session_state.page = "crm"

    with col2:
        st.subheader("🧾 Auto-Invoices")
        st.write("Automated billing for events.")
        # We give this a unique key 'inv_btn' so it doesn't clash
        st.button('Coming Soon', key='inv_btn', use_container_width=True, disabled=True)

    with col3:
        st.subheader("🤖 AI Agents")
        st.write("Marketing & Sales assistants.")
        # We give this a unique key 'agent_btn' so it doesn't clash
        st.button('Coming Soon', key='agent_btn', use_container_width=True, disabled=True)

# --- 3. PAGE: CRM (THE CUSTOMER HUB) ---
elif st.session_state.page == "crm":
    st.title("👥 Customer Relationship Management")
    
    # Back button to return to the Smart TV menu
    if st.button("← Back to Menu", key='back_home'):
        st.session_state.page = "home"
    
    st.markdown("---")

    # PART A: THE INPUT FORM
    with st.expander("➕ Add a New Lead (Market or Event)"):
        with st.form("new_lead_form"):
            name = st.text_input("Customer Name")
            email = st.text_input("Customer Email")
            source = st.selectbox("Where did they come from?", ["ADX Sydney", "Gold Coast", "Wedding Giveaway", "Market"])
            
            submit = st.form_submit_button("Save Lead")
            if submit:
                # For now, this just shows a success message. 
                # Real "saving" happens once we connect a database!
                st.success(f"✅ Lead '{name}' captured! We'll save this to your list in the next step.")

    st.markdown("---")

    # PART B: THE DATABASE VIEW
    try:
        # This reaches into your GitHub to grab that leads.csv file
        df = pd.read_csv("leads.csv")
        st.write("### Current Active Leads")
        st.dataframe(df, use_container_width=True)
        
        # PART C: THE AI BRAIN (PRACTICE)
        st.write("### 🧠 AI Analysis")
        if st.button("Run AI Sales Audit", key='ai_audit_btn'):
            st.balloons()
            st.info("AI is scanning your sources for high-value leads...")
            
            # Simple AI Logic: Look for Wedding leads
            wedding_count = len(df[df['Source'] == 'Wedding Giveaway'])
            st.success(f"AI Found **{wedding_count}** potential wedding bookings!")
            st.write("💡 **AI Tip:** Follow up with these leads via email using the 'Roi Soleil' template.")
            
    except Exception as e:
        st.error(f"Error loading leads: {e}")
