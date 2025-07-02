# REST API Documentation

Flask backend API for Homelab Manager operations.

## Base URL

- **Development**: `http://localhost:5001`
- **Production**: `http://your-server:5001`

## Common Response Format

### Success
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed"
}
```

### Error
```json
{
  "success": false,
  "error": "Error description",
  "details": { ... }
}
```

## Repository Management

### `GET /api/repos`
List all registered lab repositories.

**Response:**
```json
{
  "repositories": [
    {
      "id": "bgp-lab",
      "name": "BGP Advanced Lab",
      "description": "BGP communities and policies",
      "category": "Routing",
      "vendor": "Juniper",
      "difficulty": "Intermediate",
      "version": "1.0.0",
      "tags": ["v1.0.0", "v1.1.0"],
      "requirements": {
        "memory_gb": 32,
        "cpu_cores": 16
      }
    }
  ]
}
```

### `POST /api/repos`
Add a new lab repository.

**Request:**
```json
{
  "url": "git@github.com:user/lab.git"
}
```

### `PUT /api/repos/{lab_id}`
Update repository (pull latest changes).

### `DELETE /api/repos/{lab_id}`
Remove lab repository.

## Lab Deployment

### `GET /api/labs`
List active deployments.

**Response:**
```json
{
  "deployments": [
    {
      "lab_id": "bgp-lab",
      "deployment_id": "bgp-lab_20250702_143022",
      "status": "running",
      "version": "v1.0.0",
      "deployed_at": "2025-07-02T14:30:22Z",
      "allocated_ips": ["10.100.100.1", "10.100.100.2"]
    }
  ]
}
```

### `POST /api/labs/{lab_id}/deploy`
Deploy a lab.

**Request:**
```json
{
  "version": "v1.0.0",
  "allocate_ips": true
}
```

**Response:**
```json
{
  "success": true,
  "task_id": "deploy_12345",
  "deployment_id": "bgp-lab_20250702_143022"
}
```

### `POST /api/labs/{lab_id}/destroy`
Destroy lab deployment.

### `GET /api/labs/{lab_id}/status`
Get lab status and node information.

### `GET /api/labs/{lab_id}/logs`
Get deployment logs (returns plain text).

## Configuration Scenarios

### `GET /api/labs/{lab_id}/scenarios`
List available configuration scenarios.

### `POST /api/labs/{lab_id}/scenarios/{scenario_name}`
Apply configuration scenario.

## Task Management

### `GET /api/tasks/{task_id}`
Check async operation status.

**Response:**
```json
{
  "task_id": "deploy_12345",
  "status": "completed",
  "progress": 100,
  "started_at": "2025-07-02T14:30:22Z",
  "result": {
    "success": true,
    "message": "Lab deployed successfully"
  }
}
```

**Status values**: `pending`, `running`, `completed`, `failed`

## Settings Management

### `GET /api/config/settings`
Get configuration (passwords masked).

### `POST /api/config/settings`
Update configuration settings.

**Request:**
```json
{
  "clab_tools_password": "password",
  "remote_credentials": {
    "ssh_password": "ssh-pass",
    "sudo_password": "sudo-pass"
  },
  "netbox": {
    "enabled": true,
    "url": "http://netbox.example.com",
    "token": "api-token"
  }
}
```

## Health and Status

### `GET /api/health`
System health check.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": "2 hours",
  "components": {
    "git": "healthy",
    "clab_tools": "healthy"
  },
  "stats": {
    "total_repos": 5,
    "active_deployments": 2
  }
}
```

### `GET /api/config`
System configuration.

## NetBox Integration

### `GET /api/netbox/validate`
Test NetBox connectivity.

**Response:**
```json
{
  "valid": true,
  "message": "NetBox connection successful",
  "details": {
    "url": "http://netbox.example.com",
    "version": "3.5.0",
    "available_prefixes": ["10.100.100.0/24"]
  }
}
```

## Web UI Routes

### Static Files
- `GET /` → Main dashboard (`index.html`)
- `GET /settings.html` → Settings page
- `GET /static/*` → CSS, JS, images

## HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `404` - Not Found
- `409` - Conflict
- `500` - Internal Server Error

## Client Examples

### JavaScript
```javascript
// Deploy lab
const response = await fetch('/api/labs/bgp-lab/deploy', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ version: 'v1.0.0' })
});
const result = await response.json();
```

### Python
```python
import requests

# Get repositories
response = requests.get('http://localhost:5001/api/repos')
repos = response.json()['repositories']

# Deploy lab
response = requests.post(
  'http://localhost:5001/api/labs/bgp-lab/deploy',
  json={'version': 'latest'}
)
```

### curl
```bash
# Health check
curl http://localhost:5001/api/health

# Deploy lab
curl -X POST http://localhost:5001/api/labs/bgp-lab/deploy \
  -H "Content-Type: application/json" \
  -d '{"version": "v1.0.0"}'
```

## Error Codes

Common application error codes:
- `REPO_NOT_FOUND` - Repository doesn't exist
- `LAB_ALREADY_DEPLOYED` - Lab is already running  
- `LAB_NOT_DEPLOYED` - Lab is not currently deployed
- `INVALID_VERSION` - Requested version doesn't exist
- `NETBOX_ERROR` - NetBox operation failed
- `DEPLOYMENT_FAILED` - Lab deployment failed