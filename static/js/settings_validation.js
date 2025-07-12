// Settings Validation JavaScript - Form Validation & Data Integrity
class SettingsValidation {
    constructor() {
        this.validationRules = {
            displayName: {
                minLength: 2,
                maxLength: 50,
                pattern: /^[a-zA-Z0-9\s\-_]+$/,
                required: true
            },
            emailAddress: {
                pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                required: true
            },
            preferredLanguage: {
                required: true,
                validOptions: [
                    'EN', 'EN-US', 'EN-GB', 'ES', 'ES-419', 'FR', 'DE', 'IT', 'PT', 'PT-BR', 'PT-PT',
                    'RU', 'JA', 'KO', 'ZH', 'ZH-HANS', 'ZH-HANT', 'AR', 'BG', 'CS', 'DA', 'NL',
                    'ET', 'FI', 'EL', 'HU', 'LV', 'LT', 'NB', 'PL', 'RO', 'SK', 'SL', 'SV', 'TR',
                    'UK', 'ID', 'HE', 'TH', 'VI'
                ]
            },
            profileVisibility: {
                required: true,
                validOptions: ['public', 'friends', 'private']
            }
        };
        
        this.init();
    }

    init() {
        this.setupRealTimeValidation();
        this.setupFormValidation();
    }

    setupRealTimeValidation() {
        // Add real-time validation for input fields
        const validatedFields = ['displayName', 'emailAddress'];
        
        validatedFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.addEventListener('blur', (e) => {
                    this.validateField(fieldId, e.target.value);
                });
                
                field.addEventListener('input', (e) => {
                    this.clearFieldError(fieldId);
                    // Debounced validation
                    clearTimeout(this.validationTimeout);
                    this.validationTimeout = setTimeout(() => {
                        this.validateField(fieldId, e.target.value, true);
                    }, 500);
                });
            }
        });

        // Validate select fields on change
        const selectFields = ['preferredLanguage', 'profileVisibility'];
        selectFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.addEventListener('change', (e) => {
                    this.validateField(fieldId, e.target.value);
                });
            }
        });
    }

    setupFormValidation() {
        // Override the save function to include validation
        const originalSaveSettings = window.settingsCore.saveSettings;
        window.settingsCore.saveSettings = async () => {
            if (this.validateAllFields()) {
                await originalSaveSettings.call(window.settingsCore);
            } else {
                window.settingsCore.announceToScreenReader('Please fix validation errors before saving');
            }
        };
    }

    validateField(fieldId, value, silent = false) {
        const rules = this.validationRules[fieldId];
        if (!rules) return true;

        const errors = [];

        // Required field validation
        if (rules.required && (!value || value.trim() === '')) {
            errors.push('This field is required');
        }

        // Only validate further if field has content
        if (value && value.trim() !== '') {
            // Length validation
            if (rules.minLength && value.length < rules.minLength) {
                errors.push(`Must be at least ${rules.minLength} characters`);
            }
            
            if (rules.maxLength && value.length > rules.maxLength) {
                errors.push(`Must be no more than ${rules.maxLength} characters`);
            }

            // Pattern validation
            if (rules.pattern && !rules.pattern.test(value)) {
                errors.push(this.getPatternErrorMessage(fieldId));
            }

            // Valid options validation
            if (rules.validOptions && !rules.validOptions.includes(value)) {
                errors.push('Please select a valid option');
            }
        }

        if (errors.length > 0 && !silent) {
            this.showFieldError(fieldId, errors[0]);
            return false;
        } else {
            this.clearFieldError(fieldId);
            return true;
        }
    }

    getPatternErrorMessage(fieldId) {
        const messages = {
            displayName: 'Display name can only contain letters, numbers, spaces, hyphens, and underscores',
            emailAddress: 'Please enter a valid email address'
        };
        return messages[fieldId] || 'Invalid format';
    }

    showFieldError(fieldId, message) {
        this.clearFieldError(fieldId);
        
        const field = document.getElementById(fieldId);
        if (!field) return;

        // Create error element
        const errorElement = document.createElement('div');
        errorElement.id = `${fieldId}-error`;
        errorElement.className = 'text-red-400 text-sm mt-1';
        errorElement.textContent = message;
        errorElement.setAttribute('role', 'alert');

        // Add error styling to field
        field.classList.add('border-red-500', 'bg-red-900', 'bg-opacity-20');
        field.setAttribute('aria-invalid', 'true');
        field.setAttribute('aria-describedby', `${fieldId}-error`);

        // Insert error message after field
        field.parentNode.insertBefore(errorElement, field.nextSibling);

        // Announce error to screen readers
        window.settingsCore.announceToScreenReader(`${this.getFieldLabel(fieldId)}: ${message}`);
    }

    clearFieldError(fieldId) {
        const field = document.getElementById(fieldId);
        const errorElement = document.getElementById(`${fieldId}-error`);
        
        if (field) {
            field.classList.remove('border-red-500', 'bg-red-900', 'bg-opacity-20');
            field.removeAttribute('aria-invalid');
            field.removeAttribute('aria-describedby');
        }
        
        if (errorElement) {
            errorElement.remove();
        }
    }

    getFieldLabel(fieldId) {
        const labelMap = {
            displayName: 'Display Name',
            emailAddress: 'Email Address',
            preferredLanguage: 'Preferred Language',
            profileVisibility: 'Profile Visibility'
        };
        return labelMap[fieldId] || fieldId;
    }

    validateAllFields() {
        let isValid = true;
        const fieldsToValidate = Object.keys(this.validationRules);

        fieldsToValidate.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                const fieldValid = this.validateField(fieldId, field.value);
                if (!fieldValid) {
                    isValid = false;
                }
            }
        });

        // Focus first invalid field
        if (!isValid) {
            const firstError = document.querySelector('[aria-invalid="true"]');
            if (firstError) {
                firstError.focus();
            }
        }

        return isValid;
    }

    // Settings-specific validation
    validateLanguageSettings(settings) {
        const errors = [];

        // Check if preferred language is supported
        if (!this.validationRules.preferredLanguage.validOptions.includes(settings.preferredLanguage)) {
            errors.push('Selected language is not supported');
        }

        // Validate auto-translate logic
        if (!settings.autoTranslate && settings.showOriginal) {
            errors.push('Show original text requires auto-translate to be enabled');
        }

        return {
            isValid: errors.length === 0,
            errors
        };
    }

    validateAccessibilitySettings(settings) {
        const errors = [];

        // Check for conflicting settings
        if (settings.highContrast && settings.reduceMotion && settings.largeText) {
            // This is actually fine, just a note
        }

        // Validate screen reader mode dependencies
        if (settings.screenReaderMode && !settings.keyboardHelp) {
            // Recommend enabling keyboard help with screen reader
            errors.push('Consider enabling keyboard help with screen reader mode for better navigation');
        }

        return {
            isValid: errors.length === 0,
            errors,
            warnings: errors // In this case, these are warnings, not blocking errors
        };
    }

    validatePrivacySettings(settings) {
        const errors = [];

        // Check privacy consistency
        if (settings.profileVisibility === 'private' && settings.dataAnalytics) {
            errors.push('Private profile with data analytics enabled may reduce privacy');
        }

        return {
            isValid: errors.length === 0,
            errors
        };
    }

    validateNotificationSettings(settings) {
        const errors = [];

        // Check notification logic
        if (!settings.messageNotifications && settings.soundNotifications) {
            errors.push('Sound notifications require message notifications to be enabled');
        }

        if (!settings.messageNotifications && settings.translationAlerts) {
            errors.push('Translation alerts require message notifications to be enabled');
        }

        return {
            isValid: errors.length === 0,
            errors
        };
    }

    // Comprehensive settings validation
    validateCompleteSettings(settingsData) {
        const validationResults = {
            isValid: true,
            errors: [],
            warnings: []
        };

        // Validate each category
        const languageValidation = this.validateLanguageSettings(settingsData.language);
        const accessibilityValidation = this.validateAccessibilitySettings(settingsData.accessibility);
        const privacyValidation = this.validatePrivacySettings(settingsData.privacy);
        const notificationValidation = this.validateNotificationSettings(settingsData.notifications);

        // Collect all errors
        [languageValidation, accessibilityValidation, privacyValidation, notificationValidation].forEach(result => {
            if (!result.isValid) {
                validationResults.isValid = false;
                validationResults.errors.push(...result.errors);
            }
            if (result.warnings) {
                validationResults.warnings.push(...result.warnings);
            }
        });

        return validationResults;
    }

    // Sanitization methods
    sanitizeDisplayName(value) {
        return value.trim().replace(/[<>]/g, '');
    }

    sanitizeEmail(value) {
        return value.trim().toLowerCase();
    }

    sanitizeSettings(settingsData) {
        const sanitized = { ...settingsData };

        // Sanitize account data
        if (sanitized.account) {
            if (sanitized.account.displayName) {
                sanitized.account.displayName = this.sanitizeDisplayName(sanitized.account.displayName);
            }
            if (sanitized.account.emailAddress) {
                sanitized.account.emailAddress = this.sanitizeEmail(sanitized.account.emailAddress);
            }
        }

        return sanitized;
    }

    // Show validation summary
    showValidationSummary(validationResult) {
        if (!validationResult.isValid) {
            const message = `Settings validation failed: ${validationResult.errors.join(', ')}`;
            window.settingsCore.announceToScreenReader(message);
        }

        if (validationResult.warnings && validationResult.warnings.length > 0) {
            const warningMessage = `Settings warnings: ${validationResult.warnings.join(', ')}`;
            console.warn(warningMessage);
        }
    }

    // Public API methods
    isValid() {
        return this.validateAllFields();
    }

    getFieldValue(fieldId) {
        const field = document.getElementById(fieldId);
        return field ? field.value : '';
    }

    setFieldValue(fieldId, value) {
        const field = document.getElementById(fieldId);
        if (field) {
            field.value = value;
            this.validateField(fieldId, value);
        }
    }
}

// Initialize global instance
window.settingsValidation = new SettingsValidation();