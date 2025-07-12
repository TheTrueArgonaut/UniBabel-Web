// Settings Core JavaScript - State Management & Initialization
class SettingsCore {
    constructor() {
        this.settings = {
            accessibility: {},
            language: {},
            privacy: {},
            notifications: {},
            account: {}
        };
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadSettings();
        this.detectSystemPreferences();
    }

    setupEventListeners() {
        document.addEventListener('DOMContentLoaded', () => {
            this.bindUIEvents();
            this.setupKeyboardShortcuts();
            this.announceToScreenReader('Settings page loaded. Use keyboard navigation to adjust your preferences.');
        });

        // Real-time setting changes
        document.addEventListener('change', (e) => {
            if (e.target.type === 'checkbox') {
                this.handleCheckboxChange(e);
            }
        });
    }

    bindUIEvents() {
        // Bind save button
        const saveButton = document.querySelector('.btn[onclick="saveSettings()"]');
        if (saveButton) {
            saveButton.onclick = () => this.saveSettings();
        }

        // Bind 2FA setup
        window.setup2FA = () => this.setup2FA();
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+S to save settings
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                this.saveSettings();
            }

            // Escape to focus back button
            if (e.key === 'Escape') {
                const backButton = document.querySelector('.btn-secondary');
                if (backButton) {
                    backButton.focus();
                }
            }
        });
    }

    detectSystemPreferences() {
        // High contrast mode detection
        if (window.matchMedia('(prefers-contrast: high)').matches) {
            document.body.classList.add('high-contrast');
        }

        // Reduced motion detection
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            document.body.classList.add('reduce-motion');
        }
    }

    loadSettings() {
        try {
            // Load accessibility settings
            this.settings = {
                screenReaderMode: localStorage.getItem('screen-reader-mode') === 'true',
                highContrast: localStorage.getItem('high-contrast') === 'true',
                reduceMotion: localStorage.getItem('reduce-motion') === 'true',
                largeText: localStorage.getItem('large-text') === 'true',
                keyboardHelp: localStorage.getItem('keyboard-help') === 'true',
                autoTranslate: localStorage.getItem('auto-translate') !== 'false',
                showOriginal: localStorage.getItem('show-original') !== 'false',
                dataAnalytics: localStorage.getItem('data-analytics') !== 'false',
                readReceipts: localStorage.getItem('read-receipts') !== 'false',
                messageNotifications: localStorage.getItem('message-notifications') !== 'false',
                soundNotifications: localStorage.getItem('sound-notifications') !== 'false',
                translationAlerts: localStorage.getItem('translation-alerts') === 'true'
            };

            // Apply settings to checkboxes
            Object.keys(this.settings).forEach(key => {
                const element = document.getElementById(key);
                if (element && element.type === 'checkbox') {
                    element.checked = this.settings[key];
                }
            });

            // Apply theme settings immediately
            this.applyThemeSettings();

            // Load premium status
            window.settingsPremium.loadPremiumStatus();

            this.announceToScreenReader('Settings loaded successfully');

        } catch (error) {
            console.error('Error loading settings:', error);
            this.announceToScreenReader('Error loading settings');
        }
    }

    applyThemeSettings() {
        if (this.settings.highContrast) {
            document.body.classList.add('high-contrast');
        }
        if (this.settings.largeText) {
            document.body.classList.add('large-text');
        }
        if (this.settings.reduceMotion) {
            document.body.classList.add('reduce-motion');
        }
    }

    handleCheckboxChange(e) {
        const settingName = e.target.id;
        const isEnabled = e.target.checked;

        // Apply immediately for accessibility settings
        switch (settingName) {
            case 'highContrast':
                if (isEnabled) {
                    document.body.classList.add('high-contrast');
                    this.announceToScreenReader('High contrast mode enabled');
                } else {
                    document.body.classList.remove('high-contrast');
                    this.announceToScreenReader('High contrast mode disabled');
                }
                break;

            case 'largeText':
                if (isEnabled) {
                    document.body.classList.add('large-text');
                    this.announceToScreenReader('Large text mode enabled');
                } else {
                    document.body.classList.remove('large-text');
                    this.announceToScreenReader('Large text mode disabled');
                }
                break;

            case 'reduceMotion':
                if (isEnabled) {
                    document.body.classList.add('reduce-motion');
                    this.announceToScreenReader('Reduced motion enabled');
                } else {
                    document.body.classList.remove('reduce-motion');
                    this.announceToScreenReader('Reduced motion disabled');
                }
                break;

            case 'screenReaderMode':
                this.announceToScreenReader(isEnabled ? 'Screen reader mode enabled' : 'Screen reader mode disabled');
                break;
        }

        // Store in localStorage immediately
        localStorage.setItem(this.camelToKebab(settingName), isEnabled);
    }

    async saveSettings() {
        try {
            const settings = this.collectAllSettings();

            // Save to localStorage
            Object.keys(settings).forEach(key => {
                localStorage.setItem(key, settings[key]);
            });

            // Apply settings immediately
            this.applySettings(settings);

            // Send to server
            const result = await window.settingsApi.saveSettings(this.formatSettingsForAPI(settings));
            
            if (result.success) {
                this.showSaveSuccess();
            } else {
                throw new Error(result.error || 'Failed to save settings');
            }

        } catch (error) {
            console.error('Error saving settings:', error);
            this.announceToScreenReader('Error saving settings');
        }
    }

    collectAllSettings() {
        return {
            'screen-reader-mode': this.getCheckboxValue('screenReaderMode'),
            'high-contrast': this.getCheckboxValue('highContrast'),
            'reduce-motion': this.getCheckboxValue('reduceMotion'),
            'large-text': this.getCheckboxValue('largeText'),
            'keyboard-help': this.getCheckboxValue('keyboardHelp'),
            'auto-translate': this.getCheckboxValue('autoTranslate'),
            'show-original': this.getCheckboxValue('showOriginal'),
            'data-analytics': this.getCheckboxValue('dataAnalytics'),
            'read-receipts': this.getCheckboxValue('readReceipts'),
            'message-notifications': this.getCheckboxValue('messageNotifications'),
            'sound-notifications': this.getCheckboxValue('soundNotifications'),
            'translation-alerts': this.getCheckboxValue('translationAlerts'),
            'preferred-language': this.getSelectValue('preferredLanguage'),
            'profile-visibility': this.getSelectValue('profileVisibility')
        };
    }

    formatSettingsForAPI(settings) {
        return {
            accessibility: {
                screenReaderMode: settings['screen-reader-mode'],
                highContrast: settings['high-contrast'],
                reduceMotion: settings['reduce-motion'],
                largeText: settings['large-text'],
                keyboardHelp: settings['keyboard-help']
            },
            language: {
                preferredLanguage: settings['preferred-language'],
                autoTranslate: settings['auto-translate'],
                showOriginal: settings['show-original']
            },
            privacy: {
                profileVisibility: settings['profile-visibility'],
                dataAnalytics: settings['data-analytics'],
                readReceipts: settings['read-receipts']
            },
            notifications: {
                messageNotifications: settings['message-notifications'],
                soundNotifications: settings['sound-notifications'],
                translationAlerts: settings['translation-alerts']
            },
            account: {
                displayName: this.getInputValue('displayName'),
                emailAddress: this.getInputValue('emailAddress')
            }
        };
    }

    applySettings(settings) {
        // High contrast
        if (settings['high-contrast']) {
            document.body.classList.add('high-contrast');
        } else {
            document.body.classList.remove('high-contrast');
        }

        // Large text
        if (settings['large-text']) {
            document.body.classList.add('large-text');
        } else {
            document.body.classList.remove('large-text');
        }

        // Reduced motion
        if (settings['reduce-motion']) {
            document.body.classList.add('reduce-motion');
        } else {
            document.body.classList.remove('reduce-motion');
        }
    }

    showSaveSuccess() {
        this.announceToScreenReader('Settings saved successfully');

        // Show success message
        const saveButton = document.querySelector('.btn[onclick="saveSettings()"]');
        if (saveButton) {
            const originalHTML = saveButton.innerHTML;
            const originalStyle = saveButton.style.background;
            
            saveButton.innerHTML = '<i class="ri-check-line mr-2" aria-hidden="true"></i>Saved!';
            saveButton.style.background = 'linear-gradient(45deg, #10b981, #059669)';

            setTimeout(() => {
                saveButton.innerHTML = originalHTML;
                saveButton.style.background = originalStyle;
            }, 2000);
        }
    }

    setup2FA() {
        this.announceToScreenReader('Two-factor authentication setup not yet implemented');
        alert('Two-factor authentication setup will be available in a future update.');
    }

    // Utility methods
    getCheckboxValue(id) {
        const element = document.getElementById(id);
        return element ? element.checked : false;
    }

    getSelectValue(id) {
        const element = document.getElementById(id);
        return element ? element.value : '';
    }

    getInputValue(id) {
        const element = document.getElementById(id);
        return element ? element.value : '';
    }

    camelToKebab(str) {
        return str.replace(/([a-z0-9]|(?=[A-Z]))([A-Z])/g, '$1-$2').toLowerCase();
    }

    announceToScreenReader(message) {
        const announcements = document.getElementById('announcements');
        if (announcements) {
            announcements.textContent = message;
            setTimeout(() => announcements.textContent = '', 3000);
        }
    }

    refreshSettings() {
        this.loadSettings();
    }

    resetToDefaults() {
        const confirmed = confirm('Reset all settings to default values? This cannot be undone.');
        if (confirmed) {
            localStorage.clear();
            location.reload();
        }
    }
}

// Initialize global instance
window.settingsCore = new SettingsCore();