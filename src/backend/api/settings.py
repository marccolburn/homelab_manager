"""
Settings API endpoints
"""
from flask import Blueprint, request, jsonify
from ..core.config import load_config, update_config
import logging

logger = logging.getLogger(__name__)

settings_bp = Blueprint('settings', __name__)


def _mask_passwords(config):
    """Return config with passwords masked for API responses"""
    masked_config = config.copy()
    
    # Mask individual password fields
    if 'clab_tools_password' in masked_config and masked_config['clab_tools_password']:
        masked_config['clab_tools_password'] = '****'
    
    # Mask remote credentials
    if 'remote_credentials' in masked_config:
        creds = masked_config['remote_credentials'].copy()
        if creds.get('ssh_password'):
            creds['ssh_password'] = '****'
        if creds.get('sudo_password'):
            creds['sudo_password'] = '****'
        masked_config['remote_credentials'] = creds
    
    # Mask NetBox token
    if 'netbox' in masked_config and masked_config['netbox'].get('token'):
        netbox = masked_config['netbox'].copy()
        netbox['token'] = '****'
        masked_config['netbox'] = netbox
    
    return masked_config


@settings_bp.route('/api/config/settings', methods=['GET'])
def get_settings():
    """Get current configuration settings (with passwords masked)"""
    try:
        config = load_config()
        masked_config = _mask_passwords(config)
        return jsonify(masked_config)
    except Exception as e:
        logger.error(f"Error loading settings: {e}")
        return jsonify({"error": "Failed to load settings"}), 500


@settings_bp.route('/api/config/settings', methods=['POST'])
def update_settings():
    """Update configuration settings"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate the request data
        allowed_keys = {
            'clab_tools_password', 'remote_credentials', 'monitoring', 'netbox'
        }
        
        # Filter to only allowed keys
        filtered_data = {k: v for k, v in data.items() if k in allowed_keys}
        
        if not filtered_data:
            return jsonify({"error": "No valid settings provided"}), 400
        
        # Update configuration
        updated_config = update_config(filtered_data)
        
        # Return masked version
        masked_config = _mask_passwords(updated_config)
        
        logger.info("Settings updated successfully")
        return jsonify({
            "message": "Settings updated successfully",
            "config": masked_config
        })
        
    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        return jsonify({"error": "Failed to update settings"}), 500