import requests
from pypdf import PdfReader
from io import BytesIO
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.core.config import get_settings
import re

settings = get_settings()

class PDFService:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len
        )

    async def download_pdf(self, url: str) -> BytesIO:
        """Download PDF from URL"""
        # Handle Google Drive URLs
        if 'drive.google.com' in url:
            # Extract file ID from Google Drive URL
            file_id = None
            if '/file/d/' in url:
                file_id = url.split('/file/d/')[1].split('/')[0]
            elif 'id=' in url:
                file_id = url.split('id=')[1].split('&')[0]
            
            if not file_id:
                raise ValueError("Could not extract file ID from Google Drive URL")
            
            # Use the direct download link
            url = f"https://drive.google.com/uc?export=download&id={file_id}"
        
        response = requests.get(url)
        response.raise_for_status()
        return BytesIO(response.content)

    async def extract_text(self, pdf_file: BytesIO) -> str:
        """Extract text from PDF"""
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

    async def create_chunks(self, text: str) -> list:
        """Split text into chunks"""
        return self.text_splitter.split_text(text)

    async def process_pdf_url(self, url: str) -> list:
        """Process PDF URL and return chunks"""
        pdf_file = await self.download_pdf(url)
        text = await self.extract_text(pdf_file)
        chunks = await self.create_chunks(text)
        return chunks 