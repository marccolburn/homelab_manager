"""
Homelab Manager Flask Backend API
"""
import logging
from pathlib import Path
from flask import Flask, send_from_directory
from flask_cors import CORS

# Import core modules
from .core.config import load_config
from .core.lab_manager import LabManager
from .core.git_ops import GitOperations
from .core.clab_runner import ClabRunner

# Import API blueprints
from .api import repos_bp, labs_bp, tasks_bp, health_bp

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app(test_config=None):
    """Application factory pattern"""
    # Initialize Flask app with static folder configuration
    static_folder = Path(__file__).parent.parent / 'web' / 'static'
    app = Flask(__name__, static_url_path='/static', static_folder=str(static_folder))
    CORS(app)  # Enable CORS for all routes
    
    # Load configuration
    if test_config:
        config = test_config
    else:
        config = load_config()
    
    # Initialize core components
    git_ops = GitOperations(config.get("git_cmd", "git"))
    clab_runner = ClabRunner(
        config.get("clab_tools_cmd", "clab-tools"),
        Path(config.get("logs_dir", "/var/lib/labctl/logs"))
    )
    
    # Initialize lab manager with injected dependencies
    lab_manager = LabManager(config, git_ops, clab_runner)
    
    # Store lab_manager on app for blueprint access
    app.lab_manager = lab_manager
    
    # Register blueprints
    for blueprint in [repos_bp, labs_bp, tasks_bp, health_bp]:
        app.register_blueprint(blueprint)
    
    # Debug route to check paths
    @app.route('/debug/paths')
    def debug_paths():
        web_dir = Path(__file__).parent.parent / 'web' / 'static'
        return {
            'web_dir': str(web_dir),
            'web_dir_resolved': str(web_dir.resolve()),
            'web_dir_exists': web_dir.exists(),
            'cwd': str(Path.cwd()),
            'file': __file__
        }
    
    # Static file serving for web UI
    @app.route('/')
    def index():
        """Serve the web UI"""
        return send_from_directory(app.static_folder, 'index.html')
    
    return app


if __name__ == '__main__':
    # Development server
    import os
    app = create_app()
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)