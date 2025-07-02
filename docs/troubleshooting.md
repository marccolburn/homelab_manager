# Troubleshooting Guide

Common issues and solutions for Homelab Manager.

## Installation Issues

### Installation Script Fails

**Symptoms**: `./scripts/install-labctl.sh` fails with errors

**Solutions**:
```bash
# Check Python version
python3 --version  # Should be 3.11+

# Check permissions
chmod +x scripts/install-labctl.sh

# Check disk space
df -h

# Manual installation
python3 -m venv .venv
.venv/bin/pip install -r requirements/backend.txt
```

### Dependencies Not Found

**Symptoms**: Import errors when starting backend

**Solutions**:
```bash
# Reinstall dependencies
.venv/bin/pip install --upgrade -r requirements/backend.txt

# Check virtual environment
which python3
ls -la .venv/bin/

# Clear pip cache
.venv/bin/pip cache purge
```

## Backend Issues

### Backend Won't Start

**Symptoms**: `./scripts/run-backend.sh` fails or exits immediately

**Solutions**:
```bash
# Check port availability
lsof -i :5001
netstat -tulpn | grep :5001

# Check logs
tail -f ~/.labctl/logs/backend.log

# Start with debug
FLASK_DEBUG=1 ./scripts/run-backend.sh

# Change port if needed
PORT=5002 ./scripts/run-backend.sh
```

### Port Already in Use

**Symptoms**: "Port 5001 is already in use" error

**Solutions**:
```bash
# Find process using port
lsof -i :5001

# Kill process (replace PID)
kill -9 <PID>

# Use different port
PORT=5002 ./scripts/run-backend.sh

# Check if backend already running
ps aux | grep "src.backend.app"
```

### Permission Denied Errors

**Symptoms**: Cannot write to logs or configuration directories

**Solutions**:
```bash
# Check directory permissions
ls -la ~/.labctl/

# Create directories manually
mkdir -p ~/.labctl/logs ~/.labctl/repos

# Fix permissions
chmod 755 ~/.labctl/
chmod 750 ~/.labctl/logs/
chmod 600 ~/.labctl/config.yaml
```

## Web UI Issues

### Web UI Not Loading

**Symptoms**: Browser shows "This site can't be reached" at `http://localhost:5001`

**Solutions**:
1. **Check backend is running**:
   ```bash
   curl http://localhost:5001/api/health
   ```

2. **Verify URL and port**:
   - Correct URL: `http://localhost:5001`
   - Not: `http://localhost:5000`

3. **Check browser console**:
   - Open Developer Tools (F12)
   - Look for JavaScript errors
   - Check Network tab for failed requests

4. **Clear browser cache**:
   - Hard refresh: Ctrl+F5 (Windows/Linux) or Cmd+Shift+R (Mac)
   - Clear browser cache and cookies

### Settings Page 404 Error

**Symptoms**: `http://localhost:5001/settings.html` returns 404

**Solutions**:
```bash
# Check if file exists
ls -la src/web/static/settings.html

# Restart backend
./scripts/run-backend.sh

# Check Flask routes
curl http://localhost:5001/debug/paths
```

### JavaScript Errors

**Symptoms**: Web UI loads but doesn't function properly

**Solutions**:
1. **Check browser console** (F12 → Console)
2. **Common errors**:
   - API calls failing → Check backend status
   - CORS errors → Restart backend
   - Script loading failures → Check file paths

## CLI Issues

### Command Not Found

**Symptoms**: `labctl: command not found`

**Solutions**:
```bash
# Check if installed
which labctl

# Use direct path
./scripts/labctl --help

# Add to PATH (after installation)
export PATH="$HOME/.local/bin:$PATH"

# Or use full path
~/.local/bin/labctl --help
```

### CLI Can't Connect to Backend

**Symptoms**: CLI commands fail with connection errors

**Solutions**:
```bash
# Check if backend is running
curl http://localhost:5001/api/health

# Start backend
./scripts/run-backend.sh

# Check CLI configuration
labctl doctor

# Use specific backend URL
BACKEND_URL=http://localhost:5001 labctl status
```

### Authentication Errors

**Symptoms**: CLI commands fail with auth errors

**Solutions**:
- Currently no authentication required
- If using custom authentication, check credentials
- Verify backend configuration

## Deployment Issues

### Remote Connection Failures

**Symptoms**: Deployments fail immediately with SSH errors

**Solutions**:
1. **Test SSH connectivity**:
   ```bash
   ssh user@remote-host
   ```

2. **Check credentials in Settings**:
   - Go to `http://localhost:5001/settings.html`
   - Verify SSH password is correct
   - Test connection

3. **Check SSH key authentication**:
   ```bash
   ssh-copy-id user@remote-host
   ```

4. **Verify clab-tools on remote host**:
   ```bash
   ssh user@remote-host "which clab-tools"
   ```

### Deployment Hangs

**Symptoms**: Deployment starts but never completes

**Solutions**:
1. **Check deployment logs**:
   ```bash
   labctl logs lab-name
   # Or via Web UI: Active Deployments → View Logs
   ```

2. **Look for password prompts**:
   - Configure remote credentials properly
   - Use environment variables if needed

3. **Check resource availability**:
   ```bash
   ssh user@remote-host "docker system df"
   ssh user@remote-host "free -h"
   ```

### Bridge Creation Errors

**Symptoms**: Deployment fails during bridge creation

**Solutions**:
- Bridge creation prompts are handled automatically
- Check remote host Docker permissions
- Verify user can create Docker networks

### Lab Repository Issues

**Symptoms**: Can't add repositories or repositories fail validation

**Solutions**:
1. **Check Git URL format**:
   ```bash
   # SSH format
   git@github.com:user/repo.git
   
   # HTTPS format
   https://github.com/user/repo.git
   ```

2. **Verify SSH key access**:
   ```bash
   ssh -T git@github.com
   ```

3. **Check repository structure**:
   - Must have `lab-metadata.yaml`
   - Must have `clab_tools_files/` directory
   - Must have required files (config.yaml, nodes.csv, etc.)

## NetBox Integration Issues

### NetBox Connection Failures

**Symptoms**: NetBox validation fails or IP allocation fails

**Solutions**:
1. **Test NetBox connectivity**:
   ```bash
   curl http://netbox-url/api/
   ```

2. **Check API token**:
   - Verify token has proper permissions
   - Test in NetBox web UI

3. **Verify configuration**:
   ```bash
   labctl netbox
   # Or: curl http://localhost:5001/api/netbox/validate
   ```

### IP Allocation Failures

**Symptoms**: Deployment fails during IP allocation

**Solutions**:
1. **Check prefix availability**:
   - Verify prefix exists in NetBox
   - Ensure sufficient available IPs

2. **Check permissions**:
   - API token needs IP address management permissions
   - Verify device creation permissions

3. **Check site and role**:
   - Default site must exist in NetBox
   - Default role must exist in NetBox

## Performance Issues

### Slow Web UI

**Symptoms**: Web UI loads slowly or feels unresponsive

**Solutions**:
- Check backend performance with many repositories
- Clear browser cache
- Restart backend to clear memory

### Large Log Files

**Symptoms**: Deployment logs consume excessive disk space

**Solutions**:
```bash
# Check log directory size
du -sh ~/.labctl/logs/

# Clean old logs (be careful!)
find ~/.labctl/logs/ -name "*.log" -mtime +30 -delete

# Rotate logs
logrotate -f /path/to/logrotate.conf
```

## Debugging Commands

### System Health Check

```bash
# CLI health check
labctl doctor

# Backend health
curl http://localhost:5001/api/health

# Configuration check
curl http://localhost:5001/api/config
```

### Log Analysis

```bash
# Backend logs
tail -f ~/.labctl/logs/backend.log

# Deployment logs
labctl logs lab-name

# System logs (Linux)
journalctl -u labctl-backend -f
```

### Network Debugging

```bash
# Check backend connectivity
curl -v http://localhost:5001/api/health

# Check remote host connectivity
ssh -v user@remote-host

# Test NetBox connectivity
curl -H "Authorization: Token YOUR-TOKEN" http://netbox-url/api/
```

## Getting Help

### Log Collection

Before reporting issues, collect relevant logs:

```bash
# Create debug bundle
mkdir debug-info
cp ~/.labctl/config.yaml debug-info/ 2>/dev/null || echo "No config"
cp ~/.labctl/logs/backend.log debug-info/ 2>/dev/null || echo "No backend log"
labctl doctor > debug-info/doctor-output.txt 2>&1
curl http://localhost:5001/api/health > debug-info/health.json 2>&1

# Sanitize sensitive information before sharing
sed -i 's/password.*/password: REDACTED/g' debug-info/config.yaml
```

### Reporting Issues

Include the following information:
- Operating system and version
- Python version
- clab-tools version
- Error messages and logs
- Steps to reproduce
- Configuration (with passwords removed)

### Community Support

- GitHub Issues: [Repository Issues Page]
- Documentation: Complete guides in `docs/` directory
- CLI Help: `labctl --help` and `labctl COMMAND --help`