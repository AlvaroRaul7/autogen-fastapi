# RAG API with AutoGen Integration

A Retrieval-Augmented Generation (RAG) API that combines the power of FastAPI, Supabase, and AutoGen for intelligent document processing and querying.

## Features

- **PDF Processing**: Upload and process PDFs from URLs
- **Semantic Search**: Advanced document search using embeddings
- **Vector Storage**: Efficient storage and retrieval using Supabase with pgvector
- **AutoGen Integration**: 
  - Intelligent query enhancement using a researcher agent
  - Comprehensive document analysis using an analyst agent
  - Multi-agent collaboration for better results
- **Detailed Logging**: 
  - Separate logs for AutoGen operations and API endpoints
  - Comprehensive tracking of agent interactions
  - Performance monitoring and debugging support

## Project Structure

```
.
├── app/
│   ├── agents/                 # AutoGen agent implementations
│   │   ├── __init__.py
│   │   ├── base.py            # Base agent class
│   │   └── inform.py          # Information processing agents
│   ├── core/
│   │   ├── config.py          # Application configuration
│   │   └── logging.py         # Logging configuration
│   ├── models/
│   │   └── schemas.py         # Pydantic models
│   ├── routers/
│   │   ├── __init__.py
│   │   └── documents.py       # Document-related endpoints
│   ├── services/
│   │   ├── embedding_service.py    # OpenAI embeddings
│   │   ├── pdf_service.py         # PDF processing
│   │   └── supabase_service.py    # Supabase integration
│   └── main.py                # FastAPI application
├── logs/                      # Application logs directory
├── supabase/
│   └── init.sql              # Database initialization
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Prerequisites

- Python 3.8+
- Supabase account and project
- OpenAI API key
- PostgreSQL with pgvector extension (handled by Supabase)

## Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# API Settings
PROJECT_NAME="RAG API with AutoGen"
API_V1_STR="/api/v1"

# OpenAI Settings
OPENAI_API_KEY=your_openai_api_key
EMBEDDING_MODEL="text-embedding-ada-002"
COMPLETION_MODEL="gpt-4-turbo-preview"

# Supabase Settings
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_api_key
SUPABASE_TABLE="document_"

# PDF Processing Settings
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# AutoGen Settings
MAX_CONSECUTIVE_REPLIES=3
AGENT_TEMPERATURE=0.7
```

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up Supabase:
   - Create a new Supabase project
   - Enable the pgvector extension
   - Run the initialization SQL from `supabase/init.sql`

## Usage

1. Start the API server:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Access the API documentation:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

### POST /api/v1/documents/process-pdf
Process a PDF document from a URL:
```json
{
    "url": "https://example.com/document.pdf"
}
```

### POST /api/v1/documents/query
Search through processed documents:
```json
{
    "query": "What are the main topics discussed?",
    "limit": 5
}
```

## Logging

The application generates two types of logs in the `logs` directory:

- `autogen_YYYYMMDD.log`: Detailed logs of AutoGen agent operations
- `api_YYYYMMDD.log`: API endpoint and request processing logs

Each log entry includes:
- Timestamp
- Logger name
- Log level
- File and line number
- Detailed message
