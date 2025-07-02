"""
Configuration management module
"""
import yaml
from pathlib import Path
from typing import Dict

# Default paths
DEFAULT_CONFIG_DIR = Path.home() / ".labctl"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.yaml"
DEFAULT_STATE_FILE = DEFAULT_CONFIG_DIR / "state.json"
DEFAULT_REPOS_DIR = DEFAULT_CONFIG_DIR / "repos"
DEFAULT_LOGS_DIR = DEFAULT_CONFIG_DIR / "logs"


def _deep_update(base: Dict, updates: Dict) -> None:
    """Recursively update nested dictionaries"""
    for key, value in updates.items():
        if isinstance(value, dict) and key in base and isinstance(base[key], dict):
            _deep_update(base[key], value)
        else:
            base[key] = value


def load_config(config_file: Path = None) -> Dict:
    """Load configuration from file or create default"""
    if config_file is None:
        config_file = DEFAULT_CONFIG_FILE
    
    if not config_file.exists():
        # Create default config
        config_file.parent.mkdir(parents=True, exist_ok=True)
        default_config = {
            "repos_dir": str(DEFAULT_REPOS_DIR),
            "logs_dir": str(DEFAULT_LOGS_DIR),
            "state_file": str(DEFAULT_STATE_FILE),
            "clab_tools_cmd": "clab-tools",
            "git_cmd": "git",
            "clab_tools_password": "",  # Set password for remote operations
            "remote_credentials": {
                "ssh_password": "",
                "sudo_password": ""
            },
            "monitoring": {
                "prometheus": "http://localhost:9090",
                "grafana": "http://localhost:3000"
            },
            "netbox": {
                "enabled": False,
                "url": "",
                "token": "",
                "default_prefix": "10.100.100.0/24"
            }
        }
        with open(config_file, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        return default_config
    
    with open(config_file) as f:
        return yaml.safe_load(f)


def update_config(updates: Dict, config_file: Path = None) -> Dict:
    """Update configuration with new values"""
    if config_file is None:
        config_file = DEFAULT_CONFIG_FILE
    
    # Load current config
    config = load_config(config_file)
    
    # Update with new values
    _deep_update(config, updates)
    
    # Save updated config
    with open(config_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    return config


def save_config(config: Dict, config_file: Path = None):
    """Save configuration to file"""
    if config_file is None:
        config_file = DEFAULT_CONFIG_FILE
    
    config_file.parent.mkdir(parents=True, exist_ok=True)
    with open(config_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)