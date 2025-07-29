import click
from datetime import datetime
import requests
from django.core.management import call_command
from django.conf import settings
from  .watcher import ensure_single_monitor, get_monitor_thread
from ..models import FileChangeLog

@click.group()
def cli():
    """SecureNet File Monitoring CLI"""
    pass

@cli.command()
@click.argument('path', required=False)
def start(path):
    """Start monitoring a path (uses WATCH_FOLDER from settings if no path provided)"""
    monitor_thread = ensure_single_monitor(path)
    if monitor_thread and monitor_thread.is_alive():
        click.echo(f"✅ Monitor started successfully on: {path or settings.WATCH_FOLDER}")
    else:
        click.echo("❌ Failed to start monitor")

@cli.command()
def stop():
    """Stop the file monitor"""
    monitor_thread = get_monitor_thread()
    if monitor_thread and monitor_thread.is_alive():
        # Your watcher.py already handles stopping via threading.Event
        monitor_thread.join()
        click.echo("✅ Monitor stopped successfully")
    else:
        click.echo("ℹ️ No active monitor found")

@cli.command()
def status():
    """Show monitoring status"""
    monitor_thread = get_monitor_thread()
    click.echo("\nSecureNet Monitor Status")
    click.echo("-" * 40)
    
    if monitor_thread and monitor_thread.is_alive():
        click.echo("Status: 🟢 Active")
        click.echo(f"Watching: {settings.WATCH_FOLDER}")
        
        # Get recent events
        recent_logs = FileChangeLog.objects.order_by('-timestamp')[:5]
        if recent_logs:
            click.echo("\nRecent Events:")
            for log in recent_logs:
                click.echo(f"- [{log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] "
                          f"{log.change_type}: {log.file_path} "
                          f"(Risk: {log.risk_level})")
    else:
        click.echo("Status: 🔴 Inactive")

@cli.command()
def list():
    """List monitored files and their status"""
    try:
        logs = FileChangeLog.objects.order_by('-timestamp')
        
        click.echo("\nSecureNet Monitor - File Status")
        click.echo("-" * 40)
        
        # Group by file path to show latest status
        file_status = {}
        for log in logs:
            if log.file_path not in file_status:
                file_status[log.file_path] = {
                    'last_change': log.timestamp,
                    'status': log.change_type,
                    'risk_level': log.risk_level
                }
        
        for path, info in file_status.items():
            click.echo(f"\nFile: {path}")
            click.echo(f"Last Change: {info['last_change'].strftime('%Y-%m-%d %H:%M:%S')}")
            click.echo(f"Status: {info['status']}")
            click.echo(f"Risk Level: {info['risk_level']}")
            
    except Exception as e:
        click.echo(f"Error retrieving file status: {str(e)}")

if __name__ == '__main__':
    cli()