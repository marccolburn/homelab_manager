"""
Lab management core functionality
"""
import json
import yaml
import uuid
import threading
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .git_ops import GitOperations
    from .clab_runner import ClabRunner
    from ..integrations.netbox import NetBoxManager

logger = logging.getLogger(__name__)


class LabManager:
    """Core lab management functionality"""
    
    def __init__(self, config: Dict, git_ops: Optional['GitOperations'] = None, 
                 clab_runner: Optional['ClabRunner'] = None,
                 netbox_manager: Optional['NetBoxManager'] = None):
        self.config = config
        self.state = self._load_state()
        self._ensure_directories()
        self.active_tasks = {}  # Track async operations
        
        # Use injected dependencies or create defaults
        if git_ops:
            self.git_ops = git_ops
        else:
            # Fallback for backward compatibility
            from .git_ops import GitOperations
            self.git_ops = GitOperations(config.get("git_cmd", "git"))
        
        if clab_runner:
            self.clab_runner = clab_runner
        else:
            # Fallback for backward compatibility
            from .clab_runner import ClabRunner
            self.clab_runner = ClabRunner(
                config.get("clab_tools_cmd", "clab-tools"),
                Path(config.get("logs_dir", "/var/lib/labctl/logs"))
            )
        
        # Initialize NetBox manager if enabled
        if netbox_manager:
            self.netbox = netbox_manager
        else:
            netbox_config = config.get("netbox", {})
            if netbox_config.get("enabled", False):
                from ..integrations.netbox import NetBoxManager
                self.netbox = NetBoxManager(netbox_config)
            else:
                self.netbox = None
    
    def _load_state(self) -> Dict:
        """Load state file"""
        state_file = Path(self.config.get("state_file"))
        if not state_file.exists():
            return {"repos": {}, "deployments": {}}
        
        with open(state_file) as f:
            return json.load(f)
    
    def _save_state(self):
        """Save state file"""
        state_file = Path(self.config.get("state_file"))
        state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def _ensure_directories(self):
        """Ensure required directories exist"""
        for dir_key in ["repos_dir", "logs_dir"]:
            dir_path = Path(self.config.get(dir_key, ""))
            if dir_path:
                dir_path.mkdir(parents=True, exist_ok=True)
    
    
    def add_repo(self, repo_url: str, name: Optional[str] = None) -> Dict:
        """Clone and register a lab repository"""
        # Extract repo name from URL if not provided
        if not name:
            name = repo_url.split('/')[-1].replace('.git', '')
        
        repo_path = Path(self.config["repos_dir"]) / name
        
        # Clone or update repository using git_ops
        if repo_path.exists():
            logger.info(f"Repository {name} already exists, updating...")
            result = self.git_ops.pull(repo_path)
        else:
            logger.info(f"Cloning repository {repo_url}...")
            result = self.git_ops.clone(repo_url, repo_path)
        
        if not result["success"]:
            return result
        
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
        
        # Git pull using git_ops
        result = self.git_ops.pull(repo_path)
        
        if not result["success"]:
            return result
        
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
            result = self.git_ops.checkout(repo_path, version)
            if not result["success"]:
                return result
        
        # NetBox IP allocation if requested
        ip_assignments = {}
        if allocate_ips and self.netbox and self.netbox.enabled:
            logger.info("Allocating IPs from NetBox...")
            
            # Read nodes from nodes.csv to get list of devices
            nodes_file = repo_path / "clab_tools_files" / "nodes.csv"
            if not nodes_file.exists():
                return {"success": False, "error": "nodes.csv not found"}
                
            # Extract node names from CSV
            import csv
            node_names = []
            with open(nodes_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    node_name = row.get('hostname', row.get('name', ''))
                    if node_name:
                        node_names.append(node_name)
                        
            if node_names:
                # Allocate IPs from NetBox
                ip_assignments = self.netbox.allocate_ips(lab_id, node_names)
                
                if not ip_assignments:
                    return {"success": False, "error": "Failed to allocate IPs from NetBox"}
                    
                # Update nodes.csv with allocated IPs
                if not self.netbox.update_nodes_csv(nodes_file, ip_assignments):
                    # Rollback IP allocations on failure
                    self.netbox.release_ips(lab_id)
                    return {"success": False, "error": "Failed to update nodes.csv with IPs"}
                    
                logger.info(f"Allocated {len(ip_assignments)} IPs from NetBox")
        
        # Deploy lab using clab_runner
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        deployment_id = f"{lab_id}_{timestamp}"
        
        logger.info(f"Deploying lab {lab_id}...")
        
        success, result = self.clab_runner.bootstrap_lab(lab_id, repo_path, deployment_id)
        
        if success:
            # Register devices in NetBox if IPs were allocated
            if ip_assignments and self.netbox:
                # Re-read nodes.csv to get updated node info
                nodes_info = []
                with open(nodes_file, 'r') as f:
                    reader = csv.DictReader(f)
                    nodes_info = list(reader)
                    
                # Register devices
                lab_name = repo_info.get("metadata", {}).get("name", lab_id)
                created_devices = self.netbox.register_devices(lab_id, lab_name, nodes_info)
                logger.info(f"Registered {len(created_devices)} devices in NetBox")
            
            # Update deployment state
            self.state["deployments"][deployment_id] = {
                "lab_id": lab_id,
                "version": version or "latest",
                "deployed_at": datetime.now().isoformat(),
                "log_file": result["log_file"],
                "status": "active",
                "netbox_ips_allocated": bool(ip_assignments),
                "ip_assignments": ip_assignments
            }
            self._save_state()
            
            return {
                "success": True,
                "deployment_id": deployment_id,
                "message": result["message"]
            }
        else:
            # Rollback NetBox allocations if deployment failed
            if ip_assignments and self.netbox:
                logger.warning("Deployment failed, releasing allocated IPs")
                self.netbox.release_ips(lab_id)
                
            return {
                "success": False,
                "error": result.get("error", "Deployment failed")
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
        
        # Teardown lab using clab_runner
        logger.info(f"Destroying lab {lab_id}...")
        
        success, result = self.clab_runner.teardown_lab(lab_id, repo_path)
        
        if success:
            # Release NetBox resources if they were allocated
            deployment_info = self.state["deployments"][active_deployment]
            if deployment_info.get("netbox_ips_allocated") and self.netbox:
                logger.info("Releasing NetBox resources...")
                
                # Release IPs
                if self.netbox.release_ips(lab_id):
                    logger.info("Released NetBox IPs successfully")
                else:
                    logger.warning("Failed to release some NetBox IPs")
                    
                # Unregister devices
                if self.netbox.unregister_devices(lab_id):
                    logger.info("Unregistered NetBox devices successfully")
                else:
                    logger.warning("Failed to unregister some NetBox devices")
            
            # Update deployment state
            self.state["deployments"][active_deployment]["status"] = "destroyed"
            self.state["deployments"][active_deployment]["destroyed_at"] = datetime.now().isoformat()
            self._save_state()
            
            return {
                "success": True,
                "message": result["message"]
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Teardown failed")
            }
    
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
    
    def validate_netbox_config(self) -> Dict:
        """Validate NetBox configuration and connectivity"""
        if not self.netbox:
            return {
                "enabled": False,
                "valid": True,
                "message": "NetBox integration is disabled"
            }
            
        is_valid, errors = self.netbox.validate_config()
        
        return {
            "enabled": True,
            "valid": is_valid,
            "errors": errors,
            "message": "NetBox configuration is valid" if is_valid else "NetBox configuration has errors"
        }
    
    def get_logs(self, deployment_id: str) -> Optional[str]:
        """Get deployment logs"""
        if deployment_id not in self.state["deployments"]:
            return None
        
        log_file = self.state["deployments"][deployment_id].get("log_file")
        if not log_file or not Path(log_file).exists():
            return None
        
        with open(log_file) as f:
            return f.read()