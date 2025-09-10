"""Code Analysis Tool for understanding repository structure and patterns"""

import ast
import re
import asyncio
import concurrent.futures
from typing import Dict, List, Any, Optional
from langchain.tools import BaseTool
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field


class CodeAnalyzerInput(BaseModel):
    repo_data: Dict[str, Any] = Field(description="Repository data from repo_reader tool")
    llm: Optional[Any] = Field(default=None, description="Language model for dynamic analysis")


class CodeAnalyzerTool(BaseTool):
    name: str = "code_analyzer"
    description: str = "Analyzes code structure, patterns, and generates insights about the codebase"
    args_schema: type[BaseModel] = CodeAnalyzerInput

    def _run(self, repo_data: Dict[str, Any], llm: Optional[Any] = None) -> Dict[str, Any]:
        """Analyze code structure and patterns"""
        try:
            analysis = {
                "complexity_score": 0,
                "architecture_pattern": "Unknown",
                "entry_points": [],
                "key_components": [],
                "dependencies": [],
                "code_quality": {},
                "learning_path": []
            }
            
            # Use LLM for dynamic analysis if available
            if llm:
                analysis.update(self._parallel_llm_analysis(repo_data, llm))
            else:
                # Run static analysis in parallel using ThreadPoolExecutor
                analysis.update(self._parallel_static_analysis(repo_data))
            
            return analysis
            
        except Exception as e:
            return {"error": f"Code analysis failed: {str(e)}"}

    def _llm_powered_analysis(self, repo_data: Dict[str, Any], llm) -> Dict[str, Any]:
        """Use LLM to perform dynamic code analysis"""
        try:
            # Prepare repository context for LLM
            repo_context = self._prepare_repo_context(repo_data)
            
            analysis_prompt = f"""
            Analyze this repository and provide detailed insights:

            Repository: {repo_data.get('repo_name', 'Unknown')}
            URL: {repo_data.get('github_url', 'Unknown')}
            Languages: {', '.join(repo_data.get('languages', []))}
            Frameworks: {', '.join(repo_data.get('frameworks', []))}

            Key Files:
            {repo_context['key_files']}

            Code Samples:
            {repo_context['code_samples']}

            Please analyze and provide:
            1. Architecture pattern (be specific, not just "Monolithic")
            2. Complexity score (0-100) with reasoning
            3. 3-5 key entry points with explanations
            4. 5-8 most important components to understand
            5. Code quality assessment
            6. A personalized 4-5 step learning path for this specific codebase

            Respond in JSON format with these keys:
            - architecture_pattern: string
            - architecture_reasoning: string  
            - complexity_score: number
            - complexity_reasoning: string
            - entry_points: array of objects with file, type, language, explanation
            - key_components: array of objects with file, type, importance_reason, learning_focus
            - code_quality: object with documentation_score, test_coverage_estimate, code_organization, naming_consistency, reasoning
            - learning_path: array of 4-5 learning steps with step, title, description, difficulty, estimated_time, focus_files, why_important

            Make this analysis specific to THIS repository, not generic.
            """

            # Get LLM response
            response = llm.invoke([HumanMessage(content=analysis_prompt)])
            
            # Parse JSON response
            import json
            try:
                llm_analysis = json.loads(response.content)
                return llm_analysis
            except json.JSONDecodeError:
                # Fallback to static analysis if JSON parsing fails
                return self._fallback_analysis(repo_data)
                
        except Exception as e:
            # LLM analysis failed
            return self._fallback_analysis(repo_data)

    def _prepare_repo_context(self, repo_data: Dict[str, Any]) -> Dict[str, str]:
        """Prepare repository context for LLM analysis"""
        key_files_summary = []
        for file in repo_data.get('key_files', [])[:5]:  # Top 5 key files
            key_files_summary.append(f"- {file['name']} ({file['type']}): {file['content'][:200]}...")
        
        code_samples = []
        for file in repo_data.get('files', [])[:3]:  # Top 3 code files
            if file.get('content'):
                code_samples.append(f"File: {file['path']}\nLanguage: {file['language']}\nContent:\n{file['content'][:500]}...\n")
        
        return {
            'key_files': '\n'.join(key_files_summary),
            'code_samples': '\n'.join(code_samples)
        }

    def _fallback_analysis(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback to static analysis"""
        return {
            "architecture_pattern": self._detect_architecture_pattern(repo_data),
            "architecture_reasoning": "Static analysis based on file patterns",
            "complexity_score": self._calculate_complexity(repo_data),
            "complexity_reasoning": "Based on file count, languages, and frameworks",
            "entry_points": self._find_entry_points(repo_data),
            "key_components": self._analyze_components(repo_data)[:8],
            "code_quality": self._assess_code_quality(repo_data),
            "learning_path": self._generate_learning_path(repo_data, {})
        }

    def _detect_architecture_pattern(self, repo_data: Dict[str, Any]) -> str:
        """Detect common architecture patterns"""
        frameworks = repo_data.get('frameworks', [])
        files = repo_data.get('files', [])
        
        # Check for common patterns
        if 'Next.js' in frameworks or 'React' in frameworks:
            if any('pages/' in f['path'] for f in files):
                return "Next.js App Router" if any('app/' in f['path'] for f in files) else "Next.js Pages Router"
            return "React SPA"
        
        if 'Flask' in frameworks:
            if any('models/' in f['path'] for f in files) and any('views/' in f['path'] for f in files):
                return "Flask MVC"
            return "Flask Microservice"
        
        if 'Django' in frameworks:
            return "Django MVT"
        
        # Check file structure patterns
        has_mvc = any('models/' in f['path'] for f in files) and any('views/' in f['path'] for f in files)
        has_components = any('components/' in f['path'] for f in files)
        
        if has_mvc:
            return "MVC Architecture"
        elif has_components:
            return "Component-Based Architecture"
        
        return "Monolithic"

    def _find_entry_points(self, repo_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Find main entry points of the application"""
        entry_points = []
        
        # Common entry point files
        entry_patterns = {
            'main.py': 'Python Main',
            'app.py': 'Flask App',
            'index.js': 'JavaScript Entry',
            'index.ts': 'TypeScript Entry',
            'server.js': 'Node.js Server',
            'main.js': 'JavaScript Main',
            'App.js': 'React App',
            'App.tsx': 'React App (TypeScript)',
            'layout.tsx': 'Next.js Layout',
            'page.tsx': 'Next.js Page'
        }
        
        for file_info in repo_data.get('files', []):
            filename = file_info['path'].split('/')[-1]
            if filename in entry_patterns:
                entry_points.append({
                    'file': file_info['path'],
                    'type': entry_patterns[filename],
                    'language': file_info.get('language', 'Unknown')
                })
        
        # Also check key_files
        for key_file in repo_data.get('key_files', []):
            if key_file['name'] == 'package.json':
                # Extract scripts from package.json
                content = key_file.get('content', '')
                if 'scripts' in content:
                    entry_points.append({
                        'file': key_file['path'],
                        'type': 'Package Scripts',
                        'language': 'JSON'
                    })
        
        return entry_points

    def _analyze_components(self, repo_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze key components and their relationships"""
        components = []
        
        for file_info in repo_data.get('files', []):
            component_info = {
                'file': file_info['path'],
                'language': file_info.get('language', 'Unknown'),
                'type': self._classify_component_type(file_info),
                'complexity': self._estimate_file_complexity(file_info),
                'dependencies': self._extract_file_dependencies(file_info)
            }
            
            if component_info['type'] != 'Unknown':
                components.append(component_info)
        
        # Sort by complexity/importance
        components.sort(key=lambda x: x['complexity'], reverse=True)
        return components[:20]  # Return top 20 most important components

    def _classify_component_type(self, file_info: Dict[str, Any]) -> str:
        """Classify the type of component based on file path and content"""
        path = file_info['path'].lower()
        content = file_info.get('content', '').lower()
        
        # Directory-based classification
        if 'components/' in path:
            return 'UI Component'
        elif 'models/' in path:
            return 'Data Model'
        elif 'views/' in path or 'pages/' in path:
            return 'View/Page'
        elif 'controllers/' in path:
            return 'Controller'
        elif 'services/' in path:
            return 'Service'
        elif 'utils/' in path or 'helpers/' in path:
            return 'Utility'
        elif 'api/' in path:
            return 'API Endpoint'
        elif 'tests/' in path or 'test' in path:
            return 'Test'
        
        # Content-based classification
        if 'class' in content and 'def __init__' in content:
            return 'Python Class'
        elif 'function ' in content or 'def ' in content:
            return 'Function Collection'
        elif 'export default' in content or 'export const' in content:
            return 'JavaScript/TypeScript Module'
        
        return 'Unknown'

    def _estimate_file_complexity(self, file_info: Dict[str, Any]) -> int:
        """Estimate file complexity based on size and content"""
        content = file_info.get('content', '')
        complexity = 0
        
        # Basic metrics
        lines = len(content.split('\n'))
        complexity += min(lines // 10, 10)  # Max 10 points for lines
        
        # Language-specific complexity indicators
        if file_info.get('language') == 'Python':
            complexity += content.count('class ') * 3
            complexity += content.count('def ') * 2
            complexity += content.count('if ') + content.count('for ') + content.count('while ')
        elif file_info.get('language') in ['JavaScript', 'TypeScript']:
            complexity += content.count('function ') * 2
            complexity += content.count('class ') * 3
            complexity += content.count('if (') + content.count('for (') + content.count('while (')
        
        return min(complexity, 50)  # Cap at 50

    def _extract_file_dependencies(self, file_info: Dict[str, Any]) -> List[str]:
        """Extract dependencies from file content"""
        content = file_info.get('content', '')
        dependencies = []
        
        # Python imports
        import_patterns = [
            r'from\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s+import',
            r'import\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)'
        ]
        
        # JavaScript/TypeScript imports
        js_patterns = [
            r'import.*from\s+[\'"]([^\'"]*)[\'"]',
            r'require\([\'"]([^\'"]*)[\'"]\)'
        ]
        
        all_patterns = import_patterns + js_patterns
        
        for pattern in all_patterns:
            matches = re.findall(pattern, content)
            dependencies.extend(matches)
        
        return list(set(dependencies))  # Remove duplicates

    def _extract_dependencies(self, repo_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract project dependencies from configuration files"""
        dependencies = []
        
        for key_file in repo_data.get('key_files', []):
            if key_file['name'] == 'package.json':
                # Extract npm dependencies
                content = key_file.get('content', '')
                import re
                deps = re.findall(r'"([^"]+)":\s*"([^"]+)"', content)
                for dep, version in deps:
                    if not dep.startswith('@types/'):  # Skip type definitions
                        dependencies.append({
                            'name': dep,
                            'version': version,
                            'type': 'npm'
                        })
            elif key_file['name'] == 'requirements.txt':
                # Extract Python dependencies
                lines = key_file.get('content', '').strip().split('\n')
                for line in lines:
                    if line.strip() and not line.startswith('#'):
                        parts = line.split('==')
                        name = parts[0].strip()
                        version = parts[1].strip() if len(parts) > 1 else 'latest'
                        dependencies.append({
                            'name': name,
                            'version': version,
                            'type': 'python'
                        })
        
        return dependencies

    def _calculate_complexity(self, repo_data: Dict[str, Any]) -> int:
        """Calculate overall repository complexity score"""
        files = repo_data.get('files', [])
        
        # Base score from file count
        file_count = len(files)
        complexity = min(file_count // 5, 20)  # Max 20 points from file count
        
        # Language diversity
        languages = set(f.get('language', 'Unknown') for f in files)
        complexity += len(languages) * 2
        
        # Framework complexity
        frameworks = repo_data.get('frameworks', [])
        complexity += len(frameworks) * 3
        
        # Dependency complexity
        dependencies = len(repo_data.get('key_files', []))
        complexity += dependencies * 2
        
        return min(complexity, 100)  # Cap at 100

    def _assess_code_quality(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess code quality metrics"""
        files = repo_data.get('files', [])
        
        quality_metrics = {
            'documentation_score': 0,
            'test_coverage_estimate': 0,
            'code_organization': 'Poor',
            'naming_consistency': 'Poor'
        }
        
        # Check for documentation
        doc_indicators = ['README.md', 'docs/', 'documentation/']
        has_docs = any(any(indicator in f['path'] for indicator in doc_indicators) 
                      for f in files + repo_data.get('key_files', []))
        
        if has_docs:
            quality_metrics['documentation_score'] = 8
        
        # Estimate test coverage
        test_files = [f for f in files if 'test' in f['path'].lower()]
        if test_files:
            test_ratio = len(test_files) / max(len(files), 1)
            quality_metrics['test_coverage_estimate'] = min(int(test_ratio * 100), 90)
        
        # Check code organization
        has_structure = any('components/' in f['path'] or 'services/' in f['path'] 
                           or 'models/' in f['path'] for f in files)
        if has_structure:
            quality_metrics['code_organization'] = 'Good'
        
        return quality_metrics

    def _generate_learning_path(self, repo_data: Dict[str, Any], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate a structured learning path for understanding the codebase"""
        learning_steps = []
        
        # Step 1: Overview
        learning_steps.append({
            'step': 1,
            'title': 'Repository Overview',
            'description': f"Understand the {analysis['architecture_pattern']} architecture",
            'difficulty': 'Beginner',
            'estimated_time': '10-15 minutes',
            'focus_files': [f['path'] for f in repo_data.get('key_files', [])]
        })
        
        # Step 2: Entry Points
        if analysis['entry_points']:
            learning_steps.append({
                'step': 2,
                'title': 'Application Entry Points',
                'description': 'Explore how the application starts and main components',
                'difficulty': 'Beginner',
                'estimated_time': '15-20 minutes',
                'focus_files': [ep['file'] for ep in analysis['entry_points'][:3]]
            })
        
        # Step 3: Core Components
        if analysis['key_components']:
            core_components = analysis['key_components'][:5]
            learning_steps.append({
                'step': 3,
                'title': 'Core Components Deep Dive',
                'description': 'Understand the main business logic and components',
                'difficulty': 'Intermediate',
                'estimated_time': '30-45 minutes',
                'focus_files': [comp['file'] for comp in core_components]
            })
        
        # Step 4: Dependencies and Integration
        if analysis['dependencies']:
            learning_steps.append({
                'step': 4,
                'title': 'Dependencies and Integration',
                'description': 'Understand external dependencies and how they integrate',
                'difficulty': 'Intermediate',
                'estimated_time': '20-30 minutes',
                'focus_files': []
            })
        
        # Step 5: Advanced Patterns
        learning_steps.append({
            'step': 5,
            'title': 'Advanced Patterns and Architecture',
            'description': 'Explore advanced patterns and architectural decisions',
            'difficulty': 'Advanced',
            'estimated_time': '45-60 minutes',
            'focus_files': []
        })
        
        return learning_steps
    
    def _parallel_static_analysis(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run static analysis tasks in parallel"""
        
        # Define analysis tasks that can run concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all analysis tasks
            futures = {
                'architecture_pattern': executor.submit(self._detect_architecture_pattern, repo_data),
                'entry_points': executor.submit(self._find_entry_points, repo_data),
                'key_components': executor.submit(self._analyze_components, repo_data),
                'dependencies': executor.submit(self._extract_dependencies, repo_data),
                'complexity_score': executor.submit(self._calculate_complexity, repo_data),
                'code_quality': executor.submit(self._assess_code_quality, repo_data)
            }
            
            # Collect results as they complete
            results = {}
            for key, future in futures.items():
                try:
                    results[key] = future.result(timeout=30)  # 30s timeout per task
                except Exception as e:
                    # Error in analysis component
                    # Set default values based on key
                    if key == 'architecture_pattern':
                        results[key] = 'Unknown'
                    elif key in ['entry_points', 'key_components', 'dependencies']:
                        results[key] = []
                    elif key == 'complexity_score':
                        results[key] = 0
                    elif key == 'code_quality':
                        results[key] = {}
            
            # Generate learning path after other analysis is complete
            try:
                results['learning_path'] = self._generate_learning_path(repo_data, results)
            except Exception as e:
                # Error generating learning path
                results['learning_path'] = []
            
            return results
    
    def _parallel_llm_analysis(self, repo_data: Dict[str, Any], llm: Any) -> Dict[str, Any]:
        """Run LLM-powered analysis with some parallel operations"""
        
        # For LLM analysis, we can still do some static analysis in parallel
        # while running the main LLM analysis
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            # Submit LLM analysis and some quick static analysis
            llm_future = executor.submit(self._llm_powered_analysis, repo_data, llm)
            static_future = executor.submit(self._quick_static_analysis, repo_data)
            
            try:
                llm_results = llm_future.result(timeout=60)  # 60s timeout for LLM
                static_results = static_future.result(timeout=30)  # 30s for static
                
                # Merge results, prioritizing LLM results
                final_results = {**static_results, **llm_results}
                return final_results
                
            except Exception as e:
                # Error in parallel LLM analysis
                # Fallback to static analysis only
                return self._parallel_static_analysis(repo_data)
    
    def _quick_static_analysis(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Quick static analysis for supplementing LLM analysis"""
        return {
            'dependencies': self._extract_dependencies(repo_data),
            'complexity_score': self._calculate_complexity(repo_data)
        }