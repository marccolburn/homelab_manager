#!/usr/bin/env python3
"""
labctl - Homelab Manager CLI

A lightweight CLI that communicates with the Flask backend API.
"""

import click
import sys
from rich.console import Console

from .client import LabCtlClient
from .commands import repo, lab_commands, config, system_commands

console = Console()

# Default API endpoint
DEFAULT_API_URL = "http://localhost:5001"


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
    
    # Only check backend health if we're running an actual command (not help)
    if ctx.invoked_subcommand and ctx.invoked_subcommand not in ['--help', '-h']:
        if not ctx.obj['client'].health_check():
            console.print(f"[red]Error: Backend is not healthy at {api_url}[/red]")
            console.print("[yellow]Start the backend with: python app.py[/yellow]")
            sys.exit(1)


# Register command groups
cli.add_command(repo)
cli.add_command(config)

# Register individual lab commands
for command in lab_commands:
    cli.add_command(command)

# Register system commands
for command in system_commands:
    cli.add_command(command)


if __name__ == '__main__':
    cli()