#!/usr/bin/env python3
"""
labctl - Homelab Manager CLI

A lightweight CLI that communicates with the Flask backend API.
"""

import click
import requests
import json
import sys
import time
from pathlib import Path
from typing import Dict, Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

# Default API endpoint
DEFAULT_API_URL = "http://localhost:5000"


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


# CLI Commands
@click.group()
@click.option('--api-url', '-a', 
              default=DEFAULT_API_URL,
              envvar='LABCTL_API_URL',
              help='Backend API URL')
@click.pass_context
def cli(ctx, api_url):
    """Homelab Manager CLI - Manage containerlab-based network labs"""
    ctx.ensure_object(dict)
    ctx.obj['client'] = LabCtlClient(api_url)
    
    # Check backend health
    if not ctx.obj['client'].health_check():
        console.print(f"[red]Error: Backend is not healthy at {api_url}[/red]")
        console.print("[yellow]Start the backend with: python app.py[/yellow]")
        sys.exit(1)


@cli.group()
def repo():
    """Manage lab repositories"""
    pass


@repo.command()
@click.argument('repo_url')
@click.option('--name', '-n', help='Repository name (defaults to repo name)')
@click.pass_context
def add(ctx, repo_url, name):
    """Clone and register a lab repository"""
    client = ctx.obj['client']
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Adding repository...", total=None)
        result = client.add_repo(repo_url, name)
    
    if result.get('success'):
        console.print(f"[green]✓ Successfully added lab: {result['metadata']['name']}[/green]")
    else:
        console.print(f"[red]✗ Failed to add repository[/red]")
        sys.exit(1)


@repo.command()
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
@click.pass_context
def list(ctx, output_json):
    """List all registered lab repositories"""
    client = ctx.obj['client']
    repos = client.list_repos()
    
    if output_json:
        click.echo(json.dumps(repos, indent=2))
    else:
        table = Table(title="Registered Labs")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Version")
        table.add_column("Category")
        table.add_column("Vendor")
        table.add_column("Difficulty")
        
        for repo in repos:
            table.add_row(
                repo["id"],
                repo["name"],
                repo["version"],
                repo["category"],
                repo["vendor"],
                repo["difficulty"]
            )
        
        console.print(table)


@repo.command()
@click.argument('lab_id')
@click.pass_context
def update(ctx, lab_id):
    """Update a lab repository (git pull)"""
    client = ctx.obj['client']
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(f"Updating {lab_id}...", total=None)
        result = client.update_repo(lab_id)
    
    if result.get('success'):
        console.print(f"[green]✓ {result['message']}[/green]")
    else:
        console.print(f"[red]✗ Update failed[/red]")
        sys.exit(1)


@repo.command()
@click.argument('lab_id')
@click.confirmation_option(prompt='Are you sure you want to remove this lab?')
@click.pass_context
def remove(ctx, lab_id):
    """Remove a lab repository"""
    client = ctx.obj['client']
    result = client.remove_repo(lab_id)
    
    if result.get('success'):
        console.print(f"[green]✓ {result['message']}[/green]")
    else:
        console.print(f"[red]✗ Removal failed[/red]")
        sys.exit(1)


@cli.command()
@click.argument('lab_id')
@click.option('--version', '-v', default='latest', help='Version to deploy')
@click.option('--allocate-ips', is_flag=True, help='Allocate IPs from NetBox')
@click.pass_context
def deploy(ctx, lab_id, version, allocate_ips):
    """Deploy a lab"""
    client = ctx.obj['client']
    
    # Start deployment (async)
    result = client.deploy_lab(lab_id, version, allocate_ips)
    task_id = result.get('task_id')
    
    if not task_id:
        console.print("[red]Failed to start deployment[/red]")
        sys.exit(1)
    
    console.print(f"[blue]Deployment started (task: {task_id})[/blue]")
    
    # Wait for completion with progress
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(f"Deploying {lab_id}...", total=None)
        
        while True:
            status = client.get_task_status(task_id)
            if status.get('status') == 'completed':
                break
            elif status.get('status') == 'failed':
                console.print("[red]✗ Deployment failed[/red]")
                if 'result' in status and 'error' in status['result']:
                    console.print(f"[red]Error: {status['result']['error']}[/red]")
                sys.exit(1)
            time.sleep(2)
    
    # Get final result
    final_status = client.get_task_status(task_id)
    if final_status.get('result', {}).get('success'):
        console.print(f"[green]✓ Successfully deployed {lab_id}[/green]")
    else:
        console.print("[red]✗ Deployment failed[/red]")
        sys.exit(1)


@cli.command()
@click.argument('lab_id')
@click.pass_context
def destroy(ctx, lab_id):
    """Teardown a deployed lab"""
    client = ctx.obj['client']
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(f"Destroying {lab_id}...", total=None)
        result = client.destroy_lab(lab_id)
    
    if result.get('success'):
        console.print(f"[green]✓ {result['message']}[/green]")
    else:
        console.print(f"[red]✗ Destruction failed[/red]")
        sys.exit(1)


@cli.command()
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
@click.pass_context
def status(ctx, output_json):
    """Show deployed labs"""
    client = ctx.obj['client']
    data = client.get_deployments()
    deployments = data.get('deployments', [])
    
    if output_json:
        click.echo(json.dumps(deployments, indent=2))
    else:
        if not deployments:
            console.print("[yellow]No active deployments[/yellow]")
        else:
            table = Table(title="Active Deployments")
            table.add_column("Lab ID", style="cyan")
            table.add_column("Lab Name", style="green")
            table.add_column("Version")
            table.add_column("Deployed At")
            
            for dep in deployments:
                table.add_row(
                    dep["lab_id"],
                    dep["lab_name"],
                    dep["version"],
                    dep["deployed_at"]
                )
            
            console.print(table)


@cli.group()
def config():
    """Manage lab configurations"""
    pass


@config.command('list')
@click.argument('lab_id')
@click.pass_context
def list_scenarios(ctx, lab_id):
    """List available configuration scenarios"""
    client = ctx.obj['client']
    scenarios = client.list_scenarios(lab_id)
    
    if not scenarios:
        console.print(f"[yellow]No configuration scenarios found for {lab_id}[/yellow]")
    else:
        console.print(f"[bold]Configuration scenarios for {lab_id}:[/bold]")
        for scenario in scenarios:
            console.print(f"  • {scenario}")


@config.command('apply')
@click.argument('lab_id')
@click.argument('scenario')
@click.pass_context
def apply_scenario(ctx, lab_id, scenario):
    """Apply a configuration scenario to a deployed lab"""
    client = ctx.obj['client']
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(f"Applying scenario {scenario}...", total=None)
        result = client.apply_scenario(lab_id, scenario)
    
    if result.get('success'):
        console.print(f"[green]✓ {result['message']}[/green]")
        if 'note' in result:
            console.print(f"[yellow]Note: {result['note']}[/yellow]")
    else:
        console.print(f"[red]✗ Failed to apply scenario[/red]")
        sys.exit(1)


@cli.command()
@click.argument('lab_id')
@click.option('--tail', '-n', type=int, help='Number of lines to show')
@click.pass_context
def logs(ctx, lab_id, tail):
    """View deployment logs for a lab"""
    client = ctx.obj['client']
    
    try:
        result = client.get_logs(lab_id)
        log_content = result.get('log', '')
        
        if tail:
            lines = log_content.split('\n')
            log_content = '\n'.join(lines[-tail:])
        
        console.print(f"[bold]Deployment log for {lab_id}:[/bold]")
        console.print(log_content)
    except:
        console.print(f"[yellow]No logs found for {lab_id}[/yellow]")


@cli.command()
def version():
    """Show version information"""
    console.print("labctl version 1.0.0")
    console.print("Copyright (c) 2024 Homelab Manager")


if __name__ == '__main__':
    cli()