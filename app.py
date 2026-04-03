import streamlit as st
import pandas as pd

# 1. SETUP
st.set_page_config(layout="wide", page_title="Unique Parfum HQ")

if 'page' not in st.session_state:
    st.session_state.page = "home"

# --- PAGE 1: THE MAIN MENU ---
if st.session_state.page == "home":
    st.title("📺 Unique Parfum: Pilot Room")
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("👥 CRM")
        if st.button('Open CRM', use_container_width=True):
            st.session_state.page = "crm"

    with col2:
        st.subheader("🧾 Auto-Invoices")
        st.button('Coming Soon', use_container_width=True, disabled=True)

    with col3:
        st.subheader("🤖 AI Agents")
        st.button('Coming Soon', use_container_width=True, disabled=True)

# --- PAGE 2: THE CRM ---
elif st.session_state.page == "crm":
    st.title("👥 Customer Relationship Management")
    if st.button("← Back to Menu"):
        st.session_state.page = "home"
    
    st.markdown("---")

    # A. THE INPUT (Adding a Lead)
    with st.expander("➕ Add a New Lead (Market or Event)"):
        with st.form("lead_form"):
            name = st.text_input("Name")
            email = st.text_input("Email")
            source = st.selectbox("Source", ["ADX Sydney", "Gold Coast", "Wedding Giveaway", "Market"])
            if st.form_submit_button("Save to CRM"):
                st.success(f"Captured {name}! (In Step 3, we will make this permanent)")

    st.markdown("---")

    # B. THE MEMORY (The Table)
    try:
        df = pd.read_csv("leads.csv")
        st.write("### Current Lead List")
        st.dataframe(df, use_container_width=True)
        
        # C. THE AI BRAIN (Practice Logic)
        st.write("### 🧠 AI Lead Analyzer")
        if st.button("Run AI Sales Analysis"):
            st.info("AI is analyzing lead sources...")
            # We are teaching the "Brain" to look for "Wedding" sources
            wedding_leads = df[df['Source'] == 'Wedding Giveaway']
            st.write(f"✅ AI Found **{len(wedding_leads)}** high-potential wedding leads.")
            st.write("💡 **Recommendation:** Send a 'Versailles' sample to these leads first.")
            
    except:
        st.error("Missing leads.csv file!")
