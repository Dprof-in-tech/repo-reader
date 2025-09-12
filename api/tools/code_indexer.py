"""Code Indexing Tool for TiDB Vector Store Integration"""

from typing import Dict, List, Any, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from .tidb_vector_store_fixed import TiDBVectorStore


class CodeIndexerInput(BaseModel):
    repo_data: Dict[str, Any] = Field(description="Repository data to index")
    force_reindex: bool = Field(default=False, description="Force reindexing even if repo exists")


class CodeIndexerTool(BaseTool):
    """Tool for indexing repository code into TiDB vector store"""
    
    name: str = "code_indexer"
    description: str = "Indexes repository code into TiDB vector store for semantic search and RAG"
    args_schema: type[BaseModel] = CodeIndexerInput
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._vector_store = None
        self._initialize_vector_store()
    
    def _initialize_vector_store(self):
        """Initialize TiDB vector store connection"""
        try:
            self._vector_store = TiDBVectorStore()
            print("✅ TiDB Vector Store initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize TiDB Vector Store: {e}")
            self._vector_store = None
    
    def _run(self, repo_data: Dict[str, Any], force_reindex: bool = False) -> Dict[str, Any]:
        """Index repository code into vector store"""
        if not self._vector_store:
            return {
                "success": False,
                "error": "TiDB Vector Store not available",
                "indexed_files": 0,
                "total_chunks": 0
            }
        
        try:
            repo_name = repo_data.get('repo_name', 'unknown_repo')
            
            # Check if repository already exists (unless force reindex)
            if not force_reindex:
                existing_stats = self._vector_store.get_repository_stats(repo_name)
                if existing_stats['total_chunks'] > 0:
                    return {
                        "success": True,
                        "message": f"Repository '{repo_name}' already indexed",
                        "existing_stats": existing_stats,
                        "indexed_files": existing_stats['total_files'],
                        "total_chunks": existing_stats['total_chunks'],
                        "reindexed": False
                    }
            
            # Index the repository
            print(f"🔄 Indexing repository: {repo_name}")
            result = self._vector_store.index_repository(repo_data)
            
            if result['success']:
                print(f"✅ Successfully indexed {result['indexed_files']} files, {result['total_chunks']} chunks")
                return {
                    "success": True,
                    "message": f"Successfully indexed repository '{repo_name}'",
                    "indexed_files": result['indexed_files'],
                    "total_chunks": result['total_chunks'],
                    "reindexed": force_reindex
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to index repository",
                    "indexed_files": 0,
                    "total_chunks": 0
                }
                
        except Exception as e:
            print(f"❌ Error during code indexing: {e}")
            return {
                "success": False,
                "error": f"Indexing failed: {str(e)}",
                "indexed_files": 0,
                "total_chunks": 0
            }
    
    async def _arun(self, repo_data: Dict[str, Any], force_reindex: bool = False) -> Dict[str, Any]:
        """Async version of the tool"""
        return self._run(repo_data, force_reindex)


class CodeSearchInput(BaseModel):
    query: str = Field(description="Search query for code")
    repo_name: str = Field(description="Repository name to search in") 
    search_type: str = Field(default="hybrid", description="Search type: vector, fulltext, or hybrid")
    limit: int = Field(default=5, description="Maximum number of results")


class CodeSearchTool(BaseTool):
    """Tool for searching indexed code using vector and full-text search"""
    
    name: str = "code_search"
    description: str = "Search indexed code using vector similarity, full-text search, or hybrid approach"
    args_schema: type[BaseModel] = CodeSearchInput
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._vector_store = None
        self._initialize_vector_store()
    
    def _initialize_vector_store(self):
        """Initialize TiDB vector store connection"""
        try:
            self._vector_store = TiDBVectorStore()
            print("✅ TiDB Vector Store initialized for search")
        except Exception as e:
            print(f"❌ Failed to initialize TiDB Vector Store for search: {e}")
            self._vector_store = None
    
    def _run(self, query: str, repo_name: str, search_type: str = "hybrid", limit: int = 5) -> Dict[str, Any]:
        """Search for relevant code chunks"""
        if not self._vector_store:
            return {
                "success": False,
                "error": "TiDB Vector Store not available",
                "results": []
            }
        
        try:
            print(f"🔍 Searching for: '{query}' in {repo_name} (type: {search_type})")
            
            # Perform search based on type
            if search_type == "vector":
                results = self._vector_store.vector_search(query, repo_name, limit)
            elif search_type == "fulltext":
                results = self._vector_store.fulltext_search(query, repo_name, limit)
            elif search_type == "hybrid":
                results = self._vector_store.hybrid_search(query, repo_name, limit)
            else:
                return {
                    "success": False,
                    "error": f"Invalid search type: {search_type}",
                    "results": []
                }
            
            # Process results for better presentation
            processed_results = []
            for result in results:
                processed_result = {
                    "file_path": result['file_path'],
                    "chunk_id": result['chunk_id'],
                    "content": result['content'][:500] + "..." if len(result['content']) > 500 else result['content'],
                    "full_content": result['content'],
                    "metadata": result['metadata'],
                    "search_type": result.get('search_type', search_type)
                }
                
                # Add appropriate score
                if 'similarity_score' in result:
                    processed_result['similarity_score'] = result['similarity_score']
                if 'relevance_score' in result:
                    processed_result['relevance_score'] = result['relevance_score']
                if 'combined_score' in result:
                    processed_result['combined_score'] = result['combined_score']
                
                processed_results.append(processed_result)
            
            print(f"✅ Found {len(results)} relevant code chunks")
            
            return {
                "success": True,
                "query": query,
                "repo_name": repo_name,
                "search_type": search_type,
                "results_count": len(results),
                "results": processed_results
            }
            
        except Exception as e:
            print(f"❌ Error during code search: {e}")
            return {
                "success": False,
                "error": f"Search failed: {str(e)}",
                "results": []
            }
    
    async def _arun(self, query: str, repo_name: str, search_type: str = "hybrid", limit: int = 5) -> Dict[str, Any]:
        """Async version of the tool"""
        return self._run(query, repo_name, search_type, limit)