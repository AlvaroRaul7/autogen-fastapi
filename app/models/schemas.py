from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict

class PDFUploadRequest(BaseModel):
    url: HttpUrl = Field(
        ...,
        description="The URL of the PDF document to process",
        example="https://example.com/document.pdf"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
            }
        }

class QueryRequest(BaseModel):
    query: str = Field(
        ...,
        description="The search query to find relevant document chunks",
        min_length=1,
        max_length=1000,
        example="What is the main topic of the document?"
    )
    limit: Optional[int] = Field(
        5,
        description="Maximum number of chunks to return",
        ge=1,
        le=20
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are the key points discussed in the document?",
                "limit": 5
            }
        }

class ChunkResponse(BaseModel):
    content: str = Field(
        ...,
        description="The text content of the document chunk"
    )
    metadata: Dict = Field(
        ...,
        description="Additional information about the chunk including source URL and timestamp"
    )
    similarity: Optional[float] = Field(
        None,
        description="Cosine similarity score between the query and this chunk",
        ge=0,
        le=1
    )

    class Config:
        json_schema_extra = {
            "example": {
                "content": "This is a sample text chunk from the document...",
                "metadata": {
                    "source_url": "https://example.com/document.pdf",
                    "timestamp": 1234567890,
                    "chunk_index": 1
                },
                "similarity": 0.85
            }
        }

class QueryResponse(BaseModel):
    chunks: List[ChunkResponse] = Field(
        ...,
        description="List of relevant document chunks with their metadata and similarity scores"
    )
    total_chunks: int = Field(
        ...,
        description="Total number of chunks returned",
        ge=0
    )

    class Config:
        json_schema_extra = {
            "example": {
                "chunks": [
                    {
                        "content": "This is a sample text chunk from the document...",
                        "metadata": {
                            "source_url": "https://example.com/document.pdf",
                            "timestamp": 1234567890,
                            "chunk_index": 1
                        },
                        "similarity": 0.85
                    }
                ],
                "total_chunks": 1
            }
        } 