"""
Context Agent - Advanced Memory and System Awareness
Maintains comprehensive system context across sessions
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import hashlib
import subprocess

from memory import embed_and_store, retrieve_context, search_by_type

@dataclass
class FileSystemSnapshot:
    path: str
    content_hash: str
    size: int
    modified_time: datetime
    file_type: str

@dataclass
class CommandExecution:
    command: str
    exit_code: int
    stdout: str
    stderr: str
    duration: float
    timestamp: datetime
    working_directory: str

@dataclass
class AgentInteraction:
    session_id: str
    agent_from: str
    agent_to: str
    message_type: str
    content: str
    timestamp: datetime
    task_id: Optional[str] = None

@dataclass
class SystemMetrics:
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_activity: Dict[str, Any]
    timestamp: datetime

class ContextAgent:
    """Advanced context and memory management agent"""
    
    def __init__(self, workspace_dir: str = "/tmp/ai_workspace", monitoring_interval: int = 30):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(exist_ok=True)
        
        self.monitoring_interval = monitoring_interval
        self.last_fs_snapshot: Dict[str, FileSystemSnapshot] = {}
        self.command_history: List[CommandExecution] = []
        self.agent_interactions: List[AgentInteraction] = []
        self.system_metrics_history: List[SystemMetrics] = []
        
        # Initialize monitoring
        self.is_monitoring = False
        
    def start_monitoring(self):
        """Start continuous system monitoring"""
        self.is_monitoring = True
        self._monitor_filesystem()
        self._monitor_system_metrics()
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        self.is_monitoring = False
    
    def record_command_execution(self, command: str, exit_code: int, stdout: str, 
                               stderr: str, duration: float, working_directory: str):
        """Record command execution for context"""
        execution = CommandExecution(
            command=command,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            duration=duration,
            timestamp=datetime.now(),
            working_directory=working_directory
        )
        
        self.command_history.append(execution)
        
        # Store in vector database
        context_text = f"""Command Execution:
Command: {command}
Exit Code: {exit_code}
Duration: {duration:.2f}s
Working Directory: {working_directory}
Output: {stdout[:500]}
Error: {stderr[:500]}"""
        
        embed_and_store(
            id=f"cmd_{int(time.time())}_{hash(command) % 10000}",
            text=context_text,
            metadata={
                "type": "command_execution",
                "command": command,
                "exit_code": exit_code,
                "timestamp": execution.timestamp.isoformat()
            }
        )
    
    def record_agent_interaction(self, session_id: str, agent_from: str, agent_to: str,
                               message_type: str, content: str, task_id: Optional[str] = None):
        """Record inter-agent communication"""
        interaction = AgentInteraction(
            session_id=session_id,
            agent_from=agent_from,
            agent_to=agent_to,
            message_type=message_type,
            content=content,
            timestamp=datetime.now(),
            task_id=task_id
        )
        
        self.agent_interactions.append(interaction)
        
        # Store in vector database
        context_text = f"""Agent Interaction:
Session: {session_id}
From: {agent_from} → To: {agent_to}
Type: {message_type}
Task: {task_id or 'N/A'}
Content: {content[:1000]}"""
        
        embed_and_store(
            id=f"interaction_{session_id}_{int(time.time())}",
            text=context_text,
            metadata={
                "type": "agent_interaction",
                "session_id": session_id,
                "agent_from": agent_from,
                "agent_to": agent_to,
                "task_id": task_id,
                "timestamp": interaction.timestamp.isoformat()
            }
        )
    
    def record_file_system_change(self, file_path: str, change_type: str, content: Optional[str] = None):
        """Record filesystem changes"""
        try:
            path = Path(file_path)
            if path.exists():
                stat = path.stat()
                file_size = stat.st_size
                modified_time = datetime.fromtimestamp(stat.st_mtime)
                
                # Calculate content hash if it's a text file and small enough
                content_hash = ""
                if path.is_file() and file_size < 1024 * 1024:  # 1MB limit
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            file_content = f.read()
                            content_hash = hashlib.md5(file_content.encode()).hexdigest()
                    except:
                        content_hash = "binary_or_unreadable"
                
                snapshot = FileSystemSnapshot(
                    path=str(path),
                    content_hash=content_hash,
                    size=file_size,
                    modified_time=modified_time,
                    file_type=path.suffix
                )
                
                self.last_fs_snapshot[str(path)] = snapshot
                
                # Store in vector database
                context_text = f"""File System Change:
Path: {file_path}
Change Type: {change_type}
Size: {file_size} bytes
Modified: {modified_time}
Type: {path.suffix}
Content Preview: {content[:200] if content else 'N/A'}"""
                
                embed_and_store(
                    id=f"fs_{change_type}_{int(time.time())}_{hash(file_path) % 10000}",
                    text=context_text,
                    metadata={
                        "type": "filesystem_change",
                        "change_type": change_type,
                        "file_path": file_path,
                        "file_type": path.suffix,
                        "timestamp": datetime.now().isoformat()
                    }
                )
                
        except Exception as e:
            print(f"Error recording filesystem change: {e}")
    
    def get_session_context(self, session_id: str, context_types: List[str] = None) -> Dict[str, Any]:
        """Get comprehensive context for a session"""
        if context_types is None:
            context_types = ["agent_interaction", "command_execution", "filesystem_change"]
        
        context = {}
        
        for context_type in context_types:
            results = search_by_type(context_type, f"session {session_id}", n_results=10)
            context[context_type] = results
        
        # Add recent system metrics
        if self.system_metrics_history:
            context["system_metrics"] = self.system_metrics_history[-5:]
        
        # Add recent command history
        recent_commands = [
            cmd for cmd in self.command_history[-10:]
            if datetime.now() - cmd.timestamp < timedelta(hours=1)
        ]
        context["recent_commands"] = [asdict(cmd) for cmd in recent_commands]
        
        return context
    
    def get_development_context(self, project_path: str) -> Dict[str, Any]:
        """Get development-specific context for a project"""
        project_path = Path(project_path)
        context = {
            "project_files": [],
            "git_status": {},
            "dependencies": {},
            "recent_changes": []
        }
        
        try:
            # Scan project files
            if project_path.exists():
                for file_path in project_path.rglob("*"):
                    if file_path.is_file() and not any(part.startswith('.') for part in file_path.parts):
                        relative_path = file_path.relative_to(project_path)
                        context["project_files"].append({
                            "path": str(relative_path),
                            "size": file_path.stat().st_size,
                            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                        })
            
            # Get git status if it's a git repo
            try:
                git_status = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=project_path,
                    capture_output=True,
                    text=True
                )
                if git_status.returncode == 0:
                    context["git_status"] = {
                        "is_git_repo": True,
                        "changes": git_status.stdout.split('\n') if git_status.stdout else [],
                        "clean": len(git_status.stdout.strip()) == 0
                    }
            except:
                context["git_status"] = {"is_git_repo": False}
            
            # Check for common dependency files
            dep_files = {
                "package.json": "npm",
                "requirements.txt": "pip",
                "Cargo.toml": "cargo",
                "go.mod": "go",
                "pom.xml": "maven"
            }
            
            for dep_file, package_manager in dep_files.items():
                if (project_path / dep_file).exists():
                    context["dependencies"][package_manager] = dep_file
            
        except Exception as e:
            context["error"] = str(e)
        
        return context
    
    def get_trading_context(self, strategy_name: str = None) -> Dict[str, Any]:
        """Get trading and quantitative analysis context"""
        context = {
            "recent_backtests": [],
            "strategy_performance": {},
            "market_data_status": {},
            "risk_metrics": {}
        }
        
        # Get recent backtest results from vector database
        backtest_results = search_by_type("backtest_result", strategy_name or "backtest", n_results=5)
        context["recent_backtests"] = backtest_results
        
        # Get strategy-specific context
        if strategy_name:
            strategy_context = search_by_type("trading_strategy", strategy_name, n_results=10)
            context["strategy_performance"] = strategy_context
        
        return context
    
    def _monitor_filesystem(self):
        """Monitor filesystem changes (simplified version)"""
        if not self.is_monitoring:
            return
        
        try:
            # This is a simplified version - in production, you'd use watchdog or similar
            for root, dirs, files in os.walk(self.workspace_dir):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    if not file.startswith('.'):
                        file_path = Path(root) / file
                        # Check if file has changed since last snapshot
                        current_mtime = file_path.stat().st_mtime
                        
                        if str(file_path) not in self.last_fs_snapshot:
                            self.record_file_system_change(str(file_path), "created")
                        else:
                            last_snapshot = self.last_fs_snapshot[str(file_path)]
                            if current_mtime > last_snapshot.modified_time.timestamp():
                                self.record_file_system_change(str(file_path), "modified")
        
        except Exception as e:
            print(f"Filesystem monitoring error: {e}")
    
    def _monitor_system_metrics(self):
        """Monitor system performance metrics"""
        if not self.is_monitoring:
            return
        
        try:
            import psutil
            
            metrics = SystemMetrics(
                cpu_usage=psutil.cpu_percent(),
                memory_usage=psutil.virtual_memory().percent,
                disk_usage=psutil.disk_usage('/').percent,
                network_activity={
                    "bytes_sent": psutil.net_io_counters().bytes_sent,
                    "bytes_recv": psutil.net_io_counters().bytes_recv
                },
                timestamp=datetime.now()
            )
            
            self.system_metrics_history.append(metrics)
            
            # Keep only last 100 metrics
            if len(self.system_metrics_history) > 100:
                self.system_metrics_history = self.system_metrics_history[-100:]
        
        except ImportError:
            print("psutil not available for system monitoring")
        except Exception as e:
            print(f"System monitoring error: {e}")
    
    def get_relevant_context(self, query: str, session_id: str = None, limit: int = 10) -> str:
        """Get relevant context based on query"""
        # Use vector similarity search
        context_parts = []
        
        # Get general context
        general_context = retrieve_context(query, limit // 2)
        if general_context:
            context_parts.append(f"General Context:\n{general_context}")
        
        # Get session-specific context if provided
        if session_id:
            session_context = self.get_session_context(session_id)
            if session_context.get("agent_interaction"):
                interactions = session_context["agent_interaction"][:3]
                interaction_text = "\n".join([
                    f"- {item['metadata'].get('agent_from', 'Unknown')} → {item['metadata'].get('agent_to', 'Unknown')}: {item['content'][:100]}..."
                    for item in interactions
                ])
                context_parts.append(f"Recent Session Interactions:\n{interaction_text}")
        
        # Get recent commands
        if self.command_history:
            recent_commands = self.command_history[-3:]
            commands_text = "\n".join([
                f"- {cmd.command} (exit: {cmd.exit_code})"
                for cmd in recent_commands
            ])
            context_parts.append(f"Recent Commands:\n{commands_text}")
        
        return "\n\n".join(context_parts)
    
    def cleanup_old_data(self, days_old: int = 7):
        """Clean up old context data"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        # Clean command history
        self.command_history = [
            cmd for cmd in self.command_history
            if cmd.timestamp > cutoff_date
        ]
        
        # Clean agent interactions
        self.agent_interactions = [
            interaction for interaction in self.agent_interactions
            if interaction.timestamp > cutoff_date
        ]
        
        # Clean system metrics
        self.system_metrics_history = [
            metrics for metrics in self.system_metrics_history
            if metrics.timestamp > cutoff_date
        ]
    
    def export_session_context(self, session_id: str) -> Dict[str, Any]:
        """Export complete session context for analysis"""
        context = self.get_session_context(session_id)
        
        # Add summary statistics
        context["summary"] = {
            "total_interactions": len([
                i for i in self.agent_interactions 
                if i.session_id == session_id
            ]),
            "total_commands": len([
                cmd for cmd in self.command_history
                if session_id in cmd.command  # Simple heuristic
            ]),
            "session_duration": None,  # Would calculate from first/last interaction
            "success_rate": None  # Would calculate from task completion rates
        }
        
        return context

# Global context agent instance
context_agent = ContextAgent()