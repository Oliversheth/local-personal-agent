"""
Enterprise Development Tools
Advanced file system, shell, git, and deployment operations
"""

import os
import subprocess
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
import docker
import git
from datetime import datetime

class EnterpriseTools:
    def __init__(self, workspace_dir: str = "/tmp/ai_workspace"):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(exist_ok=True)
        self.current_project_path: Optional[Path] = None
        
        # Initialize Docker client
        try:
            self.docker_client = docker.from_env()
        except Exception as e:
            print(f"Docker not available: {e}")
            self.docker_client = None

    def write_file(self, file_path: str, content: str, project_relative: bool = True) -> Dict[str, Any]:
        """Write content to a file"""
        try:
            if project_relative and self.current_project_path:
                full_path = self.current_project_path / file_path
            else:
                full_path = Path(file_path)
            
            # Create directory if it doesn't exist
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "path": str(full_path),
                "size": len(content),
                "message": f"File written successfully: {full_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "path": file_path
            }

    def read_file(self, file_path: str, project_relative: bool = True) -> Dict[str, Any]:
        """Read content from a file"""
        try:
            if project_relative and self.current_project_path:
                full_path = self.current_project_path / file_path
            else:
                full_path = Path(file_path)
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "success": True,
                "path": str(full_path),
                "content": content,
                "size": len(content)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "path": file_path
            }

    def run_shell(self, command: str, cwd: Optional[str] = None, timeout: int = 300) -> Dict[str, Any]:
        """Execute shell command"""
        try:
            work_dir = cwd or (str(self.current_project_path) if self.current_project_path else str(self.workspace_dir))
            
            result = subprocess.run(
                command,
                shell=True,
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": command,
                "cwd": work_dir
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Command timed out after {timeout} seconds",
                "command": command
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": command
            }

    def create_project(self, project_name: str, project_type: str = "fullstack") -> Dict[str, Any]:
        """Create a new project structure"""
        try:
            project_path = self.workspace_dir / project_name
            project_path.mkdir(exist_ok=True)
            self.current_project_path = project_path
            
            # Create basic structure based on project type
            if project_type == "fullstack":
                self._create_fullstack_structure(project_path)
            elif project_type == "python":
                self._create_python_structure(project_path)
            elif project_type == "react":
                self._create_react_structure(project_path)
            elif project_type == "trading":
                self._create_trading_structure(project_path)
            
            return {
                "success": True,
                "project_path": str(project_path),
                "project_type": project_type,
                "message": f"Project {project_name} created successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "project_name": project_name
            }

    def _create_fullstack_structure(self, project_path: Path):
        """Create full-stack project structure"""
        # Frontend
        (project_path / "frontend" / "src" / "components").mkdir(parents=True)
        (project_path / "frontend" / "public").mkdir(parents=True)
        
        # Backend
        (project_path / "backend" / "src" / "routes").mkdir(parents=True)
        (project_path / "backend" / "tests").mkdir(parents=True)
        
        # Database
        (project_path / "database" / "migrations").mkdir(parents=True)
        
        # DevOps
        (project_path / "docker").mkdir(parents=True)
        (project_path / ".github" / "workflows").mkdir(parents=True)
        
        # Docs
        (project_path / "docs").mkdir(parents=True)

    def _create_python_structure(self, project_path: Path):
        """Create Python project structure"""
        (project_path / "src").mkdir(parents=True)
        (project_path / "tests").mkdir(parents=True)
        (project_path / "docs").mkdir(parents=True)

    def _create_react_structure(self, project_path: Path):
        """Create React project structure"""
        (project_path / "src" / "components").mkdir(parents=True)
        (project_path / "src" / "hooks").mkdir(parents=True)
        (project_path / "src" / "utils").mkdir(parents=True)
        (project_path / "public").mkdir(parents=True)

    def _create_trading_structure(self, project_path: Path):
        """Create trading project structure"""
        (project_path / "strategies").mkdir(parents=True)
        (project_path / "backtesting").mkdir(parents=True)
        (project_path / "data").mkdir(parents=True)
        (project_path / "risk_management").mkdir(parents=True)
        (project_path / "notebooks").mkdir(parents=True)

    def install_dependencies(self, language: str, packages: List[str]) -> Dict[str, Any]:
        """Install dependencies for various languages"""
        try:
            if language.lower() == "python":
                command = f"pip install {' '.join(packages)}"
            elif language.lower() in ["node", "javascript", "react"]:
                command = f"npm install {' '.join(packages)}"
            elif language.lower() == "go":
                command = f"go get {' '.join(packages)}"
            else:
                return {
                    "success": False,
                    "error": f"Unsupported language: {language}"
                }
            
            result = self.run_shell(command)
            return {
                "success": result["success"],
                "language": language,
                "packages": packages,
                "output": result.get("stdout", ""),
                "error": result.get("stderr", "")
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "language": language,
                "packages": packages
            }

    def git_init(self, remote_url: Optional[str] = None) -> Dict[str, Any]:
        """Initialize git repository"""
        try:
            if not self.current_project_path:
                return {"success": False, "error": "No active project"}
            
            repo = git.Repo.init(self.current_project_path)
            
            if remote_url:
                repo.create_remote('origin', remote_url)
            
            return {
                "success": True,
                "path": str(self.current_project_path),
                "remote_url": remote_url,
                "message": "Git repository initialized"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def git_commit(self, message: str, add_all: bool = True) -> Dict[str, Any]:
        """Commit changes to git"""
        try:
            if not self.current_project_path:
                return {"success": False, "error": "No active project"}
            
            repo = git.Repo(self.current_project_path)
            
            if add_all:
                repo.git.add('.')
            
            commit = repo.index.commit(message)
            
            return {
                "success": True,
                "commit_hash": commit.hexsha,
                "message": message,
                "files_changed": len(commit.stats.files)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def git_push(self, branch: str = "main") -> Dict[str, Any]:
        """Push changes to remote repository"""
        try:
            if not self.current_project_path:
                return {"success": False, "error": "No active project"}
            
            repo = git.Repo(self.current_project_path)
            origin = repo.remote('origin')
            origin.push(branch)
            
            return {
                "success": True,
                "branch": branch,
                "message": f"Pushed to {branch}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def docker_build(self, image_name: str, dockerfile_path: str = "Dockerfile") -> Dict[str, Any]:
        """Build Docker image"""
        try:
            if not self.docker_client:
                return {"success": False, "error": "Docker not available"}
            
            if not self.current_project_path:
                return {"success": False, "error": "No active project"}
            
            image, logs = self.docker_client.images.build(
                path=str(self.current_project_path),
                dockerfile=dockerfile_path,
                tag=image_name
            )
            
            return {
                "success": True,
                "image_id": image.id,
                "image_name": image_name,
                "size": image.attrs.get('Size', 0)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def docker_run(self, image_name: str, ports: Dict[str, str] = None, environment: Dict[str, str] = None) -> Dict[str, Any]:
        """Run Docker container"""
        try:
            if not self.docker_client:
                return {"success": False, "error": "Docker not available"}
            
            container = self.docker_client.containers.run(
                image_name,
                detach=True,
                ports=ports or {},
                environment=environment or {}
            )
            
            return {
                "success": True,
                "container_id": container.id,
                "container_name": container.name,
                "status": container.status
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def open_vscode(self, path: Optional[str] = None) -> Dict[str, Any]:
        """Open project in VSCode"""
        try:
            target_path = path or (str(self.current_project_path) if self.current_project_path else str(self.workspace_dir))
            
            result = self.run_shell(f"code {target_path}")
            return {
                "success": result["success"],
                "path": target_path,
                "message": "VSCode opened" if result["success"] else "Failed to open VSCode"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def deploy_local(self, deployment_type: str = "docker-compose") -> Dict[str, Any]:
        """Deploy application locally"""
        try:
            if not self.current_project_path:
                return {"success": False, "error": "No active project"}
            
            if deployment_type == "docker-compose":
                result = self.run_shell("docker-compose up -d")
            elif deployment_type == "npm":
                result = self.run_shell("npm start")
            elif deployment_type == "python":
                result = self.run_shell("python main.py")
            else:
                return {"success": False, "error": f"Unknown deployment type: {deployment_type}"}
            
            return {
                "success": result["success"],
                "deployment_type": deployment_type,
                "output": result.get("stdout", ""),
                "error": result.get("stderr", "")
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def list_files(self, directory: str = ".", recursive: bool = False) -> Dict[str, Any]:
        """List files in directory"""
        try:
            if self.current_project_path:
                base_path = self.current_project_path / directory
            else:
                base_path = Path(directory)
            
            if recursive:
                files = [str(p.relative_to(base_path)) for p in base_path.rglob("*") if p.is_file()]
            else:
                files = [p.name for p in base_path.iterdir() if p.is_file()]
            
            return {
                "success": True,
                "directory": str(base_path),
                "files": files,
                "count": len(files)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_project_status(self) -> Dict[str, Any]:
        """Get current project status"""
        if not self.current_project_path:
            return {
                "has_project": False,
                "workspace_dir": str(self.workspace_dir)
            }
        
        try:
            # Check git status
            git_status = {}
            try:
                repo = git.Repo(self.current_project_path)
                git_status = {
                    "is_git_repo": True,
                    "active_branch": str(repo.active_branch),
                    "is_dirty": repo.is_dirty(),
                    "untracked_files": repo.untracked_files
                }
            except:
                git_status = {"is_git_repo": False}
            
            # Count files
            file_count = len(list(self.current_project_path.rglob("*")))
            
            return {
                "has_project": True,
                "project_path": str(self.current_project_path),
                "project_name": self.current_project_path.name,
                "file_count": file_count,
                "git_status": git_status,
                "docker_available": self.docker_client is not None
            }
        except Exception as e:
            return {
                "has_project": True,
                "project_path": str(self.current_project_path),
                "error": str(e)
            }