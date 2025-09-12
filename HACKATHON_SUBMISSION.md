# TiDB Hackathon Submission: Enhanced Repo Reader with RAG

## 🎯 Project Overview

**Enhanced Repo Reader** is an AI-powered repository analysis tool that now leverages **TiDB Serverless** to create intelligent, multi-step agentic workflows for code understanding through RAG (Retrieval-Augmented Generation).

## 🚀 Multi-Step Agentic Workflow

Our enhanced solution chains together the following building blocks in a single automated workflow:

### Step 1: Ingest & Index Data
- **Clone GitHub repositories** and extract code files
- **Chunk code files** into semantically meaningful segments  
- **Generate vector embeddings** using sentence transformers
- **Store in TiDB Serverless** with vector search capabilities
- **Index with full-text search** for hybrid retrieval

### Step 2: Search Your Data  
- **Vector similarity search** for semantic code understanding
- **Full-text search** for exact keyword matching
- **Hybrid search** combining both approaches for optimal results
- **Context-aware retrieval** of relevant code chunks

### Step 3: Chain LLM Calls
- **RAG-powered question answering** about repository code
- **Context-enhanced responses** using retrieved code chunks
- **Multi-turn conversations** with persistent code context
- **Difficulty-adaptive explanations** (beginner/intermediate/advanced)

### Step 4: Invoke External Tools
- **GitHub API integration** for repository cloning
- **TiDB Cloud APIs** for vector storage and retrieval
- **OpenAI/Local LLM APIs** for intelligent analysis
- **Real-time streaming** for progress updates

### Step 5: Build Multi-Step Flow
- **Automated workflow orchestration** using LangGraph
- **State management** across processing steps
- **Error handling and fallbacks** for robust operation
- **Interactive chat widget** for seamless user experience

## 🛠 TiDB Integration Details

### Database Schema
```sql
CREATE TABLE code_embeddings (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    repo_name VARCHAR(255) NOT NULL,
    repo_url VARCHAR(500) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    chunk_id VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(384) NOT NULL COMMENT 'hnsw(distance=cosine)',
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_repo_name (repo_name),
    INDEX idx_file_path (file_path),
    FULLTEXT KEY ft_content (content),
    UNIQUE KEY unique_chunk (repo_name, file_path, chunk_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### Key Features Leveraged
- **Vector Search**: `VEC_COSINE_DISTANCE()` for semantic similarity
- **Full-text Search**: MySQL FULLTEXT indexes for keyword matching
- **JSON Storage**: Metadata storage with JSON querying
- **HNSW Indexing**: High-performance vector similarity search
- **Hybrid Queries**: Combined vector + full-text results

## 📊 Data Flow Architecture

```
GitHub Repo → Code Extraction → Text Chunking → Embedding Generation → TiDB Storage
     ↓
User Question → Hybrid Search (TiDB) → Context Retrieval → LLM Processing → AI Answer
     ↓
Chat Widget ← Formatted Response ← Source Citations ← RAG Pipeline ← Vector Results
```

## 🎮 Enhanced User Experience

### Before: Basic Repository Analysis
- Static walkthrough generation
- Pre-defined learning modules
- No interactive code exploration

### After: Interactive RAG-Powered Learning
- **Real-time code questions** via chat widget
- **Contextual answers** with source code citations
- **Semantic code search** across the entire repository
- **Multi-modal interaction** (guided walkthrough + Q&A)

## 🔧 Technical Implementation

### New Components Added:
1. **TiDB Vector Store** (`api/tidb_vector_store.py`)
2. **Code Indexer Tool** (`api/tools/code_indexer.py`) 
3. **RAG Query Tool** (`api/tools/rag_query_tool.py`)
4. **Chat Widget UI** (`components/CodeChatWidget.tsx`)
5. **API Endpoints** for `/api/ask` and `/api/search`

### Integration Points:
- **LangGraph Agent** updated with indexing step
- **Flask API** extended with RAG endpoints
- **Frontend Components** enhanced with chat interface
- **Workflow Pipeline** now includes TiDB indexing

## 🌟 Key Innovations

1. **Seamless Integration**: TiDB indexing happens automatically during repository analysis
2. **Hybrid Search Strategy**: Combines vector similarity with full-text search for better results
3. **Context-Aware Responses**: LLM answers include relevant source code citations
4. **Progressive Enhancement**: Existing functionality enhanced, not replaced
5. **Error Resilience**: System continues working even if TiDB is unavailable

## 🚀 Getting Started

### Prerequisites
```bash
# TiDB Cloud account and connection details
# OpenAI API key (or local LLM setup)
# Node.js 18+ and Python 3.13+
```

### Setup Instructions
```bash
# 1. Clone and install dependencies
git clone <repo-url>
cd repo-reader
npm install
pip install -r requirements.txt

# 2. Configure TiDB connection
cp .env.example .env
# Add your TiDB Serverless connection details:
# TIDB_HOST=gateway01.your-region.prod.aws.tidbcloud.com
# TIDB_USER=your_username  
# TIDB_PASSWORD=your_password
# TIDB_DATABASE=your_database_name

# 3. Start the application
npm run dev
```

### Usage Example
```bash
# 1. Analyze a repository (automatic TiDB indexing)
POST /api/analyze
{
  "github_url": "https://github.com/user/repo",
  "user_level": "intermediate" 
}

# 2. Ask questions about the code
POST /api/ask
{
  "question": "How does the authentication system work?",
  "repo_name": "user/repo",
  "user_level": "intermediate"
}

# 3. Search code semantically  
POST /api/search
{
  "query": "database connection pooling",
  "repo_name": "user/repo",
  "search_type": "hybrid"
}
```

## 📈 Demonstration Video

[Demo Video URL - showing the complete workflow from repository analysis to interactive Q&A]

## 🏆 Hackathon Compliance

✅ **TiDB Serverless Integration**: Vector storage with HNSW indexing
✅ **Multi-Step Workflow**: 5-step automated pipeline  
✅ **Agentic Solution**: LangGraph orchestration with intelligent decision making
✅ **Innovative Use Case**: Code understanding through conversational AI
✅ **Working Application**: Fully functional with real-time chat interface
✅ **Public Repository**: Open source with clear documentation

## 🔮 Future Enhancements

- **Code generation assistance** based on repository patterns
- **Pull request analysis** with TiDB-powered context
- **Team collaboration features** with shared code insights
- **Advanced search filters** by language, complexity, and patterns
- **Integration with IDEs** for in-editor code assistance

---

**TiDB Cloud Account**: [Your TiDB account email]
**Repository**: https://github.com/[your-username]/repo-reader
**License**: MIT (Open Source)