# Configuration Guide

This guide covers all configuration options for Homelab Manager, including environment variables, configuration files, and advanced settings.

## Configuration Overview

Homelab Manager uses multiple configuration methods:
1. **Environment Variables** - Runtime configuration
2. **Configuration Files** - Persistent settings
3. **Command-line Arguments** - Override settings
4. **Default Values** - Built-in defaults

Configuration priority (highest to lowest):
1. Command-line arguments
2. Environment variables
3. Configuration files
4. Default values

## Environment Variables

### Core Settings

#### LABCTL_API_URL
Sets the backend API URL for the CLI client.

```bash
export LABCTL_API_URL="http://lab-server:5000"

# For HTTPS with custom port
export LABCTL_API_URL="https://lab-api.example.com:8443"

# For SSH tunnel
export LABCTL_API_URL="http://localhost:5000"
```

#### LAB_REPOS_PATH
Directory where lab repositories are cloned.

```bash
# Default: ~/lab_repos
export LAB_REPOS_PATH="/opt/labs"

# For shared lab storage
export LAB_REPOS_PATH="/mnt/shared/labs"
```

#### LABCTL_LOG_LEVEL
Controls logging verbosity.

```bash
# Options: DEBUG, INFO, WARNING, ERROR
export LABCTL_LOG_LEVEL="DEBUG"
```

### Backend-Specific Variables

#### FLASK_ENV
Flask application environment.

```bash
# For development
export FLASK_ENV="development"

# For production (default)
export FLASK_ENV="production"
```

#### LABCTL_BACKEND_PORT
Port for the backend API server.

```bash
# Default: 5000
export LABCTL_BACKEND_PORT="8080"
```

#### LABCTL_BACKEND_HOST
Host binding for the backend server.

```bash
# Default: 0.0.0.0 (all interfaces)
export LABCTL_BACKEND_HOST="127.0.0.1"  # Local only
```

## Configuration Files

### Backend Configuration

The backend looks for configuration in these locations (in order):
1. `/etc/homelab-manager/config.yaml`
2. `~/.config/homelab-manager/config.yaml`
3. `./lab_manager_config.yaml` (current directory)

**Example backend configuration (`lab_manager_config.yaml`):**

```yaml
# Server Configuration
server:
  host: "0.0.0.0"
  port: 5000
  debug: false
  
# Lab Repository Settings
labs:
  base_path: "~/lab_repos"
  git_timeout: 300  # seconds
  max_concurrent_deployments: 3
  
# Deployment Settings
deployment:
  log_retention_days: 30
  state_file: "~/.homelab-manager/state.json"
  cleanup_on_failure: true
  
# Security Settings
security:
  api_key_required: false
  allowed_origins: ["*"]
  max_request_size: "16MB"
  
# Logging Configuration
logging:
  level: "INFO"
  file: "/var/log/homelab-manager/backend.log"
  max_size: "100MB"
  backup_count: 5
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### CLI Configuration

The CLI looks for configuration in:
1. `~/.config/labctl/config.yaml`
2. Environment variables

**Example CLI configuration (`~/.config/labctl/config.yaml`):**

```yaml
# API Connection
api:
  url: "http://lab-server:5000"
  timeout: 30
  verify_ssl: true
  
# Display Settings
display:
  color: true
  progress_bars: true
  table_format: "grid"  # Options: grid, simple, fancy_grid
  
# CLI Behavior
cli:
  confirm_destructive: true
  auto_refresh_status: false
  default_version: "latest"
```

## NetBox Integration

### Basic Configuration

Configure NetBox integration for dynamic IP allocation:

```yaml
# In lab_manager_config.yaml
netbox:
  enabled: true
  url: "https://netbox.example.com"
  token: "your-api-token-here"
  verify_ssl: true
  
  # IP Allocation Settings
  allocation:
    prefix: "10.100.100.0/24"      # Default prefix for labs
    site: "Lab Environment"         # NetBox site name
    role: "Lab Device"             # Device role
    tenant: "Lab Team"             # Optional tenant
    
  # Cleanup Settings
  cleanup:
    on_destroy: true               # Release IPs when lab destroyed
    grace_period: 300              # Seconds before cleanup
    
  # Device Registration
  devices:
    manufacturer: "Virtual"
    device_type: "container"
    platform: "linux"
```

### Advanced NetBox Settings

```yaml
netbox:
  # ... basic settings ...
  
  # Custom Fields
  custom_fields:
    lab_id: true
    deployment_date: true
    owner: true
    
  # IP Pool Management
  pools:
    management:
      prefix: "10.100.100.0/24"
      description: "Lab Management Network"
    data:
      prefix: "10.100.101.0/24"
      description: "Lab Data Network"
      
  # Tagging
  tags:
    - "lab-device"
    - "containerlab"
    - "automated"
```

### Environment Variable Override

```bash
# Override NetBox settings via environment
export NETBOX_URL="https://netbox.example.com"
export NETBOX_TOKEN="your-token"
export NETBOX_VERIFY_SSL="false"  # For self-signed certs
```

## Lab Repository Configuration

### lab-metadata.yaml

Each lab repository must contain a `lab-metadata.yaml` file:

```yaml
# Required fields
name: "BGP Advanced Lab"
id: "bgp-advanced"
version: "1.0.0"

# Optional fields
category: "Routing"
vendor: "Juniper"
difficulty: "Intermediate"

# Description
description:
  short: "Advanced BGP features and policies"
  long: |
    Comprehensive lab covering:
    - BGP communities
    - Route reflection
    - Complex policies

# Resource requirements
requirements:
  memory_gb: 32
  cpu_cores: 16
  disk_gb: 40
  containerlab_version: ">=0.48.0"

# Platform (for future multi-platform support)
platform: "containerlab"

# Tags for searchability
tags:
  - bgp
  - routing
  - service-provider

# Git repository info
repository:
  url: "git@github.com:org/bgp-advanced.git"
  branch: "main"
  
# NetBox integration (optional)
netbox:
  enabled: true
  prefix: "10.100.200.0/24"  # Override default
  site: "BGP Lab"
  
# Custom variables (passed to deployment scripts)
variables:
  region: "us-east"
  environment: "training"
```

## Systemd Service Configuration

### Backend Service

The systemd service file is installed at `/etc/systemd/system/labctl-backend.service`:

```ini
[Unit]
Description=Homelab Manager Backend API
After=network.target

[Service]
Type=simple
User=labctl
Group=labctl
WorkingDirectory=/opt/homelab-manager

# Environment
Environment="PATH=/opt/homelab-manager/.venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="FLASK_ENV=production"
Environment="PYTHONUNBUFFERED=1"

# Custom environment file (optional)
EnvironmentFile=-/etc/homelab-manager/environment

# Start command
ExecStart=/opt/homelab-manager/.venv/bin/python -m src.backend.app

# Restart policy
Restart=on-failure
RestartSec=10

# Security
NoNewPrivileges=true
PrivateTmp=true

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=labctl-backend

[Install]
WantedBy=multi-user.target
```

### Custom Environment File

Create `/etc/homelab-manager/environment` for additional settings:

```bash
# API Configuration
LABCTL_BACKEND_PORT=8080
LABCTL_LOG_LEVEL=INFO

# NetBox Integration
NETBOX_URL=https://netbox.example.com
NETBOX_TOKEN=your-secure-token

# Lab Settings
LAB_REPOS_PATH=/var/lib/homelab-manager/labs
```

## Security Configuration

### API Authentication (Future Feature)

```yaml
# In lab_manager_config.yaml
security:
  authentication:
    enabled: true
    type: "token"  # Options: token, oauth, ldap
    
  # Token Authentication
  token:
    header: "X-API-Token"
    expiry: 86400  # seconds
    
  # Rate Limiting
  rate_limit:
    enabled: true
    requests_per_minute: 60
    burst: 10
```

### SSL/TLS Configuration

For production deployments, use a reverse proxy:

```nginx
# /etc/nginx/conf.d/labctl.conf
server {
    listen 443 ssl http2;
    server_name lab-api.example.com;
    
    ssl_certificate /etc/ssl/certs/labctl.crt;
    ssl_certificate_key /etc/ssl/private/labctl.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts for long-running operations
        proxy_read_timeout 300s;
        proxy_connect_timeout 10s;
    }
}
```

## Monitoring Configuration

### Prometheus Metrics (Future Feature)

```yaml
# In lab_manager_config.yaml
monitoring:
  prometheus:
    enabled: true
    port: 9090
    path: "/metrics"
    
  # Custom metrics
  metrics:
    - lab_deployments_total
    - lab_deployment_duration_seconds
    - active_labs_gauge
    - api_request_duration_seconds
```

### Logging Configuration

```yaml
logging:
  # Console logging
  console:
    enabled: true
    level: "INFO"
    
  # File logging
  file:
    enabled: true
    path: "/var/log/homelab-manager/backend.log"
    level: "DEBUG"
    rotation:
      max_size: "100MB"
      backup_count: 5
      
  # Syslog forwarding
  syslog:
    enabled: false
    host: "syslog.example.com"
    port: 514
    facility: "local0"
```

## Performance Tuning

### Backend Performance

```yaml
# In lab_manager_config.yaml
performance:
  # Worker settings
  workers:
    processes: 4  # For production with gunicorn
    threads: 2
    
  # Connection pooling
  database:
    pool_size: 10
    max_overflow: 20
    
  # Caching
  cache:
    enabled: true
    backend: "redis"  # Future feature
    ttl: 300
```

### Git Operations

```yaml
labs:
  git:
    # Concurrent operations
    max_concurrent_clones: 3
    max_concurrent_pulls: 5
    
    # Timeouts
    clone_timeout: 600  # seconds
    fetch_timeout: 120
    
    # Performance
    shallow_clone: false
    single_branch: true
```

## Troubleshooting Configuration

### Debug Mode

Enable detailed debugging:

```bash
# Via environment
export LABCTL_LOG_LEVEL="DEBUG"
export FLASK_ENV="development"

# Via config file
logging:
  level: "DEBUG"
  
server:
  debug: true
```

### Configuration Validation

Test configuration without starting services:

```bash
# Validate backend config
python -m src.backend.app --validate-config

# Test NetBox connection
python -m src.backend.integrations.netbox --test

# Check lab repository
labctl repo validate <lab-id>
```

## Best Practices

1. **Use Configuration Files** for static settings
2. **Use Environment Variables** for secrets and deployment-specific values
3. **Never commit secrets** to version control
4. **Validate configuration** before deploying
5. **Use separate configs** for development and production
6. **Monitor configuration changes** in production
7. **Document custom settings** in your deployment notes

## Configuration Examples

### Development Setup

```yaml
# dev-config.yaml
server:
  debug: true
  
logging:
  level: "DEBUG"
  
labs:
  cleanup_on_failure: false  # Keep failed deployments for debugging
```

### Production Setup

```yaml
# prod-config.yaml
server:
  debug: false
  
security:
  api_key_required: true
  allowed_origins: ["https://lab-ui.example.com"]
  
performance:
  workers:
    processes: 4
    
monitoring:
  prometheus:
    enabled: true
```

### Minimal Setup

```yaml
# minimal-config.yaml
# Uses all defaults except API URL
api:
  url: "http://lab-server:5000"
```