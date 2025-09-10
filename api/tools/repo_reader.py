"""GitHub Repository Reading Tool for LangGraph Agent"""

import os
import hashlib
import json
import time
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Any
from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class RepoReaderInput(BaseModel):
    github_url: str = Field(description="GitHub repository URL to analyze")
    max_files: int = Field(default=50, description="Maximum number of files to read")


class RepoReaderTool(BaseTool):
    # Simple in-memory cache
    _cache = {}
    _cache_expiry = 300  # 5 minutes
    name: str = "repo_reader"
    description: str = "Clones and reads GitHub repositories, extracting file structure and code content"
    args_schema: type[BaseModel] = RepoReaderInput

    def _run(self, github_url: str, max_files: int = 50, progress_callback=None) -> Dict[str, Any]:
        """Clone and read a GitHub repository"""
        try:
            # Extract repo name from URL
            repo_name = github_url.split('/')[-1].replace('.git', '')
            clone_path = f"/tmp/repo_analysis/{repo_name}"
            
            # Clean up existing directory
            if os.path.exists(clone_path):
                shutil.rmtree(clone_path)
            
            # Ensure parent directory exists
            os.makedirs(os.path.dirname(clone_path), exist_ok=True)
            
            # Clone repository with progress display
            if progress_callback:
                progress_callback(f"🚀 Starting to clone {github_url}")
                progress_callback(f"📁 Cloning into {clone_path}")
            
            # Clone repository using git command with progress
            process = subprocess.Popen(
                ["git", "clone", "--progress", github_url, clone_path],
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True
            )
            
            # Monitor progress in real-time
            clone_output = []
            while True:
                output = process.stderr.readline()
                if output == '' and process.poll() is not None:
                    break
                if output and progress_callback:
                    # Parse git progress output
                    line = output.strip()
                    if line:
                        clone_output.append(line)
                        if "Cloning into" in line:
                            progress_callback(f"📁 {line}")
                        elif "remote:" in line or "Receiving objects:" in line:
                            progress_callback(f"📦 {line}")
                        elif "Resolving deltas:" in line:
                            progress_callback(f"🔗 {line}")
                        elif "%" in line:
                            progress_callback(f"⬇️ {line}")
                        else:
                            progress_callback(f"ℹ️ {line}")
            
            return_code = process.wait()
            
            if return_code != 0:
                error_msg = f"Git clone failed: {' '.join(clone_output)}"
                if progress_callback:
                    progress_callback(f"❌ Clone failed: {' '.join(clone_output)}")
                raise Exception(error_msg)
            
            if progress_callback:
                progress_callback("✅ Repository cloned successfully")
                progress_callback("🔍 Analyzing repository structure...")
            
            # Analyze repository structure
            repo_data = self._analyze_repo_structure(clone_path, max_files, progress_callback)
            repo_data['repo_name'] = repo_name
            repo_data['github_url'] = github_url
            repo_data['clone_progress'] = "completed"
            
            if progress_callback:
                progress_callback(f"📊 Analysis complete: {len(repo_data.get('files', []))} files analyzed")
            
            return repo_data
            
        except Exception as e:
            error_msg = f"Failed to clone repository: {str(e)}"
            if progress_callback:
                progress_callback(f"❌ Error: {error_msg}")
            return {"error": error_msg}

    def _analyze_repo_structure(self, repo_path: str, max_files: int, progress_callback=None) -> Dict[str, Any]:
        """Analyze repository structure and extract key information"""
        repo_data = {
            "structure": {},
            "files": [],
            "languages": set(),
            "frameworks": set(),
            "key_files": []
        }
        
        # File extensions to analyze
        code_extensions = {
            '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript', 
            '.jsx': 'React', '.tsx': 'React/TypeScript', '.java': 'Java',
            '.cpp': 'C++', '.c': 'C', '.go': 'Go', '.rs': 'Rust',
            '.rb': 'Ruby', '.php': 'PHP', '.swift': 'Swift', '.kt': 'Kotlin'
        }
        
        # Key configuration files
        key_files = {
            'package.json': 'Node.js/JavaScript',
            'requirements.txt': 'Python',
            'Pipfile': 'Python',
            'Cargo.toml': 'Rust',
            'pom.xml': 'Java/Maven',
            'build.gradle': 'Java/Gradle',
            'Dockerfile': 'Docker',
            'docker-compose.yml': 'Docker Compose',
            'README.md': 'Documentation'
        }
        
        file_count = 0
        total_files_found = 0
        
        # First pass: count total files for progress
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') 
                      and d not in ['node_modules', '__pycache__', 'build', 'dist', 'target']]
            total_files_found += len(files)
        
        if progress_callback:
            progress_callback(f"📁 Found {total_files_found} files, analyzing up to {max_files}")
        
        # Second pass: analyze files with progress
        for root, dirs, files in os.walk(repo_path):
            # Skip common directories to ignore
            dirs[:] = [d for d in dirs if not d.startswith('.') 
                      and d not in ['node_modules', '__pycache__', 'build', 'dist', 'target']]
            
            for file in files:
                if file_count >= max_files:
                    break
                    
                file_path = Path(root) / file
                rel_path = file_path.relative_to(repo_path)
                
                # Check for key configuration files
                if file in key_files:
                    repo_data['key_files'].append({
                        'name': file,
                        'type': key_files[file],
                        'path': str(rel_path),
                        'content': self._read_file_content(file_path)
                    })
                
                # Analyze code files
                ext = file_path.suffix.lower()
                if ext in code_extensions:
                    repo_data['languages'].add(code_extensions[ext])
                    
                    if file_count < max_files:
                        content = self._read_file_content(file_path)
                        if content:
                            repo_data['files'].append({
                                'path': str(rel_path),
                                'language': code_extensions[ext],
                                'size': len(content),
                                'content': content[:2000] if len(content) > 2000 else content
                            })
                            file_count += 1
                            
                            # Progress update every 10 files
                            if progress_callback and file_count % 10 == 0:
                                progress_callback(f"📄 Analyzed {file_count}/{max_files} files...")
                            elif progress_callback and file_count <= 5:
                                progress_callback(f"📄 Reading {rel_path}")
        
        # Convert sets to lists for JSON serialization
        repo_data['languages'] = list(repo_data['languages'])
        repo_data['frameworks'] = list(repo_data['frameworks'])
        
        # Detect frameworks based on files and content
        self._detect_frameworks(repo_data)
        
        return repo_data

    def _read_file_content(self, file_path: Path) -> str:
        """Safely read file content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except (UnicodeDecodeError, PermissionError, FileNotFoundError):
            return ""

    def _detect_frameworks(self, repo_data: Dict[str, Any]):
        """Detect frameworks based on file patterns and content"""
        frameworks = set()
        
        # Check key files for framework indicators
        for key_file in repo_data['key_files']:
            if key_file['name'] == 'package.json':
                content = key_file['content']
                if 'react' in content.lower():
                    frameworks.add('React')
                if 'next' in content.lower():
                    frameworks.add('Next.js')
                if 'express' in content.lower():
                    frameworks.add('Express.js')
                if 'vue' in content.lower():
                    frameworks.add('Vue.js')
                    
            elif key_file['name'] == 'requirements.txt':
                content = key_file['content'].lower()
                if 'django' in content:
                    frameworks.add('Django')
                if 'flask' in content:
                    frameworks.add('Flask')
                if 'fastapi' in content:
                    frameworks.add('FastAPI')
        
        # Check file patterns
        for file_info in repo_data['files']:
            path = file_info['path'].lower()
            if 'components/' in path and file_info['language'] in ['React', 'React/TypeScript']:
                frameworks.add('React')
            if 'pages/' in path and file_info['language'] in ['React', 'React/TypeScript']:
                frameworks.add('Next.js')
        
        repo_data['frameworks'] = list(frameworks)
    
    def _parallel_file_reading(self, file_list: List[tuple]) -> List[Dict[str, Any]]:
        """Read multiple files in parallel"""
        import concurrent.futures
        
        def read_single_file(file_info):
            file_path, rel_path, language = file_info
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    return {
                        "path": str(rel_path),
                        "language": language,
                        "size": len(content),
                        "content": content[:1000] if len(content) > 1000 else content  # Reduced from 2000 to 1000
                    }
            except (UnicodeDecodeError, PermissionError, FileNotFoundError):
                return {
                    "path": str(rel_path),
                    "language": language,
                    "size": 0,
                    "content": ""
                }
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_to_file = {executor.submit(read_single_file, file_info): file_info for file_info in file_list}
            results = []
            
            for future in concurrent.futures.as_completed(future_to_file):
                try:
                    result = future.result(timeout=10)  # 10s timeout per file
                    if result and result["content"]:  # Only add files with content
                        results.append(result)
                except Exception as e:
                    # Error reading file - skip this file
                    pass
            return results
