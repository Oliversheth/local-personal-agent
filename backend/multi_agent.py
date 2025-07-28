"""
Multi-Agent Orchestration System
Coordinates three specialized agents for autonomous task execution
"""

import json
import asyncio
import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import requests
from datetime import datetime

class AgentRole(Enum):
    PLANNER = "planner"
    DESIGNER = "designer" 
    CODER = "coder"
    CONTEXT = "context"

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_REVISION = "needs_revision"

@dataclass
class Task:
    id: str
    type: str
    description: str
    agent: AgentRole
    status: TaskStatus
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    dependencies: List[str]
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None

@dataclass
class AgentMessage:
    id: str
    from_agent: AgentRole
    to_agent: AgentRole
    content: str
    task_id: str
    timestamp: datetime

class MultiAgentOrchestrator:
    def __init__(self, ollama_url: str, control_model: str, code_model: str):
        self.ollama_url = ollama_url
        self.control_model = control_model
        self.code_model = code_model
        self.tasks: Dict[str, Task] = {}
        self.messages: List[AgentMessage] = []
        self.active_session_id: Optional[str] = None
        
        # Agent system prompts
        self.agent_prompts = {
            AgentRole.PLANNER: """You are the Planner Agent in a multi-agent autonomous system. Your role is to:

1. Break down high-level objectives into ordered, actionable subtasks
2. Coordinate with Designer and Coder agents
3. Monitor progress and adapt plans based on results
4. Ensure task dependencies are properly sequenced

When given a complex goal, output a JSON plan with this structure:
{
    "plan_id": "unique_id",
    "objective": "high_level_goal",
    "subtasks": [
        {
            "id": "task_1",
            "type": "design|code|analysis|deployment",
            "description": "specific task description",
            "agent": "designer|coder",
            "dependencies": ["previous_task_ids"],
            "input_requirements": "what this task needs",
            "success_criteria": "how to measure completion"
        }
    ],
    "success_metrics": "overall success criteria"
}

Always think step-by-step and consider enterprise-grade requirements including testing, deployment, and risk management.""",

            AgentRole.DESIGNER: """You are the Designer/Imagination Agent in a multi-agent system. Your role is to:

1. Create detailed technical specifications from Planner requirements
2. Design system architecture, data flows, and user interfaces
3. Outline trading strategies and risk management frameworks
4. Generate wireframes, schemas, and configuration templates

Output detailed specifications including:
- System architecture diagrams (as text descriptions)
- Database schemas and API contracts
- UI/UX wireframes and component hierarchies
- Trading strategy logic and risk parameters
- Deployment and infrastructure requirements

Focus on enterprise-grade, production-ready designs with proper error handling, security, and scalability considerations.""",

            AgentRole.CODER: """You are the Coder Agent in a multi-agent system. Your role is to:

1. Implement code based on Designer specifications
2. Write tests and ensure code quality
3. Execute shell commands and file operations
4. Deploy and configure systems

You have access to these tools:
- write_file(path, content)
- run_shell(command)
- git_operations(action, params)
- docker_operations(action, params)
- install_dependencies(language, packages)

Always:
- Write clean, documented, production-ready code
- Include comprehensive error handling
- Follow best practices and design patterns
- Run tests before marking tasks complete
- Provide clear feedback on success/failure""",

            AgentRole.CONTEXT: """You are the Context Agent responsible for maintaining system memory and awareness. Your role is to:

1. Monitor filesystem changes and development progress
2. Track CLI history and system interactions
3. Maintain conversation and task context in vector database
4. Provide relevant context to other agents

You continuously update the knowledge base with:
- Code changes and development progress
- System interactions and command history
- Task results and agent communications
- Performance metrics and system status"""
        }

    async def process_goal(self, goal: str) -> Dict[str, Any]:
        """Main entry point for processing high-level goals"""
        session_id = str(uuid.uuid4())
        self.active_session_id = session_id
        
        try:
            # Step 1: Planner breaks down the goal
            plan = await self._call_planner(goal, session_id)
            
            # Step 2: Execute plan through agent coordination
            results = await self._execute_plan(plan, session_id)
            
            # Step 3: Final validation and delivery
            final_result = await self._finalize_execution(plan, results, session_id)
            
            return {
                "session_id": session_id,
                "status": "completed",
                "plan": plan,
                "results": results,
                "final_output": final_result
            }
            
        except Exception as e:
            return {
                "session_id": session_id,
                "status": "failed",
                "error": str(e),
                "tasks": [task.__dict__ for task in self.tasks.values()]
            }

    async def _call_planner(self, goal: str, session_id: str) -> Dict[str, Any]:
        """Have Planner agent create execution plan"""
        prompt = f"{self.agent_prompts[AgentRole.PLANNER]}\n\nGOAL: {goal}\n\nCreate a detailed execution plan:"
        
        response = await self._call_ollama(self.control_model, prompt)
        
        try:
            # Extract JSON from response
            plan = self._extract_json(response)
            plan["session_id"] = session_id
            
            # Create tasks from plan
            for subtask in plan.get("subtasks", []):
                task = Task(
                    id=subtask["id"],
                    type=subtask["type"],
                    description=subtask["description"],
                    agent=AgentRole(subtask["agent"]),
                    status=TaskStatus.PENDING,
                    input_data=subtask,
                    output_data={},
                    dependencies=subtask.get("dependencies", []),
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                self.tasks[task.id] = task
            
            return plan
            
        except Exception as e:
            raise Exception(f"Planner failed to create valid plan: {e}")

    async def _execute_plan(self, plan: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Execute plan through agent coordination"""
        results = {}
        
        # Execute tasks in dependency order
        executed_tasks = set()
        
        while len(executed_tasks) < len(plan.get("subtasks", [])):
            # Find tasks ready to execute (dependencies met)
            ready_tasks = []
            for task_id, task in self.tasks.items():
                if (task.status == TaskStatus.PENDING and 
                    all(dep in executed_tasks for dep in task.dependencies)):
                    ready_tasks.append(task)
            
            if not ready_tasks:
                # Check for circular dependencies or stuck tasks
                pending_tasks = [t for t in self.tasks.values() if t.status == TaskStatus.PENDING]
                if pending_tasks:
                    raise Exception(f"Execution stuck - unable to proceed with tasks: {[t.id for t in pending_tasks]}")
                break
            
            # Execute ready tasks
            for task in ready_tasks:
                try:
                    task.status = TaskStatus.IN_PROGRESS
                    task.updated_at = datetime.now()
                    
                    if task.agent == AgentRole.DESIGNER:
                        result = await self._call_designer(task)
                    elif task.agent == AgentRole.CODER:
                        result = await self._call_coder(task)
                    else:
                        raise Exception(f"Unknown agent type: {task.agent}")
                    
                    task.output_data = result
                    task.status = TaskStatus.COMPLETED
                    task.updated_at = datetime.now()
                    executed_tasks.add(task.id)
                    results[task.id] = result
                    
                except Exception as e:
                    task.status = TaskStatus.FAILED
                    task.error_message = str(e)
                    task.updated_at = datetime.now()
                    
                    # Attempt recovery
                    recovery_result = await self._attempt_recovery(task, e)
                    if recovery_result:
                        task.status = TaskStatus.COMPLETED
                        task.output_data = recovery_result
                        executed_tasks.add(task.id)
                        results[task.id] = recovery_result
                    else:
                        raise Exception(f"Task {task.id} failed: {e}")
        
        return results

    async def _call_designer(self, task: Task) -> Dict[str, Any]:
        """Call Designer agent for specification creation"""
        # Get context from previous tasks
        context = self._get_task_context(task)
        
        prompt = f"""{self.agent_prompts[AgentRole.DESIGNER]}

TASK: {task.description}
TYPE: {task.type}
INPUT: {json.dumps(task.input_data, indent=2)}
CONTEXT: {context}

Create detailed technical specifications for this task:"""

        response = await self._call_ollama(self.control_model, prompt)
        
        return {
            "type": "design_spec",
            "content": response,
            "task_id": task.id,
            "created_at": datetime.now().isoformat()
        }

    async def _call_coder(self, task: Task) -> Dict[str, Any]:
        """Call Coder agent for implementation"""
        # Get context and design specs
        context = self._get_task_context(task)
        
        prompt = f"""{self.agent_prompts[AgentRole.CODER]}

TASK: {task.description}
TYPE: {task.type}
INPUT: {json.dumps(task.input_data, indent=2)}
CONTEXT: {context}

Implement this task with code and configurations:"""

        response = await self._call_ollama(self.code_model, prompt)
        
        # Parse and execute any tool calls from the response
        tool_results = await self._execute_tool_calls(response, task)
        
        return {
            "type": "implementation",
            "content": response,
            "tool_results": tool_results,
            "task_id": task.id,
            "created_at": datetime.now().isoformat()
        }

    async def _call_ollama(self, model: str, prompt: str) -> str:
        """Make API call to Ollama"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=120
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama API error: {response.text}")
            
            return response.json().get("response", "")
            
        except Exception as e:
            raise Exception(f"Failed to call Ollama: {e}")

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON from text response"""
        # Look for JSON blocks
        import re
        
        # Try to find JSON in code blocks
        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        matches = re.findall(json_pattern, text, re.DOTALL)
        
        if matches:
            try:
                return json.loads(matches[0])
            except:
                pass
        
        # Try to find JSON in the text directly
        try:
            # Find the first { and last }
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end > start:
                return json.loads(text[start:end])
        except:
            pass
        
        raise Exception(f"No valid JSON found in response: {text[:200]}...")

    def _get_task_context(self, task: Task) -> str:
        """Get relevant context for a task"""
        context_parts = []
        
        # Add completed dependency outputs
        for dep_id in task.dependencies:
            if dep_id in self.tasks and self.tasks[dep_id].status == TaskStatus.COMPLETED:
                dep_task = self.tasks[dep_id]
                context_parts.append(f"Task {dep_id} Output: {dep_task.output_data}")
        
        # Add recent messages
        recent_messages = self.messages[-5:] if self.messages else []
        for msg in recent_messages:
            context_parts.append(f"{msg.from_agent.value} to {msg.to_agent.value}: {msg.content[:200]}")
        
        return "\n".join(context_parts)

    async def _execute_tool_calls(self, response: str, task: Task) -> List[Dict[str, Any]]:
        """Execute any tool calls found in the response"""
        tool_results = []
        
        # Import tool systems
        from enterprise_tools import EnterpriseTools
        from context_agent import context_agent
        
        enterprise_tools = EnterpriseTools()
        
        # Look for tool calls in response
        import re
        
        # Pattern to match old-style tool calls like: TOOL_CALL:function_name(param1, param2)
        tool_pattern = r'TOOL_CALL:(\w+)\((.*?)\)'
        tool_matches = re.findall(tool_pattern, response)
        
        for function_name, params_str in tool_matches:
            try:
                # Parse parameters
                params = self._parse_tool_params(params_str)
                
                # Execute the tool call
                if hasattr(enterprise_tools, function_name):
                    tool_func = getattr(enterprise_tools, function_name)
                    result = tool_func(**params)
                    
                    # Record the tool execution in context
                    context_agent.record_command_execution(
                        command=f"{function_name}({params_str})",
                        exit_code=0 if result.get('success', False) else 1,
                        stdout=str(result.get('output', '')),
                        stderr=str(result.get('error', '')),
                        duration=0.1,  # Estimated
                        working_directory=str(enterprise_tools.workspace_dir)
                    )
                    
                    tool_results.append({
                        "function": function_name,
                        "params": params,
                        "result": result,
                        "success": result.get('success', False)
                    })
                
            except Exception as e:
                tool_results.append({
                    "function": function_name,
                    "params": params_str,
                    "error": str(e),
                    "success": False
                })
        
        # Look for new-style JSON tool calls like: {"tool": "write_file", "args": {"path": "...", "content": "..."}}
        json_tool_pattern = r'\{"tool":\s*"([^"]+)",\s*"args":\s*(\{[^}]*\})\}'
        json_tool_matches = re.findall(json_tool_pattern, response)
        
        for tool_name, args_str in json_tool_matches:
            try:
                # Parse JSON arguments
                args = json.loads(args_str)
                
                # Execute the tool call via HTTP endpoint
                result = await self._call_tool_endpoint(tool_name, args)
                
                tool_results.append({
                    "tool": tool_name,
                    "args": args,
                    "result": result,
                    "success": result.get('success', False)
                })
                
            except Exception as e:
                tool_results.append({
                    "tool": tool_name,
                    "args": args_str,
                    "error": str(e),
                    "success": False
                })
        
        return tool_results

    async def _call_tool_endpoint(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Call the appropriate v1/tools endpoint for the given tool"""
        try:
            # Map tool names to endpoint paths and HTTP methods
            tool_endpoints = {
                "write_file": ("POST", "/v1/tools/write-file"),
                "make_dir": ("POST", "/v1/tools/make-dir"), 
                "run_shell": ("POST", "/v1/tools/run-shell"),
                "open_app": ("POST", "/v1/tools/open-app"),
                "list_dir": ("GET", "/v1/tools/list-dir")
            }
            
            if tool_name not in tool_endpoints:
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}"
                }
            
            method, endpoint = tool_endpoints[tool_name]
            base_url = "http://127.0.0.1:8001"  # FastAPI server
            
            if method == "GET" and tool_name == "list_dir":
                # Handle list_dir as GET with query parameter
                path = args.get("path", "")
                response = requests.get(f"{base_url}{endpoint}?path={path}", timeout=30)
            else:
                # Handle POST requests with JSON body
                response = requests.post(f"{base_url}{endpoint}", json=args, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _parse_tool_params(self, params_str: str) -> Dict[str, Any]:
        """Parse tool parameters from string"""
        params = {}
        if not params_str.strip():
            return params
        
        try:
            # Simple parameter parsing - in production, use proper parser
            parts = params_str.split(',')
            for part in parts:
                if '=' in part:
                    key, value = part.split('=', 1)
                    key = key.strip().strip('"\'')
                    value = value.strip().strip('"\'')
                    params[key] = value
        except Exception as e:
            print(f"Error parsing tool params: {e}")
        
        return params

    async def _attempt_recovery(self, task: Task, error: Exception) -> Optional[Dict[str, Any]]:
        """Attempt to recover from task failure"""
        # Simplified recovery - in full implementation, this would
        # involve re-planning or getting help from other agents
        return None

    async def _finalize_execution(self, plan: Dict[str, Any], results: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Finalize execution and prepare deliverables"""
        return {
            "execution_complete": True,
            "tasks_completed": len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED]),
            "tasks_failed": len([t for t in self.tasks.values() if t.status == TaskStatus.FAILED]),
            "deliverables": results,
            "session_id": session_id
        }

    def get_session_status(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get current session status"""
        target_session = session_id or self.active_session_id
        
        return {
            "session_id": target_session,
            "tasks": [
                {
                    "id": task.id,
                    "description": task.description,
                    "agent": task.agent.value,
                    "status": task.status.value,
                    "progress": self._calculate_task_progress(task),
                    "updated_at": task.updated_at.isoformat()
                }
                for task in self.tasks.values()
            ],
            "overall_progress": self._calculate_overall_progress()
        }

    def _calculate_task_progress(self, task: Task) -> float:
        """Calculate progress percentage for a task"""
        if task.status == TaskStatus.COMPLETED:
            return 100.0
        elif task.status == TaskStatus.IN_PROGRESS:
            return 50.0
        elif task.status == TaskStatus.FAILED:
            return 0.0
        else:
            return 0.0

    def _calculate_overall_progress(self) -> float:
        """Calculate overall progress percentage"""
        if not self.tasks:
            return 0.0
        
        total_progress = sum(self._calculate_task_progress(task) for task in self.tasks.values())
        return total_progress / len(self.tasks)