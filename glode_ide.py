import streamlit as st
import subprocess
import os

# Supported languages
supported_languages = [
    "English", "Bengali", "Egyptian Arabic", "French", "German", "Hindi",
    "Indonesian", "Japanese", "Mandarin", "Marathi", "Nigerian Pidgin", 
    "Portuguese", "Russian", "Spanish", "Tamil", "Telugu", 
    "Turkish", "Urdu", "Yue Chinese"
]

# Streamlit app
st.title("Glode Language Code Validator")

# Dropdown for selecting the language
selected_language = st.selectbox("Choose a programming language:", supported_languages)

# Automatically add the language as a comment at the top
code_editor = st.text_area("Write your code below:", value=f"#{selected_language}\n", height=300)

# Submit button
if st.button("Run"):
    # Save the input to a temporary .glode file
    file_name = "temp_code.glode"
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(code_editor)

    # Run the existing script
    try:
        result = subprocess.run(
            ["python", "glode_compiler.py", file_name],
            capture_output=True,
            text=True
        )

        # Display the result
        if result.returncode == 0:
            st.success("Processing Complete!")
            st.text_area("Output:", result.stdout, height=300)
        else:
            st.error("Error occurred while processing the code.")
            st.text_area("Error Output:", result.stderr, height=300)
    finally:
        # Clean up the temporary file
        if os.path.exists(file_name):
            os.remove(file_name)