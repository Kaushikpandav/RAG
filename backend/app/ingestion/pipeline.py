import asyncio
from app.ingestion.loaders import ingestor
from app.vector_store.chroma_client import chroma_client
from app.rag.embeddings import get_embeddings_model
from app.data.sources import ALL_URLS
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_ingestion():
    logger.info("Starting ingestion process...")
    
    # 1. Load Documents
    # Separate PDFs from regular URLs if needed, but for now we pass all to load_web_urls 
    # and let the loader logic we wrote handle the split, OR we iterate here.
    # Our previous loaders.py split logic was simple string check.
    
    urls = ALL_URLS
    logger.info(f"Found {len(urls)} URLs to ingest.")
    
    # We might want to limit for testing to avoid huge time
    # urls = urls[:5] 
    
    # Split into actual PDFs and Web pages
    pdf_urls = [u for u in urls if u.lower().endswith('.pdf')]
    web_urls = [u for u in urls if not u.lower().endswith('.pdf')]
    
    all_chunks = []
    
    # Process Web URLs
    if web_urls:
        logger.info(f"Loading {len(web_urls)} web pages...")
        try:
            web_chunks = ingestor.load_web_urls(web_urls)
            all_chunks.extend(web_chunks)
            logger.info(f"Loaded {len(web_chunks)} chunks from web pages.")
        except Exception as e:
            logger.error(f"Error loading web pages: {e}")

    # Process PDF URLs
    # Note: PyPDFLoader expects local files usually, but can handle URLs in some versions 
    # or we need to download them first. For simplicity, we skip remote PDF download in this step 
    # unless we add a downloader. Let's assume we stick to web pages for now or 
    # rely on Unstructured if we had it fully set up for remote.
    # "requests" to download temp file is safer.
    
    if pdf_urls:
        logger.info(f"Found {len(pdf_urls)} PDF/Arxiv links. Downloading and processing...")
        import requests
        import tempfile
        import os
        
        for p_url in pdf_urls:
            try:
                response = requests.get(p_url)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(response.content)
                    tmp_path = tmp.name
                
                pdf_chunks = ingestor.load_pdf(tmp_path)
                all_chunks.extend(pdf_chunks)
                os.remove(tmp_path)
                logger.info(f"Processed PDF: {p_url}")
            except Exception as e:
                logger.error(f"Failed to process PDF {p_url}: {e}")

    logger.info(f"Total chunks to embed: {len(all_chunks)}")
    
    if not all_chunks:
        logger.warning("No documents loaded.")
        return

    # 2. Embed and Store
    embeddings_model = get_embeddings_model()
    
    # Chroma requires us to embed documents. LangChain's Chroma wrapper does it automatically.
    # But we are using raw chromadb client in our wrapper.
    # We need to generate embeddings manually or update our Chromawrapper to use an embedding function.
    # Let's update ChromaVectorStore to accept an embedding function or do it here. 
    # Actually, using LangChain's Chroma wrapper is much easier.
    # Let's pivot our vector_store implementation to use LangChain's `Chroma` for convenience?
    # No, I already wrote the raw client. Let's stick to it but use the embedding model to generate vectors.
    
    # Actually, raw Chroma client can take an embedding function.
    # Let's instantiate a simple embedding function wrapper for Chroma.
    
    from chromadb.utils import embedding_functions
    # But we have a HuggingFace model via LangChain. 
    # We can just use the embeddings_model.embed_documents(texts) -> list[list[float]]
    
    batch_size = 100
    total_docs = len(all_chunks)
    
    for i in range(0, total_docs, batch_size):
        batch = all_chunks[i : i + batch_size]
        texts = [d.page_content for d in batch]
        metadatas = [d.metadata for d in batch]
        ids = [f"doc_{i}_{j}" for j in range(len(batch))] # Simple IDs
        
        logger.info(f"Embedding batch {i} to {i+len(batch)}...")
        embeddings = embeddings_model.embed_documents(texts)
        
        chroma_client.get_collection().add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )
    
    logger.info("Ingestion complete.")

if __name__ == "__main__":
    asyncio.run(run_ingestion())
