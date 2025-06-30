"""
Device configuration scenario CLI commands
"""
import click
import json
import sys
from rich.console import Console
from rich.table import Table

console = Console()


@click.group()
def config():
    """Manage device configuration scenarios"""
    pass


@config.command()
@click.argument('lab_id')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
@click.pass_context
def list(ctx, lab_id, output_json):
    """List available device configuration scenarios for a lab"""
    client = ctx.obj['client']
    scenarios = client.list_scenarios(lab_id)
    
    if output_json:
        click.echo(json.dumps({"lab_id": lab_id, "scenarios": scenarios}, indent=2))
    else:
        if scenarios:
            table = Table(title=f"Device Configuration Scenarios for {lab_id}")
            table.add_column("Scenario", style="cyan")
            table.add_column("Description", style="green")
            
            for scenario in scenarios:
                # For now, just show scenario name
                # Could be enhanced to read description from scenario metadata
                table.add_row(scenario, "Device configuration scenario")
            
            console.print(table)
        else:
            console.print(f"[yellow]No device configuration scenarios found for {lab_id}[/yellow]")


@config.command()
@click.argument('lab_id')
@click.argument('scenario')
@click.pass_context
def apply(ctx, lab_id, scenario):
    """Apply a device configuration scenario to a deployed lab"""
    client = ctx.obj['client']
    
    console.print(f"[yellow]Applying device configuration scenario '{scenario}' to {lab_id}...[/yellow]")
    
    result = client.apply_scenario(lab_id, scenario)
    
    if result.get('success'):
        console.print(f"[green]✓ {result['message']}[/green]")
        if 'note' in result:
            console.print(f"[yellow]Note: {result['note']}[/yellow]")
    else:
        console.print(f"[red]✗ Failed to apply scenario: {result.get('error')}[/red]")
        sys.exit(1)