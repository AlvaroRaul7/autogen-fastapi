from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.core.config import get_settings
from app.routers import documents

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    A Retrieval-Augmented Generation (RAG) API that processes PDF documents and enables semantic search.
    
    ## Features
    
    * **PDF Processing**: Upload and process PDFs from URLs
    * **Semantic Search**: Search through processed documents using natural language
    * **Vector Storage**: Efficient storage and retrieval of document embeddings
    * **AutoGen Integration**: Enhanced query processing and document analysis using AI agents
    
    ## How it works
    
    1. Upload a PDF using the `/documents/process-pdf` endpoint
    2. The PDF is processed into chunks and stored with embeddings
    3. Use the `/documents/query` endpoint to search through the processed documents
    
    ## Authentication
    
    This API uses environment variables for OpenAI and Supabase authentication.
    Make sure to set up your `.env` file with the required credentials.
    """,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router, prefix=settings.API_V1_STR)

# Customize OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description=app.description,
        routes=app.routes,
    )
    
    # Add API server URLs
    openapi_schema["servers"] = [
        {"url": "http://localhost:8000", "description": "Development server"},
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint that returns a welcome message.
    
    Returns:
        dict: A simple welcome message with links to documentation
    """
    return {
        "message": "Welcome to RAG API",
        "docs": "/docs",
        "redoc": "/redoc"
    } 