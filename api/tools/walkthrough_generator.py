"""Gamified Walkthrough Generation Tool"""

from typing import Dict, List, Any, Optional
from langchain.tools import BaseTool
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
import random
import json
import concurrent.futures
import asyncio
from .codebase_quiz_generator import CodebaseQuizGenerator


class WalkthroughGeneratorInput(BaseModel):
    repo_data: Dict[str, Any] = Field(description="Repository data from repo_reader tool")
    analysis_data: Dict[str, Any] = Field(description="Analysis data from code_analyzer tool")
    user_level: str = Field(default="beginner", description="User experience level: beginner, intermediate, advanced")
    llm: Optional[Any] = Field(default=None, description="Language model for dynamic content generation")


class WalkthroughGeneratorTool(BaseTool):
    name: str = "walkthrough_generator"  
    description: str = "Generates gamified, interactive walkthroughs for understanding codebases"
    args_schema: type[BaseModel] = WalkthroughGeneratorInput

    def _run(self, repo_data: Dict[str, Any], analysis_data: Dict[str, Any], user_level: str = "beginner", llm: Optional[Any] = None) -> Dict[str, Any]:
        """Generate a gamified walkthrough based on repository analysis"""
        try:
            walkthrough = {
                "title": f"🎮 Code Quest: {repo_data.get('repo_name', 'Unknown Repository')}",
                "description": self._generate_quest_description(repo_data, analysis_data),
                "difficulty_level": self._calculate_difficulty(analysis_data, user_level),
                "estimated_completion_time": self._estimate_completion_time(analysis_data),
                "achievements": self._generate_achievements(repo_data, analysis_data),
                "learning_modules": self._create_learning_modules(repo_data, analysis_data, user_level, llm),
                "progress_tracking": self._create_progress_system(),
                "interactive_elements": self._create_interactive_elements(repo_data, analysis_data),
                "gamification_elements": self._create_gamification_elements()
            }
            
            return walkthrough
            
        except Exception as e:
            return {"error": f"Walkthrough generation failed: {str(e)}"}

    def _generate_quest_description(self, repo_data: Dict[str, Any], analysis_data: Dict[str, Any]) -> str:
        """Generate an engaging quest description"""
        frameworks = repo_data.get('frameworks', [])
        languages = repo_data.get('languages', [])
        architecture = analysis_data.get('architecture_pattern', 'Unknown')
        key_components = analysis_data.get('key_components', [])
        complexity_score = analysis_data.get('complexity_score', 0)
        
        framework_text = f" built with {', '.join(frameworks)}" if frameworks else ""
        language_text = f" using {', '.join(languages)}" if languages else ""
        
        # Dynamic difficulty messaging
        difficulty_msg = ""
        if complexity_score > 70:
            difficulty_msg = " This is an advanced quest that will challenge even experienced developers!"
        elif complexity_score > 40:
            difficulty_msg = " This intermediate-level adventure will expand your coding knowledge!"
        else:
            difficulty_msg = " Perfect for developers ready to learn new concepts!"
        
        # Dynamic component messaging
        component_msg = ""
        if len(key_components) > 10:
            component_msg = f" Explore {len(key_components)} interconnected components in this complex system."
        elif len(key_components) > 5:
            component_msg = f" Navigate through {len(key_components)} well-structured components."
        else:
            component_msg = f" Master {len(key_components)} core components."
        
        descriptions = [
            f"🚀 Welcome, Code Explorer! You're about to embark on an exciting journey through a {architecture} codebase{framework_text}{language_text}.{difficulty_msg}",
            f"⚔️ Prepare to unravel the mysteries of this {architecture} application!{component_msg}{difficulty_msg}",
            f"🗺️ As a digital archaeologist, you'll discover the secrets of this {architecture} system{language_text}, learning how {len(repo_data.get('files', []))} files work together.{difficulty_msg}"
        ]
        
        return random.choice(descriptions)

    def _calculate_difficulty(self, analysis_data: Dict[str, Any], user_level: str) -> Dict[str, Any]:
        """Calculate difficulty based on complexity and user level"""
        complexity_score = analysis_data.get('complexity_score', 0)
        
        # Base difficulty from complexity
        if complexity_score < 25:
            base_difficulty = "Beginner"
        elif complexity_score < 60:
            base_difficulty = "Intermediate"
        else:
            base_difficulty = "Advanced"
        
        # Adjust based on user level
        difficulty_mapping = {
            "beginner": {"Beginner": "⭐", "Intermediate": "⭐⭐", "Advanced": "⭐⭐⭐"},
            "intermediate": {"Beginner": "Easy", "Intermediate": "⭐⭐", "Advanced": "⭐⭐⭐"},
            "advanced": {"Beginner": "Easy", "Intermediate": "Easy", "Advanced": "⭐⭐"}
        }
        
        return {
            "level": base_difficulty,
            "stars": difficulty_mapping[user_level][base_difficulty],
            "complexity_score": complexity_score,
            "user_adjusted": True if user_level != "beginner" else False
        }

    def _estimate_completion_time(self, analysis_data: Dict[str, Any]) -> str:
        """Estimate completion time based on complexity"""
        complexity = analysis_data.get('complexity_score', 0)
        component_count = len(analysis_data.get('key_components', []))
        
        # Base time calculation
        base_time = 30 + (complexity * 2) + (component_count * 5)
        
        if base_time < 60:
            return f"{base_time} minutes"
        else:
            hours = base_time // 60
            minutes = base_time % 60
            return f"{hours}h {minutes}m"

    def _generate_achievements(self, repo_data: Dict[str, Any], analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate gamified achievements"""
        achievements = []
        
        # Base achievements
        achievements.extend([
            {
                "id": "first_steps",
                "title": "🚀 First Steps",
                "description": "Started your code exploration journey",
                "points": 100,
                "unlocked": True
            },
            {
                "id": "architecture_detective",
                "title": "🕵️ Architecture Detective",
                "description": f"Discovered the {analysis_data.get('architecture_pattern', 'Unknown')} pattern",
                "points": 200,
                "unlocked": False
            }
        ])
        
        # Language-specific achievements
        languages = repo_data.get('languages', [])
        for lang in languages[:3]:  # Max 3 language achievements
            achievements.append({
                "id": f"{lang.lower()}_master",
                "title": f"💎 {lang} Master",
                "description": f"Mastered {lang} components in this codebase",
                "points": 250,
                "unlocked": False
            })
        
        # Framework achievements
        frameworks = repo_data.get('frameworks', [])
        for framework in frameworks:
            achievements.append({
                "id": f"{framework.lower().replace('.', '').replace(' ', '_')}_expert",
                "title": f"⚡ {framework} Expert",
                "description": f"Understood {framework} implementation patterns",
                "points": 300,
                "unlocked": False
            })
        
        # Completion achievements
        achievements.extend([
            {
                "id": "component_explorer",
                "title": "🗺️ Component Explorer",
                "description": "Explored all key components",
                "points": 400,
                "unlocked": False
            },
            {
                "id": "code_master",
                "title": "👑 Code Master",
                "description": "Completed the entire walkthrough",
                "points": 500,
                "unlocked": False
            }
        ])
        
        return achievements

    def _create_learning_modules(self, repo_data: Dict[str, Any], analysis_data: Dict[str, Any], user_level: str, llm: Optional[Any] = None) -> List[Dict[str, Any]]:
        """Create structured learning modules"""
        modules = []
        learning_path = analysis_data.get('learning_path', [])
        
        for i, step in enumerate(learning_path):
            activities = self._create_module_activities(step, repo_data, user_level)
            quiz_questions = self._generate_quiz_questions(step, repo_data, llm)
            resources = step.get('focus_files', [])
            
            module = {
                "id": f"module_{i+1}",
                "title": f"📚 {step.get('title', f'Module {i+1}')}",
                "description": step.get('description', ''),
                "difficulty": step.get('difficulty', 'Beginner'),
                "estimated_time": step.get('estimated_time', '15 minutes'),
                "learning_objectives": self._generate_learning_objectives(step, repo_data),
                "activities": activities,
                "quiz": quiz_questions,
                "resources": resources,
                "unlocked": i == 0,  # Only first module unlocked initially
                "completion_criteria": {
                    "read_files": min(len(resources), 3),  # Max 3 files to read
                    "answer_quiz": min(len(quiz_questions), 5),  # All quiz questions
                    "activities_completed": max(1, len(activities))  # At least 1, or all activities
                }
            }
            modules.append(module)
        
        return modules

    def _generate_learning_objectives(self, step: Dict[str, Any], repo_data: Dict[str, Any]) -> List[str]:
        """Generate learning objectives for each module"""
        title = step.get('title', '').lower()
        
        if 'overview' in title:
            return [
                "Understand the overall project structure",
                "Identify key technologies and frameworks used",
                "Recognize architectural patterns employed"
            ]
        elif 'entry' in title:
            return [
                "Locate application entry points",
                "Understand initialization flow",
                "Identify main execution paths"
            ]
        elif 'component' in title:
            return [
                "Analyze core business logic components",
                "Understand component relationships",
                "Identify data flow patterns"
            ]
        elif 'dependencies' in title:
            return [
                "Map external dependencies",
                "Understand integration patterns",
                "Identify potential upgrade paths"
            ]
        else:
            return [
                "Deep dive into advanced concepts",
                "Understand design patterns used",
                "Analyze architectural decisions"
            ]

    def _create_module_activities(self, step: Dict[str, Any], repo_data: Dict[str, Any], user_level: str) -> List[Dict[str, Any]]:
        """Create interactive activities for each module"""
        activities = []
        focus_files = step.get('focus_files', [])
        
        # File exploration activity
        if focus_files:
            activities.append({
                "type": "file_exploration",
                "title": "🔍 Code Detective",
                "description": f"Explore {len(focus_files)} key files and identify main functions/classes",
                "instructions": [
                    "Open each file in the resources list",
                    "Identify the main purpose of each file",
                    "Note any patterns you observe",
                    "Look for connections between files"
                ],
                "expected_discoveries": min(len(focus_files) * 2, 8),
                "points": 50
            })
        
        # Pattern recognition activity
        activities.append({
            "type": "pattern_recognition",
            "title": "🧩 Pattern Hunter",
            "description": "Identify and document architectural patterns",
            "instructions": [
                "Look for repeated code structures",
                "Identify naming conventions",
                "Note error handling patterns",
                "Document any design patterns used"
            ],
            "expected_patterns": 3,
            "points": 75
        })
        
        # Code tracing activity
        if user_level in ["intermediate", "advanced"]:
            activities.append({
                "type": "code_tracing",
                "title": "🏃‍♂️ Flow Tracer",
                "description": "Trace code execution flow through the system",
                "instructions": [
                    "Start from an entry point",
                    "Follow the execution path",
                    "Document key decision points",
                    "Map data transformations"
                ],
                "expected_traces": 2,
                "points": 100
            })
        
        return activities

    def _llm_powered_quiz_generation(self, step: Dict[str, Any], repo_data: Dict[str, Any], llm: Any) -> List[Dict[str, Any]]:
        """Generate dynamic quiz questions using LLM based on actual code content"""
        
        # Get relevant files for this step
        focus_files = step.get('focus_files', [])
        step_title = step.get('title', 'Code Module')
        
        # Extract code snippets from focus files
        code_samples = []
        for file_path in focus_files[:3]:  # Limit to 3 files for context
            file_info = next((f for f in repo_data.get('files', []) if f['path'] == file_path), None)
            if file_info and file_info.get('content'):
                # Get first 500 chars of content
                content = file_info['content'][:500].replace('\n', '\\n')
                code_samples.append(f"{file_path}:\n{content}")
        
        code_context = "\n\n".join(code_samples) if code_samples else "No specific code files available"
        
        prompt = f"""
You are creating quiz questions for a coding walkthrough module titled "{step_title}".

Repository Context:
- Name: {repo_data.get('repo_name', 'Unknown')}
- Languages: {', '.join(repo_data.get('languages', []))}
- Frameworks: {', '.join(repo_data.get('frameworks', []))}

Code Context from this module:
{code_context}

Create 3-4 quiz questions that test understanding of the actual code shown above. Include:
1. Multiple choice questions about specific code patterns or functions
2. True/false questions about the implementation
3. Short answer questions about the code's purpose or behavior

Return ONLY a valid JSON array with this exact structure:
[
  {
    "type": "multiple_choice",
    "question": "Question text here",
    "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
    "correct": 0,
    "explanation": "Explanation of the correct answer"
  },
  {
    "type": "true_false", 
    "question": "Question text here",
    "correct": true,
    "explanation": "Explanation here"
  },
  {
    "type": "short_answer",
    "question": "Question text here",
    "sample_answer": "Sample correct answer",
    "explanation": "What makes this answer correct"
  }
]
"""
        
        try:
            from langchain_core.messages import HumanMessage
            
            response = llm.invoke([HumanMessage(content=prompt)])
            response_text = response.content.strip()
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                questions = json.loads(json_str)
                
                # Validate and sanitize questions
                validated_questions = []
                for q in questions:
                    if self._validate_quiz_question(q):
                        validated_questions.append(q)
                
                if validated_questions:
                    return validated_questions
            
            # LLM response didn't contain valid JSON, falling back
            
        except Exception as e:
            # Error in LLM quiz generation
            pass
        
        # Fallback to contextually appropriate questions based on step content
        focus_files = step.get('focus_files', [])
        
        # Check if this is about config files
        if any(f.endswith('.json') for f in focus_files):
            return [{
                "type": "multiple_choice",
                "question": f"What is the typical role of JSON configuration files in software projects?",
                "options": ["Execute business logic", "Store project settings and dependencies", "Render user interfaces", "Process user input"],
                "correct": 1,
                "explanation": "JSON files like package.json store configuration data, dependencies, and project metadata."
            }]
        
        # Generic fallback with better context
        return [{
            "type": "multiple_choice",
            "question": f"What is the main learning goal for exploring {step_title}?",
            "options": ["Memorizing code syntax", "Understanding system architecture", "Learning keyboard shortcuts", "Installing software"],
            "correct": 1,
            "explanation": "Understanding how different parts of the system work together is key to mastering any codebase."
        }]
    
    def _validate_quiz_question(self, question: Dict[str, Any]) -> bool:
        """Validate that a quiz question has the required structure"""
        if not isinstance(question, dict):
            return False
            
        question_type = question.get('type')
        if question_type not in ['multiple_choice', 'true_false', 'short_answer']:
            return False
            
        if not question.get('question') or not question.get('explanation'):
            return False
            
        if question_type == 'multiple_choice':
            options = question.get('options', [])
            correct = question.get('correct')
            return (isinstance(options, list) and len(options) >= 2 and 
                   isinstance(correct, int) and 0 <= correct < len(options))
                   
        elif question_type == 'true_false':
            return isinstance(question.get('correct'), bool)
            
        elif question_type == 'short_answer':
            return bool(question.get('sample_answer'))
            
        return False

    def _generate_quiz_questions(self, step: Dict[str, Any], repo_data: Dict[str, Any], llm: Optional[Any] = None) -> List[Dict[str, Any]]:
        """Generate quiz questions for knowledge assessment with codebase-specific content"""
        
        # Initialize codebase quiz generator
        codebase_quiz = CodebaseQuizGenerator()
        
        # Try LLM-powered generation first
        if llm:
            try:
                llm_questions = self._llm_powered_quiz_generation(step, repo_data, llm)
                if llm_questions and len(llm_questions) >= 2:
                    # Using LLM-generated quiz questions
                    return llm_questions
            except Exception as e:
                # LLM quiz generation failed, falling back to codebase analysis
                pass
        
        # Use codebase-specific quiz generation
        try:
            codebase_questions = codebase_quiz.generate_codebase_quiz(step, repo_data)
            if codebase_questions and len(codebase_questions) >= 2:
                # Using codebase-specific quiz questions
                return codebase_questions
        except Exception as e:
            # Codebase quiz generation failed, using generic fallback
            pass
        
        # Final fallback - generic but contextual questions
        # Using generic fallback questions
        return self._generate_generic_fallback_questions(step, repo_data)
    
    def _generate_generic_fallback_questions(self, step: Dict[str, Any], repo_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate generic but contextual fallback questions"""
        step_title = step.get('title', 'this module')
        focus_files = step.get('focus_files', [])
        repo_name = repo_data.get('repo_name', 'the repository')
        
        questions = []
        
        # Question about the files in this step
        if focus_files:
            file_count = len(focus_files)
            questions.append({
                "type": "multiple_choice",
                "question": f"How many key files does the '{step_title}' module ask you to explore?",
                "options": [str(file_count), str(file_count + 1), str(max(1, file_count - 1)), "More than 5"],
                "correct": 0,
                "explanation": f"This module focuses on exploring {file_count} key files to understand its functionality."
            })
        
        # Question about understanding the walkthrough
        questions.append({
            "type": "short_answer", 
            "question": f"After completing the '{step_title}' walkthrough, what is one specific thing you learned about how this part of {repo_name} works?",
            "sample_answer": f"I learned how the {step_title.lower()} components interact to provide the main functionality, including their data flow and key responsibilities.",
            "explanation": "This question tests whether you actually engaged with the code and understood the architectural patterns."
        })
        
        # Question about practical application
        questions.append({
            "type": "true_false",
            "question": f"Understanding the '{step_title}' module helps you know where to make changes if you wanted to modify this part of the application.",
            "correct": True,
            "explanation": "Yes, understanding the code structure and relationships helps you identify the right places to make modifications."
        })
        
        return questions[:3]  # Return exactly 3 questions

    def _create_progress_system(self) -> Dict[str, Any]:
        """Create progress tracking system"""
        return {
            "total_points": 0,
            "current_level": 1,
            "progress_percentage": 0,
            "modules_completed": 0,
            "achievements_unlocked": 1,  # Start with "First Steps"
            "level_thresholds": [0, 500, 1200, 2000, 3000, 4500],
            "level_titles": [
                "Code Newbie",
                "Junior Explorer", 
                "Code Detective",
                "Architecture Analyst",
                "System Master",
                "Code Wizard"
            ]
        }

    def _create_interactive_elements(self, repo_data: Dict[str, Any], analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create interactive elements for engagement"""
        return {
            "code_snippets": self._extract_interesting_snippets(repo_data),
            "interactive_diagrams": {
                "architecture_overview": True,
                "component_relationships": True,
                "data_flow": True
            },
            "live_code_exploration": {
                "enabled": True,
                "supported_languages": repo_data.get('languages', []),
                "syntax_highlighting": True
            },
            "progress_visualization": {
                "progress_bar": True,
                "achievement_badges": True,
                "level_indicators": True,
                "completion_celebrations": True
            }
        }

    def _extract_interesting_snippets(self, repo_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract interesting code snippets for interactive exploration"""
        snippets = []
        
        for file_info in repo_data.get('files', [])[:10]:  # Max 10 snippets
            content = file_info.get('content', '')
            if content and len(content) > 100:
                # Extract first meaningful block (e.g., function definition)
                lines = content.split('\n')
                snippet_lines = []
                
                for line in lines:
                    if (line.strip().startswith('def ') or 
                        line.strip().startswith('function ') or
                        line.strip().startswith('class ') or
                        line.strip().startswith('export ')):
                        snippet_lines = lines[lines.index(line):lines.index(line)+10]
                        break
                
                if snippet_lines:
                    snippets.append({
                        "file": file_info['path'],
                        "language": file_info.get('language', 'text'),
                        "snippet": '\n'.join(snippet_lines),
                        "explanation": f"Key code from {file_info['path']}"
                    })
        
        return snippets

    def _create_gamification_elements(self) -> Dict[str, Any]:
        """Create gamification elements"""
        return {
            "point_system": {
                "file_read": 25,
                "quiz_correct": 50,
                "activity_complete": 75,
                "module_complete": 200,
                "achievement_unlock": 100
            },
            "streaks": {
                "daily_learning": 0,
                "perfect_quiz": 0,
                "module_completion": 0
            },
            "social_features": {
                "leaderboard": False,  # Can be enabled later
                "sharing": True,
                "progress_sharing": True
            },
            "rewards": {
                "virtual_badges": True,
                "completion_certificates": True,
                "skill_endorsements": True
            }
        }
    
    def _parallel_quiz_generation(self, learning_path: List[Dict[str, Any]], repo_data: Dict[str, Any], llm: Any) -> List[List[Dict[str, Any]]]:
        """Generate quizzes for all learning modules in parallel"""
        
        if not learning_path:
            return []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            # Submit quiz generation tasks for each module
            futures = []
            for step in learning_path:
                future = executor.submit(self._generate_quiz_questions, step, repo_data, llm)
                futures.append(future)
            
            # Collect results as they complete
            all_quiz_questions = []
            for i, future in enumerate(futures):
                try:
                    quiz_questions = future.result(timeout=30)  # 30s timeout per quiz
                    all_quiz_questions.append(quiz_questions)
                except Exception as e:
                    # Error generating quiz for module
                    # Fallback to contextually appropriate quiz
                    step_data = learning_path[i] if i < len(learning_path) else {}
                    fallback_quiz = self._generate_quiz_questions(step_data, repo_data, None)
                    all_quiz_questions.append(fallback_quiz)
            
            return all_quiz_questions
