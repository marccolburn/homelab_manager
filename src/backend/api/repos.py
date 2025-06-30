"""
Repository management API endpoints
"""
from flask import Blueprint, jsonify, request
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.lab_manager import LabManager

repos_bp = Blueprint('repos', __name__)

# This will be set by the main app
lab_manager: 'LabManager' = None


@repos_bp.route('/api/repos', methods=['GET'])
def list_repos():
    """List all lab repositories"""
    repos = lab_manager.list_repos()
    return jsonify(repos)


@repos_bp.route('/api/repos', methods=['POST'])
def add_repo():
    """Add a new lab repository"""
    data = request.json
    if not data or 'url' not in data:
        return jsonify({"error": "Repository URL required"}), 400
    
    result = lab_manager.add_repo(data['url'], data.get('name'))
    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 400


@repos_bp.route('/api/repos/<lab_id>', methods=['PUT'])
def update_repo(lab_id):
    """Update a lab repository"""
    result = lab_manager.update_repo(lab_id)
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400


@repos_bp.route('/api/repos/<lab_id>', methods=['DELETE'])
def remove_repo(lab_id):
    """Remove a lab repository"""
    result = lab_manager.remove_repo(lab_id)
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400