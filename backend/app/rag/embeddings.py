from langchain_huggingface import HuggingFaceEmbeddings
from app.core.config import settings

def get_embeddings_model():
    """
    Returns the HuggingFace embeddings model.
    """
    model_name = settings.EMBEDDING_MODEL
    model_kwargs = {'device': 'cpu'} # Use 'cuda' if GPU is available
    encode_kwargs = {'normalize_embeddings': False}
    
    hf = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
    return hf
