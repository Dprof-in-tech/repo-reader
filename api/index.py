import os
import json
import threading
import queue
from flask import Flask, request, jsonify, Response, stream_template
from flask_cors import CORS
from agent import RepoAnalysisAgent

app = Flask(__name__)
CORS(app)

# Initialize the LangGraph agent
agent = RepoAnalysisAgent()

# Global dictionary to store progress streams
progress_streams = {}

@app.route("/api/health")
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "repo-analysis-agent"})

@app.route("/api/analyze", methods=["POST"])
def analyze_repository():
    """Analyze a GitHub repository and generate walkthrough"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        github_url = data.get("github_url")
        if not github_url:
            return jsonify({"error": "github_url is required"}), 400
        
        user_level = data.get("user_level", "beginner")
        stream = data.get("stream", False)
        
        # Validate user level
        valid_levels = ["beginner", "intermediate", "advanced"]
        if user_level not in valid_levels:
            return jsonify({
                "error": f"Invalid user_level. Must be one of: {', '.join(valid_levels)}"
            }), 400
        
        if stream:
            # Return a task ID for streaming
            import uuid
            task_id = str(uuid.uuid4())
            
            # Start analysis in background thread
            def run_analysis():
                result = agent.analyze_repository(github_url, user_level, progress_streams[task_id])
                progress_streams[task_id]['final_result'] = result
                progress_streams[task_id]['completed'] = True
            
            # Initialize progress stream
            progress_streams[task_id] = {
                'messages': [],
                'completed': False,
                'final_result': None
            }
            
            thread = threading.Thread(target=run_analysis)
            thread.daemon = True
            thread.start()
            
            return jsonify({
                "task_id": task_id,
                "stream_url": f"/api/analyze/stream/{task_id}",
                "status": "started"
            }), 202
        else:
            # Run the agent analysis synchronously
            result = agent.analyze_repository(github_url, user_level)
            
            if not result.get("success"):
                return jsonify({
                    "error": result.get("error", "Analysis failed"),
                    "current_step": result.get("current_step")
                }), 500
            
            return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/api/analyze/stream/<task_id>")
def stream_analysis_progress(task_id):
    """Stream analysis progress via Server-Sent Events"""
    def generate():
        if task_id not in progress_streams:
            yield f"data: {json.dumps({'error': 'Task not found'})}\n\n"
            return
            
        stream_data = progress_streams[task_id]
        sent_count = 0
        
        while not stream_data['completed']:
            # Send new messages
            messages = stream_data['messages']
            while sent_count < len(messages):
                message = messages[sent_count]
                yield f"data: {json.dumps({'type': 'progress', 'message': message})}\n\n"
                sent_count += 1
            
            # Short delay to prevent busy waiting
            import time
            time.sleep(0.1)
        
        # Send any remaining messages
        messages = stream_data['messages']
        while sent_count < len(messages):
            message = messages[sent_count]
            yield f"data: {json.dumps({'type': 'progress', 'message': message})}\n\n"
            sent_count += 1
        
        # Send final result
        final_result = stream_data['final_result']
        yield f"data: {json.dumps({'type': 'complete', 'result': final_result})}\n\n"
        
        # Cleanup
        del progress_streams[task_id]
    
    return Response(generate(), mimetype='text/event-stream',
                   headers={'Cache-Control': 'no-cache', 
                           'Connection': 'keep-alive',
                           'Access-Control-Allow-Origin': '*'})

@app.route("/api/status")
def get_agent_status():
    """Get agent workflow status and capabilities"""
    try:
        status = agent.get_workflow_status()
        return jsonify(status), 200
    except Exception as e:
        return jsonify({"error": f"Status error: {str(e)}"}), 500

@app.route("/api/demo", methods=["GET"])
def demo_walkthrough():
    """Demo endpoint with sample walkthrough data"""
    sample_walkthrough = {
        "title": "🎮 Code Quest: Sample Repository",
        "description": "🚀 Welcome, Code Explorer! This is a demo walkthrough.",
        "difficulty_level": {
            "level": "Beginner",
            "stars": "⭐",
            "complexity_score": 25
        },
        "estimated_completion_time": "45 minutes",
        "achievements": [
            {
                "id": "first_steps",
                "title": "🚀 First Steps",
                "description": "Started your code exploration journey",
                "points": 100,
                "unlocked": True
            }
        ],
        "learning_modules": [
            {
                "id": "module_1",
                "title": "📚 Repository Overview",
                "description": "Understand the overall project structure",
                "difficulty": "Beginner",
                "estimated_time": "15 minutes",
                "unlocked": True
            }
        ],
        "progress_tracking": {
            "total_points": 0,
            "current_level": 1,
            "progress_percentage": 0
        }
    }
    
    return jsonify({
        "success": True,
        "walkthrough_data": sample_walkthrough,
        "demo": True
    }), 200

@app.route("/api/llm-status")
def llm_status():
    """Get current LLM status and configuration"""
    try:
        if hasattr(agent, 'llm') and agent.llm and hasattr(agent.llm, 'get_status'):
            status = agent.llm.get_status()
            return jsonify(status)
        else:
            return jsonify({
                "local_model": {"available": False, "type": None},
                "cloud_model": {"available": False, "type": None},
                "has_fallback": False,
                "mode": "static_fallback"
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/llm-test", methods=["POST"])
def test_llm():
    """Test LLM functionality with a simple prompt"""
    try:
        data = request.get_json() or {}
        test_prompt = data.get("prompt", "Hello, can you help with code analysis?")
        prefer_local = data.get("prefer_local", True)
        
        if hasattr(agent, 'llm') and agent.llm and hasattr(agent.llm, 'invoke'):
            from langchain_core.messages import HumanMessage
            
            messages = [HumanMessage(content=test_prompt)]
            response = agent.llm.invoke(messages, prefer_local=prefer_local)
            
            if response and hasattr(response, 'content'):
                return jsonify({
                    "success": True,
                    "response": response.content[:200] + "..." if len(response.content) > 200 else response.content,
                    "model_used": "local" if prefer_local else "cloud"
                })
            else:
                return jsonify({"success": False, "error": "No response from LLM"})
        else:
            return jsonify({"success": False, "error": "LLM not available"})
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/ask", methods=["POST"])
def ask_code_question():
    """Ask a question about repository code using RAG"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        question = data.get("question")
        repo_name = data.get("repo_name")
        user_level = data.get("user_level", "intermediate")
        stream = data.get("stream", False)
        
        if not question:
            return jsonify({"error": "question is required"}), 400
        
        if not repo_name:
            return jsonify({"error": "repo_name is required"}), 400
        
        if stream:
            # Return streaming response for long queries
            def generate_response():
                import json
                import time
                
                # Send progress update
                yield f"data: {json.dumps({'type': 'progress', 'message': '🔍 Searching for relevant code...'})}\n\n"
                time.sleep(0.1)
                
                # Use the agent's RAG functionality
                result = agent.ask_code_question(question, repo_name, user_level)
                
                # Send final result
                yield f"data: {json.dumps({'type': 'complete', 'result': result})}\n\n"
            
            return Response(generate_response(), mimetype='text/event-stream',
                          headers={'Cache-Control': 'no-cache', 
                                 'Connection': 'keep-alive',
                                 'Access-Control-Allow-Origin': '*'})
        else:
            # Use the agent's RAG functionality
            result = agent.ask_code_question(question, repo_name, user_level)
            
            if result.get("success"):
                return jsonify(result), 200
            else:
                return jsonify(result), 500
            
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/api/search", methods=["POST"])
def search_code():
    """Search repository code using vector/full-text search"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        query = data.get("query")
        repo_name = data.get("repo_name")
        search_type = data.get("search_type", "hybrid")
        limit = data.get("limit", 5)
        
        if not query:
            return jsonify({"error": "query is required"}), 400
        
        if not repo_name:
            return jsonify({"error": "repo_name is required"}), 400
        
        # Validate search type
        valid_types = ["vector", "fulltext", "hybrid"]
        if search_type not in valid_types:
            return jsonify({
                "error": f"Invalid search_type. Must be one of: {', '.join(valid_types)}"
            }), 400
        
        # Use the agent's search functionality
        result = agent.search_code(query, repo_name, search_type, limit)
        
        if result.get("success"):
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5328)