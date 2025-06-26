# app.py

import os
import streamlit as st
import pandas as pd

from utils.analytics import filter_by_date, get_users
from utils.parser import parse_input_file
from utils.visualization import show_visuals

# Optional fix for Streamlit file-watching errors
os.environ["STREAMLIT_WATCH_USE_POLLING"] = "true"

# Set page config
st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="centered")
st.header("📊 WhatsApp Chat Analyzer")

st.subheader("Uncover the hidden patterns in your WhatsApp chats. Analyze message frequency, word count, emoji usage, and more with this analysis tool.")

# Initialize session state
if "chats_data" not in st.session_state:
    st.session_state.chats_data = None
if "parsed" not in st.session_state:
    st.session_state.parsed = False

# File uploader
st.info("ℹ️ Upload WhatsApp Chat export (.txt or .zip)")
input_file = st.file_uploader("📤 Upload your file", type=["txt", "zip"])

if input_file:
    # Show file details
    with st.expander("View file details", expanded=False):
        st.write(f"**Filename:** {input_file.name}")
        st.write(f"**Size:** {round(input_file.size / 1024, 2)} KB")

    # Confirm and parse file
    if st.button("✅ Confirm and Parse File", type="primary"):
        with st.spinner("Parsing chat file... Please wait..."):
            chats_data = parse_input_file(input_file)

        if chats_data.empty:
            st.error("❌ Could not parse the chat. File might be invalid or unsupported.")
            st.session_state.chats_data = None
            st.session_state.parsed = False
        else:
            st.success("✅ File parsed successfully!")
            st.session_state.chats_data = chats_data
            st.session_state.parsed = True

# Proceed only if file is parsed
if st.session_state.parsed and st.session_state.chats_data is not None:
    chats_data = st.session_state.chats_data

    # Date selection
    min_date = chats_data["datetime"].min().date()
    max_date = chats_data["datetime"].max().date()
    date_range = st.date_input(
        "📅 Select date range for analysis",
        (min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Filter by date
    filtered_data = filter_by_date(chats_data, date_range)

    # Chat preview
    st.subheader("🔍 Chat Preview")
    st.write("Have a look at the first 5 parsed messages:")
    st.dataframe(filtered_data.head(5), use_container_width=True)

    # User selection
    users = get_users(filtered_data)
    selected_users = st.multiselect("👤 Select users to include", users, default=users)

    # Filter by user
    final_df = filtered_data[filtered_data['sender'].isin(selected_users)]

    # Run analysis
    if st.button("Run Analysis"):
        if final_df.empty:
            st.warning("⚠️ No data found for the selected filters.")
        else:
            show_visuals(final_df)


