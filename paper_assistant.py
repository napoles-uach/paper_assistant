import json
import os
import logging
from openai import OpenAI

class PaperAssistant:
    def __init__(self, api_key, local_file_path):
        self.api_key = api_key
        self.local_file_path = local_file_path
        self.client = OpenAI(api_key=api_key)
        self.vector_store_id_path = "vector_store_id.json"
        self.file_id_path = "file_id.json"
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def save_data_to_json(self, data, path):
        try:
            with open(path, 'w') as f:
                json.dump(data, f)
        except IOError as e:
            logging.error(f"Error saving data to {path}: {e}")
            raise

    def load_data_from_json(self, path):
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    return json.load(f)
            return None
        except IOError as e:
            logging.error(f"Error loading data from {path}: {e}")
            raise

    def manage_vector_store(self):
        vector_store_id = self.load_data_from_json(self.vector_store_id_path).get("vector_store_id") if self.load_data_from_json(self.vector_store_id_path) else None
        if vector_store_id is None:
            try:
                vector_store = self.client.beta.vector_stores.create(name="Paper")
                vector_store_id = vector_store.id
                self.save_data_to_json({"vector_store_id": vector_store_id}, self.vector_store_id_path)
            except Exception as e:
                logging.error(f"Error creating vector store: {e}")
                raise
        return vector_store_id

    def upload_document(self):
        if os.path.exists(self.local_file_path):
            file_id = self.load_data_from_json(self.file_id_path).get("file_id") if self.load_data_from_json(self.file_id_path) else None
            if file_id is None:
                try:
                    with open(self.local_file_path, "rb") as file_stream:
                        message_file = self.client.files.create(file=file_stream, purpose="assistants")
                    file_id = message_file.id
                    self.save_data_to_json({"file_id": file_id}, self.file_id_path)
                except Exception as e:
                    logging.error(f"Error uploading document: {e}")
                    raise
            return file_id
        else:
            logging.error("The specified file does not exist.")
            raise FileNotFoundError("The specified file does not exist.")

    def setup_assistant(self):
        try:
            vector_store_id = self.manage_vector_store()
            file_id = self.upload_document()
            return "Setup complete.", vector_store_id, file_id
        except Exception as e:
            return f"Error during setup: {e}", None, None
