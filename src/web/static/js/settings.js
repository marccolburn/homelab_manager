// Settings page functionality

class SettingsManager {
    constructor() {
        this.api = new APIClient();
        this.form = document.getElementById('settingsForm');
        this.testBtn = document.getElementById('testConnectionBtn');
        this.alertContainer = document.getElementById('alertContainer');
        this.testResults = document.getElementById('connectionTestResults');
        
        this.bindEvents();
        this.loadSettings();
    }

    bindEvents() {
        // Form submission
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveSettings();
        });

        // Test connection button
        this.testBtn.addEventListener('click', () => {
            this.testConnection();
        });

        // NetBox toggle
        const netboxEnabled = document.getElementById('netboxEnabled');
        netboxEnabled.addEventListener('change', () => {
            this.toggleNetBoxFields(netboxEnabled.checked);
        });
    }

    async loadSettings() {
        try {
            this.showAlert('Loading settings...', 'info');
            const settings = await this.api.getSettings();
            this.populateForm(settings);
            this.clearAlert();
        } catch (error) {
            this.showAlert(`Failed to load settings: ${error.message}`, 'error');
        }
    }

    populateForm(settings) {
        // clab-tools password
        if (settings.clab_tools_password && settings.clab_tools_password !== '****') {
            document.getElementById('clabToolsPassword').placeholder = 'Password configured';
        }

        // Remote credentials
        if (settings.remote_credentials) {
            const creds = settings.remote_credentials;
            if (creds.ssh_password && creds.ssh_password !== '****') {
                document.getElementById('sshPassword').placeholder = 'Password configured';
            }
            if (creds.sudo_password && creds.sudo_password !== '****') {
                document.getElementById('sudoPassword').placeholder = 'Password configured';
            }
        }

        // NetBox settings
        if (settings.netbox) {
            const netbox = settings.netbox;
            document.getElementById('netboxEnabled').checked = netbox.enabled || false;
            document.getElementById('netboxUrl').value = netbox.url || '';
            if (netbox.token && netbox.token !== '****') {
                document.getElementById('netboxToken').placeholder = 'Token configured';
            }
            document.getElementById('netboxPrefix').value = netbox.default_prefix || '10.100.100.0/24';
            this.toggleNetBoxFields(netbox.enabled || false);
        }

        // Monitoring settings
        if (settings.monitoring) {
            const monitoring = settings.monitoring;
            document.getElementById('prometheusUrl').value = monitoring.prometheus || 'http://localhost:9090';
            document.getElementById('grafanaUrl').value = monitoring.grafana || 'http://localhost:3000';
        }
    }

    toggleNetBoxFields(enabled) {
        const groups = ['netboxUrlGroup', 'netboxTokenGroup', 'netboxPrefixGroup'];
        groups.forEach(groupId => {
            const group = document.getElementById(groupId);
            if (group) {
                group.style.display = enabled ? 'block' : 'none';
            }
        });
    }

    async saveSettings() {
        try {
            this.showAlert('Saving settings...', 'info');
            
            const formData = new FormData(this.form);
            const settings = this.buildSettingsObject(formData);
            
            await this.api.updateSettings(settings);
            this.showAlert('Settings saved successfully! 💾', 'success');
            
            // Reload settings to get updated placeholders
            setTimeout(() => this.loadSettings(), 1000);
            
        } catch (error) {
            this.showAlert(`Failed to save settings: ${error.message}`, 'error');
        }
    }

    buildSettingsObject(formData) {
        const settings = {};

        // clab-tools password
        const clabPassword = formData.get('clab_tools_password');
        if (clabPassword && clabPassword.trim()) {
            settings.clab_tools_password = clabPassword.trim();
        }

        // Remote credentials
        const sshPassword = formData.get('ssh_password');
        const sudoPassword = formData.get('sudo_password');
        if ((sshPassword && sshPassword.trim()) || (sudoPassword && sudoPassword.trim())) {
            settings.remote_credentials = {};
            if (sshPassword && sshPassword.trim()) {
                settings.remote_credentials.ssh_password = sshPassword.trim();
            }
            if (sudoPassword && sudoPassword.trim()) {
                settings.remote_credentials.sudo_password = sudoPassword.trim();
            }
        }

        // NetBox settings
        const netboxEnabled = formData.get('netbox_enabled') === 'on';
        if (netboxEnabled) {
            settings.netbox = {
                enabled: true,
                url: formData.get('netbox_url') || '',
                default_prefix: formData.get('netbox_prefix') || '10.100.100.0/24'
            };
            
            const netboxToken = formData.get('netbox_token');
            if (netboxToken && netboxToken.trim()) {
                settings.netbox.token = netboxToken.trim();
            }
        } else {
            settings.netbox = { enabled: false };
        }

        // Monitoring settings
        const prometheusUrl = formData.get('prometheus_url');
        const grafanaUrl = formData.get('grafana_url');
        if (prometheusUrl || grafanaUrl) {
            settings.monitoring = {};
            if (prometheusUrl) settings.monitoring.prometheus = prometheusUrl;
            if (grafanaUrl) settings.monitoring.grafana = grafanaUrl;
        }

        return settings;
    }

    async testConnection() {
        try {
            this.testBtn.disabled = true;
            this.testBtn.textContent = '🔄 Testing...';
            this.showAlert('Testing connections...', 'info');
            
            const results = await this.api.testConnections();
            this.displayTestResults(results);
            this.showAlert('Connection test completed', 'success');
            
        } catch (error) {
            this.showAlert(`Connection test failed: ${error.message}`, 'error');
        } finally {
            this.testBtn.disabled = false;
            this.testBtn.textContent = '🔍 Test Connection';
        }
    }

    displayTestResults(results) {
        const content = document.getElementById('testResultsContent');
        
        if (!results || Object.keys(results).length === 0) {
            content.innerHTML = '<p>No test results available.</p>';
            this.testResults.style.display = 'block';
            return;
        }

        const html = Object.entries(results).map(([test, result]) => {
            const status = result.success ? 'success' : 'error';
            const icon = result.success ? '✅' : '❌';
            
            return `
                <div class="test-item">
                    <span class="test-status ${status}">${icon} ${test}</span>
                    <div class="test-details">${result.message || ''}</div>
                </div>
            `;
        }).join('');

        content.innerHTML = html;
        this.testResults.style.display = 'block';
    }

    showAlert(message, type = 'info') {
        this.clearAlert();
        
        const icons = {
            success: '✅',
            error: '❌',
            info: 'ℹ️'
        };
        
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.innerHTML = `
            <span>${icons[type] || ''}  ${message}</span>
        `;
        
        this.alertContainer.appendChild(alert);
        
        // Auto-hide success and info alerts
        if (type === 'success' || type === 'info') {
            setTimeout(() => this.clearAlert(), 5000);
        }
    }

    clearAlert() {
        this.alertContainer.innerHTML = '';
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    new SettingsManager();
});