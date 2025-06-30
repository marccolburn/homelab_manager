"""
Git operations module for lab repository management
"""
import logging
import subprocess
from pathlib import Path
from typing import List, Optional, Dict

logger = logging.getLogger(__name__)


class GitOperations:
    """Handles all Git-related operations for lab repositories"""
    
    def __init__(self, git_cmd: str = "git"):
        self.git_cmd = git_cmd
    
    def _run_command(self, cmd: List[str], cwd: Optional[Path] = None, 
                     capture_output: bool = True) -> subprocess.CompletedProcess:
        """Run a git command and handle errors"""
        logger.debug(f"Running command: {' '.join(cmd)}")
        if cwd:
            logger.debug(f"Working directory: {cwd}")
        
        result = subprocess.run(
            cmd, 
            cwd=cwd, 
            capture_output=capture_output,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Command failed: {' '.join(cmd)}")
            if capture_output:
                logger.error(f"Error output: {result.stderr}")
        
        return result
    
    def clone(self, repo_url: str, target_path: Path) -> Dict:
        """Clone a repository to the specified path"""
        logger.info(f"Cloning repository {repo_url} to {target_path}...")
        
        # Ensure parent directory exists
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        result = self._run_command(
            [self.git_cmd, "clone", repo_url, str(target_path)]
        )
        
        if result.returncode == 0:
            return {"success": True, "message": f"Repository cloned to {target_path}"}
        else:
            return {"success": False, "error": f"Git clone failed: {result.stderr}"}
    
    def pull(self, repo_path: Path) -> Dict:
        """Pull latest changes in a repository"""
        logger.info(f"Pulling latest changes in {repo_path}...")
        
        if not self.is_git_repo(repo_path):
            return {"success": False, "error": f"{repo_path} is not a git repository"}
        
        result = self._run_command([self.git_cmd, "pull"], cwd=repo_path)
        
        if result.returncode == 0:
            return {"success": True, "message": "Repository updated"}
        else:
            return {"success": False, "error": f"Git pull failed: {result.stderr}"}
    
    def fetch_tags(self, repo_path: Path) -> Dict:
        """Fetch all tags from remote"""
        logger.info(f"Fetching tags for {repo_path}...")
        
        if not self.is_git_repo(repo_path):
            return {"success": False, "error": f"{repo_path} is not a git repository"}
        
        result = self._run_command([self.git_cmd, "fetch", "--tags"], cwd=repo_path)
        
        if result.returncode == 0:
            return {"success": True, "message": "Tags fetched"}
        else:
            return {"success": False, "error": f"Git fetch failed: {result.stderr}"}
    
    def checkout(self, repo_path: Path, ref: str) -> Dict:
        """Checkout a specific branch, tag, or commit"""
        logger.info(f"Checking out {ref} in {repo_path}...")
        
        if not self.is_git_repo(repo_path):
            return {"success": False, "error": f"{repo_path} is not a git repository"}
        
        result = self._run_command([self.git_cmd, "checkout", ref], cwd=repo_path)
        
        if result.returncode == 0:
            return {"success": True, "message": f"Checked out {ref}"}
        else:
            return {"success": False, "error": f"Git checkout failed: {result.stderr}"}
    
    def get_tags(self, repo_path: Path) -> List[str]:
        """Get all tags in a repository"""
        if not self.is_git_repo(repo_path):
            return []
        
        result = self._run_command(
            [self.git_cmd, "tag", "-l"],
            cwd=repo_path
        )
        
        if result.returncode == 0:
            return [tag.strip() for tag in result.stdout.strip().split('\n') if tag.strip()]
        else:
            return []
    
    def get_current_branch(self, repo_path: Path) -> Optional[str]:
        """Get the current branch name"""
        if not self.is_git_repo(repo_path):
            return None
        
        result = self._run_command(
            [self.git_cmd, "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=repo_path
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return None
    
    def get_current_commit(self, repo_path: Path) -> Optional[str]:
        """Get the current commit hash"""
        if not self.is_git_repo(repo_path):
            return None
        
        result = self._run_command(
            [self.git_cmd, "rev-parse", "HEAD"],
            cwd=repo_path
        )
        
        if result.returncode == 0:
            return result.stdout.strip()[:8]  # Return short hash
        else:
            return None
    
    def is_git_repo(self, path: Path) -> bool:
        """Check if a path is a git repository"""
        if not path.exists():
            return False
        
        git_dir = path / ".git"
        return git_dir.exists() and git_dir.is_dir()
    
    def get_remote_url(self, repo_path: Path) -> Optional[str]:
        """Get the remote origin URL"""
        if not self.is_git_repo(repo_path):
            return None
        
        result = self._run_command(
            [self.git_cmd, "config", "--get", "remote.origin.url"],
            cwd=repo_path
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return None
    
    def reset_to_ref(self, repo_path: Path, ref: str = "HEAD") -> Dict:
        """Reset repository to a specific reference"""
        logger.info(f"Resetting {repo_path} to {ref}...")
        
        if not self.is_git_repo(repo_path):
            return {"success": False, "error": f"{repo_path} is not a git repository"}
        
        # First, clean any untracked files
        clean_result = self._run_command(
            [self.git_cmd, "clean", "-fd"],
            cwd=repo_path
        )
        
        if clean_result.returncode != 0:
            logger.warning(f"Git clean failed: {clean_result.stderr}")
        
        # Then reset to the specified ref
        result = self._run_command(
            [self.git_cmd, "reset", "--hard", ref],
            cwd=repo_path
        )
        
        if result.returncode == 0:
            return {"success": True, "message": f"Repository reset to {ref}"}
        else:
            return {"success": False, "error": f"Git reset failed: {result.stderr}"}