"""
Health check and system status API endpoints
"""
from flask import Blueprint, jsonify
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.lab_manager import LabManager

health_bp = Blueprint('health', __name__)

# This will be set by the main app
lab_manager: 'LabManager' = None


@health_bp.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "labctl-backend"})


@health_bp.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    # Remove sensitive data
    config = lab_manager.config.copy()
    if 'netbox' in config and 'token' in config['netbox']:
        config['netbox']['token'] = "***"
    return jsonify(config)