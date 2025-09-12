"""RAG Query Tool for Code Question Answering"""

from typing import Dict, List, Any, Optional
from langchain.tools import BaseTool
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
from .code_indexer import CodeSearchTool


class RAGQueryInput(BaseModel):
    question: str = Field(description="Question about the codebase")
    repo_name: str = Field(description="Repository name to query")
    user_level: str = Field(default="intermediate", description="User experience level")
    llm: Optional[Any] = Field(default=None, description="Language model for answering")


class RAGQueryTool(BaseTool):
    """Tool for answering questions about code using RAG (Retrieval-Augmented Generation)"""
    
    name: str = "rag_query"
    description: str = "Answer questions about repository code using retrieval-augmented generation"
    args_schema: type[BaseModel] = RAGQueryInput
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._code_search_tool = CodeSearchTool()
    
    def _run(self, question: str, repo_name: str, user_level: str = "intermediate", llm: Optional[Any] = None) -> Dict[str, Any]:
        """Answer a question about the codebase using RAG"""
        try:
            # Step 1: Search for relevant code chunks
            search_result = self._code_search_tool._run(
                query=question,
                repo_name=repo_name,
                search_type="hybrid",
                limit=8
            )
            
            if not search_result['success']:
                return {
                    "success": False,
                    "error": f"Failed to search code: {search_result['error']}",
                    "answer": None
                }
            
            relevant_chunks = search_result['results']
            
            if not relevant_chunks:
                return {
                    "success": True,
                    "answer": "I couldn't find any relevant code for your question. The repository might not be indexed yet or your question might be too specific.",
                    "sources": [],
                    "search_results": []
                }
            
            # Step 2: Prepare context from retrieved chunks
            context_parts = []
            sources = []
            
            for i, chunk in enumerate(relevant_chunks[:5]):  # Use top 5 chunks
                file_path = chunk['file_path']
                content = chunk['full_content']
                metadata = chunk.get('metadata', {})
                
                context_parts.append(f"""
File: {file_path}
Lines: {metadata.get('start_line', '?')}-{metadata.get('end_line', '?')}
Language: {metadata.get('language', 'unknown')}
Content:
```
{content}
```
""")
                
                sources.append({
                    'file_path': file_path,
                    'lines': f"{metadata.get('start_line', '?')}-{metadata.get('end_line', '?')}",
                    'language': metadata.get('language', 'unknown'),
                    'similarity_score': chunk.get('combined_score', chunk.get('similarity_score', 0))
                })
            
            context = "\n".join(context_parts)
            
            # Step 3: Generate answer using LLM
            if not llm:
                # Fallback response without LLM
                return {
                    "success": True,
                    "answer": f"I found {len(relevant_chunks)} relevant code sections, but I need an LLM connection to provide a detailed analysis. Here are the most relevant files: {', '.join([chunk['file_path'] for chunk in relevant_chunks[:3]])}",
                    "sources": sources,
                    "search_results": relevant_chunks,
                    "fallback_mode": True
                }
            
            # Create prompt based on user level
            system_prompts = {
                "beginner": """You are a helpful coding tutor explaining code to beginners. 
Use simple language, explain concepts clearly, and provide step-by-step explanations.
Avoid complex jargon and include examples when helpful.""",
                
                "intermediate": """You are a knowledgeable software developer helping another developer.
Provide clear, technical explanations with good detail about how the code works.
Include relevant patterns, best practices, and potential improvements.""",
                
                "advanced": """You are a senior software architect providing detailed technical analysis.
Focus on design patterns, architecture decisions, performance considerations, 
and advanced concepts. Be concise but comprehensive."""
            }
            
            system_prompt = system_prompts.get(user_level, system_prompts["intermediate"])
            
            user_prompt = f"""Based on the following code from the repository "{repo_name}", please answer this question:

QUESTION: {question}

RELEVANT CODE CONTEXT:
{context}

Please provide a clear, helpful answer based on the code above. If the code doesn't fully answer the question, acknowledge what's missing and provide your best guidance based on what is available.

Include references to specific files and line numbers when relevant.
"""

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            # Get response from LLM
            try:
                if hasattr(llm, 'invoke'):
                    response = llm.invoke(messages)
                    answer = response.content if hasattr(response, 'content') else str(response)
                else:
                    # Try direct call
                    answer = llm(user_prompt)
                
                return {
                    "success": True,
                    "answer": answer,
                    "sources": sources,
                    "search_results": relevant_chunks,
                    "context_used": len(context_parts),
                    "user_level": user_level
                }
                
            except Exception as e:
                print(f"❌ LLM error: {e}")
                return {
                    "success": True,
                    "answer": f"I found relevant code sections but encountered an error with the AI model. Based on the code I found in {', '.join([chunk['file_path'] for chunk in relevant_chunks[:3]])}, you can examine these files for more details about your question.",
                    "sources": sources,
                    "search_results": relevant_chunks,
                    "llm_error": str(e)
                }
        
        except Exception as e:
            print(f"❌ RAG query error: {e}")
            return {
                "success": False,
                "error": f"RAG query failed: {str(e)}",
                "answer": None
            }
    
    async def _arun(self, question: str, repo_name: str, user_level: str = "intermediate", llm: Optional[Any] = None) -> Dict[str, Any]:
        """Async version of the tool"""
        return self._run(question, repo_name, user_level, llm)


class CodeQuestionInput(BaseModel):
    question: str = Field(description="Question about the code")
    repo_name: str = Field(description="Repository name")
    user_level: str = Field(default="intermediate", description="User experience level")


class CodeQuestionTool(BaseTool):
    """Simplified tool for asking questions about code"""
    
    name: str = "code_question"
    description: str = "Ask questions about repository code and get AI-powered answers"
    args_schema: type[BaseModel] = CodeQuestionInput
    
    def __init__(self, llm=None, **kwargs):
        super().__init__(**kwargs)
        self._rag_tool = RAGQueryTool()
        self._llm = llm
    
    def _run(self, question: str, repo_name: str, user_level: str = "intermediate") -> Dict[str, Any]:
        """Ask a question about the code"""
        return self._rag_tool._run(question, repo_name, user_level, self._llm)
    
    async def _arun(self, question: str, repo_name: str, user_level: str = "intermediate") -> Dict[str, Any]:
        """Async version"""
        return self._run(question, repo_name, user_level)