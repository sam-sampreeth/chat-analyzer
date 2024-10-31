import zipfile
import streamlit as st

def parse_input_file(file_input):
    data = []
    
    if file_input is not None:
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
                    return None
                
                # Read the selected .txt file
                with zip_ref.open(chat_file_name) as file:
                    data = file.read().decode('utf-8').splitlines()
        
        else:
            # For direct .txt file
            data = file_input.read().decode('utf-8').splitlines()
    
    return data
