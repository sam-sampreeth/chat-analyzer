import zipfile
import re
from datetime import datetime
import streamlit as st

# Module to parse the file input by the user
def parse_input_file(file_input):
    data = []
    
    # Check if file is provided
    if file_input is not None:
        # If the file is a .zip, extract the .txt file
        if file_input.name.endswith(".zip"):
            with zipfile.ZipFile(file_input, 'r') as zip_ref:
                # Get all .txt files in the zip
                txt_files = [f for f in zip_ref.namelist() if f.endswith('.txt')]
                
                if len(txt_files) == 1:
                    # Only one .txt file, proceed with reading
                    chat_file_name = txt_files[0]
                elif len(txt_files) > 1:
                    # Multiple .txt files, ask user to select one
                    chat_file_name = st.selectbox("Multiple chat files found. Please select the correct file:", txt_files)
                else:
                    st.error("No .txt file found in the zip.")
                    return []
                
                # Read the selected .txt file
                with zip_ref.open(chat_file_name) as file:
                    data = file.read().decode('utf-8').splitlines()
        
        else:
            # For direct .txt file
            data = file_input.read().decode('utf-8').splitlines()
    
    # Combine multi-line messages and filter out system messages
    chat_data = []
    current_message = ""
    message_start_pattern = re.compile(r"^\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2}\s*[ap]m -")

    for line in data:
        line = line.strip()
        
        # Check if line is the start of a new message
        if message_start_pattern.match(line):
            if current_message:
                chat_data.append(current_message)
            current_message = line
        else:
            current_message += f" {line}"
    
    if current_message:
        chat_data.append(current_message)  # Add the last message

    # Process structured data, ignoring system messages
    structured_data = []
    for message in chat_data:
        if "Messages and calls are end-to-end encrypted" not in message:
            match = re.match(r"(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}\s*[ap]m) - (.*?): (.*)", message)
            if match:
                date_str, time_str, sender, content = match.groups()
                date_time_str = f"{date_str}, {time_str}"
                date_time = datetime.strptime(date_time_str, "%d/%m/%y, %I:%M %p")  # Adjust date format as necessary
                structured_data.append({"date": date_time, "sender": sender, "message": content})
    
    return structured_data
