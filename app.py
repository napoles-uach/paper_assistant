import streamlit as st
from paper_assistant import PaperAssistant

def main():
    st.title("Paper Assistant Setup")
    api_key = st.secrets["api_key"]
    file_path = "paper.pdf"

    assistant = None

    if st.button("Setup Assistant"):
        if api_key and file_path:
            assistant = PaperAssistant(api_key, file_path)
            message, vector_store_id, file_id = assistant.setup_assistant()
            st.write(message)
            st.session_state.vector_store_id = vector_store_id
            st.session_state.file_id = file_id
            st.session_state.assistant = assistant
        else:
            st.error("Please provide both API key and file path.")

    if 'assistant' in st.session_state:
        assistant = st.session_state.assistant
        vector_store_id = st.session_state.vector_store_id
        file_id = st.session_state.file_id

        ask = st.chat_input("Ask something about the paper")
        if ask:
            response = assistant.ask_question(ask, vector_store_id, file_id)
            st.write(response)

if __name__ == "__main__":
    main()
