"""
Async task management API endpoints
"""
from flask import Blueprint, jsonify
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.lab_manager import LabManager

tasks_bp = Blueprint('tasks', __name__)

# This will be set by the main app
lab_manager: 'LabManager' = None


@tasks_bp.route('/api/tasks/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Get status of an async task"""
    status = lab_manager.get_task_status(task_id)
    if 'error' in status:
        return jsonify(status), 404
    return jsonify(status)