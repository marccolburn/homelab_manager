#!/usr/bin/env python3
"""
Flask Backend API for Homelab Manager

Provides RESTful API endpoints for lab management operations.
Both the CLI and web UI communicate with this backend.
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import yaml
import json
import subprocess
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging
import threading
import uuid

app = Flask(__name__, static_folder='web/static')
CORS(app)

# Configuration
DEFAULT_CONFIG_DIR = Path.home() / ".labctl"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.yaml"
DEFAULT_STATE_FILE = DEFAULT_CONFIG_DIR / "state.json"
DEFAULT_REPOS_DIR = DEFAULT_CONFIG_DIR / "repos"
DEFAULT_LOGS_DIR = DEFAULT_CONFIG_DIR / "logs"

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LabManager:
    """Core lab management functionality"""
    
    def __init__(self):
        self.config = self._load_config()
        self.state = self._load_state()
        self._ensure_directories()
        self.active_tasks = {}  # Track async operations
    
    def _load_config(self) -> Dict:
        """Load configuration file"""
        if not DEFAULT_CONFIG_FILE.exists():
            # Create default config
            DEFAULT_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            default_config = {
                "repos_dir": str(DEFAULT_REPOS_DIR),
                "logs_dir": str(DEFAULT_LOGS_DIR),
                "state_file": str(DEFAULT_STATE_FILE),
                "clab_tools_cmd": "clab-tools",
                "git_cmd": "git",
                "monitoring": {
                    "prometheus": "http://localhost:9090",
                    "grafana": "http://localhost:3000"
                },
                "netbox": {
                    "enabled": False,
                    "url": "",
                    "token": "",
                    "default_prefix": "10.100.100.0/24"
                }
            }
            with open(DEFAULT_CONFIG_FILE, 'w') as f:
                yaml.dump(default_config, f, default_flow_style=False)
            return default_config
        
        with open(DEFAULT_CONFIG_FILE) as f:
            return yaml.safe_load(f)
    
    def _load_state(self) -> Dict:
        """Load state file"""
        state_file = Path(self.config.get("state_file", DEFAULT_STATE_FILE))
        if not state_file.exists():
            return {"repos": {}, "deployments": {}}
        
        with open(state_file) as f:
            return json.load(f)
    
    def _save_state(self):
        """Save state file"""
        state_file = Path(self.config.get("state_file", DEFAULT_STATE_FILE))
        state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def _ensure_directories(self):
        """Ensure required directories exist"""
        for dir_key in ["repos_dir", "logs_dir"]:
            dir_path = Path(self.config.get(dir_key, ""))
            if dir_path:
                dir_path.mkdir(parents=True, exist_ok=True)
    
    def _run_command(self, cmd: List[str], cwd: Optional[Path] = None, 
                     capture_output: bool = True) -> subprocess.CompletedProcess:
        """Run a command and handle errors"""
        logger.debug(f"Running command: {' '.join(cmd)}")
        if cwd:
            logger.debug(f"Working directory: {cwd}")
        
        result = subprocess.run(
            cmd, 
            cwd=cwd, 
            capture_output=capture_output,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Command failed: {' '.join(cmd)}")
            if capture_output:
                logger.error(f"Error output: {result.stderr}")
        
        return result
    
    def add_repo(self, repo_url: str, name: Optional[str] = None) -> Dict:
        """Clone and register a lab repository"""
        # Extract repo name from URL if not provided
        if not name:
            name = repo_url.split('/')[-1].replace('.git', '')
        
        repo_path = Path(self.config["repos_dir"]) / name
        
        # Clone repository
        if repo_path.exists():
            logger.info(f"Repository {name} already exists, updating...")
            result = self._run_command([self.config["git_cmd"], "pull"], cwd=repo_path)
        else:
            logger.info(f"Cloning repository {repo_url}...")
            result = self._run_command(
                [self.config["git_cmd"], "clone", repo_url, str(repo_path)]
            )
        
        if result.returncode != 0:
            return {
                "success": False,
                "error": f"Git operation failed: {result.stderr}"
            }
        
        # Load lab metadata
        metadata_file = repo_path / "lab-metadata.yaml"
        if not metadata_file.exists():
            return {
                "success": False,
                "error": f"lab-metadata.yaml not found in {name}"
            }
        
        with open(metadata_file) as f:
            metadata = yaml.safe_load(f)
        
        # Update state
        self.state["repos"][name] = {
            "path": str(repo_path),
            "url": repo_url,
            "metadata": metadata,
            "added": datetime.now().isoformat()
        }
        self._save_state()
        
        return {
            "success": True,
            "lab_id": name,
            "metadata": metadata
        }
    
    def list_repos(self) -> List[Dict]:
        """List all registered lab repositories"""
        repos = []
        for repo_id, repo_info in self.state["repos"].items():
            metadata = repo_info.get("metadata", {})
            repos.append({
                "id": repo_id,
                "name": metadata.get("name", repo_id),
                "version": metadata.get("version", "unknown"),
                "category": metadata.get("category", "uncategorized"),
                "vendor": metadata.get("vendor", "unknown"),
                "difficulty": metadata.get("difficulty", "unknown"),
                "description": metadata.get("description", {}),
                "requirements": metadata.get("requirements", {}),
                "tags": metadata.get("tags", []),
                "path": repo_info["path"],
                "url": repo_info["url"]
            })
        return repos
    
    def update_repo(self, lab_id: str) -> Dict:
        """Update a lab repository"""
        if lab_id not in self.state["repos"]:
            return {"success": False, "error": f"Lab {lab_id} not found"}
        
        repo_path = Path(self.state["repos"][lab_id]["path"])
        
        # Git pull
        result = self._run_command(
            [self.config["git_cmd"], "pull"],
            cwd=repo_path
        )
        
        if result.returncode != 0:
            return {"success": False, "error": f"Git pull failed: {result.stderr}"}
        
        # Reload metadata
        metadata_file = repo_path / "lab-metadata.yaml"
        with open(metadata_file) as f:
            metadata = yaml.safe_load(f)
        
        self.state["repos"][lab_id]["metadata"] = metadata
        self._save_state()
        
        return {"success": True, "message": "Repository updated"}
    
    def remove_repo(self, lab_id: str) -> Dict:
        """Remove a lab repository"""
        if lab_id not in self.state["repos"]:
            return {"success": False, "error": f"Lab {lab_id} not found"}
        
        # Check if lab is deployed
        for dep_id, dep_info in self.state["deployments"].items():
            if dep_info["lab_id"] == lab_id and dep_info["status"] == "active":
                return {
                    "success": False,
                    "error": f"Cannot remove lab with active deployment: {dep_id}"
                }
        
        # Remove from state
        del self.state["repos"][lab_id]
        self._save_state()
        
        # Optionally remove directory
        # repo_path = Path(self.state["repos"][lab_id]["path"])
        # if repo_path.exists():
        #     shutil.rmtree(repo_path)
        
        return {"success": True, "message": f"Lab {lab_id} removed"}
    
    def deploy_lab_async(self, lab_id: str, version: Optional[str] = None, 
                        allocate_ips: bool = False) -> str:
        """Deploy a lab asynchronously"""
        task_id = str(uuid.uuid4())
        
        def deploy_task():
            self.active_tasks[task_id] = {
                "status": "running",
                "lab_id": lab_id,
                "started": datetime.now().isoformat()
            }
            
            result = self._deploy_lab(lab_id, version, allocate_ips)
            
            self.active_tasks[task_id]["status"] = "completed"
            self.active_tasks[task_id]["result"] = result
            self.active_tasks[task_id]["completed"] = datetime.now().isoformat()
        
        thread = threading.Thread(target=deploy_task)
        thread.start()
        
        return task_id
    
    def _deploy_lab(self, lab_id: str, version: Optional[str] = None, 
                    allocate_ips: bool = False) -> Dict:
        """Deploy a lab using clab-tools"""
        if lab_id not in self.state["repos"]:
            return {"success": False, "error": f"Lab {lab_id} not found"}
        
        repo_info = self.state["repos"][lab_id]
        repo_path = Path(repo_info["path"])
        
        # Checkout specific version if requested
        if version and version != "latest":
            logger.info(f"Checking out version {version}...")
            result = self._run_command(
                [self.config["git_cmd"], "checkout", version],
                cwd=repo_path
            )
            if result.returncode != 0:
                return {"success": False, "error": f"Failed to checkout version: {result.stderr}"}
        
        # TODO: Implement NetBox IP allocation if allocate_ips is True
        if allocate_ips and self.config.get("netbox", {}).get("enabled"):
            logger.info("Allocating IPs from NetBox...")
            # Implementation needed
        
        # Create deployment log
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        deployment_id = f"{lab_id}_{timestamp}"
        log_file = Path(self.config["logs_dir"]) / f"{deployment_id}.log"
        
        # Run bootstrap script
        bootstrap_script = repo_path / "clab_tools_files" / "bootstrap.sh"
        if not bootstrap_script.exists():
            return {"success": False, "error": "bootstrap.sh not found"}
        
        logger.info(f"Deploying lab {lab_id}...")
        
        # Make bootstrap script executable
        os.chmod(bootstrap_script, 0o755)
        
        # Run bootstrap with output to log file
        with open(log_file, 'w') as log:
            result = subprocess.run(
                [str(bootstrap_script)],
                cwd=repo_path / "clab_tools_files",
                stdout=log,
                stderr=subprocess.STDOUT,
                text=True
            )
        
        if result.returncode == 0:
            # Update deployment state
            self.state["deployments"][deployment_id] = {
                "lab_id": lab_id,
                "version": version or "latest",
                "deployed_at": datetime.now().isoformat(),
                "log_file": str(log_file),
                "status": "active"
            }
            self._save_state()
            
            return {
                "success": True,
                "deployment_id": deployment_id,
                "message": f"Lab {lab_id} deployed successfully"
            }
        else:
            return {
                "success": False,
                "error": f"Deployment failed. Check log: {log_file}"
            }
    
    def destroy_lab(self, lab_id: str) -> Dict:
        """Teardown a deployed lab"""
        # Find active deployment
        active_deployment = None
        for dep_id, dep_info in self.state["deployments"].items():
            if dep_info["lab_id"] == lab_id and dep_info["status"] == "active":
                active_deployment = dep_id
                break
        
        if not active_deployment:
            return {"success": False, "error": f"No active deployment found for {lab_id}"}
        
        repo_info = self.state["repos"][lab_id]
        repo_path = Path(repo_info["path"])
        
        # Run teardown script
        teardown_script = repo_path / "clab_tools_files" / "teardown.sh"
        if not teardown_script.exists():
            return {"success": False, "error": "teardown.sh not found"}
        
        logger.info(f"Destroying lab {lab_id}...")
        
        # Make teardown script executable
        os.chmod(teardown_script, 0o755)
        
        # Run teardown
        result = self._run_command(
            [str(teardown_script)],
            cwd=repo_path / "clab_tools_files",
            capture_output=False
        )
        
        if result.returncode == 0:
            # Update deployment state
            self.state["deployments"][active_deployment]["status"] = "destroyed"
            self.state["deployments"][active_deployment]["destroyed_at"] = datetime.now().isoformat()
            self._save_state()
            
            return {
                "success": True,
                "message": f"Lab {lab_id} destroyed successfully"
            }
        else:
            return {"success": False, "error": "Teardown failed"}
    
    def get_status(self) -> Dict:
        """Get status of all deployments"""
        active_deployments = []
        for dep_id, dep_info in self.state["deployments"].items():
            if dep_info["status"] == "active":
                lab_metadata = self.state["repos"][dep_info["lab_id"]]["metadata"]
                active_deployments.append({
                    "deployment_id": dep_id,
                    "lab_id": dep_info["lab_id"],
                    "lab_name": lab_metadata.get("name", dep_info["lab_id"]),
                    "version": dep_info["version"],
                    "deployed_at": dep_info["deployed_at"]
                })
        
        return {
            "deployments": active_deployments,
            "total": len(active_deployments)
        }
    
    def get_task_status(self, task_id: str) -> Dict:
        """Get status of an async task"""
        if task_id not in self.active_tasks:
            return {"error": "Task not found"}
        
        return self.active_tasks[task_id]
    
    def list_config_scenarios(self, lab_id: str) -> List[str]:
        """List available configuration scenarios for a lab"""
        if lab_id not in self.state["repos"]:
            return []
        
        repo_path = Path(self.state["repos"][lab_id]["path"])
        configs_dir = repo_path / "device_configs"
        
        if not configs_dir.exists():
            return []
        
        scenarios = []
        for item in configs_dir.iterdir():
            if item.is_dir() and item.name != "__pycache__":
                scenarios.append(item.name)
        
        return sorted(scenarios)
    
    def apply_config_scenario(self, lab_id: str, scenario: str) -> Dict:
        """Apply a configuration scenario to a deployed lab"""
        if lab_id not in self.state["repos"]:
            return {"success": False, "error": f"Lab {lab_id} not found"}
        
        # Check if lab is deployed
        is_deployed = False
        for dep_info in self.state["deployments"].values():
            if dep_info["lab_id"] == lab_id and dep_info["status"] == "active":
                is_deployed = True
                break
        
        if not is_deployed:
            return {"success": False, "error": f"Lab {lab_id} is not deployed"}
        
        repo_path = Path(self.state["repos"][lab_id]["path"])
        scenario_dir = repo_path / "device_configs" / scenario
        
        if not scenario_dir.exists():
            return {"success": False, "error": f"Scenario {scenario} not found"}
        
        # TODO: Implement configuration loading using clab-tools node config
        # This would iterate through the scenario directory and apply configs
        # to each device using clab-tools node config commands
        
        return {
            "success": True,
            "message": f"Configuration scenario {scenario} applied",
            "note": "Implementation pending for clab-tools integration"
        }


# Initialize lab manager
lab_manager = LabManager()


# API Routes
@app.route('/')
def index():
    """Serve the web UI"""
    return send_from_directory('web', 'index.html')


@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "labctl-backend"})


@app.route('/api/repos', methods=['GET'])
def list_repos():
    """List all lab repositories"""
    repos = lab_manager.list_repos()
    return jsonify(repos)


@app.route('/api/repos', methods=['POST'])
def add_repo():
    """Add a new lab repository"""
    data = request.json
    if not data or 'url' not in data:
        return jsonify({"error": "Repository URL required"}), 400
    
    result = lab_manager.add_repo(data['url'], data.get('name'))
    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 400


@app.route('/api/repos/<lab_id>', methods=['PUT'])
def update_repo(lab_id):
    """Update a lab repository"""
    result = lab_manager.update_repo(lab_id)
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400


@app.route('/api/repos/<lab_id>', methods=['DELETE'])
def remove_repo(lab_id):
    """Remove a lab repository"""
    result = lab_manager.remove_repo(lab_id)
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400


@app.route('/api/labs/<lab_id>/deploy', methods=['POST'])
def deploy_lab(lab_id):
    """Deploy a lab (async)"""
    data = request.json or {}
    version = data.get('version', 'latest')
    allocate_ips = data.get('allocate_ips', False)
    
    task_id = lab_manager.deploy_lab_async(lab_id, version, allocate_ips)
    
    return jsonify({
        "task_id": task_id,
        "message": f"Deployment of {lab_id} started"
    }), 202


@app.route('/api/labs/<lab_id>/destroy', methods=['POST'])
def destroy_lab(lab_id):
    """Destroy a deployed lab"""
    result = lab_manager.destroy_lab(lab_id)
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400


@app.route('/api/deployments', methods=['GET'])
def get_deployments():
    """Get all active deployments"""
    return jsonify(lab_manager.get_status())


@app.route('/api/tasks/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Get status of an async task"""
    status = lab_manager.get_task_status(task_id)
    if 'error' in status:
        return jsonify(status), 404
    return jsonify(status)


@app.route('/api/labs/<lab_id>/scenarios', methods=['GET'])
def list_scenarios(lab_id):
    """List configuration scenarios for a lab"""
    scenarios = lab_manager.list_config_scenarios(lab_id)
    return jsonify({"lab_id": lab_id, "scenarios": scenarios})


@app.route('/api/labs/<lab_id>/scenarios/<scenario>', methods=['POST'])
def apply_scenario(lab_id, scenario):
    """Apply a configuration scenario"""
    result = lab_manager.apply_config_scenario(lab_id, scenario)
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    # Remove sensitive data
    config = lab_manager.config.copy()
    if 'netbox' in config and 'token' in config['netbox']:
        config['netbox']['token'] = "***"
    return jsonify(config)


@app.route('/api/logs/<lab_id>', methods=['GET'])
def get_logs(lab_id):
    """Get deployment logs for a lab"""
    # Find the most recent deployment log
    for dep_id, dep_info in sorted(lab_manager.state["deployments"].items(), reverse=True):
        if dep_info["lab_id"] == lab_id:
            log_file = Path(dep_info.get("log_file", ""))
            if log_file.exists():
                with open(log_file) as f:
                    return jsonify({
                        "deployment_id": dep_id,
                        "log": f.read()
                    })
    
    return jsonify({"error": "No logs found"}), 404


if __name__ == '__main__':
    # Development server
    app.run(host='0.0.0.0', port=5000, debug=True)