"""
Async task management API endpoints
"""
from flask import Blueprint, jsonify, current_app

tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('/api/tasks/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Get status of an async task"""
    status = current_app.lab_manager.get_task_status(task_id)
    if 'error' in status:
        return jsonify(status), 404
    return jsonify(status)