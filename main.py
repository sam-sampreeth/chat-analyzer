import streamlit as st
from datetime import datetime
from modules import parse_input_file

# Header and description
st.header("Advanced WhatsApp Chat Analyzer")
info = """\
Uncover the hidden patterns in your WhatsApp chats. \
Analyze message frequency, word count, emoji usage, and more. \
Gain insights into your digital conversations with this Python-powered tool.
"""
st.write(info)

# Input file from user
file_input = st.file_uploader("Upload WhatsApp Chat File", type=["txt", "zip"], help="Upload '.txt' or '.zip' files only.")

# Parse input file
if file_input is not None:
    chat_data = parse_input_file(file_input)
    
    # Display a sample of chat_data for debugging
    st.write("Sample of parsed chat data:", chat_data[:5])

    # Date range selection
    st.subheader("Select Date Range")
    min_date = st.date_input("From", value=datetime(2024, 10, 30).date())  # Ensure it’s a date object
    max_date = st.date_input("To", value=datetime(2024, 11, 1).date())  # Ensure it’s a date object
    
    # Filter chat data by date range (convert datetime to date for comparison)
    filtered_data = [entry for entry in chat_data if min_date <= entry['date'].date() <= max_date]
    
    # Identify unique participants
    participants = sorted(set(entry['sender'] for entry in filtered_data))

    # Edit participant names and include/exclude them from analysis
    st.subheader("Edit Participants")
    edited_participants = {}
    include_participants = []
    
    for participant in participants:
        col1, col2 = st.columns([1, 2])
        
        # Checkbox to include/exclude the participant
        include = col1.checkbox("Include", value=True, key=f"include_{participant}")
        
        # Text input to edit participant's name
        edited_name = col2.text_input("Edit Name", value=participant, key=f"edit_{participant}")
        
        if include:
            include_participants.append(edited_name)
        edited_participants[participant] = edited_name
    
    # Filter the chat data to include only selected participants with edited names
    final_filtered_data = [
        {**entry, "sender": edited_participants[entry['sender']]}
        for entry in filtered_data if edited_participants[entry['sender']] in include_participants
    ]
    
    # Display results
    st.write(f"People involved between {min_date} and {max_date} (after edits):")
    st.write(", ".join(include_participants) if include_participants else "No participants selected for analysis.")
    st.write("Filtered chat data for analysis:", final_filtered_data[:5])  # Show first 5 entries for verification