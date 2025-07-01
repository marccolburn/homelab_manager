// Main application logic

const app = {
    // Application state
    labs: [],
    deployments: {},
    repositories: [],
    refreshInterval: null,
    currentTab: 'labs',

    // Initialize the application
    async init() {
        // Load initial data
        await this.loadLabs();
        await this.loadDeployments();
        
        // Set up automatic refresh for deployments
        this.refreshInterval = setInterval(() => {
            this.loadDeployments();
        }, REFRESH_INTERVALS.deployments);
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Handle initial hash
        this.handleHashChange();
    },

    // Data loading functions
    async loadLabs() {
        ui.showLoading('labs-container', 'Loading available labs...');
        try {
            this.labs = await api.getLabs();
            ui.displayLabs(this.labs);
        } catch (error) {
            ui.showError('labs-container', 'Failed to load labs. Please try again later.');
            ui.showNotification('Failed to load labs', 'error');
        }
    },

    async loadDeployments() {
        try {
            const response = await api.getDeployments();
            // Handle both old format (direct object) and new format ({deployments: {}, total: n})
            this.deployments = response.deployments || response;
            ui.displayDeployments(this.deployments);
        } catch (error) {
            ui.showError('deployments-container', 'Failed to load deployments.');
        }
    },

    // Lab deployment functions
    async deployLab(labId, version = 'latest', allocateIps = false) {
        ui.showNotification('Starting lab deployment...', 'success');
        
        try {
            const result = await api.deployLab(labId, version, allocateIps);
            
            if (result.task_id) {
                ui.showNotification(`Lab ${labId} deployment started!`, 'success');
                // Start monitoring the task
                this.monitorTask(result.task_id, labId);
            } else {
                ui.showNotification(`Lab ${labId} deployed successfully!`, 'success');
            }
            
            // Refresh deployments
            await this.loadDeployments();
        } catch (error) {
            ui.showNotification(`Deployment failed: ${error.message}`, 'error');
        }
    },

    async teardownDeployment(labId) {
        if (!confirm(`Are you sure you want to teardown the deployment for ${labId}?`)) {
            return;
        }

        ui.showNotification('Tearing down deployment...', 'success');
        
        try {
            await api.destroyLab(labId);
            ui.showNotification('Deployment torn down successfully!', 'success');
            await this.loadDeployments();
        } catch (error) {
            ui.showNotification(`Teardown failed: ${error.message}`, 'error');
        }
    },

    // Task monitoring
    async monitorTask(taskId, labId) {
        const checkTask = async () => {
            try {
                const task = await api.getTaskStatus(taskId);
                
                if (task.status === 'completed') {
                    ui.showNotification(`Lab ${labId} deployment completed!`, 'success');
                    await this.loadDeployments();
                } else if (task.status === 'failed') {
                    ui.showNotification(`Lab ${labId} deployment failed: ${task.error}`, 'error');
                    await this.loadDeployments();
                } else {
                    // Still running, check again
                    setTimeout(checkTask, REFRESH_INTERVALS.tasks);
                }
            } catch (error) {
                console.error('Failed to check task status:', error);
            }
        };
        
        // Start checking
        setTimeout(checkTask, REFRESH_INTERVALS.tasks);
    },

    // Repository management functions
    async loadRepositories() {
        ui.showLoading('repositories-container', 'Loading repositories...');
        try {
            this.repositories = await api.getLabs(); // Repos and labs are the same
            ui.displayRepositories(this.repositories);
        } catch (error) {
            ui.showError('repositories-container', 'Failed to load repositories.');
        }
    },

    async handleAddRepo(event) {
        event.preventDefault();
        const form = event.target;
        const gitUrl = form.git_url.value;
        
        try {
            ui.showNotification('Adding repository...', 'success');
            await api.addRepository(gitUrl);
            ui.showNotification('Repository added successfully!', 'success');
            ui.closeModal('add-repo-modal');
            await this.loadRepositories();
            await this.loadLabs(); // Refresh labs too
        } catch (error) {
            ui.showNotification(`Failed to add repository: ${error.message}`, 'error');
        }
    },

    async updateRepository(repoId) {
        try {
            ui.showNotification('Updating repository...', 'success');
            await api.updateRepository(repoId);
            ui.showNotification('Repository updated successfully!', 'success');
            await this.loadRepositories();
            await this.loadLabs(); // Refresh labs too
        } catch (error) {
            ui.showNotification(`Failed to update repository: ${error.message}`, 'error');
        }
    },

    async deleteRepository(repoId) {
        if (!confirm(`Are you sure you want to remove this repository?`)) {
            return;
        }
        
        try {
            ui.showNotification('Removing repository...', 'success');
            await api.deleteRepository(repoId);
            ui.showNotification('Repository removed successfully!', 'success');
            await this.loadRepositories();
            await this.loadLabs(); // Refresh labs too
        } catch (error) {
            ui.showNotification(`Failed to remove repository: ${error.message}`, 'error');
        }
    },

    // Tab switching
    switchTab(tabName) {
        // Update active tab
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`.nav-tab[href="#${tabName}"]`).classList.add('active');
        
        // Show/hide content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-section`).classList.add('active');
        
        // Load data if needed
        this.currentTab = tabName;
        if (tabName === 'repositories' && this.repositories.length === 0) {
            this.loadRepositories();
        }
        
        // Update URL hash
        window.location.hash = tabName;
    },

    handleHashChange() {
        const hash = window.location.hash.slice(1) || 'labs';
        if (['labs', 'deployments', 'repositories'].includes(hash)) {
            this.switchTab(hash);
        }
    },

    // Event listeners setup
    setupEventListeners() {
        window.addEventListener('hashchange', () => {
            this.handleHashChange();
        });
    },

    // Cleanup function
    destroy() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
    }
};

// Initialize the app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    app.init();
});

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    app.destroy();
});