from langchain_community.document_loaders import PyPDFLoader
import os

def load_pdfs_from_folder(folder_path: str):
    docs = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf'):
            loader = PyPDFLoader(os.path.join(folder_path, filename))
            pages = loader.load()
            docs.extend(pages)
    return docs