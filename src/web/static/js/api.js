// API client module for all backend communication

const api = {
    // Repository management
    async getLabs() {
        try {
            const response = await fetch(API_ENDPOINTS.repos);
            if (!response.ok) throw new Error('Failed to fetch labs');
            return await response.json();
        } catch (error) {
            console.error('Failed to load labs:', error);
            throw error;
        }
    },

    async addRepository(gitUrl) {
        try {
            const response = await fetch(API_ENDPOINTS.repos, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: gitUrl })
            });
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to add repository');
            }
            return await response.json();
        } catch (error) {
            console.error('Failed to add repository:', error);
            throw error;
        }
    },

    async updateRepository(labId) {
        try {
            const response = await fetch(API_ENDPOINTS.repo(labId), {
                method: 'PUT'
            });
            if (!response.ok) throw new Error('Failed to update repository');
            return await response.json();
        } catch (error) {
            console.error('Failed to update repository:', error);
            throw error;
        }
    },

    async deleteRepository(labId) {
        try {
            const response = await fetch(API_ENDPOINTS.repo(labId), {
                method: 'DELETE'
            });
            if (!response.ok) throw new Error('Failed to delete repository');
            return await response.json();
        } catch (error) {
            console.error('Failed to delete repository:', error);
            throw error;
        }
    },

    // Deployment management
    async getDeployments() {
        try {
            const response = await fetch(API_ENDPOINTS.deployments);
            if (!response.ok) throw new Error('Failed to fetch deployments');
            return await response.json();
        } catch (error) {
            console.error('Failed to load deployments:', error);
            throw error;
        }
    },

    async deployLab(labId, version = 'latest', allocateIps = false) {
        try {
            const response = await fetch(API_ENDPOINTS.deploy(labId), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    version: version,
                    allocate_ips: allocateIps
                })
            });
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to deploy lab');
            }
            return await response.json();
        } catch (error) {
            console.error('Failed to deploy lab:', error);
            throw error;
        }
    },

    async destroyLab(labId) {
        try {
            const response = await fetch(API_ENDPOINTS.destroy(labId), {
                method: 'POST'
            });
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to destroy lab');
            }
            return await response.json();
        } catch (error) {
            console.error('Failed to destroy lab:', error);
            throw error;
        }
    },

    // Configuration scenarios
    async getScenarios(labId) {
        try {
            const response = await fetch(API_ENDPOINTS.scenarios(labId));
            if (!response.ok) throw new Error('Failed to fetch scenarios');
            return await response.json();
        } catch (error) {
            console.error('Failed to load scenarios:', error);
            throw error;
        }
    },

    async applyScenario(labId, scenario) {
        try {
            const response = await fetch(API_ENDPOINTS.applyScenario(labId, scenario), {
                method: 'POST'
            });
            if (!response.ok) throw new Error('Failed to apply scenario');
            return await response.json();
        } catch (error) {
            console.error('Failed to apply scenario:', error);
            throw error;
        }
    },

    // Logs and tasks
    async getLogs(labId) {
        try {
            const response = await fetch(API_ENDPOINTS.logs(labId));
            if (!response.ok) throw new Error('Failed to fetch logs');
            return await response.text();
        } catch (error) {
            console.error('Failed to load logs:', error);
            throw error;
        }
    },

    async getTaskStatus(taskId) {
        try {
            const response = await fetch(API_ENDPOINTS.tasks(taskId));
            if (!response.ok) throw new Error('Failed to fetch task status');
            return await response.json();
        } catch (error) {
            console.error('Failed to get task status:', error);
            throw error;
        }
    },

    // System
    async getHealth() {
        try {
            const response = await fetch(API_ENDPOINTS.health);
            if (!response.ok) throw new Error('Failed to fetch health status');
            return await response.json();
        } catch (error) {
            console.error('Failed to get health status:', error);
            throw error;
        }
    },

    async validateNetbox() {
        try {
            const response = await fetch(API_ENDPOINTS.netbox);
            if (!response.ok) throw new Error('Failed to validate NetBox');
            return await response.json();
        } catch (error) {
            console.error('Failed to validate NetBox:', error);
            throw error;
        }
    }
};