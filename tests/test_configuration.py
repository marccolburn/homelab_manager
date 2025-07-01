#!/usr/bin/env python3
"""
Configuration validation and debugging script for Homelab Manager

This script helps verify:
1. Configuration files are loaded correctly
2. Remote deployment settings are valid
3. NetBox integration is configured
4. Lab repository configurations are correct
"""

import os
import sys
from pathlib import Path
import yaml
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.backend.core.config import load_config, DEFAULT_CONFIG_FILE


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def check_backend_config():
    """Check the backend configuration file"""
    print_section("Backend Configuration (~/.labctl/config.yaml)")
    
    if DEFAULT_CONFIG_FILE.exists():
        print(f"✅ Config file found: {DEFAULT_CONFIG_FILE}")
        config = load_config()
        print("\nConfiguration contents:")
        for key, value in config.items():
            if isinstance(value, dict):
                print(f"\n{key}:")
                for k, v in value.items():
                    print(f"  {k}: {v}")
            else:
                print(f"{key}: {value}")
    else:
        print(f"❌ Config file not found at: {DEFAULT_CONFIG_FILE}")
        print("  Backend will create default config on first run")
    
    return load_config()


def check_environment_vars():
    """Check required environment variables"""
    print_section("Environment Variables")
    
    vars_to_check = {
        'CLAB_TOOLS_PASSWORD': 'Required for remote deployments with sudo',
        'PYTHONPATH': 'Required for running the backend',
        'HOME': 'Used to locate config files'
    }
    
    for var, description in vars_to_check.items():
        value = os.environ.get(var)
        if value:
            if var == 'CLAB_TOOLS_PASSWORD':
                print(f"✅ {var}: {'*' * len(value)} ({description})")
            else:
                print(f"✅ {var}: {value} ({description})")
        else:
            print(f"❌ {var}: Not set ({description})")


def check_lab_config(lab_path):
    """Check a specific lab's configuration"""
    print_section(f"Lab Configuration: {lab_path}")
    
    lab_path = Path(lab_path)
    if not lab_path.exists():
        print(f"❌ Lab path not found: {lab_path}")
        return None
    
    # Check lab-metadata.yaml
    metadata_file = lab_path / "lab-metadata.yaml"
    if metadata_file.exists():
        print(f"✅ Found lab-metadata.yaml")
        with open(metadata_file) as f:
            metadata = yaml.safe_load(f)
            print(f"\n  Lab Name: {metadata.get('name', 'N/A')}")
            print(f"  Lab ID: {metadata.get('id', 'N/A')}")
            
            # Check NetBox config in metadata
            if 'netbox' in metadata:
                print("\n  NetBox Configuration (from metadata):")
                for k, v in metadata['netbox'].items():
                    print(f"    {k}: {v}")
    else:
        print(f"❌ lab-metadata.yaml not found")
    
    # Check clab_tools_files/config.yaml
    clab_config_file = lab_path / "clab_tools_files" / "config.yaml"
    if clab_config_file.exists():
        print(f"\n✅ Found clab_tools_files/config.yaml")
        with open(clab_config_file) as f:
            clab_config = yaml.safe_load(f)
            
            # Check for remote configuration
            if 'remote' in clab_config:
                print("\n  Remote Host Configuration:")
                remote = clab_config['remote']
                print(f"    Host: {remote.get('host', 'Not specified')}")
                print(f"    User: {remote.get('user', 'Not specified')}")
                print(f"    Password: {'Set in config' if 'password' in remote else 'Not in config (use env var)'}")
            else:
                print("\n  ℹ️  No remote configuration (will deploy locally)")
    else:
        print(f"❌ clab_tools_files/config.yaml not found")
    
    # Check bootstrap.sh
    bootstrap_file = lab_path / "clab_tools_files" / "bootstrap.sh"
    if bootstrap_file.exists():
        print(f"\n✅ Found bootstrap.sh")
        if os.access(bootstrap_file, os.X_OK):
            print("  ✅ bootstrap.sh is executable")
        else:
            print("  ❌ bootstrap.sh is NOT executable")
            print(f"     Run: chmod +x {bootstrap_file}")
    else:
        print(f"❌ bootstrap.sh not found")
    
    return metadata if 'metadata' in locals() else None


def check_netbox_config(config):
    """Check NetBox configuration and connectivity"""
    print_section("NetBox Configuration Check")
    
    netbox_config = config.get('netbox', {})
    
    if not netbox_config.get('enabled'):
        print("ℹ️  NetBox is disabled in backend configuration")
        return
    
    print("✅ NetBox is enabled")
    print(f"  URL: {netbox_config.get('url', 'Not set')}")
    print(f"  Token: {'Set' if netbox_config.get('token') else 'Not set'}")
    print(f"  Default Prefix: {netbox_config.get('default_prefix', 'Not set')}")
    
    # Try to connect to NetBox
    if netbox_config.get('url') and netbox_config.get('token'):
        try:
            import requests
            headers = {'Authorization': f"Token {netbox_config['token']}"}
            response = requests.get(f"{netbox_config['url']}/api/", headers=headers, timeout=5)
            if response.status_code == 200:
                print("\n✅ Successfully connected to NetBox API")
            else:
                print(f"\n❌ NetBox API returned status {response.status_code}")
        except Exception as e:
            print(f"\n❌ Failed to connect to NetBox: {e}")


def check_deployment_directories(config):
    """Check deployment-related directories"""
    print_section("Deployment Directories")
    
    dirs_to_check = {
        'repos_dir': "Lab repositories",
        'logs_dir': "Deployment logs",
    }
    
    for key, description in dirs_to_check.items():
        path = Path(config.get(key, 'Not configured'))
        if path.exists():
            print(f"✅ {description}: {path}")
            if key == 'repos_dir':
                repos = list(path.iterdir()) if path.is_dir() else []
                if repos:
                    print(f"   Found {len(repos)} repositories:")
                    for repo in repos[:5]:  # Show first 5
                        print(f"   - {repo.name}")
        else:
            print(f"❌ {description}: {path} (does not exist)")


def main():
    """Main function to run all checks"""
    print("\n🔍 Homelab Manager Configuration Check")
    print("=====================================")
    
    # Check backend config
    config = check_backend_config()
    
    # Check environment
    check_environment_vars()
    
    # Check deployment directories
    check_deployment_directories(config)
    
    # Check NetBox
    check_netbox_config(config)
    
    # Check specific lab if provided
    if len(sys.argv) > 1:
        lab_path = sys.argv[1]
        check_lab_config(lab_path)
    else:
        print_section("Lab Configuration Check")
        print("ℹ️  To check a specific lab configuration, run:")
        print(f"   python {sys.argv[0]} /path/to/lab/repo")
        
        # Try to check jncie_sp_ssb if it exists
        default_lab = Path.cwd() / "jncie_sp_ssb"
        if default_lab.exists():
            print(f"\nFound lab in current directory: {default_lab}")
            check_lab_config(default_lab)
    
    print("\n✅ Configuration check complete!")
    print("\nFor remote deployments, ensure:")
    print("1. SSH key authentication is set up")
    print("2. CLAB_TOOLS_PASSWORD environment variable is set (if needed)")
    print("3. Remote host has clab-tools installed")
    print("4. bootstrap.sh is executable")


if __name__ == "__main__":
    main()