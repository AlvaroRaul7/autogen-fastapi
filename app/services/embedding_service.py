from openai import OpenAI
from app.core.config import get_settings

settings = get_settings()

class EmbeddingService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.EMBEDDING_MODEL

    async def create_embedding(self, text: str) -> list:
        """Create embedding for a text using OpenAI's API"""
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding

    async def create_embeddings_batch(self, texts: list[str]) -> list:
        """Create embeddings for a batch of texts"""
        response = self.client.embeddings.create(
            model=self.model,
            input=texts
        )
        return [data.embedding for data in response.data] 