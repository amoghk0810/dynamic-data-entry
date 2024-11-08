import streamlit as st
import os
from pathlib import Path

# Define the folder where you want to save uploaded files
UPLOAD_FOLDER = "uploaded_files"
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)

st.title("Upload and Save Files Example")

# File uploader
uploaded_file = st.file_uploader("Choose a file to upload")

if uploaded_file is not None:
    # Define the file path to save
    save_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
    
    # Save the file to the specified folder
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.success(f"File saved successfully at {save_path}")

# Optional: List all files in the upload folder
if st.button("Show uploaded files"):
    files = os.listdir(UPLOAD_FOLDER)
    if files:
        st.write("Uploaded Files:")
        for file in files:
            st.write(file)
    else:
        st.write("No files uploaded yet.")
