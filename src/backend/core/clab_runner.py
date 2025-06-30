"""
Containerlab tools runner module
Handles all interactions with clab-tools for lab deployment and management
"""
import os
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class ClabRunner:
    """Executes clab-tools commands for lab management"""
    
    def __init__(self, clab_tools_cmd: str = "clab-tools", logs_dir: Path = None):
        self.clab_tools_cmd = clab_tools_cmd
        self.logs_dir = logs_dir or Path("/var/lib/labctl/logs")
        self.logs_dir.mkdir(parents=True, exist_ok=True)
    
    def _run_command(self, cmd: List[str], cwd: Optional[Path] = None,
                     capture_output: bool = True, log_file: Optional[Path] = None) -> subprocess.CompletedProcess:
        """Run a command with optional logging"""
        logger.debug(f"Running command: {' '.join(cmd)}")
        if cwd:
            logger.debug(f"Working directory: {cwd}")
        
        if log_file:
            with open(log_file, 'w') as log:
                result = subprocess.run(
                    cmd,
                    cwd=cwd,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    text=True
                )
        else:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=capture_output,
                text=True
            )
        
        if result.returncode != 0:
            logger.error(f"Command failed: {' '.join(cmd)}")
            if capture_output and not log_file:
                logger.error(f"Error output: {result.stderr}")
        
        return result
    
    def bootstrap_lab(self, lab_id: str, repo_path: Path, 
                     deployment_id: Optional[str] = None) -> Tuple[bool, Dict]:
        """Bootstrap a lab using the bootstrap.sh script"""
        bootstrap_script = repo_path / "clab_tools_files" / "bootstrap.sh"
        
        if not bootstrap_script.exists():
            return False, {"error": "bootstrap.sh not found"}
        
        # Create deployment ID if not provided
        if not deployment_id:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            deployment_id = f"{lab_id}_{timestamp}"
        
        # Create log file
        log_file = self.logs_dir / f"{deployment_id}.log"
        
        logger.info(f"Bootstrapping lab {lab_id} with deployment ID {deployment_id}")
        
        # Make bootstrap script executable
        os.chmod(bootstrap_script, 0o755)
        
        # Set environment variables for the script
        env = os.environ.copy()
        env["LAB_ID"] = lab_id
        env["DEPLOYMENT_ID"] = deployment_id
        
        # Run bootstrap script
        result = subprocess.run(
            [str(bootstrap_script)],
            cwd=repo_path / "clab_tools_files",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=env
        )
        
        # Write output to log file
        with open(log_file, 'w') as log:
            log.write(f"=== Lab Bootstrap Log ===\n")
            log.write(f"Lab ID: {lab_id}\n")
            log.write(f"Deployment ID: {deployment_id}\n")
            log.write(f"Timestamp: {datetime.now().isoformat()}\n")
            log.write(f"Script: {bootstrap_script}\n")
            log.write(f"Exit Code: {result.returncode}\n")
            log.write(f"\n=== Output ===\n")
            log.write(result.stdout)
        
        if result.returncode == 0:
            return True, {
                "deployment_id": deployment_id,
                "log_file": str(log_file),
                "message": f"Lab {lab_id} deployed successfully"
            }
        else:
            return False, {
                "error": "Bootstrap failed",
                "log_file": str(log_file),
                "exit_code": result.returncode
            }
    
    def teardown_lab(self, lab_id: str, repo_path: Path) -> Tuple[bool, Dict]:
        """Teardown a lab using the teardown.sh script"""
        teardown_script = repo_path / "clab_tools_files" / "teardown.sh"
        
        if not teardown_script.exists():
            return False, {"error": "teardown.sh not found"}
        
        logger.info(f"Tearing down lab {lab_id}")
        
        # Make teardown script executable
        os.chmod(teardown_script, 0o755)
        
        # Set environment variables for the script
        env = os.environ.copy()
        env["LAB_ID"] = lab_id
        
        # Run teardown script
        result = self._run_command(
            [str(teardown_script)],
            cwd=repo_path / "clab_tools_files",
            capture_output=False
        )
        
        if result.returncode == 0:
            return True, {"message": f"Lab {lab_id} destroyed successfully"}
        else:
            return False, {"error": "Teardown failed", "exit_code": result.returncode}
    
    def get_lab_status(self, lab_id: str, repo_path: Path) -> Dict:
        """Get the status of a deployed lab"""
        # This would typically check if containers are running
        # For now, we'll check if the .clab.yml file exists
        clab_file = repo_path / f"{lab_id}.clab.yml"
        
        if clab_file.exists():
            return {
                "deployed": True,
                "clab_file": str(clab_file),
                "message": f"Lab {lab_id} appears to be deployed"
            }
        else:
            return {
                "deployed": False,
                "message": f"Lab {lab_id} is not deployed"
            }
    
    def apply_node_config(self, lab_id: str, node_name: str, 
                         config_file: Path, repo_path: Path) -> Tuple[bool, Dict]:
        """Apply configuration to a specific node using clab-tools"""
        if not config_file.exists():
            return False, {"error": f"Config file {config_file} not found"}
        
        # Construct clab-tools command
        # Example: clab-tools node config --name router1 --config router1.conf
        cmd = [
            self.clab_tools_cmd,
            "node", "config",
            "--name", node_name,
            "--config", str(config_file)
        ]
        
        logger.info(f"Applying config to node {node_name} in lab {lab_id}")
        
        result = self._run_command(cmd, cwd=repo_path)
        
        if result.returncode == 0:
            return True, {"message": f"Config applied to {node_name}"}
        else:
            return False, {
                "error": f"Failed to apply config to {node_name}",
                "output": result.stderr
            }
    
    def get_node_list(self, lab_id: str, repo_path: Path) -> List[str]:
        """Get list of nodes in a deployed lab"""
        nodes_file = repo_path / "clab_tools_files" / "nodes.csv"
        
        if not nodes_file.exists():
            return []
        
        nodes = []
        with open(nodes_file) as f:
            # Skip header line
            next(f, None)
            for line in f:
                if line.strip():
                    # First column is the node name
                    node_name = line.split(',')[0].strip()
                    if node_name:
                        nodes.append(node_name)
        
        return nodes
    
    def validate_lab_files(self, repo_path: Path) -> Tuple[bool, List[str]]:
        """Validate that all required lab files exist"""
        required_files = [
            "lab-metadata.yaml",
            "clab_tools_files/config.yaml",
            "clab_tools_files/nodes.csv",
            "clab_tools_files/connections.csv",
            "clab_tools_files/bootstrap.sh",
            "clab_tools_files/teardown.sh"
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = repo_path / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        is_valid = len(missing_files) == 0
        return is_valid, missing_files
    
    def check_clab_tools(self) -> bool:
        """Check if clab-tools is available"""
        try:
            result = self._run_command([self.clab_tools_cmd, "--version"])
            return result.returncode == 0
        except FileNotFoundError:
            logger.error(f"clab-tools command '{self.clab_tools_cmd}' not found")
            return False