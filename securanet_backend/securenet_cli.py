#!/usr/bin/env python
import click
import os
import sys
import django
import yaml
from datetime import datetime
import time
import subprocess

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'securanet_backend.settings')
django.setup()

from django.conf import settings
from myapp.file_monitor.watcher import ensure_single_monitor, get_monitor_thread
from myapp.models import FileChangeLog, FileAnalysis

@click.group()
def cli():
    """SecureNet Security Monitoring System"""
    pass

@cli.command()
def start():
    """Start the SecureNet monitoring and API server"""
    click.echo("Starting SecureNet Security Monitoring...")
    
    # Start Django server
    django_process = subprocess.Popen([
        sys.executable, 'manage.py', 'runserver'
    ])
    
    # Start file monitor
    monitor_thread = ensure_single_monitor()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        click.echo("\nShutting down services...")
        django_process.terminate()
        # Monitor thread will be stopped by Python shutdown
        django_process.wait()
        click.echo("Services stopped")

@cli.command()
@click.argument('path', required=False)
def monitor(path):
    """Start monitoring a specific path"""
    monitor_thread = ensure_single_monitor(path)
    if monitor_thread and monitor_thread.is_alive():
        click.echo(f"✅ Monitor started successfully on: {path or settings.WATCH_FOLDER}")
    else:
        click.echo("❌ Failed to start monitor")

@cli.command()
def configure():
    """Configure monitoring settings"""
    # Run the configure command
    subprocess.run([sys.executable, 'manage.py', 'configure'])

@cli.command()
def status():
    """Show monitoring status"""
    monitor_thread = get_monitor_thread()
    
    # Get config file
    config_file = os.path.join(settings.BASE_DIR, 'monitor_config.yaml')
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
    else:
        config = {'monitoring': {'mode': 'custom', 'paths': []}}
    
    click.echo("\n╔══════════════════════════════════════════╗")
    click.echo("║         SecureNet Monitor Status         ║")
    click.echo("╚══════════════════════════════════════════╝")
    
    # Monitor status
    if monitor_thread and monitor_thread.is_alive():
        click.echo("Status: 🟢 Active")
    else:
        click.echo("Status: 🔴 Inactive")
    
    # Configuration info
    click.echo(f"\nMonitoring Mode: {config['monitoring'].get('mode', 'custom')}")
    
    # Paths being monitored
    click.echo("\nMonitored Paths:")
    for path in config['monitoring'].get('paths', []):
        click.echo(f"  • {path}")
    
    # Recent activity
    click.echo("\nRecent Activity:")
    recent_logs = FileChangeLog.objects.order_by('-timestamp')[:5]
    if recent_logs:
        for log in recent_logs:
            risk_indicator = "🟢" if log.risk_level == "safe" else "🟠" if log.risk_level == "suspicious" else "🔴"
            click.echo(f"  {risk_indicator} [{log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] "
                      f"{log.change_type.upper()}: {log.file_path}")
    else:
        click.echo("  No recent activity")
    
    # Statistics
    total_logs = FileChangeLog.objects.count()
    safe_logs = FileChangeLog.objects.filter(risk_level="safe").count()
    suspicious_logs = FileChangeLog.objects.filter(risk_level="suspicious").count()
    dangerous_logs = FileChangeLog.objects.filter(risk_level="dangerous").count()
    
    click.echo("\nStatistics:")
    click.echo(f"  Total Events: {total_logs}")
    click.echo(f"  Safe: {safe_logs}")
    click.echo(f"  Suspicious: {suspicious_logs}")
    click.echo(f"  Dangerous: {dangerous_logs}")

@cli.command()
@click.option('--risk', type=click.Choice(['safe', 'suspicious', 'dangerous', 'all']), default='all',
              help='Filter by risk level')
@click.option('--limit', type=int, default=10, help='Number of logs to display')
def logs(risk, limit):
    """Display file activity logs with filtering"""
    query = FileChangeLog.objects.order_by('-timestamp')
    
    if risk != 'all':
        query = query.filter(risk_level=risk)
    
    logs = query[:limit]
    
    click.echo("\n╔══════════════════════════════════════════╗")
    click.echo("║           File Activity Logs            ║")
    click.echo("╚══════════════════════════════════════════╝")
    
    if not logs:
        click.echo("No logs found matching your criteria.")
        return
    
    for log in logs:
        risk_indicator = "🟢" if log.risk_level == "safe" else "🟠" if log.risk_level == "suspicious" else "🔴"
        click.echo(f"\n{risk_indicator} {log.change_type.upper()}: {log.file_path}")
        click.echo(f"  Time: {log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        click.echo(f"  Risk: {log.risk_level.upper()}")
        
        if log.recommendation:
            click.echo(f"  Recommendation: {log.recommendation.split('Risk Level:')[0].strip()}")

if __name__ == '__main__':
    cli()