import streamlit as st

# Setup the screen layout
st.set_page_config(layout="wide", page_title="Unique Parfum HQ")

# The Main Header
st.title("📺 Unique Parfum: Smart TV Menu")
st.markdown("---")

# Create the Menu Tiles
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("👥 CRM")
    if st.button('Open CRM', use_container_width=True):
        st.write("Target: Sydney & Gold Coast Leads")

with col2:
    st.subheader("🧾 Auto-Invoices")
    if st.button('Open Invoices', use_container_width=True):
        st.write("Target: Automated Billing")

with col3:
    st.subheader("🤖 AI Agents")
    if st.button('Talk to Agents', use_container_width=True):
        st.write("Target: Marketing & Sales")
