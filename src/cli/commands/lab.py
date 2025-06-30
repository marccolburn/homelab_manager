"""
Lab deployment and management CLI commands
"""
import click
import json
import sys
import time
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


@click.command()
@click.argument('lab_id')
@click.option('--version', '-v', default='latest', help='Version to deploy')
@click.option('--allocate-ips', is_flag=True, help='Allocate IPs from NetBox')
@click.pass_context
def deploy(ctx, lab_id, version, allocate_ips):
    """Deploy a lab"""
    client = ctx.obj['client']
    
    console.print(f"[yellow]Starting deployment of {lab_id}...[/yellow]")
    
    # Start deployment
    result = client.deploy_lab(lab_id, version, allocate_ips)
    task_id = result.get('task_id')
    
    if not task_id:
        console.print(f"[red]✗ Failed to start deployment[/red]")
        sys.exit(1)
    
    # Monitor deployment progress
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Deploying lab...", total=None)
        
        while True:
            status = client.get_task_status(task_id)
            
            if status.get('status') == 'completed':
                break
            elif status.get('status') == 'failed':
                console.print(f"[red]✗ Deployment failed[/red]")
                sys.exit(1)
            
            time.sleep(2)
    
    # Get final result
    final_status = client.get_task_status(task_id)
    final_result = final_status.get('result', {})
    
    if final_result.get('success'):
        console.print(f"[green]✓ {final_result['message']}[/green]")
        console.print(f"[cyan]Deployment ID: {final_result.get('deployment_id')}[/cyan]")
    else:
        console.print(f"[red]✗ Deployment failed: {final_result.get('error')}[/red]")
        sys.exit(1)


@click.command()
@click.argument('lab_id')
@click.confirmation_option(prompt='Are you sure you want to destroy this lab?')
@click.pass_context
def destroy(ctx, lab_id):
    """Destroy a deployed lab"""
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
        console.print(f"[red]✗ Destroy failed: {result.get('error')}[/red]")
        sys.exit(1)


@click.command()
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
@click.pass_context
def status(ctx, output_json):
    """Show status of all deployments"""
    client = ctx.obj['client']
    deployments = client.get_deployments()
    
    if output_json:
        click.echo(json.dumps(deployments, indent=2))
    else:
        table = Table(title="Active Deployments")
        table.add_column("Deployment ID", style="cyan")
        table.add_column("Lab ID", style="green")
        table.add_column("Lab Name")
        table.add_column("Version")
        table.add_column("Deployed At")
        
        for deployment in deployments.get('deployments', []):
            table.add_row(
                deployment["deployment_id"],
                deployment["lab_id"],
                deployment["lab_name"],
                deployment["version"],
                deployment["deployed_at"]
            )
        
        console.print(table)
        console.print(f"\n[cyan]Total active deployments: {deployments.get('total', 0)}[/cyan]")


@click.command()
@click.argument('lab_id')
@click.pass_context
def logs(ctx, lab_id):
    """Show deployment logs for a lab"""
    client = ctx.obj['client']
    result = client.get_logs(lab_id)
    
    if 'error' in result:
        console.print(f"[red]✗ {result['error']}[/red]")
        sys.exit(1)
    
    console.print(f"[cyan]Deployment logs for {lab_id} (ID: {result['deployment_id']})[/cyan]")
    console.print("[yellow]" + "="*60 + "[/yellow]")
    console.print(result['log'])


# Group commands for easier import
lab_commands = [deploy, destroy, status, logs]