import streamlit as st
from paper_assistant import PaperAssistant

def main():
    st.title("Paper Assistant Setup")
    api_key = st.secrets("api_key")
    file_path = "paper.pdf"

    if st.button("Setup Assistant"):
        if api_key and file_path:
            assistant = PaperAssistant(api_key, file_path)
            message, vector_store_id, file_id = assistant.setup_assistant()
            st.write(message)
        else:
            st.error("Please provide both API key and file path.")

if __name__ == "__main__":
    main()
