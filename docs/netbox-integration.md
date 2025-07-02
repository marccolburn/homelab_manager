# NetBox Integration Guide

NetBox integration for dynamic IP allocation and device management in Homelab Manager.

## Overview

NetBox integration provides:
- Dynamic IP allocation from NetBox IPAM during lab deployment
- Automatic IP release when labs are destroyed
- Device registration in NetBox for deployed lab nodes
- IP assignment tracking in deployment state
- Configuration validation tools

## Prerequisites

1. **NetBox Instance**: Running NetBox instance (v3.0+)
2. **API Token**: Generated from your NetBox user profile
3. **IP Prefix**: Configured prefix in NetBox for lab allocations
4. **Python Package**: `pynetbox` (installed automatically)

## Configuration

### Backend Configuration

Configure NetBox in `~/.labctl/config.yaml`:

```yaml
netbox:
  enabled: true
  url: "http://10.1.80.12:8080"
  token: "your-api-token-here"
  default_prefix: "10.100.100.0/24"
  default_site: "Lab Environment"
  default_role: "Lab Device"
  cleanup_on_destroy: true
```

### Web UI Configuration

1. Navigate to `http://localhost:5001/settings.html`
2. Scroll to "NetBox Integration" section
3. Configure:
   - Enable NetBox integration
   - NetBox URL
   - API Token
   - Default settings
4. Click "Save Settings"
5. Click "Test Connection" to verify

### Configuration Options

| Option | Description | Required | Default |
|--------|-------------|----------|---------|
| `enabled` | Enable/disable NetBox integration | Yes | `false` |
| `url` | NetBox instance URL (without /api/) | Yes | - |
| `token` | NetBox API token | Yes | - |
| `default_prefix` | IP prefix for allocations | Yes | - |
| `default_site` | Site name for devices | No | "Lab Environment" |
| `default_role` | Device role name | No | "Lab Device" |
| `cleanup_on_destroy` | Release IPs on destroy | No | `true` |

## Usage

### Deploy with Dynamic IPs

```bash
# Deploy lab with NetBox IP allocation
labctl deploy bgp-lab --allocate-ips

# Deploy specific version with IPs
labctl deploy bgp-lab --version v1.2.0 --allocate-ips
```

### Web UI Deployment

1. Go to lab dashboard
2. Select lab to deploy
3. Check "Allocate IPs from NetBox"
4. Click "Deploy"

### What Happens During Deployment

1. **IP Allocation**:
   - Reads nodes from `nodes.csv`
   - Requests available IPs from NetBox prefix
   - Updates `nodes.csv` with allocated IPs
   - Tracks allocations in deployment state

2. **Device Registration**:
   - Creates devices in NetBox
   - Associates allocated IPs as primary addresses
   - Tags devices with `lab-{lab-id}`
   - Sets device role and site

3. **Rollback on Failure**:
   - If deployment fails after allocation
   - Automatically releases allocated IPs
   - Removes created devices
   - Prevents resource orphaning

### Destroy and Cleanup

```bash
# Destroy lab - automatically releases IPs
labctl destroy bgp-lab
```

During destruction:
- Releases all allocated IPs back to pool
- Removes devices from NetBox
- Cleans up tags and associations

### Validate Configuration

```bash
# Check NetBox connectivity and config
labctl netbox

# Expected output:
✓ NetBox configuration is valid
Connected to NetBox at http://10.1.80.12:8080
API Version: 3.5.0
Available prefixes:
  - 10.100.100.0/24 (Lab Management)
```

## Lab Repository Requirements

### Lab Metadata Configuration

In `lab-metadata.yaml`:

```yaml
netbox:
  enabled: true
  prefix: "10.100.100.0/24"  # Override default prefix
  site: "Lab Environment"     # Override default site
  role: "Lab Device"          # Override default role
```

### nodes.csv Format

Your `nodes.csv` must have proper columns:

```csv
hostname,platform,type,mgmt_ip
r1,juniper,router,
r2,juniper,router,
sw1,arista,switch,
```

After allocation:

```csv
hostname,platform,type,mgmt_ip
r1,juniper,router,10.100.100.5
r2,juniper,router,10.100.100.6
sw1,arista,switch,10.100.100.7
```

## API Endpoints

### Deploy with IP Allocation

```bash
curl -X POST http://localhost:5001/api/labs/bgp-lab/deploy \
  -H "Content-Type: application/json" \
  -d '{"version": "latest", "allocate_ips": true}'
```

### Validate NetBox Configuration

```bash
curl http://localhost:5001/api/netbox/validate
```

Response:
```json
{
  "valid": true,
  "message": "NetBox connection successful",
  "details": {
    "url": "http://10.1.80.12:8080",
    "version": "3.5.0",
    "available_prefixes": ["10.100.100.0/24"],
    "api_permissions": ["view", "add", "change", "delete"]
  }
}
```

## Troubleshooting

### Common Issues

1. **"Prefix not found in NetBox"**
   - Ensure prefix exists and is active in NetBox
   - Check prefix notation matches exactly
   - Verify API token has IPAM permissions

2. **"Not enough IPs available"**
   - Check available IPs in NetBox prefix
   - Release stale IP assignments
   - Consider larger prefix or cleanup

3. **"Failed to connect to NetBox"**
   - Verify NetBox URL (no trailing slash)
   - Test API token permissions
   - Check network connectivity

### Debug Commands

```bash
# Test NetBox API directly
curl -H "Authorization: Token your-token" \
  http://10.1.80.12:8080/api/ipam/prefixes/

# Check backend logs
tail -f ~/.labctl/logs/backend.log

# Verify pynetbox installation
python -c "import pynetbox; print(pynetbox.__version__)"
```

### Manual Cleanup

If automatic cleanup fails:

1. **In NetBox UI**:
   - Filter IPs by tag `lab-{lab-id}`
   - Bulk delete tagged IPs
   - Filter devices by same tag
   - Bulk delete tagged devices

2. **Using labctl**:
   ```bash
   # Force cleanup for specific lab
   labctl destroy bgp-lab --force
   ```

## Implementation Details

### NetBox Client Module

Located in `src/backend/integrations/netbox.py`:

```python
class NetBoxClient:
    def allocate_ips(self, prefix: str, count: int) -> List[str]
    def register_devices(self, devices: List[Dict]) -> Dict
    def release_ips(self, ips: List[str]) -> Dict
    def cleanup_lab(self, lab_id: str) -> Dict
```

### State Tracking

Deployments track NetBox allocations:

```json
{
  "deployment_id": "bgp-lab_20250702_150000",
  "lab_id": "bgp-lab",
  "netbox_ips_allocated": true,
  "allocated_ips": [
    "10.100.100.5",
    "10.100.100.6", 
    "10.100.100.7"
  ]
}
```

## Best Practices

1. **Dedicated Prefix**: Use separate prefix for lab allocations
2. **Regular Cleanup**: Monitor for orphaned resources
3. **Consistent Tagging**: All resources tagged with `lab-{lab-id}`
4. **IP Planning**: Size prefixes appropriately for concurrent labs
5. **Access Control**: Use minimal API token permissions

## Security Considerations

1. **API Token Security**:
   - Store in backend configuration only
   - Never commit to version control
   - Use read/write permissions only for required objects
   - Rotate tokens periodically

2. **Network Isolation**:
   - Consider separate management network
   - Implement appropriate firewall rules

3. **Audit Trail**:
   - NetBox logs all API changes
   - Review logs for unexpected activity

## Integration Status

✅ **Implemented Features**:
- Dynamic IP allocation from prefixes
- Device registration with metadata
- Automatic cleanup on destroy
- Configuration validation
- Web UI settings management
- CLI validation command
- Error handling and rollback

🔄 **Future Enhancements**:
- VLAN assignment support
- Circuit tracking for connections
- Webhook integration for real-time updates
- Bulk lab deployments with IP planning
- Usage reporting and statistics

This integration provides enterprise-grade IP management for lab deployments while maintaining simplicity for users.