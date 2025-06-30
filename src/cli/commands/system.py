"""
System and server configuration CLI commands
"""
import click
import json
from rich.console import Console

console = Console()


@click.command()
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
@click.pass_context
def doctor(ctx, output_json):
    """Check system health and show backend configuration"""
    client = ctx.obj['client']
    
    # Check backend health
    is_healthy = client.health_check()
    
    if not is_healthy:
        console.print("[red]✗ Backend is not healthy[/red]")
        return
    
    # Get configuration
    config_data = client.get_config()
    
    if output_json:
        health_info = {
            "backend_healthy": is_healthy,
            "configuration": config_data
        }
        click.echo(json.dumps(health_info, indent=2))
    else:
        console.print("[green]✓ Backend is healthy[/green]")
        console.print("\n[cyan]Backend Configuration[/cyan]")
        console.print("[yellow]" + "="*40 + "[/yellow]")
        
        # Display key configuration items
        console.print(f"Repositories directory: {config_data.get('repos_dir')}")
        console.print(f"Logs directory: {config_data.get('logs_dir')}")
        console.print(f"State file: {config_data.get('state_file')}")
        console.print(f"Git command: {config_data.get('git_cmd')}")
        console.print(f"Clab-tools command: {config_data.get('clab_tools_cmd')}")
        
        # NetBox configuration
        netbox = config_data.get('netbox', {})
        console.print(f"\nNetBox integration: {'Enabled' if netbox.get('enabled') else 'Disabled'}")
        if netbox.get('enabled'):
            console.print(f"NetBox URL: {netbox.get('url')}")
            console.print(f"Default prefix: {netbox.get('default_prefix')}")
        
        # Monitoring configuration
        monitoring = config_data.get('monitoring', {})
        console.print(f"\nMonitoring endpoints:")
        console.print(f"Prometheus: {monitoring.get('prometheus')}")
        console.print(f"Grafana: {monitoring.get('grafana')}")


@click.command()
@click.pass_context
def version(ctx):
    """Show version information"""
    # For now, just show basic info
    # Could be enhanced to get version from backend API
    console.print("[cyan]labctl - Homelab Manager CLI[/cyan]")
    console.print("Version: 1.0.0-dev")
    console.print("Backend API: Connected")
    
    # Check if backend is healthy
    client = ctx.obj['client']
    if client.health_check():
        console.print("[green]Backend Status: Healthy[/green]")
    else:
        console.print("[red]Backend Status: Unhealthy[/red]")


# Individual commands for easier import
system_commands = [doctor, version]