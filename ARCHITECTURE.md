# 🏗️ System Architecture

## **PDF Document Analyzer - Technical Architecture**

This document provides a comprehensive overview of the system architecture, component interactions, and technical design decisions.

## 📊 **High-Level Architecture**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE LAYER                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐ │
│  │   Streamlit UI  │  │  File Upload    │  │        Chat Interface       │ │
│  │   (Frontend)    │  │   Interface     │  │         (Q&A)               │ │
│  │                 │  │                 │  │                             │ │
│  │ • Web Interface │  │ • File Handler  │  │ • Question Input            │ │
│  │ • State Mgmt    │  │ • Validation    │  │ • Answer Display            │ │
│  │ • User Session  │  │ • Progress UI   │  │ • Source Attribution       │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        APPLICATION LAYER                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐ │
│  │   PDF Loader    │  │   QA Pipeline   │  │      Session Manager        │ │
│  │  (Text Extract) │  │ (AI Processing) │  │                             │ │
│  │                 │  │                 │  │                             │ │
│  │ • Text Extract  │  │ • Chain Setup   │  │ • State Management          │ │
│  │ • Smart Chunking│  │ • Query Handler │  │ • Context Preservation      │ │
│  │ • Validation    │  │ • Result Format │  │ • Memory Management         │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AI/ML LAYER                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐ │
│  │    LangChain    │  │   HuggingFace   │  │        OpenRouter           │ │
│  │ (Orchestration) │  │  (Embeddings)   │  │       (LLM API)             │ │
│  │                 │  │                 │  │                             │ │
│  │ • Chain Mgmt    │  │ • Text Embedding│  │ • Model Access              │ │
│  │ • Prompt Engine │  │ • Vector Gen    │  │ • API Integration           │ │
│  │ • Retrieval QA  │  │ • Semantic Search│ │ • Response Generation       │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            DATA LAYER                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐ │
│  │    ChromaDB     │  │  Vector Store   │  │     Document Storage        │ │
│  │  (Vector DB)    │  │  (Embeddings)   │  │                             │ │
│  │                 │  │                 │  │                             │ │
│  │ • Vector Index  │  │ • Embedding DB  │  │ • File Management           │ │
│  │ • Similarity    │  │ • Fast Retrieval│  │ • Metadata Storage          │ │
│  │ • Search Engine │  │ • Context Cache │  │ • Session Persistence       │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🔄 **Data Flow Architecture**

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   PDF File  │───▶│ Text Extract│───▶│   Chunking  │───▶│  Embeddings │
│   Upload    │    │   (PyPDF2)  │    │ (Recursive  │    │(HuggingFace)│
│             │    │             │    │  Splitter)  │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                              │
                                                              ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Question  │───▶│  Query      │───▶│  Vector     │───▶│   LLM       │
│   Input     │    │  Processing │    │  Search     │    │ (OpenRouter) │
│             │    │             │    │ (ChromaDB)  │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                              │
                                                              ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Answer    │◀───│  Response   │◀───│  Context    │◀───│  Generated  │
│   Display   │    │  Formatting │    │  Assembly   │    │   Answer    │
│             │    │             │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## 🧩 **Component Details**

### **1. User Interface Layer**

#### **Streamlit Frontend**
- **Technology**: Streamlit 1.28.1+
- **Purpose**: Web-based user interface
- **Features**: 
  - Responsive design
  - Real-time updates
  - Session state management
  - Professional styling

#### **File Upload Interface**
- **Technology**: Streamlit file uploader
- **Purpose**: Secure document handling
- **Features**:
  - File type validation
  - Size limit enforcement (50MB)
  - Progress indicators
  - Error handling

#### **Chat Interface**
- **Technology**: Streamlit text input + display
- **Purpose**: Natural language Q&A
- **Features**:
  - Question input
  - Answer display
  - Source attribution
  - Quick question buttons

### **2. Application Layer**

#### **PDF Loader Module**
- **Technology**: PyPDF2 + LangChain text splitter
- **Purpose**: Document processing and chunking
- **Features**:
  - Text extraction from PDFs
  - Intelligent chunking (500 chars)
  - Overlap management (50 chars)
  - Error handling and validation

#### **QA Pipeline**
- **Technology**: LangChain + custom components
- **Purpose**: AI-powered question answering
- **Features**:
  - RetrievalQA chain setup
  - Vector store integration
  - Prompt engineering
  - Result formatting

#### **Session Manager**
- **Technology**: Streamlit session state
- **Purpose**: Application state management
- **Features**:
  - Document context preservation
  - Pipeline state management
  - Memory cleanup
  - User session isolation

### **3. AI/ML Layer**

#### **LangChain Framework**
- **Technology**: LangChain 0.0.350+
- **Purpose**: AI orchestration and chain management
- **Features**:
  - RetrievalQA chain implementation
  - Prompt template management
  - Chain type configuration
  - Result processing

#### **HuggingFace Embeddings**
- **Technology**: sentence-transformers
- **Purpose**: Semantic text representation
- **Features**:
  - Text embedding generation
  - Semantic similarity search
  - Model: all-MiniLM-L6-v2
  - Local processing capability

#### **OpenRouter Integration**
- **Technology**: OpenAI-compatible API
- **Purpose**: Large Language Model access
- **Features**:
  - Mistral-7B model access
  - API key management
  - Response generation
  - Error handling

### **4. Data Layer**

#### **ChromaDB**
- **Technology**: ChromaDB 0.4.18+
- **Purpose**: Vector database for embeddings
- **Features**:
  - In-memory vector storage
  - Similarity search
  - Collection management
  - Fast retrieval

#### **Vector Store**
- **Technology**: LangChain Chroma integration
- **Purpose**: Embedding storage and retrieval
- **Features**:
  - Vector indexing
  - Semantic search
  - Context retrieval
  - Memory management

#### **Document Storage**
- **Technology**: Temporary file system
- **Purpose**: Document processing and cleanup
- **Features**:
  - Temporary file management
  - Automatic cleanup
  - Memory optimization
  - Session isolation

## 🔧 **Technical Specifications**

### **Performance Characteristics**
- **Document Processing**: 2-5 seconds per MB
- **Question Response**: 1-3 seconds average
- **Memory Usage**: 100-500MB typical
- **Concurrent Users**: Single-user architecture

### **Scalability Considerations**
- **Horizontal Scaling**: Stateless design enables scaling
- **Vertical Scaling**: Memory and CPU optimization
- **Database Scaling**: ChromaDB supports clustering
- **API Scaling**: OpenRouter handles high throughput

### **Security Features**
- **API Key Management**: Secure credential handling
- **File Validation**: Comprehensive upload security
- **Error Handling**: Graceful failure management
- **Session Isolation**: User context separation

## 🚀 **Deployment Architecture**

### **Development Environment**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Local Dev     │    │   Virtual Env   │    │   Dependencies  │
│   Environment   │    │   (Python 3.8+) │    │   (requirements)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Production Deployment**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   Streamlit     │    │   Vector DB     │
│   (Optional)    │    │   Application   │    │   (ChromaDB)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Server    │    │   AI/ML Layer   │    │   Storage Layer │
│   (Nginx/Apache)│    │   (LangChain)   │    │   (File System) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📈 **Monitoring & Observability**

### **Key Metrics**
- **Processing Time**: Document analysis duration
- **Response Time**: Question answering latency
- **Memory Usage**: Application memory consumption
- **Error Rates**: API and processing failures

### **Logging Strategy**
- **Application Logs**: Streamlit and Python logging
- **Error Tracking**: Exception handling and reporting
- **Performance Monitoring**: Response time tracking
- **User Analytics**: Usage pattern analysis

## 🔮 **Future Architecture Enhancements**

### **Planned Improvements**
- **Microservices**: Component separation for scaling
- **Database Integration**: Persistent storage solution
- **API Gateway**: RESTful API endpoints
- **Containerization**: Docker deployment support

### **Advanced Features**
- **Multi-tenancy**: Multi-user support
- **Real-time Processing**: WebSocket integration
- **Advanced Analytics**: Usage and performance metrics
- **Machine Learning Pipeline**: Automated model training

---

*This architecture document provides a comprehensive overview of the system design and can be used for development, deployment, and maintenance purposes.* 