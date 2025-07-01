# NetBox Integration Guide

This guide covers the NetBox integration feature for dynamic IP allocation and device management in Homelab Manager.

## Overview

The NetBox integration provides:
- **Dynamic IP allocation** from NetBox IPAM during lab deployment
- **Automatic IP release** when labs are destroyed
- **Device registration** in NetBox for deployed lab nodes
- **IP assignment tracking** in deployment state
- **Validation tools** to verify NetBox connectivity

## Prerequisites

1. **NetBox Instance**: A running NetBox instance (v3.0+)
2. **API Token**: Generated from your NetBox user profile
3. **IP Prefix**: A configured prefix in NetBox for lab allocations
4. **Python Package**: `pynetbox` (installed automatically with backend)

## Configuration

### Backend Configuration

Update your `lab_manager_config.yaml` to enable NetBox:

```yaml
# NetBox integration settings
netbox:
  enabled: true
  url: "https://netbox.example.com"
  token: "your-api-token-here"
  default_prefix: "10.100.100.0/24"
  default_site: "Lab Environment"
  default_role: "Lab Device"
  cleanup_on_destroy: true
```

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

### NetBox Setup

1. **Create IP Prefix**:
   - Navigate to IPAM → Prefixes
   - Create a prefix (e.g., `10.100.100.0/24`)
   - Set status to "Active"
   - Optionally set role to "Lab Management"

2. **Generate API Token**:
   - Go to your user profile
   - Click "API Tokens"
   - Create a new token with read/write permissions

3. **Optional - Create Tags**:
   - Create tag `lab-managed` for easy filtering
   - Labs will auto-create `lab-{lab-id}` tags

## Usage

### Deploy with Dynamic IPs

```bash
# Deploy lab with NetBox IP allocation
labctl deploy bgp-lab --allocate-ips

# Deploy specific version with IPs
labctl deploy bgp-lab --version v1.2.0 --allocate-ips
```

### What Happens During Deployment

1. **IP Allocation**:
   - Reads nodes from `nodes.csv`
   - Requests IPs from NetBox prefix
   - Updates `nodes.csv` with allocated IPs
   - Tracks allocations in deployment state

2. **Device Registration**:
   - Creates devices in NetBox
   - Associates allocated IPs
   - Tags devices with lab identifiers
   - Sets device metadata

3. **Rollback on Failure**:
   - If deployment fails after allocation
   - Automatically releases allocated IPs
   - Prevents IP address orphaning

### Destroy and Cleanup

```bash
# Destroy lab - automatically releases IPs
labctl destroy bgp-lab
```

During destruction:
- Releases all allocated IPs back to pool
- Removes devices from NetBox
- Updates deployment state

### Validate Configuration

```bash
# Check NetBox connectivity and config
labctl netbox

# Sample output:
✓ NetBox configuration is valid

# Or if there are errors:
✗ NetBox configuration has errors:
  - Default prefix 10.100.100.0/24 not found in NetBox
  - Failed to connect to NetBox API
```

## Lab Repository Requirements

### nodes.csv Format

Your `nodes.csv` must have a `hostname` or `name` column:

```csv
hostname,platform,type,mgmt_ip
r1,juniper,router,
r2,juniper,router,
sw1,arista,switch,
```

The `mgmt_ip` column will be populated by NetBox allocation.

### After Allocation

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
  "enabled": true,
  "valid": true,
  "message": "NetBox configuration is valid"
}
```

## Deployment State

Deployments track NetBox allocation status:

```json
{
  "deployment_id": "bgp-lab_20241201_150000",
  "lab_id": "bgp-lab",
  "netbox_ips_allocated": true,
  "ip_assignments": {
    "r1": "10.100.100.5",
    "r2": "10.100.100.6",
    "sw1": "10.100.100.7"
  }
}
```

## Troubleshooting

### Common Issues

1. **"Prefix not found in NetBox"**
   - Ensure prefix exists and is active
   - Check prefix notation matches exactly
   - Verify API token has IPAM read permissions

2. **"Not enough IPs available"**
   - Check available IPs in prefix
   - Remove stale IP assignments
   - Increase prefix size if needed

3. **"Failed to connect to NetBox"**
   - Verify NetBox URL (no trailing slash)
   - Test API token with curl
   - Check firewall/proxy settings

### Debug Commands

```bash
# Test NetBox API directly
curl -H "Authorization: Token your-token" \
  https://netbox.example.com/api/ipam/prefixes/

# Check backend logs
journalctl -u labctl-backend -f

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

2. **Using API**:
```python
import pynetbox
nb = pynetbox.api('https://netbox.example.com', token='your-token')

# Delete IPs
for ip in nb.ipam.ip_addresses.filter(tag='lab-bgp-lab'):
    ip.delete()

# Delete devices  
for device in nb.dcim.devices.filter(tag='lab-bgp-lab'):
    device.delete()
```

## Best Practices

1. **Dedicated Prefix**: Use a dedicated prefix for lab allocations
2. **Regular Cleanup**: Periodically check for orphaned resources
3. **Tag Management**: Use consistent tagging for easy filtering
4. **Monitoring**: Track IP utilization in your lab prefix
5. **Documentation**: Document which prefixes are for labs

## Security Considerations

1. **API Token**: 
   - Use minimal required permissions
   - Rotate tokens regularly
   - Never commit tokens to version control

2. **Network Isolation**:
   - Consider separate VRF for lab management
   - Implement firewall rules for lab networks

3. **Audit Trail**:
   - NetBox logs all changes
   - Review audit logs periodically

## Integration with Monitoring

NetBox data can enhance monitoring:

```yaml
# Prometheus job to scrape NetBox metrics
- job_name: 'netbox'
  static_configs:
    - targets: ['netbox.example.com:9090']
  metric_relabel_configs:
    - source_labels: [__name__]
      regex: 'netbox_.*'
      action: keep
```

## Future Enhancements

Planned improvements for NetBox integration:

1. **VLAN Assignment**: Dynamic VLAN allocation
2. **Circuit Tracking**: Link lab connections to circuits
3. **Webhook Integration**: Real-time updates to/from NetBox
4. **Bulk Operations**: Deploy multiple labs with IP planning
5. **Reporting**: IP utilization and lab statistics

This completes the NetBox integration, providing enterprise-grade IP management for your lab deployments.