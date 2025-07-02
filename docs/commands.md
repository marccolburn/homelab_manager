# labctl Command Reference

Quick reference for all `labctl` CLI commands. The CLI communicates with the Flask backend API.

## Global Options

- `--api-url`, `-a`: Backend API URL (default: `http://localhost:5001`)
  - Environment variable: `LABCTL_API_URL`
- `--help`: Show help for any command

## Command Structure

```
labctl [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS] [ARGUMENTS]
```

## Repository Management

### `labctl repo add <REPO_URL>`
Clone and register a lab repository.

```bash
labctl repo add git@github.com:user/bgp-lab.git
```

### `labctl repo list`
List all registered labs.

```bash
labctl repo list [--json]
```

### `labctl repo update <LAB_ID>`
Pull latest changes from Git.

```bash
labctl repo update bgp-lab
```

### `labctl repo remove <LAB_ID>`
Remove a lab repository (requires confirmation).

```bash
labctl repo remove old-lab
```

## Lab Deployment

### `labctl deploy <LAB_ID>`
Deploy a lab using containerlab.

```bash
labctl deploy bgp-lab [--version v1.0.0] [--allocate-ips]
```

### `labctl destroy <LAB_ID>`
Destroy a deployed lab (requires confirmation).

```bash
labctl destroy bgp-lab
```

### `labctl status`
Show all active deployments.

```bash
labctl status [--json]
```

### `labctl logs <LAB_ID>`
Show deployment logs.

```bash
labctl logs bgp-lab
```

## Device Configuration

### `labctl config list <LAB_ID>`
List available configuration scenarios.

```bash
labctl config list bgp-lab [--json]
```

### `labctl config apply <LAB_ID> <SCENARIO>`
Apply a configuration scenario to a deployed lab.

```bash
labctl config apply bgp-lab mpls-vpn
```

## System Commands

### `labctl doctor`
Check system health and show configuration.

```bash
labctl doctor [--json]
```

### `labctl version`
Show version and backend status.

```bash
labctl version
```

### `labctl netbox`
Validate NetBox configuration and connectivity.

```bash
labctl netbox
```

## Common Workflows

### Deploy a Lab
```bash
labctl repo add git@github.com:user/bgp-lab.git
labctl repo list
labctl deploy bgp-lab
labctl status
```

### Apply Configuration
```bash
labctl config list bgp-lab
labctl config apply bgp-lab scenario-1
```

### Cleanup
```bash
labctl destroy bgp-lab
labctl repo remove bgp-lab
```

## Environment Variables

- `LABCTL_API_URL`: Backend API URL (default: `http://localhost:5001`)

## Exit Codes

- `0`: Success
- `1`: Error