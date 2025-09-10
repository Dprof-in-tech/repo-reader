"""Codebase-Specific Quiz Generator"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
import random

class CodebaseQuizGenerator:
    """Generates quiz questions based on actual codebase content and walkthrough steps"""
    
    def __init__(self):
        self.question_templates = self._load_question_templates()
    
    def _load_question_templates(self) -> Dict[str, List[Dict]]:
        """Load question templates for different code patterns"""
        return {
            'function_analysis': [
                {
                    'template': 'What is the primary purpose of the function `{function_name}` in `{file_name}`?',
                    'type': 'multiple_choice',
                    'answer_generator': self._generate_function_purpose_answers
                },
                {
                    'template': 'How many parameters does the function `{function_name}` accept?',
                    'type': 'multiple_choice', 
                    'answer_generator': self._generate_parameter_count_answers
                },
                {
                    'template': 'The function `{function_name}` returns a {return_type}.',
                    'type': 'true_false',
                    'answer_generator': self._generate_return_type_answer
                }
            ],
            'import_analysis': [
                {
                    'template': 'Which library/module is imported as `{import_alias}` in `{file_name}`?',
                    'type': 'multiple_choice',
                    'answer_generator': self._generate_import_answers
                },
                {
                    'template': 'The file `{file_name}` imports `{import_name}` for {import_purpose}.',
                    'type': 'true_false',
                    'answer_generator': self._generate_import_purpose_answer
                }
            ],
            'class_analysis': [
                {
                    'template': 'What type of class is `{class_name}` in `{file_name}`?',
                    'type': 'multiple_choice',
                    'answer_generator': self._generate_class_type_answers
                },
                {
                    'template': 'How many methods does the class `{class_name}` define?',
                    'type': 'multiple_choice',
                    'answer_generator': self._generate_method_count_answers
                }
            ],
            'structure_analysis': [
                {
                    'template': 'In the file `{file_name}`, what comes after the import statements?',
                    'type': 'multiple_choice',
                    'answer_generator': self._generate_structure_answers
                },
                {
                    'template': 'The main logic in `{file_name}` is contained in {container_type}.',
                    'type': 'true_false',
                    'answer_generator': self._generate_container_answer
                }
            ],
            'config_analysis': [
                {
                    'template': 'What is the value of `{config_key}` in `{file_name}`?',
                    'type': 'multiple_choice',
                    'answer_generator': self._generate_config_value_answers
                },
                {
                    'template': 'The configuration file `{file_name}` defines {config_count} main settings.',
                    'type': 'true_false',
                    'answer_generator': self._generate_config_count_answer
                }
            ]
        }
    
    def generate_codebase_quiz(self, step: Dict[str, Any], repo_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate quiz questions based on actual codebase content"""
        focus_files = step.get('focus_files', [])
        questions = []
        
        # Analyze each focus file and generate specific questions
        for file_path in focus_files[:2]:  # Limit to 2 files per module
            file_info = self._get_file_info(file_path, repo_data)
            if not file_info:
                continue
                
            content = file_info.get('content', '')
            language = file_info.get('language', 'text')
            
            # Generate questions based on file content
            file_questions = self._analyze_file_content(file_path, content, language)
            questions.extend(file_questions)
        
        # Add walkthrough-specific questions
        walkthrough_questions = self._generate_walkthrough_questions(step, repo_data)
        questions.extend(walkthrough_questions)
        
        # Ensure we have 2-4 questions and shuffle
        questions = questions[:4]
        if len(questions) < 2:
            # Add fallback questions if we don't have enough
            questions.extend(self._generate_fallback_questions(step, repo_data))
        
        random.shuffle(questions)
        return questions[:3]  # Return exactly 3 questions
    
    def _get_file_info(self, file_path: str, repo_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get file information from repo data"""
        for file_info in repo_data.get('files', []):
            if file_info.get('path') == file_path:
                return file_info
        return None
    
    def _analyze_file_content(self, file_path: str, content: str, language: str) -> List[Dict[str, Any]]:
        """Analyze file content and generate specific questions"""
        questions = []
        file_name = file_path.split('/')[-1]
        
        if language.lower() in ['python', 'py']:
            questions.extend(self._analyze_python_file(file_name, content))
        elif language.lower() in ['javascript', 'js', 'typescript', 'ts']:
            questions.extend(self._analyze_js_file(file_name, content))
        elif language.lower() in ['json']:
            questions.extend(self._analyze_json_file(file_name, content))
        else:
            questions.extend(self._analyze_generic_file(file_name, content))
        
        return questions
    
    def _analyze_python_file(self, file_name: str, content: str) -> List[Dict[str, Any]]:
        """Analyze Python file and generate questions"""
        questions = []
        
        # Find function definitions
        functions = re.findall(r'def\s+(\w+)\s*\([^)]*\):', content)
        if functions:
            func = random.choice(functions)
            # Count parameters
            func_pattern = rf'def\s+{re.escape(func)}\s*\(([^)]*)\):'
            match = re.search(func_pattern, content)
            param_count = 0
            if match and match.group(1).strip():
                params = [p.strip() for p in match.group(1).split(',') if p.strip()]
                param_count = len(params)
            
            questions.append({
                'type': 'multiple_choice',
                'question': f'How many parameters does the function `{func}` accept in `{file_name}`?',
                'options': [str(param_count), str(param_count + 1), str(max(0, param_count - 1)), str(param_count + 2)],
                'correct': 0,
                'explanation': f'The function `{func}` accepts {param_count} parameters.'
            })
        
        # Find class definitions
        classes = re.findall(r'class\s+(\w+)', content)
        if classes:
            class_name = random.choice(classes)
            questions.append({
                'type': 'true_false',
                'question': f'The file `{file_name}` defines a class called `{class_name}`.',
                'correct': True,
                'explanation': f'Yes, `{class_name}` is defined as a class in this file.'
            })
        
        # Find imports
        imports = re.findall(r'(?:from\s+(\S+)\s+import|import\s+(\S+))', content)
        if imports:
            import_modules = [imp[0] or imp[1] for imp in imports]
            if import_modules:
                real_import = random.choice(import_modules).split('.')[0]
                fake_imports = ['numpy', 'pandas', 'matplotlib', 'django', 'fastapi']
                fake_imports = [f for f in fake_imports if f != real_import]
                
                options = [real_import] + random.sample(fake_imports, min(3, len(fake_imports)))
                random.shuffle(options)
                correct_idx = options.index(real_import)
                
                questions.append({
                    'type': 'multiple_choice',
                    'question': f'Which of these modules is actually imported in `{file_name}`?',
                    'options': options,
                    'correct': correct_idx,
                    'explanation': f'The module `{real_import}` is imported in this file.'
                })
        
        return questions
    
    def _analyze_js_file(self, file_name: str, content: str) -> List[Dict[str, Any]]:
        """Analyze JavaScript/TypeScript file and generate questions"""
        questions = []
        
        # Find function definitions
        functions = re.findall(r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=.*?(?:function|\=>))', content)
        func_names = [f[0] or f[1] for f in functions if f[0] or f[1]]
        
        if func_names:
            func = random.choice(func_names)
            questions.append({
                'type': 'true_false',
                'question': f'The file `{file_name}` defines a function called `{func}`.',
                'correct': True,
                'explanation': f'Yes, the function `{func}` is defined in this file.'
            })
        
        # Find imports/requires
        imports = re.findall(r'(?:import.*?from\s+[\'"]([^\'"]+)[\'"]|require\([\'"]([^\'"]+)[\'"]\))', content)
        if imports:
            import_modules = [imp[0] or imp[1] for imp in imports]
            if import_modules:
                real_import = random.choice(import_modules).split('/')[-1]
                questions.append({
                    'type': 'multiple_choice',
                    'question': f'Which library is imported in `{file_name}`?',
                    'options': [real_import, 'lodash', 'moment', 'axios'],
                    'correct': 0,
                    'explanation': f'The library `{real_import}` is imported in this file.'
                })
        
        # Find React components
        components = re.findall(r'(?:function\s+(\w+)\s*\([^)]*\)\s*{[^}]*return|const\s+(\w+)\s*=.*?=>\s*{[^}]*return)', content)
        if components:
            comp_names = [c[0] or c[1] for c in components if (c[0] or c[1]) and (c[0] or c[1])[0].isupper()]
            if comp_names:
                comp = random.choice(comp_names)
                questions.append({
                    'type': 'true_false',
                    'question': f'`{comp}` appears to be a React component in `{file_name}`.',
                    'correct': True,
                    'explanation': f'Based on the naming convention and structure, `{comp}` is likely a React component.'
                })
        
        return questions
    
    def _analyze_json_file(self, file_name: str, content: str) -> List[Dict[str, Any]]:
        """Analyze JSON file and generate questions"""
        questions = []
        
        try:
            data = json.loads(content)
            
            if file_name.lower() == 'package.json':
                # Package.json specific questions
                if 'dependencies' in data:
                    deps = list(data['dependencies'].keys())
                    if deps:
                        real_dep = random.choice(deps)
                        fake_deps = ['express', 'lodash', 'moment', 'axios', 'react', 'vue']
                        fake_deps = [d for d in fake_deps if d not in deps]
                        
                        options = [real_dep] + random.sample(fake_deps, min(3, len(fake_deps)))
                        random.shuffle(options)
                        correct_idx = options.index(real_dep)
                        
                        questions.append({
                            'type': 'multiple_choice',
                            'question': f'Which dependency is listed in `{file_name}`?',
                            'options': options,
                            'correct': correct_idx,
                            'explanation': f'`{real_dep}` is listed as a dependency.'
                        })
                
                if 'scripts' in data:
                    scripts = list(data['scripts'].keys())
                    if scripts:
                        script = random.choice(scripts)
                        questions.append({
                            'type': 'true_false',
                            'question': f'The `{file_name}` file defines a `{script}` script.',
                            'correct': True,
                            'explanation': f'Yes, there is a `{script}` script defined.'
                        })
            else:
                # Generic JSON questions
                keys = list(data.keys()) if isinstance(data, dict) else []
                if keys:
                    key = random.choice(keys)
                    questions.append({
                        'type': 'true_false',
                        'question': f'The `{file_name}` file contains a `{key}` property.',
                        'correct': True,
                        'explanation': f'Yes, `{key}` is a property in this JSON file.'
                    })
                    
        except json.JSONDecodeError:
            pass
        
        return questions
    
    def _analyze_generic_file(self, file_name: str, content: str) -> List[Dict[str, Any]]:
        """Analyze generic file and generate basic questions"""
        questions = []
        
        lines = content.split('\n')
        line_count = len([line for line in lines if line.strip()])
        
        questions.append({
            'type': 'multiple_choice',
            'question': f'Approximately how many non-empty lines does `{file_name}` contain?',
            'options': [
                f'{line_count}',
                f'{line_count + 10}',
                f'{max(1, line_count - 10)}',
                f'{line_count + 25}'
            ],
            'correct': 0,
            'explanation': f'The file contains approximately {line_count} non-empty lines.'
        })
        
        return questions
    
    def _generate_walkthrough_questions(self, step: Dict[str, Any], repo_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate questions specific to the walkthrough step"""
        questions = []
        step_title = step.get('title', '')
        focus_files = step.get('focus_files', [])
        
        if focus_files:
            questions.append({
                'type': 'multiple_choice',
                'question': f'How many key files does the "{step_title}" module focus on?',
                'options': [
                    str(len(focus_files)),
                    str(len(focus_files) + 1),
                    str(max(1, len(focus_files) - 1)),
                    str(len(focus_files) + 2)
                ],
                'correct': 0,
                'explanation': f'This module focuses on {len(focus_files)} key files.'
            })
        
        # Questions about completing the walkthrough
        questions.append({
            'type': 'short_answer',
            'question': f'What is the main concept you learned from exploring the "{step_title}" section?',
            'sample_answer': f'The main concept is understanding how {step_title.lower()} works in this codebase and its role in the overall architecture.',
            'explanation': 'This tests whether you actually engaged with the learning material.'
        })
        
        return questions
    
    def _generate_fallback_questions(self, step: Dict[str, Any], repo_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate fallback questions when code analysis fails"""
        step_title = step.get('title', 'this module')
        repo_name = repo_data.get('repo_name', 'the repository')
        
        return [{
            'type': 'short_answer',
            'question': f'Based on your exploration of {step_title}, describe one key insight about how {repo_name} is structured.',
            'sample_answer': f'One key insight is how the components in {step_title} work together to implement the main functionality.',
            'explanation': 'This question tests your understanding of the code structure and relationships.'
        }]
    
    # Answer generator helper methods
    def _generate_function_purpose_answers(self, context: Dict) -> Tuple[List[str], int]:
        purposes = ['Data processing', 'User interface rendering', 'Business logic', 'API communication']
        return purposes, 0
    
    def _generate_parameter_count_answers(self, context: Dict) -> Tuple[List[str], int]:
        count = context.get('param_count', 2)
        return [str(count), str(count+1), str(max(0, count-1)), str(count+2)], 0
    
    def _generate_return_type_answer(self, context: Dict) -> bool:
        return True  # Default to true for simplicity
    
    def _generate_import_answers(self, context: Dict) -> Tuple[List[str], int]:
        real_import = context.get('import_name', 'requests')
        fake_imports = ['numpy', 'pandas', 'flask']
        return [real_import] + fake_imports[:3], 0
    
    def _generate_import_purpose_answer(self, context: Dict) -> bool:
        return True
    
    def _generate_class_type_answers(self, context: Dict) -> Tuple[List[str], int]:
        types = ['Data model', 'Service class', 'Utility class', 'Configuration class']
        return types, 0
    
    def _generate_method_count_answers(self, context: Dict) -> Tuple[List[str], int]:
        count = context.get('method_count', 3)
        return [str(count), str(count+1), str(count-1), str(count+2)], 0
    
    def _generate_structure_answers(self, context: Dict) -> Tuple[List[str], int]:
        structures = ['Class definitions', 'Function definitions', 'Variable declarations', 'Configuration']
        return structures, 0
    
    def _generate_container_answer(self, context: Dict) -> bool:
        return True
    
    def _generate_config_value_answers(self, context: Dict) -> Tuple[List[str], int]:
        value = context.get('config_value', 'true')
        return [value, 'false', 'null', '0'], 0
    
    def _generate_config_count_answer(self, context: Dict) -> bool:
        return True