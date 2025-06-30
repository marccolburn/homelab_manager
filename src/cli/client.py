"""
API client for labctl backend communication
"""
import requests
import sys
from typing import Dict, Optional
from rich.console import Console

console = Console()


class LabCtlClient:
    """API client for labctl backend"""
    
    def __init__(self, api_url: str):
        self.api_url = api_url.rstrip('/')
        self.session = requests.Session()
    
    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make an API request"""
        url = f"{self.api_url}{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.ConnectionError:
            console.print(f"[red]Error: Cannot connect to backend at {self.api_url}[/red]")
            console.print("[yellow]Make sure the backend is running: python app.py[/yellow]")
            sys.exit(1)
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                console.print(f"[red]Error: Endpoint not found: {endpoint}[/red]")
            else:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get('error', str(e))
                console.print(f"[red]Error: {error_msg}[/red]")
            sys.exit(1)
    
    def health_check(self) -> bool:
        """Check if backend is healthy"""
        try:
            response = self._request('GET', '/api/health')
            return response.json().get('status') == 'healthy'
        except:
            return False
    
    # Repository management methods
    def list_repos(self) -> list:
        """List all lab repositories"""
        response = self._request('GET', '/api/repos')
        return response.json()
    
    def add_repo(self, url: str, name: Optional[str] = None) -> dict:
        """Add a new lab repository"""
        data = {'url': url}
        if name:
            data['name'] = name
        response = self._request('POST', '/api/repos', json=data)
        return response.json()
    
    def update_repo(self, lab_id: str) -> dict:
        """Update a lab repository"""
        response = self._request('PUT', f'/api/repos/{lab_id}')
        return response.json()
    
    def remove_repo(self, lab_id: str) -> dict:
        """Remove a lab repository"""
        response = self._request('DELETE', f'/api/repos/{lab_id}')
        return response.json()
    
    # Lab deployment methods
    def deploy_lab(self, lab_id: str, version: str = 'latest', 
                   allocate_ips: bool = False) -> dict:
        """Deploy a lab"""
        data = {
            'version': version,
            'allocate_ips': allocate_ips
        }
        response = self._request('POST', f'/api/labs/{lab_id}/deploy', json=data)
        return response.json()
    
    def destroy_lab(self, lab_id: str) -> dict:
        """Destroy a lab"""
        response = self._request('POST', f'/api/labs/{lab_id}/destroy')
        return response.json()
    
    def get_deployments(self) -> dict:
        """Get all deployments"""
        response = self._request('GET', '/api/deployments')
        return response.json()
    
    def get_task_status(self, task_id: str) -> dict:
        """Get task status"""
        response = self._request('GET', f'/api/tasks/{task_id}')
        return response.json()
    
    # Configuration management methods
    def list_scenarios(self, lab_id: str) -> list:
        """List configuration scenarios"""
        response = self._request('GET', f'/api/labs/{lab_id}/scenarios')
        return response.json().get('scenarios', [])
    
    def apply_scenario(self, lab_id: str, scenario: str) -> dict:
        """Apply a configuration scenario"""
        response = self._request('POST', f'/api/labs/{lab_id}/scenarios/{scenario}')
        return response.json()
    
    def get_logs(self, lab_id: str) -> dict:
        """Get deployment logs"""
        response = self._request('GET', f'/api/logs/{lab_id}')
        return response.json()
    
    def get_config(self) -> dict:
        """Get current backend configuration"""
        response = self._request('GET', '/api/config')
        return response.json()