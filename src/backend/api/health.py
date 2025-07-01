"""
Health check and system status API endpoints
"""
from flask import Blueprint, jsonify, current_app

health_bp = Blueprint('health', __name__)


@health_bp.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "labctl-backend"})


@health_bp.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    # Remove sensitive data
    config = current_app.lab_manager.config.copy()
    if 'netbox' in config and 'token' in config['netbox']:
        config['netbox']['token'] = "***"
    return jsonify(config)