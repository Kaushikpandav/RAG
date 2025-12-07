from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "RAG Web App"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    OPENAI_API_KEY: str
    HUGGINGFACEHUB_API_TOKEN: str
    CHROMA_DB_DIR: str = "./chroma_db"
    
    # Model Configuration
    LLM_MODEL: str = "gpt-4o" # Assuming 'o4' is available via OpenAI API or we map it
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2" # Good default HF model

    class Config:
        env_file = ".env"

settings = Settings()
