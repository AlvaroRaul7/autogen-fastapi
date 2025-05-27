from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "RAG API with AutoGen"
    
    # OpenAI Configuration
    OPENAI_API_KEY: str
    EMBEDDING_MODEL: str = "text-embedding-ada-002"
    COMPLETION_MODEL: str = "gpt-4-turbo-preview"  # For AutoGen agents
    
    # Supabase Configuration
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_TABLE: str = "document_chunks"
    
    # Chunking Configuration
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # AutoGen Configuration
    MAX_CONSECUTIVE_REPLIES: int = 3
    AGENT_TEMPERATURE: float = 0.7
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings() 