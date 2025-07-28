import os
import requests
from dotenv import load_dotenv
import json
from typing import List, Dict, Any
from memory import retrieve_context

# Load environment variables
load_dotenv()
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
CONTROL_MODEL = os.getenv("CONTROL_MODEL", "codellama:instruct")
CODE_MODEL = os.getenv("CODE_MODEL", "deepseek-coder")

def plan(goal: str) -> List[Dict[str, Any]]:
    """
    Takes a human-readable goal string and breaks it down into subtasks.
    Calls Ollama with CONTROL_MODEL to generate a plan.
    Returns a JSON-parsed list of subtasks.
    """
    try:
        prompt = f"""You are a planner agent. Break down the following goal into a detailed list of subtasks.
Return your response as a JSON array of task objects, where each task has:
- "id": unique task identifier
- "title": brief task title
- "description": detailed task description
- "dependencies": list of task IDs this task depends on
- "estimated_time": estimated time in minutes
- "agent": which agent should handle this ("planner", "designer", "coder", "context")

Goal: {goal}

Respond with only the JSON array, no additional text."""

        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": CONTROL_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )

        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.text}")

        response_data = response.json()
        result_text = response_data.get("response", "")
        
        # Try to parse JSON from the response
        try:
            # Look for JSON array in the response
            start_idx = result_text.find('[')
            end_idx = result_text.rfind(']') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = result_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Fallback: create a simple task structure
                return [{
                    "id": "task_1",
                    "title": "Execute Goal",
                    "description": goal,
                    "dependencies": [],
                    "estimated_time": 30,
                    "agent": "coder"
                }]
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return [{
                "id": "task_1",
                "title": "Execute Goal", 
                "description": goal,
                "dependencies": [],
                "estimated_time": 30,
                "agent": "coder"
            }]
            
    except Exception as e:
        print(f"Error in plan function: {str(e)}")
        # Return a basic fallback plan
        return [{
            "id": "task_1",
            "title": "Execute Goal",
            "description": goal,
            "dependencies": [],
            "estimated_time": 30,
            "agent": "coder"
        }]

def design(task: Dict[str, Any]) -> Dict[str, Any]:
    """
    Takes one subtask dict and elaborates the architecture or UI design.
    Calls Ollama with CONTROL_MODEL to create detailed specifications.
    Returns a JSON spec dict.
    """
    try:
        prompt = f"""You are a designer agent. Create a detailed specification for the following task.
Return your response as a JSON object with these fields:
- "architecture": high-level architecture description
- "components": list of components/modules needed
- "interfaces": API endpoints or UI interfaces
- "data_structures": required data structures
- "dependencies": external dependencies needed
- "implementation_notes": key implementation considerations

Task: {task.get('title', 'Unknown Task')}
Description: {task.get('description', 'No description')}

Respond with only the JSON object, no additional text."""

        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": CONTROL_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )

        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.text}")

        response_data = response.json()
        result_text = response_data.get("response", "")
        
        # Try to parse JSON from the response
        try:
            # Look for JSON object in the response
            start_idx = result_text.find('{')
            end_idx = result_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = result_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Fallback specification
                return {
                    "architecture": "Simple implementation",
                    "components": [task.get('title', 'Main Component')],
                    "interfaces": [],
                    "data_structures": {},
                    "dependencies": [],
                    "implementation_notes": task.get('description', 'No specific notes')
                }
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "architecture": "Simple implementation",
                "components": [task.get('title', 'Main Component')],
                "interfaces": [],
                "data_structures": {},
                "dependencies": [],
                "implementation_notes": task.get('description', 'No specific notes')
            }
            
    except Exception as e:
        print(f"Error in design function: {str(e)}")
        # Return a basic fallback design
        return {
            "architecture": "Simple implementation",
            "components": [task.get('title', 'Main Component')],
            "interfaces": [],
            "data_structures": {},
            "dependencies": [],
            "implementation_notes": task.get('description', 'Error occurred during design')
        }

def code(spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Takes a spec dict and generates code and tests.
    Calls Ollama with CODE_MODEL to implement the solution.
    Returns a dict with keys files_written, stdout, and errors.
    """
    try:
        prompt = f"""You are a coder agent. Implement the following specification.
Return your response as a JSON object with these fields:
- "files_written": array of objects with "filename" and "content" keys
- "stdout": string with any output messages
- "errors": array of any error messages

Specification:
Architecture: {spec.get('architecture', 'Not specified')}
Components: {spec.get('components', [])}
Implementation Notes: {spec.get('implementation_notes', 'None')}

Generate clean, production-ready code with appropriate error handling.
Respond with only the JSON object, no additional text."""

        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": CODE_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=120  # Longer timeout for code generation
        )

        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.text}")

        response_data = response.json()
        result_text = response_data.get("response", "")
        
        # Try to parse JSON from the response
        try:
            # Look for JSON object in the response
            start_idx = result_text.find('{')
            end_idx = result_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = result_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Fallback: extract code blocks and create structure
                files_written = []
                # Simple heuristic to find code blocks
                lines = result_text.split('\n')
                current_file = None
                current_content = []
                
                for line in lines:
                    if line.strip().endswith('.py:') or line.strip().endswith('.js:') or line.strip().endswith('.html:'):
                        if current_file:
                            files_written.append({
                                "filename": current_file,
                                "content": '\n'.join(current_content)
                            })
                        current_file = line.strip().rstrip(':')
                        current_content = []
                    elif current_file and line.strip():
                        current_content.append(line)
                
                if current_file:
                    files_written.append({
                        "filename": current_file,
                        "content": '\n'.join(current_content)
                    })
                
                return {
                    "files_written": files_written,
                    "stdout": "Code generated successfully",
                    "errors": []
                }
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "files_written": [{
                    "filename": "implementation.py",
                    "content": f"# Implementation for: {spec.get('architecture', 'Unknown')}\n# TODO: Implement based on specification"
                }],
                "stdout": "Generated basic implementation template",
                "errors": ["JSON parsing failed, created template"]
            }
            
    except Exception as e:
        print(f"Error in code function: {str(e)}")
        # Return a basic error response
        return {
            "files_written": [],
            "stdout": "",
            "errors": [f"Code generation failed: {str(e)}"]
        }

def context(query: str) -> str:
    """
    Takes a text query and retrieves relevant context from the vector store.
    Returns a single string with relevant documents joined by newlines.
    """
    try:
        # Use the memory module's retrieve_context function
        result = retrieve_context(query, n_results=5)
        return result if result else ""
    except Exception as e:
        print(f"Error in context function: {str(e)}")
        return ""
