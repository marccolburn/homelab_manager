# REST API Documentation

The Homelab Manager provides a comprehensive REST API for managing lab repositories and deployments. This API serves as the backend for both the CLI client (`labctl`) and the web interface.

## Base URL

The API is served by the Flask backend application:

```
http://localhost:5000
```

For production deployments, this would typically be behind a reverse proxy like nginx.

## Authentication

Currently, the API does not implement authentication. This is suitable for local development and lab environments. For production use, consider implementing authentication middleware.

## Response Format

All API responses are in JSON format. Standard HTTP status codes are used to indicate success or failure.

### Success Response Format
```json
{
    "success": true,
    "message": "Operation completed successfully",
    "data": { ... }
}
```

### Error Response Format
```json
{
    "success": false,
    "error": "Error description",
    "details": { ... }
}
```

## API Endpoints

### Health and Configuration

#### GET /api/health

Check API health status.

**Response:**
```json
{
    "status": "healthy",
    "service": "labctl-backend"
}
```

**Example:**
```bash
curl http://localhost:5000/api/health
```

#### GET /api/config

Get current backend configuration (sensitive data masked).

**Response:**
```json
{
    "repos_dir": "/opt/labctl/repos",
    "logs_dir": "/opt/labctl/logs", 
    "state_file": "/opt/labctl/state.json",
    "git_cmd": "git",
    "clab_tools_cmd": "clab-tools",
    "netbox": {
        "enabled": true,
        "url": "https://netbox.example.com",
        "token": "***",
        "default_prefix": "10.100.100.0/24"
    }
}
```

**Example:**
```bash
curl http://localhost:5000/api/config
```

---

### Repository Management

#### GET /api/repos

List all registered lab repositories.

**Response:**
```json
[
    {
        "id": "bgp-advanced",
        "name": "BGP Advanced Features Lab",
        "version": "1.2.0",
        "category": "Routing",
        "vendor": "Juniper",
        "difficulty": "Intermediate",
        "url": "git@github.com:user/bgp-advanced-lab.git",
        "path": "/opt/labctl/repos/bgp-advanced"
    }
]
```

**Example:**
```bash
curl http://localhost:5000/api/repos
```

#### POST /api/repos

Add a new lab repository.

**Request Body:**
```json
{
    "url": "git@github.com:user/lab-repo.git",
    "name": "Custom Lab Name (optional)"
}
```

**Response (201 Created):**
```json
{
    "success": true,
    "lab_id": "lab-repo", 
    "message": "Lab repository added successfully",
    "metadata": {
        "name": "BGP Advanced Features Lab",
        "version": "1.0.0",
        "category": "Routing"
    }
}
```

**Error Response (400 Bad Request):**
```json
{
    "success": false,
    "error": "Repository URL required"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/repos \
  -H "Content-Type: application/json" \
  -d '{"url": "git@github.com:user/my-lab.git"}'
```

#### PUT /api/repos/{lab_id}

Update a lab repository (git pull).

**Path Parameters:**
- `lab_id`: Laboratory identifier

**Response:**
```json
{
    "success": true,
    "message": "Repository updated successfully"
}
```

**Example:**
```bash
curl -X PUT http://localhost:5000/api/repos/bgp-advanced
```

#### DELETE /api/repos/{lab_id}

Remove a lab repository.

**Path Parameters:**
- `lab_id`: Laboratory identifier

**Response:**
```json
{
    "success": true,
    "message": "Repository removed successfully"
}
```

**Example:**
```bash
curl -X DELETE http://localhost:5000/api/repos/old-lab
```

---

### Lab Deployment

#### POST /api/labs/{lab_id}/deploy

Deploy a lab environment (asynchronous operation).

**Path Parameters:**
- `lab_id`: Laboratory identifier

**Request Body (optional):**
```json
{
    "version": "v1.2.0",
    "allocate_ips": false
}
```

**Response (202 Accepted):**
```json
{
    "task_id": "deploy_bgp-advanced_20241201_143022",
    "message": "Deployment of bgp-advanced started"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/labs/bgp-advanced/deploy \
  -H "Content-Type: application/json" \
  -d '{"version": "v1.2.0", "allocate_ips": true}'
```

#### POST /api/labs/{lab_id}/destroy

Destroy a deployed lab environment.

**Path Parameters:**
- `lab_id`: Laboratory identifier

**Response:**
```json
{
    "success": true,
    "message": "Lab destroyed successfully"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/labs/bgp-advanced/destroy
```

#### GET /api/deployments

Get status of all active deployments.

**Response:**
```json
{
    "total": 2,
    "deployments": [
        {
            "deployment_id": "bgp-advanced_20241201_143022",
            "lab_id": "bgp-advanced",
            "lab_name": "BGP Advanced Features Lab",
            "version": "v1.2.0",
            "deployed_at": "2024-12-01T14:30:22",
            "status": "running"
        }
    ]
}
```

**Example:**
```bash
curl http://localhost:5000/api/deployments
```

---

### Configuration Management

#### GET /api/labs/{lab_id}/scenarios

List available configuration scenarios for a lab.

**Path Parameters:**
- `lab_id`: Laboratory identifier

**Response:**
```json
{
    "lab_id": "bgp-advanced",
    "scenarios": [
        "baseline",
        "scenario-1", 
        "mpls-vpn",
        "route-reflection"
    ]
}
```

**Example:**
```bash
curl http://localhost:5000/api/labs/bgp-advanced/scenarios
```

#### POST /api/labs/{lab_id}/scenarios/{scenario}

Apply a configuration scenario to a deployed lab.

**Path Parameters:**
- `lab_id`: Laboratory identifier
- `scenario`: Scenario name

**Response:**
```json
{
    "success": true,
    "message": "Configuration scenario applied successfully",
    "note": "Allow 30-60 seconds for configuration to take effect"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/labs/bgp-advanced/scenarios/mpls-vpn
```

---

### Logging

#### GET /api/logs/{lab_id}

Get deployment logs for a lab.

**Path Parameters:**
- `lab_id`: Laboratory identifier

**Response:**
```json
{
    "deployment_id": "bgp-advanced_20241201_143022",
    "log": "[2024-12-01 14:30:22] Starting deployment...\n[2024-12-01 14:30:45] Containerlab topology created\n..."
}
```

**Error Response (404 Not Found):**
```json
{
    "error": "No logs found"
}
```

**Example:**
```bash
curl http://localhost:5000/api/logs/bgp-advanced
```

---

### Async Task Management

#### GET /api/tasks/{task_id}

Get status of an asynchronous task (primarily for deployment tracking).

**Path Parameters:**
- `task_id`: Task identifier returned from deployment

**Response (In Progress):**
```json
{
    "task_id": "deploy_bgp-advanced_20241201_143022",
    "status": "running",
    "message": "Deploying lab environment...",
    "started_at": "2024-12-01T14:30:22"
}
```

**Response (Completed):**
```json
{
    "task_id": "deploy_bgp-advanced_20241201_143022", 
    "status": "completed",
    "result": {
        "success": true,
        "message": "Lab deployed successfully",
        "deployment_id": "bgp-advanced_20241201_143022"
    },
    "started_at": "2024-12-01T14:30:22",
    "completed_at": "2024-12-01T14:31:45"
}
```

**Response (Failed):**
```json
{
    "task_id": "deploy_bgp-advanced_20241201_143022",
    "status": "failed", 
    "result": {
        "success": false,
        "error": "Bootstrap script failed: clab-tools not found"
    },
    "started_at": "2024-12-01T14:30:22",
    "completed_at": "2024-12-01T14:30:35"
}
```

**Error Response (404 Not Found):**
```json
{
    "error": "Task not found"
}
```

**Example:**
```bash
curl http://localhost:5000/api/tasks/deploy_bgp-advanced_20241201_143022
```

## HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 202 | Accepted - Async operation started |
| 400 | Bad Request - Invalid request data |
| 404 | Not Found - Resource not found |
| 500 | Internal Server Error - Server error |

## Error Handling

The API uses consistent error response format with descriptive messages:

### Validation Errors (400)
```json
{
    "error": "Repository URL required"
}
```

### Not Found Errors (404)
```json
{
    "error": "Lab not found: invalid-lab-id"
}
```

### Operational Errors (400)
```json
{
    "success": false,
    "error": "Lab is not currently deployed"
}
```

## Complete Workflow Examples

### Adding and Deploying a Lab

1. **Add Repository**
```bash
curl -X POST http://localhost:5000/api/repos \
  -H "Content-Type: application/json" \
  -d '{"url": "git@github.com:user/bgp-lab.git"}'
```

2. **List Available Labs**
```bash
curl http://localhost:5000/api/repos
```

3. **Deploy Lab**
```bash
curl -X POST http://localhost:5000/api/labs/bgp-lab/deploy \
  -H "Content-Type: application/json" \
  -d '{"version": "v1.0.0"}'
```

4. **Monitor Deployment**
```bash
# Get task_id from deploy response, then poll status
curl http://localhost:5000/api/tasks/deploy_bgp-lab_20241201_143022
```

5. **Check Active Deployments**
```bash
curl http://localhost:5000/api/deployments
```

### Configuration Management

1. **List Scenarios**
```bash
curl http://localhost:5000/api/labs/bgp-lab/scenarios
```

2. **Apply Configuration**
```bash
curl -X POST http://localhost:5000/api/labs/bgp-lab/scenarios/baseline
```

3. **View Logs**
```bash
curl http://localhost:5000/api/logs/bgp-lab
```

### Cleanup

1. **Destroy Lab**
```bash
curl -X POST http://localhost:5000/api/labs/bgp-lab/destroy
```

2. **Remove Repository**
```bash
curl -X DELETE http://localhost:5000/api/repos/bgp-lab
```

## Client Libraries

### Python (requests)
```python
import requests

# Add repository
response = requests.post('http://localhost:5000/api/repos', 
                        json={'url': 'git@github.com:user/lab.git'})
print(response.json())

# Deploy lab
response = requests.post('http://localhost:5000/api/labs/lab/deploy',
                        json={'version': 'latest'})
task_id = response.json()['task_id']

# Monitor deployment
import time
while True:
    response = requests.get(f'http://localhost:5000/api/tasks/{task_id}')
    status = response.json()
    
    if status['status'] in ['completed', 'failed']:
        break
    time.sleep(2)

print("Deployment result:", status['result'])
```

### JavaScript (fetch)
```javascript
// Add repository
const addRepo = async (url) => {
    const response = await fetch('http://localhost:5000/api/repos', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({url})
    });
    return await response.json();
};

// Deploy lab
const deployLab = async (labId, version = 'latest') => {
    const response = await fetch(`http://localhost:5000/api/labs/${labId}/deploy`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({version})
    });
    return await response.json();
};

// Monitor deployment
const monitorDeployment = async (taskId) => {
    while (true) {
        const response = await fetch(`http://localhost:5000/api/tasks/${taskId}`);
        const status = await response.json();
        
        if (status.status === 'completed' || status.status === 'failed') {
            return status;
        }
        
        await new Promise(resolve => setTimeout(resolve, 2000));
    }
};
```

### Shell (curl)
```bash
#!/bin/bash

# Function to deploy and monitor lab
deploy_lab() {
    local lab_id=$1
    local version=${2:-latest}
    
    echo "Deploying $lab_id..."
    
    # Start deployment
    response=$(curl -s -X POST "http://localhost:5000/api/labs/$lab_id/deploy" \
        -H "Content-Type: application/json" \
        -d "{\"version\": \"$version\"}")
    
    task_id=$(echo "$response" | jq -r '.task_id')
    
    # Monitor progress
    while true; do
        status=$(curl -s "http://localhost:5000/api/tasks/$task_id")
        current_status=$(echo "$status" | jq -r '.status')
        
        if [ "$current_status" = "completed" ] || [ "$current_status" = "failed" ]; then
            echo "Deployment $current_status"
            echo "$status" | jq '.result'
            break
        fi
        
        echo "Status: $current_status"
        sleep 2
    done
}

# Usage
deploy_lab "bgp-advanced" "v1.2.0"
```

## Rate Limiting

Currently, no rate limiting is implemented. For production deployments, consider implementing rate limiting middleware to prevent abuse.

## Monitoring and Observability

The API can be monitored using standard HTTP monitoring tools:

- **Health Checks**: Use `/api/health` endpoint
- **Metrics**: Integrate with Prometheus for metrics collection
- **Logging**: All operations are logged to the application logs
- **Tracing**: Consider adding OpenTelemetry for distributed tracing

## Development and Testing

### Running the API Server
```bash
# Development mode
FLASK_ENV=development python -m src.backend.app

# Production mode
gunicorn -w 4 -b 0.0.0.0:5000 src.backend.app:app
```

### API Testing
```bash
# Using the test suite
python -m pytest tests/integration/test_api_endpoints.py

# Manual testing with curl
bash docs/api_test_script.sh
```

### OpenAPI/Swagger Documentation

Future enhancement: Generate OpenAPI specification for automatic documentation and client generation.