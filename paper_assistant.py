import os
import json
import streamlit as st
from openai import OpenAI

class PaperAssistant:
    def __init__(self, api_key, local_file_path="paper.pdf", vector_store_id_path="vector_store_id.json", file_id_path="file_id.json"):
        self.api_key = api_key
        self.local_file_path = local_file_path
        self.vector_store_id_path = vector_store_id_path
        self.file_id_path = file_id_path
        self.client = OpenAI(api_key=self.api_key)

    def save_vector_store_id(self, vector_store_id):
        with open(self.vector_store_id_path, 'w') as f:
            json.dump({"vector_store_id": vector_store_id}, f)

    def load_vector_store_id(self):
        if os.path.exists(self.vector_store_id_path):
            with open(self.vector_store_id_path, 'r') as f:
                data = json.load(f)
                return data.get("vector_store_id")
        return None

    def save_file_id(self, file_id):
        with open(self.file_id_path, 'w') as f:
            json.dump({"file_id": file_id}, f)

    def load_file_id(self):
        if os.path.exists(self.file_id_path):
            with open(self.file_id_path, 'r') as f:
                data = json.load(f)
                return data.get("file_id")
        return None

    def setup_assistant(self):
        vector_store_id = self.load_vector_store_id()
        file_id = self.load_file_id()

        if vector_store_id is None:
            with st.spinner('Creating vector store...'):
                vector_store = self.client.beta.vector_stores.create(name="Paper")
                vector_store_id = vector_store.id
                self.save_vector_store_id(vector_store_id)
        else:
            with st.spinner('Using existing vector store...'):
                vector_store = self.client.beta.vector_stores.retrieve(vector_store_id)

        if file_id is None:
            if os.path.exists(self.local_file_path):
                file_streams = [open(self.local_file_path, "rb")]

                try:
                    with st.spinner('Uploading files and polling status...'):
                        file_batch = self.client.beta.vector_stores.file_batches.upload_and_poll(
                            vector_store_id=vector_store.id, files=file_streams
                        )

                    st.success('Files uploaded and processed successfully!')
                    st.write(f"Status: {file_batch.status}")
                    st.write(f"File counts: {file_batch.file_counts}")

                    with st.spinner('Uploading file to assistant...'):
                        message_file = self.client.files.create(
                            file=open(self.local_file_path, "rb"), purpose="assistants"
                        )
                        file_id = message_file.id
                        self.save_file_id(file_id)
                finally:
                    for file_stream in file_streams:
                        file_stream.close()
            else:
                st.error("The file 'paper.pdf' does not exist. Please make sure the file is in the correct location.")
                return "Error: File not found", None, None
        else:
            st.write('Document ready.')

        with st.spinner('Creating assistant...'):
            paper_assistant = self.client.beta.assistants.create(
                name="Paper Assistant",
                instructions="You are an author of a research paper. Write latex formulas only using double $$ symbols. Example $$d_{\text{max}} = x_2(y) - x_1(y)$$. using \[ and \] or \( and \) to write formulas is forbidden, only the $$ double symbol is allowed. Use your knowledge base to answer questions about the research discussed in the paper.",
                model="gpt-3.5-turbo",
                tools=[{"type": "file_search"}],
            )

            paper_assistant = self.client.beta.assistants.update(
                assistant_id=paper_assistant.id,
                tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
            )

        return "Assistant setup completed", vector_store_id, file_id
