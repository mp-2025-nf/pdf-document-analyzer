"""
QA Pipeline Module

This module handles the question-answering pipeline including:
- Text embedding using HuggingFace sentence-transformers (free, local)
- Vector storage with ChromaDB
- Retrieval and answer generation using OpenRouter (Mistral-7B)
"""

import os
from typing import List, Optional
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from pydantic import SecretStr
import chromadb
import uuid


class QAPipeline:
    """Handles the complete question-answering pipeline using OpenRouter and HuggingFace embeddings."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        llm_base_url: Optional[str] = None,
        llm_model: Optional[str] = None,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        """
        Initialize the QA pipeline with LLM and embedding settings.
        
        Args:
            api_key: OpenRouter API key (from env if not provided)
            llm_base_url: Base URL for OpenRouter API (from env if not provided)
            llm_model: Model name for the LLM (from env if not provided)
            embedding_model: HuggingFace embedding model name
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.llm_base_url = llm_base_url or os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
        self.llm_model = llm_model or os.getenv("LLM_MODEL", "mistralai/mistral-7b-instruct")
        
        if not self.api_key:
            raise ValueError("OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable.")
        
        try:
            # Initialize HuggingFace embeddings (free, no API key required)
            self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
        except Exception as e:
            raise ValueError(f"Failed to initialize embeddings: {str(e)}. Please ensure sentence-transformers is installed.")
        
        try:
            # Initialize LLM (OpenAI-compatible, configurable)
            self.llm = ChatOpenAI(
                base_url=self.llm_base_url,
                api_key=SecretStr(self.api_key),
                model=self.llm_model,
                temperature=0.1
            )
        except Exception as e:
            raise ValueError(f"Failed to initialize LLM: {str(e)}. Please check your OpenRouter API key and model configuration.")
        
        self.vector_store = None
        self.qa_chain = None
    
    def setup_qa_pipeline(self, chunks: List[str]) -> RetrievalQA:
        """
        Set up the QA pipeline with the provided text chunks.
        
        Args:
            chunks: List of text chunks to embed and store
            
        Returns:
            Configured RetrievalQA chain
        """
        if not chunks:
            raise ValueError("No text chunks provided")
        
        try:
            # Create vector store with ChromaDB (in-memory)
            collection_name = f"pdf_qa_collection_{uuid.uuid4().hex[:8]}"
            self.vector_store = Chroma.from_texts(
                texts=chunks,
                embedding=self.embeddings,
                collection_name=collection_name
            )
        except Exception as e:
            raise ValueError(f"Failed to create vector store: {str(e)}")
        
        # Create custom prompt template
        prompt_template = """Use the following context to answer the question at the end. 
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        
        Context: {context}
        
        Question: {question}
        
        Answer:"""
        
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        try:
            # Create RetrievalQA chain
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vector_store.as_retriever(
                    search_type="similarity",
                    search_kwargs={"k": 3}
                ),
                chain_type_kwargs={"prompt": prompt},
                return_source_documents=True
            )
        except Exception as e:
            raise ValueError(f"Failed to create QA chain: {str(e)}")
        
        return self.qa_chain
    
    def query_chain(self, question: str) -> dict:
        """
        Query the QA chain with a question.
        
        Args:
            question: The question to ask
            
        Returns:
            Dictionary containing answer and source documents
        """
        if not self.qa_chain:
            raise ValueError("QA pipeline not initialized. Call setup_qa_pipeline first.")
        
        if not question.strip():
            raise ValueError("Question cannot be empty")
        
        try:
            # Get answer from chain
            result = self.qa_chain({"query": question})
            
            # Extract answer and sources
            answer = result.get("result", "No answer generated")
            source_documents = result.get("source_documents", [])
            
            # Format source information
            sources = []
            for doc in source_documents:
                if hasattr(doc, 'page_content'):
                    # Truncate source content for display
                    content = doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                    sources.append(content)
                elif hasattr(doc, 'content'):
                    # Alternative attribute name
                    content = doc.content[:200] + "..." if len(doc.content) > 200 else doc.content
                    sources.append(content)
            
            return {
                "answer": answer,
                "sources": sources,
                "source_count": len(sources)
            }
            
        except Exception as e:
            return {
                "answer": f"Error processing question: {str(e)}",
                "sources": [],
                "source_count": 0
            }
    
    def get_vector_store_info(self) -> dict:
        """
        Get information about the vector store.
        
        Returns:
            Dictionary with vector store statistics
        """
        if not self.vector_store:
            return {"total_documents": 0}
        
        try:
            # Get collection info
            collection = self.vector_store._collection
            count = collection.count()
            
            return {
                "total_documents": count,
                "collection_name": collection.name
            }
        except Exception:
            return {"total_documents": 0}
    
    def clear_vector_store(self):
        """Clear the current vector store."""
        if self.vector_store:
            try:
                # Delete the collection
                collection = self.vector_store._collection
                # Use the client to delete the collection
                client = chromadb.Client()
                client.delete_collection(name=collection.name)
                self.vector_store = None
                self.qa_chain = None
            except Exception:
                pass 