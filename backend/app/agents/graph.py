from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from app.rag.llm import get_llm
from app.rag.embeddings import get_embeddings_model
from app.vector_store.chroma_client import chroma_client

# --- Retrieval Function ---
def retrieve_docs(query: str):
    print(f"--- RETRIEVING for: {query} ---")
    embeddings_model = get_embeddings_model()
    query_embedding = embeddings_model.embed_query(query)
    
    results = chroma_client.get_collection().query(
        query_embeddings=[query_embedding],
        n_results=4
    )
    
    docs = results['documents'][0] if results['documents'] else []
    metadatas = results['metadatas'][0] if results['metadatas'] else []
    
    context_parts = []
    for doc, meta in zip(docs, metadatas):
        source = meta.get('source', 'Unknown')
        context_parts.append(f"Source: {source}\nContent: {doc}")
    
    return "\n\n".join(context_parts)

# --- Chain Definition ---
def create_chain():
    llm = get_llm()
    
    template = """You are an expert AI assistant specialized in NVIDIA and OpenAI technologies.
Use the following pieces of retrieved context to answer the question.
If the answer is not in the context, you may use your internal knowledge to answer, but please mention that the information is not from the retrieved documents.
Keep the answer concise and professional.

Context:
{context}

Question: {question}

Answer:"""
    
    prompt = ChatPromptTemplate.from_template(template)
    
    chain = (
        {"context": lambda x: retrieve_docs(x["question"]), "question": lambda x: x["question"]}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain

# Singleton chain
rag_chain = create_chain()
