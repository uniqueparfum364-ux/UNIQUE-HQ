import streamlit as st
import pandas as pd

# 1. SETUP THE SCREEN
st.set_page_config(layout="wide", page_title="Unique Parfum HQ")

# This "State" tells the app which page to show
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
            st.session_state.page = "crm" # Change the page!

    with col2:
        st.subheader("🧾 Auto-Invoices")
        st.button('Open Invoices (Locked)', use_container_width=True, disabled=True)

    with col3:
        st.subheader("🤖 AI Agents")
        st.button('Talk to Agents (Locked)', use_container_width=True, disabled=True)

# --- PAGE 2: THE CRM ---
elif st.session_state.page == "crm":
    st.title("👥 Customer Relationship Management")
    if st.button("← Back to Menu"):
        st.session_state.page = "home"
    
    st.markdown("---")
    
    # Load your "Customer List" from the file we just made
    try:
        df = pd.read_csv("leads.csv")
        st.write("### Current Leads")
        st.dataframe(df, use_container_width=True) # This shows the table
    except:
        st.error("I couldn't find your leads.csv file!")
