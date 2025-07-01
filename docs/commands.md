# labctl Command Reference

This document provides a comprehensive reference for all `labctl` CLI commands. The CLI is designed as a lightweight client that communicates with the Flask backend API.

## Global Options

All commands support these global options:

- `--api-url`, `-a`: Backend API URL (default: `http://localhost:5000`)
  - Can also be set via the `LABCTL_API_URL` environment variable
- `--help`: Show help for any command or subcommand

## Command Structure

```
labctl [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS] [ARGUMENTS]
```

## Repository Management Commands

### `labctl repo`

Manage lab repositories. All repository operations work with Git-based lab repositories.

#### `labctl repo add <REPO_URL>`

Clone and register a new lab repository.

**Arguments:**
- `REPO_URL`: Git repository URL (SSH or HTTPS)

**Options:**
- `--name`, `-n`: Custom repository name (defaults to Git repository name)

**Examples:**
```bash
# Add a lab repository
labctl repo add git@github.com:user/bgp-lab.git

# Add with custom name
labctl repo add https://github.com/user/ospf-lab.git --name my-ospf-lab
```

**Expected Output:**
```
✓ Successfully added lab: BGP Advanced Features Lab
```

#### `labctl repo list`

List all registered lab repositories.

**Options:**
- `--json`: Output as JSON instead of formatted table

**Examples:**
```bash
# Table format (default)
labctl repo list

# JSON format
labctl repo list --json
```

**Expected Output (Table):**
```
                    Registered Labs                    
┌─────────────┬──────────────────────┬─────────┬──────────┬─────────┬──────────────┐
│ ID          │ Name                 │ Version │ Category │ Vendor  │ Difficulty   │
├─────────────┼──────────────────────┼─────────┼──────────┼─────────┼──────────────┤
│ bgp-lab     │ BGP Advanced Lab     │ v1.2.0  │ Routing  │ Juniper │ Intermediate │
│ ospf-basics │ OSPF Fundamentals    │ v1.0.0  │ Routing  │ Cisco   │ Beginner     │
└─────────────┴──────────────────────┴─────────┴──────────┴─────────┴──────────────┘
```

#### `labctl repo update <LAB_ID>`

Update a lab repository by pulling the latest changes from Git.

**Arguments:**
- `LAB_ID`: Lab identifier from `repo list`

**Examples:**
```bash
labctl repo update bgp-lab
```

**Expected Output:**
```
✓ Successfully updated bgp-lab to latest version
```

#### `labctl repo remove <LAB_ID>`

Remove a lab repository from the system.

**Arguments:**
- `LAB_ID`: Lab identifier from `repo list`

**Options:**
- Requires confirmation prompt

**Examples:**
```bash
labctl repo remove old-lab
# Prompts: Are you sure you want to remove this lab? [y/N]:
```

**Expected Output:**
```
✓ Successfully removed lab: old-lab
```

## Lab Deployment Commands

### `labctl deploy <LAB_ID>`

Deploy a lab environment using containerlab.

**Arguments:**
- `LAB_ID`: Lab identifier from `repo list`

**Options:**
- `--version`, `-v`: Specific version/tag to deploy (default: `latest`)
- `--allocate-ips`: Allocate IPs dynamically from NetBox

**Examples:**
```bash
# Deploy latest version
labctl deploy bgp-lab

# Deploy specific version
labctl deploy bgp-lab --version v1.2.0

# Deploy with dynamic IP allocation
labctl deploy bgp-lab --allocate-ips
```

**Expected Output:**
```
Starting deployment of bgp-lab...
⠋ Deploying lab...
✓ Lab bgp-lab deployed successfully
Deployment ID: bgp-lab-20241201-143022
```

### `labctl destroy <LAB_ID>`

Destroy a deployed lab environment.

**Arguments:**
- `LAB_ID`: Lab identifier of deployed lab

**Options:**
- Requires confirmation prompt

**Examples:**
```bash
labctl destroy bgp-lab
# Prompts: Are you sure you want to destroy this lab? [y/N]:
```

**Expected Output:**
```
⠋ Destroying bgp-lab...
✓ Lab bgp-lab destroyed successfully
```

### `labctl status`

Show status of all active lab deployments.

**Options:**
- `--json`: Output as JSON instead of formatted table

**Examples:**
```bash
# Table format (default)
labctl status

# JSON format
labctl status --json
```

**Expected Output:**
```
                           Active Deployments                           
┌──────────────────────────┬─────────────┬──────────────────────┬─────────┬─────────────────────┐
│ Deployment ID            │ Lab ID      │ Lab Name             │ Version │ Deployed At         │
├──────────────────────────┼─────────────┼──────────────────────┼─────────┼─────────────────────┤
│ bgp-lab-20241201-143022  │ bgp-lab     │ BGP Advanced Lab     │ v1.2.0  │ 2024-12-01 14:30:22 │
│ ospf-lab-20241201-150815 │ ospf-basics │ OSPF Fundamentals    │ latest  │ 2024-12-01 15:08:15 │
└──────────────────────────┴─────────────┴──────────────────────┴─────────┴─────────────────────┘

Total active deployments: 2
```

### `labctl logs <LAB_ID>`

Show deployment logs for a specific lab.

**Arguments:**
- `LAB_ID`: Lab identifier of deployed lab

**Examples:**
```bash
labctl logs bgp-lab
```

**Expected Output:**
```
Deployment logs for bgp-lab (ID: bgp-lab-20241201-143022)
============================================================
[2024-12-01 14:30:22] Starting deployment of bgp-lab...
[2024-12-01 14:30:23] Checking out version v1.2.0
[2024-12-01 14:30:24] Executing bootstrap.sh
[2024-12-01 14:30:45] Containerlab topology created
[2024-12-01 14:31:02] All containers started successfully
[2024-12-01 14:31:03] Deployment completed successfully
```

## Device Configuration Commands

### `labctl config`

Manage device configuration scenarios for deployed labs.

#### `labctl config list <LAB_ID>`

List available device configuration scenarios for a lab.

**Arguments:**
- `LAB_ID`: Lab identifier

**Options:**
- `--json`: Output as JSON instead of formatted table

**Examples:**
```bash
# Table format (default)
labctl config list bgp-lab

# JSON format
labctl config list bgp-lab --json
```

**Expected Output:**
```
     Device Configuration Scenarios for bgp-lab     
┌────────────┬──────────────────────────────────────┐
│ Scenario   │ Description                          │
├────────────┼──────────────────────────────────────┤
│ baseline   │ Device configuration scenario        │
│ scenario-1 │ Device configuration scenario        │
│ mpls-vpn   │ Device configuration scenario        │
└────────────┴──────────────────────────────────────┘
```

#### `labctl config apply <LAB_ID> <SCENARIO>`

Apply a device configuration scenario to a deployed lab.

**Arguments:**
- `LAB_ID`: Lab identifier of deployed lab
- `SCENARIO`: Scenario name from `config list`

**Examples:**
```bash
# Apply baseline configuration
labctl config apply bgp-lab baseline

# Apply specific scenario
labctl config apply bgp-lab mpls-vpn
```

**Expected Output:**
```
Applying device configuration scenario 'mpls-vpn' to bgp-lab...
✓ Configuration scenario applied successfully
Note: Allow 30-60 seconds for configuration to take effect
```

## System Commands

### `labctl doctor`

Check system health and display backend configuration.

**Options:**
- `--json`: Output as JSON instead of formatted display

**Examples:**
```bash
# Formatted display (default)
labctl doctor

# JSON format
labctl doctor --json
```

**Expected Output:**
```
✓ Backend is healthy

Backend Configuration
========================================
Repositories directory: /opt/labctl/repos
Logs directory: /opt/labctl/logs
State file: /opt/labctl/state.json
Git command: git
Clab-tools command: clab-tools

NetBox integration: Enabled
NetBox URL: https://netbox.example.com
Default prefix: 10.100.100.0/24

Monitoring endpoints:
Prometheus: http://localhost:9090
Grafana: http://localhost:3000
```

### `labctl version`

Show version information and backend connectivity status.

**Examples:**
```bash
labctl version
```

**Expected Output:**
```
labctl - Homelab Manager CLI
Version: 1.0.0-dev
Backend API: Connected
Backend Status: Healthy
```

## Exit Codes

- `0`: Success
- `1`: General error (failed operation, backend unhealthy, etc.)

## Environment Variables

- `LABCTL_API_URL`: Override default backend API URL
  - Default: `http://localhost:5000`
  - Example: `export LABCTL_API_URL=http://lab-server:5000`

## Configuration Files

The CLI itself does not use configuration files. All configuration is managed by the backend API. Use `labctl doctor` to view current backend configuration.

## Common Workflows

### Adding and Deploying a New Lab
```bash
# 1. Add the lab repository
labctl repo add git@github.com:user/new-lab.git

# 2. List available labs to get the lab ID
labctl repo list

# 3. Deploy the lab
labctl deploy new-lab

# 4. Check deployment status
labctl status

# 5. View deployment logs if needed
labctl logs new-lab
```

### Working with Configuration Scenarios
```bash
# 1. Deploy a lab first
labctl deploy bgp-lab

# 2. List available scenarios
labctl config list bgp-lab

# 3. Apply a configuration scenario
labctl config apply bgp-lab scenario-1

# 4. Apply different scenarios as needed
labctl config apply bgp-lab baseline
```

### Lab Lifecycle Management
```bash
# Deploy specific version
labctl deploy bgp-lab --version v1.2.0

# Check what's running
labctl status

# View logs for troubleshooting
labctl logs bgp-lab

# Clean up when done
labctl destroy bgp-lab
```

### System Maintenance
```bash
# Check system health
labctl doctor

# Update lab repositories
labctl repo update bgp-lab

# Remove unused labs
labctl repo remove old-lab
```

## Error Handling

- Commands exit with code 1 on failure
- Error messages are displayed in red text
- Success messages are displayed in green text
- Progress indicators show operation status
- Confirmation prompts prevent accidental destructive operations

## JSON Output

Many commands support `--json` flag for programmatic use:

```bash
# Get all repos as JSON
labctl repo list --json

# Get deployment status as JSON  
labctl status --json

# Get system info as JSON
labctl doctor --json
```

This enables integration with other tools and scripting automation.