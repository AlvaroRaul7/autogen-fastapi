from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import PDFUploadRequest, QueryRequest, QueryResponse
from app.services.pdf_service import PDFService
from app.services.embedding_service import EmbeddingService
from app.services.supabase_service import SupabaseService
from app.agents import InformAgent
from app.core.logging import api_logger
from typing import Dict

# Initialize services
pdf_service = PDFService()
embedding_service = EmbeddingService()
supabase_service = SupabaseService()
inform_agent = InformAgent()

# Create router with tags and prefix
router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
    responses={404: {"description": "Document not found"}},
)

@router.post("/process-pdf", response_model=Dict)
async def process_pdf(request: PDFUploadRequest):
    """
    Process a PDF document from a URL.
    
    - Downloads the PDF from the provided URL
    - Extracts and chunks the text content
    - Generates embeddings for each chunk
    - Stores the chunks and embeddings in Supabase
    
    Returns:
        dict: A success message with the number of chunks processed
    """
    api_logger.info(f"Processing PDF from URL: {request.url}")
    
    try:
        # Download and process PDF
        api_logger.info("Starting PDF download and processing")
        chunks = await pdf_service.process_pdf_url(str(request.url))
        api_logger.info(f"Successfully processed PDF into {len(chunks)} chunks")
        
        # Generate embeddings and store in Supabase
        api_logger.info("Starting embedding generation and storage")
        for i, chunk_text in enumerate(chunks, 1):
            api_logger.debug(f"Processing chunk {i}/{len(chunks)}")
            embedding = await embedding_service.create_embedding(chunk_text)
            await supabase_service.store_document_chunk(
                chunk_text=chunk_text,
                embedding=embedding,
                metadata={
                    "source_url": str(request.url),
                    "chunk_index": i
                }
            )
        
        api_logger.info("PDF processing completed successfully")
        return {
            "message": f"Successfully processed PDF from {request.url}",
            "chunk_count": len(chunks)
        }
    except Exception as e:
        api_logger.error(f"Error processing PDF: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Search through processed documents using semantic search.
    
    - Uses AutoGen agents to enhance the search query
    - Performs semantic search using embeddings
    - Analyzes results using AutoGen agents
    - Returns relevant chunks with similarity scores
    
    Returns:
        QueryResponse: Relevant document chunks with their metadata and similarity scores
    """
    api_logger.info(f"Processing query request: {request.query}")
    
    try:
        # Use researcher agent to enhance the query
        api_logger.info("Starting query enhancement with researcher agent")
        enhanced_query = await inform_agent._enhance_query(request.query)
        api_logger.info(f"Query enhanced: {enhanced_query}")
        
        # Generate embedding for the enhanced query
        api_logger.info("Generating embedding for enhanced query")
        query_embedding = await embedding_service.create_embedding(enhanced_query)
        
        # Search for relevant chunks
        api_logger.info(f"Searching for relevant chunks (limit: {request.limit})")
        chunks = await supabase_service.search_similar_chunks(
            query_embedding=query_embedding,
            limit=request.limit if request.limit else 5
        )
        
        if not chunks:
            api_logger.info("No relevant chunks found")
            return QueryResponse(chunks=[], total_chunks=0)
        
        api_logger.info(f"Found {len(chunks)} relevant chunks")
        
        # Use analyst agent to analyze chunks and provide a comprehensive response
        api_logger.info("Starting chunk analysis with analyst agent")
        analysis = await inform_agent._analyze_chunks(chunks=chunks, query=request.query)
        api_logger.info("Chunk analysis completed")
        
        # Add the analysis to each chunk's metadata
        for chunk in chunks:
            chunk["metadata"]["analysis"] = analysis
        
        api_logger.info("Query processing completed successfully")
        return QueryResponse(
            chunks=chunks,
            total_chunks=len(chunks)
        )
    except Exception as e:
        api_logger.error(f"Error processing query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) 