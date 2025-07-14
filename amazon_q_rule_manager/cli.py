"""Command-line interface for Amazon Q Rule Manager."""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn

from . import __version__
from .core import RuleManager, RuleManagerError, RuleNotFoundError, WorkspaceNotFoundError
from .models import RuleCategory, RuleSource

console = Console()


def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"[red]Error:[/red] {message}")


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[green]✓[/green] {message}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[yellow]Warning:[/yellow] {message}")


def print_info(message: str) -> None:
    """Print an info message."""
    console.print(f"[blue]ℹ[/blue] {message}")


@click.group()
@click.version_option(version=__version__)
@click.option('--config-dir', type=click.Path(path_type=Path), 
              help='Custom configuration directory')
@click.pass_context
def cli(ctx: click.Context, config_dir: Optional[Path]) -> None:
    """Amazon Q Rule Manager - Manage Amazon Q Developer rules globally and per workspace."""
    ctx.ensure_object(dict)
    try:
        ctx.obj['manager'] = RuleManager(config_dir)
    except Exception as e:
        print_error(f"Failed to initialize rule manager: {e}")
        sys.exit(1)


@cli.group()
def catalog():
    """Manage rule catalog."""
    pass


@catalog.command('update')
@click.option('--force', is_flag=True, help='Force update even if recently updated')
@click.pass_context
def update_catalog(ctx: click.Context, force: bool) -> None:
    """Update rule catalog from remote source."""
    manager: RuleManager = ctx.obj['manager']
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Updating catalog...", total=None)
        
        try:
            updated = manager.update_catalog(force=force)
            progress.update(task, completed=True)
            
            if updated:
                print_success("Catalog updated successfully")
            else:
                print_info("Catalog is already up to date")
                
        except RuleManagerError as e:
            progress.update(task, completed=True)
            print_error(str(e))
            sys.exit(1)


@catalog.command('list')
@click.option('--category', type=click.Choice([c.value for c in RuleCategory]), 
              help='Filter by category')
@click.option('--tag', help='Filter by tag')
@click.option('--search', help='Search rules by query')
@click.pass_context
def list_catalog(ctx: click.Context, category: Optional[str], tag: Optional[str], 
                search: Optional[str]) -> None:
    """List available rules in catalog."""
    manager: RuleManager = ctx.obj['manager']
    
    try:
        if search:
            rules = manager.search_rules(search)
        else:
            rules = manager.list_available_rules(category=category, tag=tag)
        
        if not rules:
            print_info("No rules found matching criteria")
            return
        
        table = Table(title="Available Rules")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Title", style="magenta")
        table.add_column("Category", style="green")
        table.add_column("Version", style="yellow")
        table.add_column("Description", style="white")
        
        for rule in sorted(rules, key=lambda r: r.name):
            table.add_row(
                rule.name,
                rule.title,
                rule.category,
                rule.version,
                rule.description[:60] + "..." if len(rule.description) > 60 else rule.description
            )
        
        console.print(table)
        
    except RuleManagerError as e:
        print_error(str(e))
        sys.exit(1)


@catalog.command('show')
@click.argument('rule_name')
@click.pass_context
def show_rule(ctx: click.Context, rule_name: str) -> None:
    """Show detailed information about a rule."""
    manager: RuleManager = ctx.obj['manager']
    
    try:
        metadata = manager.get_rule_metadata(rule_name)
        
        # Create info panel
        info_text = Text()
        info_text.append(f"Title: {metadata.title}\n", style="bold")
        info_text.append(f"Category: {metadata.category}\n")
        info_text.append(f"Version: {metadata.version}\n")
        info_text.append(f"Author: {metadata.author or 'Unknown'}\n")
        info_text.append(f"Description: {metadata.description}\n\n")
        
        if metadata.tags:
            info_text.append(f"Tags: {', '.join(metadata.tags)}\n")
        
        if metadata.supported_languages:
            info_text.append(f"Languages: {', '.join(metadata.supported_languages)}\n")
        
        if metadata.aws_services:
            info_text.append(f"AWS Services: {', '.join(metadata.aws_services)}\n")
        
        if metadata.terraform_providers:
            info_text.append(f"Terraform Providers: {', '.join(metadata.terraform_providers)}\n")
        
        if metadata.dependencies:
            info_text.append(f"Dependencies: {', '.join(metadata.dependencies)}\n")
        
        if metadata.conflicts:
            info_text.append(f"Conflicts: {', '.join(metadata.conflicts)}\n")
        
        if metadata.examples:
            info_text.append("\nExamples:\n", style="bold")
            for example in metadata.examples:
                info_text.append(f"  • {example}\n")
        
        panel = Panel(info_text, title=f"Rule: {rule_name}", border_style="blue")
        console.print(panel)
        
    except RuleNotFoundError as e:
        print_error(str(e))
        sys.exit(1)
    except RuleManagerError as e:
        print_error(str(e))
        sys.exit(1)


@cli.group()
def global_rules():
    """Manage global rules."""
    pass


@global_rules.command('install')
@click.argument('rule_name')
@click.option('--force', is_flag=True, help='Force installation even if rule exists')
@click.pass_context
def install_global(ctx: click.Context, rule_name: str, force: bool) -> None:
    """Install a rule globally."""
    manager: RuleManager = ctx.obj['manager']
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"Installing rule '{rule_name}'...", total=None)
        
        try:
            manager.install_rule_globally(rule_name, force=force)
            progress.update(task, completed=True)
            print_success(f"Rule '{rule_name}' installed globally")
            
        except (RuleNotFoundError, RuleManagerError) as e:
            progress.update(task, completed=True)
            print_error(str(e))
            sys.exit(1)


@global_rules.command('uninstall')
@click.argument('rule_name')
@click.pass_context
def uninstall_global(ctx: click.Context, rule_name: str) -> None:
    """Uninstall a global rule."""
    manager: RuleManager = ctx.obj['manager']
    
    try:
        manager.uninstall_rule_globally(rule_name)
        print_success(f"Rule '{rule_name}' uninstalled globally")
        
    except (RuleNotFoundError, RuleManagerError) as e:
        print_error(str(e))
        sys.exit(1)


@global_rules.command('list')
@click.pass_context
def list_global(ctx: click.Context) -> None:
    """List globally installed rules."""
    manager: RuleManager = ctx.obj['manager']
    
    try:
        rules = manager.list_global_rules()
        
        if not rules:
            print_info("No global rules installed")
            return
        
        table = Table(title="Global Rules")
        table.add_column("Rule Name", style="cyan")
        
        for rule in sorted(rules):
            table.add_row(rule)
        
        console.print(table)
        
    except RuleManagerError as e:
        print_error(str(e))
        sys.exit(1)


@cli.group()
def workspace():
    """Manage workspaces and workspace rules."""
    pass


@workspace.command('register')
@click.argument('workspace_path', type=click.Path(exists=True, path_type=Path))
@click.option('--name', help='Workspace name (defaults to directory name)')
@click.pass_context
def register_workspace(ctx: click.Context, workspace_path: Path, name: Optional[str]) -> None:
    """Register a workspace."""
    manager: RuleManager = ctx.obj['manager']
    
    try:
        workspace_config = manager.register_workspace(workspace_path, name)
        print_success(f"Workspace '{workspace_config.name}' registered at {workspace_path}")
        
    except RuleManagerError as e:
        print_error(str(e))
        sys.exit(1)


@workspace.command('unregister')
@click.argument('workspace_name')
@click.pass_context
def unregister_workspace(ctx: click.Context, workspace_name: str) -> None:
    """Unregister a workspace."""
    manager: RuleManager = ctx.obj['manager']
    
    try:
        manager.unregister_workspace(workspace_name)
        print_success(f"Workspace '{workspace_name}' unregistered")
        
    except WorkspaceNotFoundError as e:
        print_error(str(e))
        sys.exit(1)


@workspace.command('list')
@click.pass_context
def list_workspaces(ctx: click.Context) -> None:
    """List registered workspaces."""
    manager: RuleManager = ctx.obj['manager']
    
    try:
        workspaces = manager.list_workspaces()
        
        if not workspaces:
            print_info("No workspaces registered")
            return
        
        table = Table(title="Registered Workspaces")
        table.add_column("Name", style="cyan")
        table.add_column("Path", style="magenta")
        table.add_column("Rules", style="green")
        table.add_column("Updated", style="yellow")
        
        for ws in sorted(workspaces, key=lambda w: w.name):
            table.add_row(
                ws.name,
                str(ws.path),
                str(len(ws.installed_rules)),
                ws.updated_at.strftime("%Y-%m-%d %H:%M")
            )
        
        console.print(table)
        
    except RuleManagerError as e:
        print_error(str(e))
        sys.exit(1)


@workspace.command('install')
@click.argument('rule_name')
@click.argument('workspace_name')
@click.option('--force', is_flag=True, help='Force installation even if rule exists')
@click.pass_context
def install_workspace_rule(ctx: click.Context, rule_name: str, workspace_name: str, 
                          force: bool) -> None:
    """Install a rule to a workspace."""
    manager: RuleManager = ctx.obj['manager']
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"Installing rule '{rule_name}' to workspace '{workspace_name}'...", total=None)
        
        try:
            manager.install_rule_to_workspace(rule_name, workspace_name, force=force)
            progress.update(task, completed=True)
            print_success(f"Rule '{rule_name}' installed to workspace '{workspace_name}'")
            
        except (RuleNotFoundError, WorkspaceNotFoundError, RuleManagerError) as e:
            progress.update(task, completed=True)
            print_error(str(e))
            sys.exit(1)


@workspace.command('uninstall')
@click.argument('rule_name')
@click.argument('workspace_name')
@click.pass_context
def uninstall_workspace_rule(ctx: click.Context, rule_name: str, workspace_name: str) -> None:
    """Uninstall a rule from a workspace."""
    manager: RuleManager = ctx.obj['manager']
    
    try:
        manager.uninstall_rule_from_workspace(rule_name, workspace_name)
        print_success(f"Rule '{rule_name}' uninstalled from workspace '{workspace_name}'")
        
    except (RuleNotFoundError, WorkspaceNotFoundError, RuleManagerError) as e:
        print_error(str(e))
        sys.exit(1)


@workspace.command('list-rules')
@click.argument('workspace_name')
@click.pass_context
def list_workspace_rules(ctx: click.Context, workspace_name: str) -> None:
    """List rules installed in a workspace."""
    manager: RuleManager = ctx.obj['manager']
    
    try:
        rules = manager.list_workspace_rules(workspace_name)
        
        if not rules:
            print_info(f"No rules installed in workspace '{workspace_name}'")
            return
        
        table = Table(title=f"Rules in Workspace: {workspace_name}")
        table.add_column("Rule Name", style="cyan")
        
        for rule in sorted(rules):
            table.add_row(rule)
        
        console.print(table)
        
    except WorkspaceNotFoundError as e:
        print_error(str(e))
        sys.exit(1)


@workspace.command('export')
@click.argument('workspace_name')
@click.argument('export_path', type=click.Path(path_type=Path))
@click.pass_context
def export_workspace_rules(ctx: click.Context, workspace_name: str, export_path: Path) -> None:
    """Export workspace rules to a directory."""
    manager: RuleManager = ctx.obj['manager']
    
    try:
        manager.export_workspace_rules(workspace_name, export_path)
        print_success(f"Rules exported from workspace '{workspace_name}' to {export_path}")
        
    except (WorkspaceNotFoundError, RuleManagerError) as e:
        print_error(str(e))
        sys.exit(1)


@workspace.command('import')
@click.argument('workspace_name')
@click.argument('import_path', type=click.Path(exists=True, path_type=Path))
@click.option('--force', is_flag=True, help='Force import even if rules exist')
@click.pass_context
def import_workspace_rules(ctx: click.Context, workspace_name: str, import_path: Path, 
                          force: bool) -> None:
    """Import rules to a workspace from a directory."""
    manager: RuleManager = ctx.obj['manager']
    
    try:
        manager.import_workspace_rules(workspace_name, import_path, force=force)
        print_success(f"Rules imported to workspace '{workspace_name}' from {import_path}")
        
    except (WorkspaceNotFoundError, RuleManagerError) as e:
        print_error(str(e))
        sys.exit(1)


# Legacy commands for backward compatibility
@cli.command('install', hidden=True)
@click.argument('rule_name')
@click.argument('project_dir', type=click.Path(path_type=Path))
@click.pass_context
def legacy_install(ctx: click.Context, rule_name: str, project_dir: Path) -> None:
    """Legacy install command (deprecated)."""
    print_warning("This command is deprecated. Use 'workspace install' instead.")
    
    manager: RuleManager = ctx.obj['manager']
    
    # Auto-register workspace if not exists
    workspace_name = project_dir.name
    if workspace_name not in [ws.name for ws in manager.list_workspaces()]:
        manager.register_workspace(project_dir, workspace_name)
        print_info(f"Auto-registered workspace '{workspace_name}'")
    
    # Install rule
    try:
        manager.install_rule_to_workspace(rule_name, workspace_name)
        print_success(f"Rule '{rule_name}' installed to {project_dir}")
    except (RuleNotFoundError, RuleManagerError) as e:
        print_error(str(e))
        sys.exit(1)


@cli.command('list', hidden=True)
@click.argument('project_dir', type=click.Path(path_type=Path), required=False)
@click.pass_context
def legacy_list(ctx: click.Context, project_dir: Optional[Path]) -> None:
    """Legacy list command (deprecated)."""
    print_warning("This command is deprecated. Use 'catalog list' or 'workspace list-rules' instead.")
    
    manager: RuleManager = ctx.obj['manager']
    
    if project_dir:
        # List workspace rules
        workspace_name = project_dir.name
        try:
            rules = manager.list_workspace_rules(workspace_name)
            if rules:
                console.print(f"Rules in {project_dir}:")
                for rule in sorted(rules):
                    console.print(f"  • {rule}")
            else:
                print_info(f"No rules found in {project_dir}")
        except WorkspaceNotFoundError:
            print_info(f"No rules found in {project_dir}")
    else:
        # List available rules
        rules = manager.list_available_rules()
        if rules:
            console.print("Available rules:")
            for rule in sorted(rules, key=lambda r: r.name):
                console.print(f"  • {rule.name} - {rule.title}")
        else:
            print_info("No rules available")


def main() -> None:
    """Main entry point."""
    try:
        cli()
    except KeyboardInterrupt:
        print_info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
