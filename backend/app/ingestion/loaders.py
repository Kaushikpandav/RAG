from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
import os

class DocumentIngestor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            add_start_index=True,
        )

    def load_web_urls(self, urls: List[str]):
        """Load content from a list of URLs."""
        if not urls:
            return []
        
        # Filter PDF urls so we don't try to read them as HTML
        # Although WebBaseLoader might handle them or fail, it's safer to separate.
        # For now, simplistic check:
        html_urls = [u for u in urls if not u.endswith('.pdf')]
        
        if not html_urls:
            return []

        loader = WebBaseLoader(html_urls)
        docs = loader.load()
        return self.text_splitter.split_documents(docs)

    def load_pdf(self, file_path: str):
        """Load a single PDF from path."""
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        return self.text_splitter.split_documents(docs)
    
    def process_and_split(self, documents):
        # If we have raw Documents, we can split them here if not already
        return self.text_splitter.split_documents(documents)

ingestor = DocumentIngestor()
