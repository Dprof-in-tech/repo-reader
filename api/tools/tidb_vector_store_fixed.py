"""TiDB Vector Store using proper SQLAlchemy integration"""

import os
import json
import time
import hashlib
from typing import List, Dict, Any, Optional
from functools import lru_cache
from sqlalchemy import create_engine, Column, Integer, Text, String, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func, text
from sqlalchemy.pool import QueuePool
from tidb_vector.sqlalchemy import VectorType
from sentence_transformers import SentenceTransformer

Base = declarative_base()

class CodeEmbedding(Base):
    """SQLAlchemy model for code embeddings"""
    __tablename__ = 'code_embeddings'
    
    id = Column(Integer, primary_key=True)
    repo_name = Column(String(100), nullable=False, index=True)
    repo_url = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False, index=True) 
    chunk_id = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(VectorType(384), nullable=False)  # 384-dim vectors
    chunk_metadata = Column(Text)  # JSON string (renamed from metadata)
    created_at = Column(DateTime, default=func.now())
    
    # Composite index for uniqueness
    __table_args__ = (
        Index('idx_unique_chunk', 'repo_name', 'file_path', 'chunk_id'),
    )

class TiDBVectorStore:
    """TiDB-based vector store using proper SQLAlchemy integration"""
    
    def __init__(self):
        """Initialize TiDB connection and embedding model"""
        self.host = os.getenv('TIDB_HOST')
        self.port = int(os.getenv('TIDB_PORT', 4000))
        self.user = os.getenv('TIDB_USER')
        self.password = os.getenv('TIDB_PASSWORD')
        self.database = os.getenv('TIDB_DATABASE')
        self.ssl_ca = os.getenv('TIDB_SSL_CA')
        
        # Initialize sentence transformer for embeddings (with optimizations)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_model.to('mps' if hasattr(self.embedding_model, 'device') else 'cpu')  # Use MPS if available
        self.embedding_dim = 384  # Dimension for all-MiniLM-L6-v2
        
        # Create database engine with connection pooling
        self.engine = self._create_engine()
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Create tables
        self._initialize_tables()
        
        # Cache for embeddings
        self._embedding_cache = {}
        self._cache_max_size = 1000
        
        print("✅ TiDB Vector Store initialized with performance optimizations")
    
    def _create_engine(self):
        """Create SQLAlchemy engine for TiDB with connection pooling"""
        connection_string = f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        
        connect_args = {}
        if self.ssl_ca:
            connect_args['ssl_ca'] = self.ssl_ca
        else:
            connect_args['ssl_disabled'] = True
            
        return create_engine(
            connection_string, 
            connect_args=connect_args,
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=300
        )
    
    def _initialize_tables(self):
        """Initialize required tables"""
        try:
            # Drop the old table if it exists with wrong schema
            with self.SessionLocal() as session:
                session.execute(text("DROP TABLE IF EXISTS code_embeddings"))
                session.commit()
            
            # Create tables with correct schema
            Base.metadata.create_all(self.engine)
            print("✅ Tables created with proper vector schema")
        except Exception as e:
            print(f"⚠️ Table initialization warning: {e}")
            # Try to create anyway
            Base.metadata.create_all(self.engine)
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embeddings for text using sentence transformer with caching"""
        # Create cache key
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Check cache first
        if text_hash in self._embedding_cache:
            return self._embedding_cache[text_hash]
        
        # Generate embedding
        start_time = time.time()
        embedding = self.embedding_model.encode([text], show_progress_bar=False)[0]
        embedding_list = embedding.tolist()
        
        # Cache the result (with size limit)
        if len(self._embedding_cache) >= self._cache_max_size:
            # Remove oldest entries (simple FIFO)
            oldest_key = next(iter(self._embedding_cache))
            del self._embedding_cache[oldest_key]
        
        self._embedding_cache[text_hash] = embedding_list
        
        elapsed = time.time() - start_time
        print(f"⚡ Generated embedding in {elapsed:.2f}s (cached: {text_hash[:8]})")
        
        return embedding_list
    
    def chunk_code_file(self, content: str, file_path: str, chunk_size: int = 1000) -> List[Dict[str, Any]]:
        """Chunk code file into smaller pieces for embedding"""
        chunks = []
        lines = content.split('\n')
        
        current_chunk = []
        current_size = 0
        chunk_num = 0
        
        for line_num, line in enumerate(lines):
            current_chunk.append(line)
            current_size += len(line) + 1  # +1 for newline
            
            # If chunk is large enough or we're at the end
            if current_size >= chunk_size or line_num == len(lines) - 1:
                if current_chunk:  # Don't add empty chunks
                    chunk_content = '\n'.join(current_chunk)
                    chunk_id = f"chunk_{chunk_num}"
                    
                    chunks.append({
                        'chunk_id': chunk_id,
                        'content': chunk_content,
                        'start_line': line_num - len(current_chunk) + 1,
                        'end_line': line_num,
                        'file_path': file_path
                    })
                    
                    chunk_num += 1
                    current_chunk = []
                    current_size = 0
        
        return chunks
    
    def index_repository(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Index an entire repository's code files"""
        repo_name = repo_data.get('repo_name', '')
        repo_url = repo_data.get('github_url', '')
        files = repo_data.get('files', [])
        
        indexed_count = 0
        total_chunks = 0
        
        with self.SessionLocal() as session:
            # First, clear existing embeddings for this repository
            session.query(CodeEmbedding).filter(CodeEmbedding.repo_name == repo_name).delete()
            session.commit()
            
            for file_info in files:
                file_path = file_info.get('path', '')
                content = file_info.get('content', '')
                language = file_info.get('language', 'unknown')
                
                # Skip binary files and very large files
                if not content or len(content) > 100000:
                    continue
                    
                # Chunk the file content
                chunks = self.chunk_code_file(content, file_path)
                
                # Batch process chunks for this file
                chunk_contents = [chunk['content'] for chunk in chunks]
                try:
                    # Generate all embeddings for this file at once
                    start_time = time.time()
                    all_embeddings = self.embedding_model.encode(chunk_contents, show_progress_bar=False)
                    batch_time = time.time() - start_time
                    print(f"⚡ Generated {len(chunks)} embeddings in {batch_time:.2f}s ({len(chunks)/batch_time:.1f} chunks/sec)")
                    
                    # Create all embedding records
                    for chunk, embedding in zip(chunks, all_embeddings):
                        try:
                            # Prepare metadata
                            metadata = {
                                'language': language,
                                'start_line': chunk['start_line'],
                                'end_line': chunk['end_line'],
                                'chunk_size': len(chunk['content']),
                                'file_size': len(content)
                            }
                            
                            # Create embedding record
                            code_embedding = CodeEmbedding(
                                repo_name=repo_name,
                                repo_url=repo_url,
                                file_path=file_path,
                                chunk_id=chunk['chunk_id'],
                                content=chunk['content'],
                                embedding=embedding.tolist(),  # Convert numpy array to list
                                chunk_metadata=json.dumps(metadata)
                            )
                            
                            session.add(code_embedding)
                            total_chunks += 1
                            
                        except Exception as e:
                            print(f"❌ Error creating record for chunk {chunk['chunk_id']}: {e}")
                            continue
                            
                except Exception as e:
                    print(f"❌ Error batch processing file {file_path}: {e}")
                    continue
                
                indexed_count += 1
            
            # Commit all changes
            session.commit()
        
        print(f"✅ Successfully indexed {indexed_count} files, {total_chunks} chunks")
        return {
            'success': True,
            'indexed_files': indexed_count,
            'total_chunks': total_chunks,
            'repo_name': repo_name
        }
    
    def clear_repository_embeddings(self, repo_name: str):
        """Clear all embeddings for a specific repository"""
        with self.SessionLocal() as session:
            session.query(CodeEmbedding).filter(CodeEmbedding.repo_name == repo_name).delete()
            session.commit()
    
    def vector_search(self, query: str, repo_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Perform vector similarity search using TiDB vector functions"""
        try:
            start_time = time.time()
            query_embedding = self.embed_text(query)
            embed_time = time.time() - start_time
            
            search_start = time.time()
            with self.SessionLocal() as session:
                # Use TiDB's cosine distance function
                results = session.query(
                    CodeEmbedding,
                    CodeEmbedding.embedding.cosine_distance(query_embedding).label('distance')
                ).filter(
                    CodeEmbedding.repo_name == repo_name
                ).order_by('distance').limit(limit).all()
                
                formatted_results = []
                for embedding, distance in results:
                    # Truncate content for faster processing
                    content = embedding.content
                    if len(content) > 1000:
                        content = content[:1000] + "..."
                    
                    formatted_results.append({
                        'file_path': embedding.file_path,
                        'chunk_id': embedding.chunk_id,
                        'content': content,
                        'full_content': embedding.content,  # Keep full content for RAG
                        'metadata': json.loads(embedding.chunk_metadata) if embedding.chunk_metadata else {},
                        'similarity_score': 1.0 - distance  # Convert distance to similarity
                    })
            
            search_time = time.time() - search_start
            total_time = time.time() - start_time
            print(f"⚡ Vector search: embed={embed_time:.2f}s, search={search_time:.2f}s, total={total_time:.2f}s")
            
            return formatted_results
                
        except Exception as e:
            print(f"❌ Vector search error: {e}")
            return []
    
    def fulltext_search(self, query: str, repo_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Perform full-text search on code content"""
        try:
            with self.SessionLocal() as session:
                # Use LIKE for simple text search (can be enhanced with FULLTEXT if needed)
                results = session.query(CodeEmbedding).filter(
                    CodeEmbedding.repo_name == repo_name,
                    CodeEmbedding.content.contains(query)
                ).limit(limit).all()
                
                formatted_results = []
                for embedding in results:
                    formatted_results.append({
                        'file_path': embedding.file_path,
                        'chunk_id': embedding.chunk_id,
                        'content': embedding.content,
                        'metadata': json.loads(embedding.chunk_metadata) if embedding.chunk_metadata else {},
                        'relevance_score': 1.0  # Simple relevance for now
                    })
                
                return formatted_results
                
        except Exception as e:
            print(f"❌ Fulltext search error: {e}")
            return []
    
    def hybrid_search(self, query: str, repo_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Combine vector and full-text search results"""
        # Get results from both search methods
        vector_results = self.vector_search(query, repo_name, limit)
        fulltext_results = self.fulltext_search(query, repo_name, limit)
        
        # Combine and deduplicate results
        combined_results = {}
        
        # Add vector search results
        for result in vector_results:
            key = f"{result['file_path']}:{result['chunk_id']}"
            result['search_type'] = 'vector'
            result['combined_score'] = result['similarity_score']
            combined_results[key] = result
        
        # Add fulltext search results
        for result in fulltext_results:
            key = f"{result['file_path']}:{result['chunk_id']}"
            if key in combined_results:
                # Boost score for items found in both searches
                combined_results[key]['combined_score'] = (
                    combined_results[key]['similarity_score'] + 
                    (result['relevance_score'] / 10.0)  # Normalize fulltext score
                ) / 2
                combined_results[key]['search_type'] = 'hybrid'
            else:
                result['search_type'] = 'fulltext'
                result['combined_score'] = result['relevance_score'] / 10.0
                combined_results[key] = result
        
        # Sort by combined score and return top results
        sorted_results = sorted(
            combined_results.values(), 
            key=lambda x: x['combined_score'], 
            reverse=True
        )
        
        return sorted_results[:limit]
    
    def get_repository_stats(self, repo_name: str) -> Dict[str, Any]:
        """Get statistics about indexed repository"""
        try:
            with self.SessionLocal() as session:
                total_chunks = session.query(CodeEmbedding).filter(
                    CodeEmbedding.repo_name == repo_name
                ).count()
                
                total_files = session.query(CodeEmbedding.file_path).filter(
                    CodeEmbedding.repo_name == repo_name
                ).distinct().count()
                
                return {
                    'total_chunks': total_chunks,
                    'total_files': total_files,
                    'avg_chunk_size': 0  # Can be calculated if needed
                }
        except Exception as e:
            print(f"❌ Stats query error: {e}")
            return {'total_chunks': 0, 'total_files': 0, 'avg_chunk_size': 0}