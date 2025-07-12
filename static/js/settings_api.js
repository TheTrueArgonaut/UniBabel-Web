// Settings API JavaScript - Backend Communication & Data Management
class SettingsAPI {
    constructor() {
        this.baseUrl = '/api/user/settings';
    }

    async saveSettings(settingsData) {
        try {
            const response = await fetch(this.baseUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(settingsData)
            });

            const data = await response.json();

            if (response.ok) {
                return { success: true, data };
            } else {
                return { success: false, error: data.error || 'Failed to save settings' };
            }
        } catch (error) {
            console.error('Error saving settings:', error);
            return { success: false, error: 'Network error while saving settings' };
        }
    }

    async loadSettings() {
        try {
            const response = await fetch(this.baseUrl);
            const data = await response.json();

            if (response.ok) {
                return { success: true, settings: data };
            } else {
                return { success: false, error: data.error || 'Failed to load settings' };
            }
        } catch (error) {
            console.error('Error loading settings:', error);
            return { success: false, error: 'Network error while loading settings' };
        }
    }

    async resetSettings() {
        try {
            const response = await fetch(`${this.baseUrl}/reset`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const data = await response.json();

            if (response.ok) {
                return { success: true, data };
            } else {
                return { success: false, error: data.error || 'Failed to reset settings' };
            }
        } catch (error) {
            console.error('Error resetting settings:', error);
            return { success: false, error: 'Network error while resetting settings' };
        }
    }

    async exportSettings() {
        try {
            const response = await fetch(`${this.baseUrl}/export`);
            const data = await response.json();

            if (response.ok) {
                return { success: true, settings: data };
            } else {
                return { success: false, error: data.error || 'Failed to export settings' };
            }
        } catch (error) {
            console.error('Error exporting settings:', error);
            return { success: false, error: 'Network error while exporting settings' };
        }
    }

    async importSettings(settingsData) {
        try {
            const response = await fetch(`${this.baseUrl}/import`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(settingsData)
            });

            const data = await response.json();

            if (response.ok) {
                return { success: true, data };
            } else {
                return { success: false, error: data.error || 'Failed to import settings' };
            }
        } catch (error) {
            console.error('Error importing settings:', error);
            return { success: false, error: 'Network error while importing settings' };
        }
    }

    async updateProfile(profileData) {
        try {
            const response = await fetch('/api/user/profile', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(profileData)
            });

            const data = await response.json();

            if (response.ok) {
                return { success: true, data };
            } else {
                return { success: false, error: data.error || 'Failed to update profile' };
            }
        } catch (error) {
            console.error('Error updating profile:', error);
            return { success: false, error: 'Network error while updating profile' };
        }
    }

    async validateSettings(settingsData) {
        try {
            const response = await fetch(`${this.baseUrl}/validate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(settingsData)
            });

            const data = await response.json();

            if (response.ok) {
                return { success: true, validation: data };
            } else {
                return { success: false, error: data.error || 'Validation failed' };
            }
        } catch (error) {
            console.error('Error validating settings:', error);
            return { success: false, error: 'Network error while validating settings' };
        }
    }
}

// Initialize global instance
window.settingsApi = new SettingsAPI();