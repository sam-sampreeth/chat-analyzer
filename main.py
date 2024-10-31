# imports
import streamlit as st
import zipfile
from modules import parse_input_file

# Header and description
st.header("Advanced WhatsApp Chat Analyzer")
info = """\
Uncover the hidden patterns in your WhatsApp chats.\
Analyze message frequency, word count, emoji usage, and more.\
Gain insights into your digital conversations with this Python-powered tool.\
"""
st.write(info)

# Input file from user
file_input = st.file_uploader("Upload WhatsApp Chat File", type=["txt", "zip"], help="Upload '.txt' or '.zip' files only.")

# Parse input file
parse_input_file(file_input)