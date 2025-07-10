"""
PDF Q&A Chatbot - Main Application

A Streamlit-based interface for uploading PDF documents and asking questions
using OpenRouter (Mistral-7B) and LangChain for intelligent document Q&A.
"""

import streamlit as st
import os
import tempfile
from pathlib import Path
from dotenv import load_dotenv
from utils.pdf_loader import PDFLoader
from utils.qa_pipeline import QAPipeline

# Load environment variables
load_dotenv()


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'qa_pipeline' not in st.session_state:
        st.session_state.qa_pipeline = None
    if 'pdf_loaded' not in st.session_state:
        st.session_state.pdf_loaded = False
    if 'chunks' not in st.session_state:
        st.session_state.chunks = []
    if 'current_pdf_name' not in st.session_state:
        st.session_state.current_pdf_name = ""


def setup_page():
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title="PDF Document Analyzer",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for compact professional styling
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #1f77b4 0%, #2c3e50 100%);
        padding: 0.75rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        color: white;
        text-align: center;
    }
    .compact-card {
        background-color: white;
        padding: 0.75rem;
        border-radius: 6px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
        border: 1px solid #e9ecef;
    }
    .metric-compact {
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-radius: 4px;
        border-left: 3px solid #1f77b4;
        margin: 0.25rem 0;
        font-size: 0.9rem;
    }
    .sidebar-compact {
        background-color: white;
        padding: 0.5rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        border: 1px solid #e9ecef;
    }
    .upload-compact {
        border: 2px dashed #1f77b4;
        border-radius: 6px;
        padding: 1rem;
        text-align: center;
        background-color: #f8f9fa;
        margin: 0.5rem 0;
    }
    .chat-compact {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
        border: 1px solid #e9ecef;
    }
    .answer-compact {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 6px;
        border-left: 3px solid #28a745;
        margin: 0.5rem 0;
    }
    .source-compact {
        background-color: #fff3cd;
        padding: 0.5rem;
        border-radius: 4px;
        border: 1px solid #ffeaa7;
        margin: 0.25rem 0;
        font-size: 0.85rem;
    }
    .metric-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.5rem;
        margin: 0.5rem 0;
    }
    .compact-text {
        font-size: 0.9rem;
        margin: 0.25rem 0;
    }
    .compact-title {
        font-size: 1rem;
        font-weight: 600;
        margin: 0.25rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Compact professional header
    st.markdown("""
    <div class="main-header">
        <h2 style="margin: 0;">📊 PDF Document Analyzer</h2>
        <p style="margin: 0; opacity: 0.9; font-size: 0.9rem;">Enterprise AI-powered document analysis</p>
    </div>
    """, unsafe_allow_html=True)


def check_openrouter_key():
    """Check if OpenRouter API key is available."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        st.markdown("""
        <div class="compact-card">
            <div class="compact-title">⚠️ Configuration Required</div>
            <div class="compact-text">OpenRouter API key not found.</div>
        </div>
        """, unsafe_allow_html=True)
        st.info("**Setup:** `export OPENROUTER_API_KEY=your-key`")
        return False
    return True


def process_pdf(uploaded_file):
    """Process uploaded PDF file and set up QA pipeline."""
    tmp_path = None
    try:
        # Validate file size (max 50MB)
        if uploaded_file.size > 50 * 1024 * 1024:
            st.error("❌ File size exceeds 50MB limit.")
            return None, None
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        # Load and chunk PDF
        pdf_loader = PDFLoader()
        chunks = pdf_loader.load_pdf(tmp_path)
        
        # Get chunk information
        chunk_info = pdf_loader.get_chunk_info(chunks)
        
        # Set up QA pipeline
        qa_pipeline = QAPipeline()
        qa_chain = qa_pipeline.setup_qa_pipeline(chunks)
        
        # Update session state
        st.session_state.qa_pipeline = qa_pipeline
        st.session_state.chunks = chunks
        st.session_state.pdf_loaded = True
        st.session_state.current_pdf_name = uploaded_file.name
        
        return chunk_info, qa_pipeline.get_vector_store_info()
        
    except ValueError as e:
        error_msg = str(e)
        if "quota exceeded" in error_msg.lower():
            st.error("🚫 OpenRouter Quota Exceeded!")
            st.error("Your OpenRouter account has insufficient credits. Please:")
            st.markdown("""
            1. **Add credits** to your OpenRouter account at [openrouter.ai/account](https://openrouter.ai/account)
            2. **Check your usage** and billing limits
            3. **Upgrade your plan** if needed
            """)
        elif "invalid api key" in error_msg.lower():
            st.error("🔑 Invalid OpenRouter API Key!")
            st.error("Please check your API key in the `.env` file.")
        else:
            st.error(f"❌ Error: {error_msg}")
        return None, None
    except Exception as e:
        st.error(f"❌ Error processing PDF: {str(e)}")
        return None, None
    finally:
        # Clean up temporary file
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception:
                pass


def ask_question(question, qa_pipeline):
    """Ask a question and return the answer."""
    try:
        result = qa_pipeline.query_chain(question)
        return result
    except Exception as e:
        return {
            "answer": f"Error processing question: {str(e)}",
            "sources": [],
            "source_count": 0
        }


def main():
    """Main application function."""
    initialize_session_state()
    setup_page()
    
    # Check OpenRouter API key
    check_openrouter_key()
    
    # Compact sidebar
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-compact">
            <div class="compact-title">📄 Document Upload</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Compact file upload
        st.markdown("""
        <div class="upload-compact">
            <div class="compact-text">📁 Select PDF</div>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            help="Upload a PDF document to analyze",
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            st.success(f"✅ {uploaded_file.name}")
            
            if st.button("🚀 Process", type="primary", use_container_width=True):
                with st.spinner("🔄 Processing..."):
                    chunk_info, vector_info = process_pdf(uploaded_file)
                    
                    if chunk_info and vector_info:
                        st.success("✅ Processed!")
                        
                        # Compact metrics display
                        with st.expander("📊 Metrics", expanded=False):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Chunks", chunk_info['total_chunks'])
                                st.metric("Chars", f"{chunk_info['total_characters']:,}")
                            with col2:
                                st.metric("Avg Size", f"{chunk_info['avg_chunk_size']}")
                                st.metric("Vectors", vector_info['total_documents'])
        
        # Compact document info
        if st.session_state.pdf_loaded:
            st.markdown("""
            <div class="sidebar-compact">
                <div class="compact-title">📋 Active Document</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.info(f"**{st.session_state.current_pdf_name}**")
            st.info(f"**Chunks:** {len(st.session_state.chunks)}")
            
            if st.button("🗑️ Clear", type="secondary", use_container_width=True):
                if st.session_state.qa_pipeline:
                    st.session_state.qa_pipeline.clear_vector_store()
                # Clear all session state
                for key in ['qa_pipeline', 'pdf_loaded', 'chunks', 'current_pdf_name']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
    
    # Main content area
    if not st.session_state.pdf_loaded:
        # Compact welcome section
        st.markdown("""
        <div class="chat-compact">
            <div class="compact-title">🎯 Welcome to PDF Document Analyzer</div>
            <div class="compact-text">Upload a PDF document using the sidebar to begin analysis.</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Compact feature highlights
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="compact-card">
                <div class="compact-title">🔍 How It Works</div>
                <div class="compact-text">
                • Extract text from PDF documents<br>
                • Split into intelligent chunks<br>
                • Create semantic embeddings<br>
                • Enable AI-powered Q&A
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="compact-card">
                <div class="compact-title">💡 Perfect For</div>
                <div class="compact-text">
                • Research papers & documents<br>
                • Technical manuals<br>
                • Business reports<br>
                • Any PDF content
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Compact sample questions
        with st.expander("❓ Sample Questions", expanded=False):
            st.markdown("""
            Try asking:
            - "What is the main topic?"
            - "Summarize key findings"
            - "What are conclusions?"
            """)
    
    else:
        # Compact chat interface
        st.markdown("""
        <div class="chat-compact">
            <div class="compact-title">💬 Document Q&A</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Compact question input
        question = st.text_input(
            "Ask a question:",
            placeholder="What is the main topic?",
            help="Ask any question about the document",
            label_visibility="collapsed"
        )
        
        col1, col2 = st.columns([4, 1])
        with col1:
            ask_button = st.button("🔍 Ask", type="primary", use_container_width=True)
        with col2:
            if st.button("🔄 Clear", type="secondary", use_container_width=True):
                question = ""
        
        if question and ask_button:
            with st.spinner("🤔 Analyzing..."):
                result = ask_question(question, st.session_state.qa_pipeline)
                
                # Compact answer display
                st.markdown("""
                <div class="answer-compact">
                    <div class="compact-title">💡 Answer</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.write(result["answer"])
                
                # Compact sources display
                if result["source_count"] > 0:
                    with st.expander(f"📖 Sources ({result['source_count']})", expanded=False):
                        for i, source in enumerate(result["sources"], 1):
                            st.markdown(f"""
                            <div class="source-compact">
                                <strong>Source {i}:</strong> {source}
                            </div>
                            """, unsafe_allow_html=True)
        
        # Compact quick questions
        st.markdown("""
        <div class="compact-card">
            <div class="compact-title">🚀 Quick Questions</div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        quick_questions = [
            "What is the main topic?",
            "Summarize key points",
            "What are conclusions?"
        ]
        
        for i, q in enumerate(quick_questions):
            with [col1, col2, col3][i]:
                if st.button(q, key=f"quick_{i}", use_container_width=True):
                    with st.spinner("🤔 Analyzing..."):
                        result = ask_question(q, st.session_state.qa_pipeline)
                        st.markdown("""
                        <div class="answer-compact">
                            <div class="compact-title">💡 Answer</div>
                        </div>
                        """, unsafe_allow_html=True)
                        st.write(result["answer"])


if __name__ == "__main__":
    main() 