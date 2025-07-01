"""
NetBox integration module for IP allocation and device management
"""
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import csv
import ipaddress
from datetime import datetime

try:
    import pynetbox
    from pynetbox.core.api import Api
    NETBOX_AVAILABLE = True
except ImportError:
    NETBOX_AVAILABLE = False
    Api = None

logger = logging.getLogger(__name__)


class NetBoxManager:
    """Manages NetBox integration for IP allocation and device registration"""
    
    def __init__(self, config: Dict):
        """Initialize NetBox manager
        
        Args:
            config: NetBox configuration dictionary containing:
                - url: NetBox API URL
                - token: API token
                - default_prefix: Default IP prefix for labs
                - default_site: Default site name
                - default_role: Default device role
        """
        self.config = config
        self.enabled = config.get('enabled', False)
        self._api = None
        
        if self.enabled and not NETBOX_AVAILABLE:
            logger.error("NetBox integration enabled but pynetbox not installed")
            self.enabled = False
            
    @property
    def api(self) -> Optional[Api]:
        """Lazy-load NetBox API connection"""
        if not self.enabled:
            return None
            
        if self._api is None:
            try:
                self._api = pynetbox.api(
                    self.config['url'],
                    token=self.config['token']
                )
                # Test connection
                self._api.status()
                logger.info(f"Connected to NetBox at {self.config['url']}")
            except Exception as e:
                logger.error(f"Failed to connect to NetBox: {e}")
                self.enabled = False
                return None
                
        return self._api
    
    def allocate_ips(self, lab_id: str, nodes: List[str]) -> Dict[str, str]:
        """Allocate IP addresses from NetBox for lab nodes
        
        Args:
            lab_id: Unique lab identifier
            nodes: List of node names requiring IPs
            
        Returns:
            Dictionary mapping node names to allocated IP addresses
            Empty dict if allocation fails
        """
        if not self.enabled or not self.api:
            logger.warning("NetBox not available for IP allocation")
            return {}
            
        ip_assignments = {}
        allocated_ips = []
        
        try:
            # Get the prefix to allocate from
            prefix_str = self.config.get('default_prefix', '10.100.100.0/24')
            prefix = self.api.ipam.prefixes.get(prefix=prefix_str)
            
            if not prefix:
                logger.error(f"Prefix {prefix_str} not found in NetBox")
                return {}
                
            # Get available IPs from the prefix
            available_ips = prefix.available_ips.list()
            
            if len(available_ips) < len(nodes):
                logger.error(f"Not enough IPs available. Need {len(nodes)}, have {len(available_ips)}")
                return {}
                
            # Allocate IPs for each node
            for i, node in enumerate(nodes):
                try:
                    # Create IP address in NetBox
                    ip_data = {
                        "address": available_ips[i]['address'],
                        "status": "active",
                        "description": f"Lab: {lab_id}, Node: {node}",
                        "tags": [{"name": "lab-managed"}, {"name": f"lab-{lab_id}"}]
                    }
                    
                    # Create the IP address
                    ip_obj = self.api.ipam.ip_addresses.create(**ip_data)
                    allocated_ips.append(ip_obj)
                    
                    # Extract just the IP without the mask
                    ip_addr = str(ipaddress.ip_interface(ip_obj.address).ip)
                    ip_assignments[node] = ip_addr
                    
                    logger.info(f"Allocated {ip_addr} to {node} in lab {lab_id}")
                    
                except Exception as e:
                    logger.error(f"Failed to allocate IP for {node}: {e}")
                    # Rollback on failure
                    self._rollback_allocations(allocated_ips)
                    return {}
                    
            return ip_assignments
            
        except Exception as e:
            logger.error(f"IP allocation failed: {e}")
            self._rollback_allocations(allocated_ips)
            return {}
    
    def release_ips(self, lab_id: str) -> bool:
        """Release all IPs allocated to a lab
        
        Args:
            lab_id: Lab identifier
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.api:
            return True  # Nothing to release
            
        try:
            # Find all IPs tagged with this lab
            tag_name = f"lab-{lab_id}"
            ips = self.api.ipam.ip_addresses.filter(tag=tag_name)
            
            released_count = 0
            for ip in ips:
                try:
                    ip.delete()
                    released_count += 1
                    logger.info(f"Released IP {ip.address} from lab {lab_id}")
                except Exception as e:
                    logger.error(f"Failed to release IP {ip.address}: {e}")
                    
            logger.info(f"Released {released_count} IPs for lab {lab_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to release IPs for lab {lab_id}: {e}")
            return False
    
    def update_nodes_csv(self, nodes_file: Path, ip_assignments: Dict[str, str]) -> bool:
        """Update nodes.csv file with allocated IP addresses
        
        Args:
            nodes_file: Path to nodes.csv file
            ip_assignments: Dictionary of node names to IP addresses
            
        Returns:
            True if successful, False otherwise
        """
        if not ip_assignments:
            return True  # Nothing to update
            
        try:
            # Read existing CSV
            rows = []
            with open(nodes_file, 'r') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                
                # Ensure mgmt_ip column exists
                if 'mgmt_ip' not in fieldnames:
                    fieldnames = list(fieldnames) + ['mgmt_ip']
                    
                for row in reader:
                    # Update IP if node has allocation
                    node_name = row.get('hostname', row.get('name', ''))
                    if node_name in ip_assignments:
                        row['mgmt_ip'] = ip_assignments[node_name]
                    rows.append(row)
                    
            # Write updated CSV
            with open(nodes_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
                
            logger.info(f"Updated {nodes_file} with {len(ip_assignments)} IP assignments")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update nodes.csv: {e}")
            return False
    
    def register_devices(self, lab_id: str, lab_name: str, 
                        nodes: List[Dict[str, str]]) -> List[str]:
        """Register lab devices in NetBox
        
        Args:
            lab_id: Lab identifier
            lab_name: Human-readable lab name
            nodes: List of node information dictionaries
            
        Returns:
            List of created device names
        """
        if not self.enabled or not self.api:
            return []
            
        created_devices = []
        site_name = self.config.get('default_site', 'Lab Environment')
        role_name = self.config.get('default_role', 'Lab Device')
        
        try:
            # Get or create site
            site = self.api.dcim.sites.get(name=site_name)
            if not site:
                site = self.api.dcim.sites.create(
                    name=site_name,
                    slug=site_name.lower().replace(' ', '-')
                )
                
            # Get or create device role
            role = self.api.dcim.device_roles.get(name=role_name)
            if not role:
                role = self.api.dcim.device_roles.create(
                    name=role_name,
                    slug=role_name.lower().replace(' ', '-'),
                    color='0066cc'
                )
                
            # Get or create device type (generic)
            device_type = self.api.dcim.device_types.get(model='Generic Lab Device')
            if not device_type:
                # First ensure manufacturer exists
                manufacturer = self.api.dcim.manufacturers.get(name='Generic')
                if not manufacturer:
                    manufacturer = self.api.dcim.manufacturers.create(
                        name='Generic',
                        slug='generic'
                    )
                    
                device_type = self.api.dcim.device_types.create(
                    manufacturer=manufacturer.id,
                    model='Generic Lab Device',
                    slug='generic-lab-device',
                    u_height=0  # 0U for virtual devices
                )
                
            # Create devices
            for node in nodes:
                node_name = node.get('hostname', node.get('name', ''))
                device_name = f"{lab_id}-{node_name}"
                
                try:
                    # Check if device already exists
                    existing = self.api.dcim.devices.get(name=device_name)
                    if existing:
                        logger.warning(f"Device {device_name} already exists")
                        continue
                        
                    # Create device
                    device_data = {
                        "name": device_name,
                        "device_type": device_type.id,
                        "device_role": role.id,
                        "site": site.id,
                        "status": "active",
                        "comments": f"Lab: {lab_name} ({lab_id})",
                        "tags": [{"name": "lab-managed"}, {"name": f"lab-{lab_id}"}]
                    }
                    
                    device = self.api.dcim.devices.create(**device_data)
                    created_devices.append(device_name)
                    
                    # If device has an IP, associate it
                    if 'mgmt_ip' in node and node['mgmt_ip']:
                        self._associate_ip_to_device(device, node['mgmt_ip'])
                        
                    logger.info(f"Registered device {device_name} in NetBox")
                    
                except Exception as e:
                    logger.error(f"Failed to register device {device_name}: {e}")
                    
            return created_devices
            
        except Exception as e:
            logger.error(f"Device registration failed: {e}")
            return created_devices
    
    def unregister_devices(self, lab_id: str) -> bool:
        """Remove lab devices from NetBox
        
        Args:
            lab_id: Lab identifier
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.api:
            return True
            
        try:
            # Find all devices tagged with this lab
            tag_name = f"lab-{lab_id}"
            devices = self.api.dcim.devices.filter(tag=tag_name)
            
            removed_count = 0
            for device in devices:
                try:
                    device.delete()
                    removed_count += 1
                    logger.info(f"Removed device {device.name} from NetBox")
                except Exception as e:
                    logger.error(f"Failed to remove device {device.name}: {e}")
                    
            logger.info(f"Removed {removed_count} devices for lab {lab_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister devices for lab {lab_id}: {e}")
            return False
    
    def validate_config(self) -> Tuple[bool, List[str]]:
        """Validate NetBox configuration and connectivity
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not self.config.get('enabled'):
            return True, []  # Disabled is valid
            
        # Check required fields
        required_fields = ['url', 'token']
        for field in required_fields:
            if field not in self.config:
                errors.append(f"Missing required field: {field}")
                
        if not NETBOX_AVAILABLE:
            errors.append("pynetbox package not installed")
            
        if errors:
            return False, errors
            
        # Test connection
        try:
            if self.api:
                status = self.api.status()
                logger.info(f"NetBox version: {status['netbox-version']}")
                
                # Verify default prefix exists
                prefix_str = self.config.get('default_prefix')
                if prefix_str:
                    prefix = self.api.ipam.prefixes.get(prefix=prefix_str)
                    if not prefix:
                        errors.append(f"Default prefix {prefix_str} not found in NetBox")
                        
            else:
                errors.append("Failed to connect to NetBox API")
                
        except Exception as e:
            errors.append(f"NetBox connection error: {str(e)}")
            
        return len(errors) == 0, errors
    
    def _rollback_allocations(self, allocated_ips: List):
        """Rollback IP allocations on failure"""
        for ip in allocated_ips:
            try:
                ip.delete()
                logger.info(f"Rolled back IP allocation: {ip.address}")
            except Exception as e:
                logger.error(f"Failed to rollback IP {ip.address}: {e}")
                
    def _associate_ip_to_device(self, device, ip_address: str):
        """Associate an IP address with a device"""
        try:
            # Find the IP address object
            ip = self.api.ipam.ip_addresses.get(address=ip_address)
            if ip:
                # Create a primary interface if it doesn't exist
                interface = self.api.dcim.interfaces.get(
                    device_id=device.id,
                    name='mgmt0'
                )
                if not interface:
                    interface = self.api.dcim.interfaces.create(
                        device=device.id,
                        name='mgmt0',
                        type='virtual'
                    )
                    
                # Assign IP to interface
                ip.assigned_object_type = 'dcim.interface'
                ip.assigned_object_id = interface.id
                ip.save()
                
                # Set as primary IP
                device.primary_ip4 = ip.id
                device.save()
                
                logger.info(f"Associated IP {ip_address} with device {device.name}")
                
        except Exception as e:
            logger.error(f"Failed to associate IP {ip_address} with device: {e}")