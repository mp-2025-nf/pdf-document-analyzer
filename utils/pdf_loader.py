"""
PDF Loader Module

This module handles PDF file loading, text extraction, and chunking.
It provides a clean interface for processing PDF documents into
manageable text chunks for vector storage and retrieval.
"""

import os
from typing import List, Optional
from pathlib import Path
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter


class PDFLoader:
    """Handles PDF file loading and text chunking operations."""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize the PDF loader with chunking parameters.
        
        Args:
            chunk_size: Maximum size of each text chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def load_pdf(self, file_path: str) -> List[str]:
        """
        Load and extract text from a PDF file, then split into chunks.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            List of text chunks
            
        Raises:
            FileNotFoundError: If the PDF file doesn't exist
            ValueError: If the PDF is empty or invalid
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        if not file_path.lower().endswith('.pdf'):
            raise ValueError(f"File must be a PDF: {file_path}")
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                if len(pdf_reader.pages) == 0:
                    raise ValueError("PDF file is empty")
                
                # Extract text from all pages
                text_content = ""
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text + "\n"
                
                if not text_content.strip():
                    raise ValueError("No text content found in PDF")
                
                # Split text into chunks
                chunks = self.text_splitter.split_text(text_content)
                
                if not chunks:
                    raise ValueError("Failed to create text chunks")
                
                return chunks
                
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")
    def get_chunk_info(self, chunks: List[str]) -> dict:
        """
        Get information about the created chunks.
        
        Args:
            chunks: List of text chunks
            
        Returns:
            Dictionary with chunk statistics
        """
        if not chunks:
            return {"total_chunks": 0, "avg_chunk_size": 0, "total_characters": 0}
        
        total_chars = sum(len(chunk) for chunk in chunks)
        avg_size = total_chars / len(chunks)
        
        return {
            "total_chunks": len(chunks),
            "avg_chunk_size": round(avg_size, 2),
            "total_characters": total_chars
        } 