#!/usr/bin/env python3
"""
Lab Management System - Centralized lab discovery and deployment
"""

import os
import yaml
import git
import asyncio
import subprocess
from datetime import datetime
from typing import List, Dict, Optional, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pynetbox
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Network Lab Management System", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class LabMetadata(BaseModel):
    name: str
    id: str
    version: str
    category: str
    vendor: str
    difficulty: str
    description: Optional[Dict[str, str]] = {}
    requirements: Optional[Dict[str, Any]] = {}
    topology: Optional[Dict[str, Any]] = {}
    tags: Optional[List[str]] = []
    repository: Optional[Dict[str, str]] = {}

class LabManager:
    def __init__(self, config_file: str = "lab_manager_config.yaml"):
        self.config = self._load_config(config_file)
        self.netbox = self._init_netbox()
        self.lab_repos = []
        self.active_deployments = {}
        
    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from YAML file"""
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    
    def _init_netbox(self) -> Optional[pynetbox.api]:
        """Initialize NetBox API connection"""
        try:
            nb_config = self.config.get('netbox', {})
            if nb_config.get('enabled', False):
                return pynetbox.api(
                    nb_config['url'],
                    token=nb_config['token']
                )
        except Exception as e:
            logger.warning(f"NetBox initialization failed: {e}")
        return None
    
    async def discover_labs(self) -> List[LabMetadata]:
        """Discover all available labs from configured repositories"""
        labs = []
        
        for repo_config in self.config.get('repositories', []):
            try:
                # Clone or pull repository
                repo_path = await self._sync_repository(repo_config)
                
                # Check for lab-metadata.yaml
                metadata_path = os.path.join(repo_path, 'lab-metadata.yaml')
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'r') as f:
                        metadata_yaml = yaml.safe_load(f)
                        # Extract the metadata section if it exists
                        if 'metadata' in metadata_yaml:
                            metadata = metadata_yaml['metadata']
                        else:
                            metadata = metadata_yaml
                        labs.append(LabMetadata(**metadata))
                        
            except Exception as e:
                logger.error(f"Failed to discover labs from {repo_config['url']}: {e}")
                
        return labs
    
    async def _sync_repository(self, repo_config: Dict) -> str:
        """Clone or update a repository"""
        repo_name = repo_config['url'].split('/')[-1].replace('.git', '')
        repo_path = os.path.join(self.config['local_repo_path'], repo_name)
        
        if os.path.exists(repo_path):
            # Pull latest changes
            repo = git.Repo(repo_path)
            repo.remotes.origin.pull()
        else:
            # Clone repository
            git.Repo.clone_from(repo_config['url'], repo_path)
            
        return repo_path
    
    async def deploy_lab(self, lab_id: str, version: str = "latest") -> Dict:
        """Deploy a specific lab"""
        deployment_id = f"{lab_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Find lab repository
            repo_path = None
            for repo_config in self.config.get('repositories', []):
                repo_name = repo_config['url'].split('/')[-1].replace('.git', '')
                candidate_path = os.path.join(self.config['local_repo_path'], repo_name)
                metadata_path = os.path.join(candidate_path, 'lab-metadata.yaml')
                
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'r') as f:
                        metadata_yaml = yaml.safe_load(f)
                        # Extract the metadata section if it exists
                        if 'metadata' in metadata_yaml:
                            metadata = metadata_yaml['metadata']
                        else:
                            metadata = metadata_yaml
                        
                        if metadata.get('id') == lab_id:
                            repo_path = candidate_path
                            break
            
            if not repo_path:
                raise Exception(f"Lab {lab_id} not found")
            
            # Checkout specific version if requested
            if version != "latest":
                repo = git.Repo(repo_path)
                repo.git.checkout(version)
            
            # Register deployment in NetBox if enabled
            if self.netbox:
                await self._register_deployment_netbox(deployment_id, lab_id)
            
            # Execute bootstrap script
            bootstrap_script = os.path.join(repo_path, 'clab_tools_files', 'bootstrap.sh')
            if os.path.exists(bootstrap_script):
                process = await asyncio.create_subprocess_exec(
                    'bash', bootstrap_script,
                    cwd=repo_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    self.active_deployments[deployment_id] = {
                        'lab_id': lab_id,
                        'status': 'deployed',
                        'deployed_at': datetime.now(),
                        'repo_path': repo_path
                    }
                    return {
                        'deployment_id': deployment_id,
                        'status': 'success',
                        'message': 'Lab deployed successfully'
                    }
                else:
                    raise Exception(f"Bootstrap failed: {stderr.decode()}")
            
        except Exception as e:
            logger.error(f"Lab deployment failed: {e}")
            return {
                'deployment_id': deployment_id,
                'status': 'failed',
                'message': str(e)
            }
    
    async def _register_deployment_netbox(self, deployment_id: str, lab_id: str):
        """Register deployment in NetBox"""
        try:
            # Create or update NetBox entries for lab devices
            # This is a placeholder - implement based on your NetBox schema
            pass
        except Exception as e:
            logger.warning(f"NetBox registration failed: {e}")
    
    async def teardown_lab(self, deployment_id: str) -> Dict:
        """Teardown a deployed lab"""
        if deployment_id not in self.active_deployments:
            raise HTTPException(status_code=404, detail="Deployment not found")
        
        deployment = self.active_deployments[deployment_id]
        repo_path = deployment['repo_path']
        
        try:
            # Execute teardown script
            teardown_script = os.path.join(repo_path, 'clab_tools_files', 'teardown.sh')
            if os.path.exists(teardown_script):
                process = await asyncio.create_subprocess_exec(
                    'bash', teardown_script,
                    cwd=repo_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()
            
            # Remove from active deployments
            del self.active_deployments[deployment_id]
            
            return {
                'deployment_id': deployment_id,
                'status': 'success',
                'message': 'Lab torn down successfully'
            }
            
        except Exception as e:
            logger.error(f"Lab teardown failed: {e}")
            return {
                'deployment_id': deployment_id,
                'status': 'failed',
                'message': str(e)
            }

# Initialize lab manager
lab_manager = LabManager()

@app.get("/")
async def root():
    return {"message": "Network Lab Management System"}

@app.get("/web", response_class=HTMLResponse)
async def get_web_interface():
    """Serve the web interface"""
    try:
        with open("web_interface.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Web interface not found")

@app.get("/labs", response_model=List[LabMetadata])
async def list_labs():
    """List all available labs"""
    return await lab_manager.discover_labs()

@app.post("/labs/{lab_id}/deploy")
async def deploy_lab(lab_id: str, background_tasks: BackgroundTasks, version: str = "latest"):
    """Deploy a specific lab"""
    result = await lab_manager.deploy_lab(lab_id, version)
    return result

@app.delete("/deployments/{deployment_id}")
async def teardown_deployment(deployment_id: str):
    """Teardown a deployed lab"""
    return await lab_manager.teardown_lab(deployment_id)

@app.get("/deployments")
async def list_deployments():
    """List active deployments"""
    return lab_manager.active_deployments

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
