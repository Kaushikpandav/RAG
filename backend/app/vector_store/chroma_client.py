import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings
import os

class ChromaVectorStore:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChromaVectorStore, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # Ensure the directory exists
        os.makedirs(settings.CHROMA_DB_DIR, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_DB_DIR,
            settings=ChromaSettings(allow_reset=True, anonymized_telemetry=False)
        )
        self.collection_name = "rag_knowledge_base"
        self._collection = self.client.get_or_create_collection(name=self.collection_name)

    def get_collection(self):
        return self._collection

    def add_documents(self, documents, ids=None, metadatas=None):
        if not documents:
            return
        # If ids are not provided, we can generate them or let Chroma handle it if supported, 
        # but Chroma add() requires ids.
        # We will assume ids are passed or we generate UUIDs here.
        import uuid
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in documents]
            
        self._collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def query(self, query_texts, n_results=5):
        return self._collection.query(
            query_texts=query_texts,
            n_results=n_results
        )

chroma_client = ChromaVectorStore()
