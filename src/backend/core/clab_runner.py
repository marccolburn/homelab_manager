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
from .config import load_config

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
        """Bootstrap a lab using clab-tools directly"""
        clab_tools_dir = repo_path / "clab_tools_files"
        config_file = clab_tools_dir / "config.yaml"
        nodes_file = clab_tools_dir / "nodes.csv"
        connections_file = clab_tools_dir / "connections.csv"
        
        # Validate required files exist
        missing_files = []
        for file_path, name in [(config_file, "config.yaml"), (nodes_file, "nodes.csv"), (connections_file, "connections.csv")]:
            if not file_path.exists():
                missing_files.append(name)
        
        if missing_files:
            return False, {"error": f"Missing required files: {', '.join(missing_files)}"}
        
        # Create deployment ID if not provided
        if not deployment_id:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            deployment_id = f"{lab_id}_{timestamp}"
        
        # Create log file
        log_file = self.logs_dir / f"{deployment_id}.log"
        # Generate output file relative to repo directory (since we run clab-tools from there)
        output_file = f"{lab_id}.clab.yml"
        
        logger.info(f"Bootstrapping lab {lab_id} with deployment ID {deployment_id}")
        
        # Start logging
        with open(log_file, 'w') as log:
            log.write(f"=== Lab Bootstrap Log ===\n")
            log.write(f"Lab ID: {lab_id}\n")
            log.write(f"Deployment ID: {deployment_id}\n")
            log.write(f"Timestamp: {datetime.now().isoformat()}\n")
            log.write(f"Working Directory: {clab_tools_dir}\n")
            log.write(f"Output File: {output_file}\n")
            log.write(f"\n=== Deployment Steps ===\n")
            
            try:
                # Set environment variables for clab-tools
                env = os.environ.copy()
                config = load_config()
                
                # Set password for remote operations
                # Priority: 1) Environment variable, 2) Config file, 3) None
                if not env.get('CLAB_TOOLS_PASSWORD'):
                    config_password = config.get('clab_tools_password', '')
                    if config_password:
                        env['CLAB_TOOLS_PASSWORD'] = config_password
                        log.write("Using clab_tools_password from configuration\n")
                    else:
                        log.write("Warning: CLAB_TOOLS_PASSWORD not set in environment or config\n")
                else:
                    log.write("Using CLAB_TOOLS_PASSWORD from environment variable\n")
                
                # Set remote-specific passwords for clab-tools remote operations
                remote_creds = config.get('remote_credentials', {})
                
                if not env.get('CLAB_REMOTE_PASSWORD'):
                    ssh_password = remote_creds.get('ssh_password') or env.get('CLAB_TOOLS_PASSWORD') or config.get('clab_tools_password', '')
                    if ssh_password:
                        env['CLAB_REMOTE_PASSWORD'] = ssh_password
                        log.write("Using CLAB_REMOTE_PASSWORD from configuration\n")
                    else:
                        log.write("Warning: CLAB_REMOTE_PASSWORD not set, remote authentication may fail\n")
                
                if not env.get('CLAB_REMOTE_SUDO_PASSWORD'):
                    sudo_password = remote_creds.get('sudo_password') or env.get('CLAB_TOOLS_PASSWORD') or config.get('clab_tools_password', '')
                    if sudo_password:
                        env['CLAB_REMOTE_SUDO_PASSWORD'] = sudo_password
                        log.write("Using CLAB_REMOTE_SUDO_PASSWORD from configuration\n")
                    else:
                        log.write("Warning: CLAB_REMOTE_SUDO_PASSWORD not set, remote sudo operations may fail\n")
                
                # Step 1: Create lab
                log.write("Step 1: Creating lab\n")
                create_cmd = [self.clab_tools_cmd, "--quiet", "lab", "create", lab_id]
                log.write(f"Command: {' '.join(create_cmd)}\n")
                log.flush()
                
                result = subprocess.run(
                    create_cmd,
                    cwd=str(repo_path),  # Run from repo directory to use correct config
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    env=env
                )
                log.write(f"Exit Code: {result.returncode}\n")
                log.write(f"Output:\n{result.stdout}\n")
                log.flush()
                
                # Step 2: Switch to lab
                log.write("Step 2: Switching to lab\n")
                switch_cmd = [self.clab_tools_cmd, "--quiet", "lab", "switch", lab_id]
                log.write(f"Command: {' '.join(switch_cmd)}\n")
                log.flush()
                
                result = subprocess.run(
                    switch_cmd,
                    cwd=str(repo_path),  # Run from repo directory to use correct config
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    env=env
                )
                log.write(f"Exit Code: {result.returncode}\n")
                log.write(f"Output:\n{result.stdout}\n")
                log.flush()
                
                # Step 3: Use clab-tools lab bootstrap command (unified command)
                log.write("Step 3: Running clab-tools lab bootstrap\n")
                cmd = [
                    self.clab_tools_cmd,
                    "--quiet",
                    "--config", "clab_tools_files/config.yaml",
                    "lab", "bootstrap",
                    "--nodes", "clab_tools_files/nodes.csv",
                    "--connections", "clab_tools_files/connections.csv", 
                    "--output", output_file,
                ]
                log.write(f"Command: {' '.join(cmd)}\n")
                log.write(f"Working Directory: {repo_path}\n")
                log.write(f"Environment Variables:\n")
                for key in ['CLAB_TOOLS_PASSWORD', 'CLAB_REMOTE_PASSWORD', 'CLAB_REMOTE_SUDO_PASSWORD']:
                    value = env.get(key, 'NOT SET')
                    masked_value = '****' if value != 'NOT SET' else 'NOT SET'
                    log.write(f"  {key}: {masked_value}\n")
                log.write("Starting bootstrap command...\n")
                log.flush()
                
                # Run clab-tools from the lab repo directory 
                # This ensures it uses the correct config.yaml with remote settings
                try:
                    # Use Popen for real-time output streaming
                    process = subprocess.Popen(
                        cmd,
                        cwd=str(repo_path),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        stdin=subprocess.DEVNULL,  # Prevent hanging on prompts
                        text=True,
                        env=env,
                        bufsize=1,  # Line buffered
                        universal_newlines=True
                    )
                    
                    # Stream output in real-time
                    log.write("Command output (real-time):\n")
                    output_lines = []
                    for line in process.stdout:
                        log.write(f"OUT: {line}")
                        log.flush()
                        output_lines.append(line)
                    
                    # Wait for completion with timeout
                    try:
                        process.wait(timeout=90)
                    except subprocess.TimeoutExpired:
                        log.write("Command timed out, killing process...\n")
                        process.kill()
                        process.wait()
                        raise
                    
                    result_stdout = ''.join(output_lines)
                    log.write(f"Exit Code: {process.returncode}\n")
                    log.write(f"Command completed.\n")
                    log.flush()  # Ensure everything is written to disk
                    
                    if process.returncode == 0:
                        log.write("✓ Lab bootstrap completed successfully\n")
                        return True, {
                            "deployment_id": deployment_id,
                            "log_file": str(log_file),
                            "message": f"Lab {lab_id} deployed successfully"
                        }
                    else:
                        log.write("✗ Lab bootstrap failed\n")
                        return False, {
                            "error": "Bootstrap failed",
                            "log_file": str(log_file),
                            "exit_code": process.returncode,
                            "output": result_stdout
                        }
                
                except subprocess.TimeoutExpired:
                    log.write("✗ Lab bootstrap timed out after 90 seconds\n")
                    return False, {
                        "error": "Bootstrap timed out",
                        "log_file": str(log_file),
                        "timeout": 90
                    }
                    
            except Exception as e:
                log.write(f"✗ Exception during bootstrap: {str(e)}\n")
                return False, {
                    "error": f"Exception during bootstrap: {str(e)}",
                    "log_file": str(log_file)
                }
    
    def teardown_lab(self, lab_id: str, repo_path: Path) -> Tuple[bool, Dict]:
        """Teardown a lab using clab-tools directly"""
        clab_tools_dir = repo_path / "clab_tools_files"
        config_file = clab_tools_dir / "config.yaml"
        
        if not config_file.exists():
            return False, {"error": "config.yaml not found"}
        
        logger.info(f"Tearing down lab {lab_id}")
        
        # Use clab-tools lab teardown command
        cmd = [
            self.clab_tools_cmd,
            "--config", "config.yaml",
            "lab", "teardown"
        ]
        
        result = self._run_command(
            cmd,
            cwd=clab_tools_dir,
            capture_output=True
        )
        
        if result.returncode == 0:
            return True, {"message": f"Lab {lab_id} destroyed successfully"}
        else:
            return False, {
                "error": "Teardown failed", 
                "exit_code": result.returncode,
                "output": result.stderr
            }
    
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
            "clab_tools_files/connections.csv"
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