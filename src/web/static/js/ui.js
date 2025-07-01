// UI manipulation functions

const ui = {
    // Lab display functions
    displayLabs(labs) {
        const container = document.getElementById('labs-container');
        
        if (!labs || labs.length === 0) {
            container.innerHTML = `
                <div class="labs-panel">
                    <p>No labs available. Add a repository to get started.</p>
                </div>
            `;
            return;
        }

        const labsHTML = labs.map(lab => {
            const difficultyClass = `difficulty-${(lab.difficulty || 'intermediate').toLowerCase()}`;
            const tags = lab.tags || [];
            const tagsHTML = tags.map(tag => `<span class="tag">${tag}</span>`).join('');
            const requirements = lab.requirements || {};
            
            return `
                <div class="lab-card">
                    <div class="lab-header">
                        <div>
                            <div class="lab-title">${lab.name || lab.id}</div>
                            <div class="lab-difficulty ${difficultyClass}">${lab.difficulty || 'Intermediate'}</div>
                        </div>
                        <div class="lab-category">${lab.category || 'General'}</div>
                    </div>
                    
                    <div class="lab-description">${lab.description?.short || 'No description available'}</div>
                    
                    <div class="lab-tags">${tagsHTML}</div>
                    
                    <div class="lab-stats">
                        <div class="stat">
                            <div class="stat-value">${requirements.cpu_cores || 'N/A'}</div>
                            <div class="stat-label">CPU Cores</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value">${requirements.memory_gb || 'N/A'}GB</div>
                            <div class="stat-label">Memory</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value">${requirements.disk_gb || 'N/A'}GB</div>
                            <div class="stat-label">Disk</div>
                        </div>
                    </div>
                    
                    <div class="lab-actions">
                        <button class="btn btn-primary" onclick="ui.showDeployModal('${lab.id}')">
                            🚀 Deploy Lab
                        </button>
                        <button class="btn btn-secondary" onclick="ui.viewLabDetails('${lab.id}')">
                            📖 Details
                        </button>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = `<div class="lab-grid">${labsHTML}</div>`;
    },

    // Deployment display functions
    displayDeployments(deployments) {
        const container = document.getElementById('deployments-container');
        
        // Handle both object and array formats
        if (!deployments || (Array.isArray(deployments) && deployments.length === 0) || 
            (typeof deployments === 'object' && Object.keys(deployments).length === 0)) {
            container.innerHTML = '<p>No active deployments.</p>';
            return;
        }
        
        const deploymentKeys = Object.keys(deployments);

        const deploymentsHTML = deploymentKeys.map(labId => {
            const deployment = deployments[labId];
            const statusClass = `status-${deployment.status}`;
            const deployedAt = new Date(deployment.deployed_at).toLocaleString();
            
            return `
                <div class="deployment-item">
                    <div class="deployment-info">
                        <h4>
                            <span class="status-indicator ${statusClass}"></span>
                            ${labId}
                        </h4>
                        <p>Deployed: ${deployedAt} | Status: ${deployment.status}</p>
                    </div>
                    <button class="btn btn-danger" onclick="app.teardownDeployment('${labId}')">
                        🗑️ Teardown
                    </button>
                </div>
            `;
        }).join('');

        container.innerHTML = deploymentsHTML;
    },

    // Modal functions
    showDeployModal(labId) {
        // This will be implemented in Stage 2
        app.deployLab(labId);
    },

    viewLabDetails(labId) {
        // Show lab details in an alert (can be improved to a modal later)
        const lab = app.labs.find(l => l.id === labId);
        if (lab) {
            const details = `Lab: ${lab.name}\n\n${lab.description?.long || lab.description?.short || 'No details available'}\n\nRequirements:\n- CPU Cores: ${lab.requirements?.cpu_cores || 'N/A'}\n- Memory: ${lab.requirements?.memory_gb || 'N/A'} GB\n- Disk: ${lab.requirements?.disk_gb || 'N/A'} GB\n- ContainerLab: ${lab.requirements?.containerlab_version || 'Any version'}`;
            alert(details);
        }
    },

    showLogs(labId) {
        // This will be implemented in Stage 3
        console.log('Logs viewer not yet implemented for:', labId);
    },

    // Notification system
    showNotification(message, type = 'info') {
        // Remove existing notifications
        const existing = document.querySelector('.notification');
        if (existing) {
            existing.remove();
        }

        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);

        // Show notification
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);

        // Hide notification after duration
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, ANIMATION_DURATION);
        }, NOTIFICATION_DURATION);
    },

    // Loading states
    showLoading(containerId, message = 'Loading...') {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                    <p>${message}</p>
                </div>
            `;
        }
    },

    // Error display
    showError(containerId, message) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `
                <div class="loading">
                    <p style="color: #ef4444;">${message}</p>
                </div>
            `;
        }
    },

    // Repository display functions
    displayRepositories(repos) {
        const container = document.getElementById('repositories-container');
        
        if (!repos || repos.length === 0) {
            container.innerHTML = '<p>No repositories added yet. Click "Add Repository" to get started.</p>';
            return;
        }

        const reposHTML = repos.map(repo => {
            const lastUpdate = repo.last_update ? new Date(repo.last_update).toLocaleString() : 'Never';
            
            return `
                <div class="repo-card">
                    <h3>${repo.name || repo.id}</h3>
                    <div class="repo-url">${repo.id}</div>
                    <p style="color: #666; font-size: 0.9rem; margin-bottom: 15px;">
                        Last updated: ${lastUpdate}
                    </p>
                    <div class="repo-actions">
                        <button class="btn btn-secondary" onclick="app.updateRepository('${repo.id}')">
                            🔄 Update
                        </button>
                        <button class="btn btn-danger" onclick="app.deleteRepository('${repo.id}')">
                            🗑️ Remove
                        </button>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = `<div class="repo-grid">${reposHTML}</div>`;
    },

    // Modal functions
    showAddRepoModal() {
        this.showModal('add-repo-modal');
    },

    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('show');
        }
    },

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('show');
            // Clear form if it exists
            const form = modal.querySelector('form');
            if (form) form.reset();
        }
    }
};