"""LangGraph Agent for Repository Analysis and Walkthrough Generation"""

import os
from typing import Dict, Any, TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# Import our custom tools
from tools.repo_reader import RepoReaderTool
from tools.code_analyzer import CodeAnalyzerTool
from tools.walkthrough_generator import WalkthroughGeneratorTool
from tools.code_indexer import CodeIndexerTool, CodeSearchTool
from tools.rag_query_tool import RAGQueryTool, CodeQuestionTool
from llm_manager import HybridLLMManager


class AgentState(TypedDict):
    """State for the LangGraph agent"""
    github_url: str
    user_level: str
    repo_data: Dict[str, Any]
    analysis_data: Dict[str, Any]
    walkthrough_data: Dict[str, Any]
    indexing_data: Dict[str, Any]  # New: TiDB indexing results
    current_step: str
    error: str
    messages: List[Dict[str, str]]


class RepoAnalysisAgent:
    """Single LangGraph agent that orchestrates repository analysis"""
    
    def __init__(self, 
                 openai_api_key: str = None, 
                 local_model_path: str = None,
                 local_model_config: Dict[str, Any] = None):
        """Initialize the agent with hybrid LLM support"""
        
        # Initialize hybrid LLM manager
        self.llm = HybridLLMManager(
            local_model_path=local_model_path or os.getenv("CHATGPT_OSS_MODEL_PATH"),
            openai_api_key=openai_api_key,
            local_model_config=local_model_config
        )
        
        # Log LLM status
        status = self.llm.get_status()
        print(f"LLM Status: Local={status['local_model']['available']}, Cloud={status['cloud_model']['available']}")
        
        # Keep legacy compatibility - if no models available, set to None
        if not (status['local_model']['available'] or status['cloud_model']['available']):
            print("WARNING: No LLM models available - running in fallback mode")
            self.llm = None
        
        # Initialize tools
        self.tools = [
            RepoReaderTool(),
            CodeAnalyzerTool(),
            WalkthroughGeneratorTool(),
            CodeIndexerTool(),
            CodeSearchTool()
        ]
        
        # Initialize RAG tools with LLM
        self.rag_tool = RAGQueryTool()
        self.code_question_tool = CodeQuestionTool(llm=self.llm)
        
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("coordinator", self._coordinator_node)
        workflow.add_node("repo_reader", self._repo_reader_node)
        workflow.add_node("code_indexer", self._code_indexer_node)  # New: TiDB indexing
        workflow.add_node("code_analyzer", self._code_analyzer_node)
        workflow.add_node("walkthrough_generator", self._walkthrough_generator_node)
        workflow.add_node("finalizer", self._finalizer_node)
        
        # Define the flow - now includes indexing step
        workflow.add_edge("coordinator", "repo_reader")
        workflow.add_edge("repo_reader", "code_indexer")  # Index after reading
        workflow.add_edge("code_indexer", "code_analyzer")
        workflow.add_edge("code_analyzer", "walkthrough_generator")
        workflow.add_edge("walkthrough_generator", "finalizer")
        workflow.add_edge("finalizer", END)
        
        # Set entry point
        workflow.set_entry_point("coordinator")
        
        return workflow.compile()
    
    def _coordinator_node(self, state: AgentState) -> AgentState:
        """Coordinate the overall process and validate inputs"""
        
        try:
            # Validate GitHub URL
            github_url = state.get("github_url", "")
            if not github_url or "github.com" not in github_url:
                state["error"] = "Invalid GitHub URL provided"
                return state
            
            # Set default user level if not provided
            if not state.get("user_level"):
                state["user_level"] = "beginner"
            
            # Initialize workflow state
            state["current_step"] = "repository_reading"
            state["messages"] = [
                {"role": "system", "content": "Starting repository analysis workflow"}
            ]
            
            return state
            
        except Exception as e:
            state["error"] = f"Coordination failed: {str(e)}"
            return state
    
    def _repo_reader_node(self, state: AgentState) -> AgentState:
        """Read and extract repository data"""
        
        def progress_callback(message):
            """Callback to track progress and add to state messages"""
            state["messages"].append({
                "role": "system",
                "content": message
            })
            # print(f"CLONE PROGRESS: {message}")
            
            # Add to progress stream if available
            if hasattr(self, '_progress_stream') and self._progress_stream:
                self._progress_stream['messages'].append({
                    "role": "system",
                    "content": message,
                    "timestamp": __import__('time').time()
                })
        
        try:
            repo_reader = RepoReaderTool()
            result = repo_reader._run(
                github_url=state["github_url"],
                max_files=50,
                progress_callback=progress_callback
            )
            
            if "error" in result:
                state["error"] = result["error"]
                return state
            
            state["repo_data"] = result
            state["current_step"] = "code_analysis"
            state["messages"].append({
                "role": "assistant", 
                "content": f"Successfully read repository: {result.get('repo_name', 'Unknown')}"
            })
            
            return state
            
        except Exception as e:
            state["error"] = f"Repository reading failed: {str(e)}"
            return state
    
    def _code_indexer_node(self, state: AgentState) -> AgentState:
        """Index repository code into TiDB vector store"""
        
        try:
            if not state.get("repo_data"):
                state["error"] = "No repository data available for indexing"
                state["current_step"] = "indexing_failed"
                return state
            
            # Add progress message
            state["messages"].append({
                "role": "assistant",
                "content": "🗄️ Indexing code into TiDB vector store for semantic search..."
            })
            
            # Get the indexer tool and index the repository
            code_indexer = CodeIndexerTool()
            result = code_indexer._run(
                repo_data=state["repo_data"],
                force_reindex=False  # Don't reindex if already exists
            )
            
            state["indexing_data"] = result
            
            if result.get("success"):
                indexed_files = result.get("indexed_files", 0)
                total_chunks = result.get("total_chunks", 0)
                
                state["current_step"] = "code_analysis"
                state["messages"].append({
                    "role": "assistant",
                    "content": f"✅ Successfully indexed {indexed_files} files ({total_chunks} chunks) for semantic search"
                })
            else:
                # Continue even if indexing fails - it's not critical for basic functionality
                error_msg = result.get("error", "Unknown indexing error")
                print(f"⚠️ Indexing failed but continuing: {error_msg}")
                
                state["indexing_data"] = {"success": False, "error": error_msg}
                state["current_step"] = "code_analysis"
                state["messages"].append({
                    "role": "assistant", 
                    "content": "⚠️ Code indexing unavailable - continuing with basic analysis"
                })
            
            return state
            
        except Exception as e:
            # Don't fail the entire process if indexing fails
            print(f"⚠️ Indexing error but continuing: {e}")
            state["indexing_data"] = {"success": False, "error": str(e)}
            state["current_step"] = "code_analysis"
            state["messages"].append({
                "role": "assistant",
                "content": "⚠️ Code indexing encountered an error - continuing with basic analysis"
            })
            return state
    
    def _code_analyzer_node(self, state: AgentState) -> AgentState:
        """Analyze the code structure and patterns"""
        
        try:
            if not state.get("repo_data"):
                state["error"] = "No repository data available for analysis"
                state["current_step"] = "code_analysis_failed"
                return state
            
            code_analyzer = CodeAnalyzerTool()
            result = code_analyzer._run(repo_data=state["repo_data"], llm=self.llm)
            
            if "error" in result:
                state["error"] = result["error"]
                state["current_step"] = "code_analysis_failed"
                return state
            
            state["analysis_data"] = result
            state["current_step"] = "walkthrough_generation"
            state["messages"].append({
                "role": "assistant",
                "content": f"Code analysis completed. Detected: {result.get('architecture_pattern', 'Unknown')} architecture"
            })
            
            return state
            
        except Exception as e:
            state["error"] = f"Code analysis failed: {str(e)}"
            state["current_step"] = "code_analysis_failed"
            return state
    
    def _walkthrough_generator_node(self, state: AgentState) -> AgentState:
        """Generate the gamified walkthrough"""
        
        try:
            if not state.get("repo_data") or not state.get("analysis_data"):
                state["error"] = "Missing required data for walkthrough generation"
                state["current_step"] = "walkthrough_generation_failed"
                return state
            
            walkthrough_generator = WalkthroughGeneratorTool()
            result = walkthrough_generator._run(
                repo_data=state["repo_data"],
                analysis_data=state["analysis_data"],
                user_level=state.get("user_level", "beginner"),
                llm=self.llm
            )
            
            if "error" in result:
                state["error"] = result["error"]
                state["current_step"] = "walkthrough_generation_failed"
                return state
            
            state["walkthrough_data"] = result
            state["current_step"] = "finalization"
            state["messages"].append({
                "role": "assistant",
                "content": f"Generated gamified walkthrough: {result.get('title', 'Code Quest')}"
            })
            
            return state
            
        except Exception as e:
            state["error"] = f"Walkthrough generation failed: {str(e)}"
            state["current_step"] = "walkthrough_generation_failed"
            return state
    
    def _finalizer_node(self, state: AgentState) -> AgentState:
        """Finalize and prepare the response"""
        
        try:
            if state.get("error"):
                return state
            
            # Create final response summary
            repo_name = state["repo_data"].get("repo_name", "Unknown Repository")
            architecture = state["analysis_data"].get("architecture_pattern", "Unknown")
            modules_count = len(state["walkthrough_data"].get("learning_modules", []))
            
            state["current_step"] = "completed"
            state["messages"].append({
                "role": "assistant",
                "content": f"✅ Successfully generated walkthrough for {repo_name} ({architecture} architecture) with {modules_count} learning modules"
            })
            
            return state
            
        except Exception as e:
            state["error"] = f"Finalization failed: {str(e)}"
            return state
    
    def analyze_repository(self, github_url: str, user_level: str = "beginner", progress_stream=None) -> Dict[str, Any]:
        """Main method to analyze a repository and generate walkthrough"""
        
        try:
            # Initialize state
            initial_state = AgentState(
                github_url=github_url,
                user_level=user_level,
                repo_data={},
                analysis_data={},
                walkthrough_data={},
                indexing_data={},
                current_step="initialization",
                error="",
                messages=[]
            )
            
            # Store progress stream reference for callbacks
            self._progress_stream = progress_stream
            
            # Run the workflow
            final_state = self.workflow.invoke(initial_state)
            
            # Check for errors
            if final_state.get("error"):
                return {
                    "success": False,
                    "error": final_state["error"],
                    "current_step": final_state.get("current_step", "unknown")
                }
            
            # Return successful result only if we have all required data
            repo_data = final_state.get("repo_data", {})
            analysis_data = final_state.get("analysis_data", {})
            walkthrough_data = final_state.get("walkthrough_data", {})
            
            # Verify we have the essential data for a successful analysis
            if not repo_data or not analysis_data or not walkthrough_data:
                missing_components = []
                if not repo_data:
                    missing_components.append("repository data")
                if not analysis_data:
                    missing_components.append("code analysis")
                if not walkthrough_data:
                    missing_components.append("walkthrough generation")
                
                return {
                    "success": False,
                    "error": f"Incomplete analysis - missing: {', '.join(missing_components)}",
                    "current_step": final_state.get("current_step", "unknown")
                }
            
            return {
                "success": True,
                "repo_data": repo_data,
                "analysis_data": analysis_data,
                "walkthrough_data": walkthrough_data,
                "messages": final_state.get("messages", []),
                "processing_summary": {
                    "repository": repo_data.get("repo_name", "Unknown"),
                    "architecture": analysis_data.get("architecture_pattern", "Unknown"),
                    "complexity_score": analysis_data.get("complexity_score", 0),
                    "learning_modules": len(walkthrough_data.get("learning_modules", [])),
                    "estimated_time": walkthrough_data.get("estimated_completion_time", "Unknown")
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Agent execution failed: {str(e)}",
                "current_step": "agent_error"
            }
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get information about the workflow and available tools"""
        return {
            "agent_type": "Repository Analysis Agent",
            "framework": "LangGraph",
            "tools_available": [tool.name for tool in self.tools],
            "workflow_steps": [
                "coordinator",
                "repo_reader",
                "code_indexer", 
                "code_analyzer",
                "walkthrough_generator",
                "finalizer"
            ],
            "supported_features": [
                "GitHub repository cloning",
                "Code structure analysis",
                "Architecture pattern detection", 
                "TiDB vector indexing",
                "Semantic code search",
                "RAG-powered code questions",
                "Gamified walkthrough generation",
                "Progress tracking",
                "Interactive learning modules"
            ]
        }
    
    def ask_code_question(self, question: str, repo_name: str, user_level: str = "intermediate") -> Dict[str, Any]:
        """Ask a question about the indexed repository code using RAG"""
        try:
            # Use the RAG query tool to answer the question
            result = self.rag_tool._run(
                question=question,
                repo_name=repo_name,
                user_level=user_level,
                llm=self.llm
            )
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to answer code question: {str(e)}",
                "answer": None
            }
    
    def search_code(self, query: str, repo_name: str, search_type: str = "hybrid", limit: int = 5) -> Dict[str, Any]:
        """Search for code using vector and/or full-text search"""
        try:
            code_search_tool = CodeSearchTool()
            result = code_search_tool._run(
                query=query,
                repo_name=repo_name, 
                search_type=search_type,
                limit=limit
            )
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Code search failed: {str(e)}",
                "results": []
            }