from supabase import create_client
from app.core.config import get_settings
import numpy as np

settings = get_settings()

class SupabaseService:
    def __init__(self):
        self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        self.table = settings.SUPABASE_TABLE

    async def store_document_chunk(self, chunk_text: str, embedding: list, metadata: dict):
        """Store a document chunk and its embedding in Supabase"""
        data = {
            "content": chunk_text,
            "embedding": embedding,
            "metadata": metadata
        }
        return self.client.table(self.table).insert(data).execute()

    async def search_similar_chunks(self, query_embedding: list, limit: int = 5):
        """Search for similar chunks using cosine similarity"""
        # Use POST request with function call to handle large embeddings
        result = self.client.rpc(
            'match_documents',
            {
                'query_vec': query_embedding,
                'match_threshold': 0.7,
                'match_count': limit
            }
        ).execute()
        
        # If no results found, return empty list
        if not result.data:
            return []
            
        return result.data

    @staticmethod
    def calculate_similarity(embedding1: list, embedding2: list) -> float:
        """Calculate cosine similarity between two embeddings"""
        return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2)) 