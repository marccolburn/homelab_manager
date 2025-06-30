"""
Lab deployment and management API endpoints
"""
from flask import Blueprint, jsonify, request
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.lab_manager import LabManager

labs_bp = Blueprint('labs', __name__)

# This will be set by the main app
lab_manager: 'LabManager' = None


@labs_bp.route('/api/labs/<lab_id>/deploy', methods=['POST'])
def deploy_lab(lab_id):
    """Deploy a lab (async)"""
    data = request.json or {}
    version = data.get('version', 'latest')
    allocate_ips = data.get('allocate_ips', False)
    
    task_id = lab_manager.deploy_lab_async(lab_id, version, allocate_ips)
    
    return jsonify({
        "task_id": task_id,
        "message": f"Deployment of {lab_id} started"
    }), 202


@labs_bp.route('/api/labs/<lab_id>/destroy', methods=['POST'])
def destroy_lab(lab_id):
    """Destroy a deployed lab"""
    result = lab_manager.destroy_lab(lab_id)
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400


@labs_bp.route('/api/deployments', methods=['GET'])
def get_deployments():
    """Get all active deployments"""
    return jsonify(lab_manager.get_status())


@labs_bp.route('/api/labs/<lab_id>/scenarios', methods=['GET'])
def list_scenarios(lab_id):
    """List configuration scenarios for a lab"""
    scenarios = lab_manager.list_config_scenarios(lab_id)
    return jsonify({"lab_id": lab_id, "scenarios": scenarios})


@labs_bp.route('/api/labs/<lab_id>/scenarios/<scenario>', methods=['POST'])
def apply_scenario(lab_id, scenario):
    """Apply a configuration scenario"""
    result = lab_manager.apply_config_scenario(lab_id, scenario)
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400


@labs_bp.route('/api/logs/<lab_id>', methods=['GET'])
def get_logs(lab_id):
    """Get deployment logs for a lab"""
    # Find the most recent deployment log
    for dep_id, dep_info in sorted(lab_manager.state["deployments"].items(), reverse=True):
        if dep_info["lab_id"] == lab_id:
            log_file = Path(dep_info.get("log_file", ""))
            if log_file.exists():
                with open(log_file) as f:
                    return jsonify({
                        "deployment_id": dep_id,
                        "log": f.read()
                    })
    
    return jsonify({"error": "No logs found"}), 404