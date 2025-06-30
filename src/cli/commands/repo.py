"""
Repository management CLI commands
"""
import click
import json
import sys
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


@click.group()
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