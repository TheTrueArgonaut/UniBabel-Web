/**
 * 🎯 REGISTER VALIDATION MICROSERVICE - Single Responsibility: Form validation & UX feedback
 * 
 * SRIMI Principles:
 * - Single Responsibility: ONLY handles form validation and user feedback
 * - Reactive: Real-time validation as user types
 * - Injectable: Can be used across different forms
 * - Micro: Focused validation logic
 * - Interfaces: Clear validation contracts
 */

class UsernameValidationService {
    constructor() {
        this.validationRules = {
            minLength: 3,
            maxLength: 20,
            pattern: /^[a-zA-Z0-9_]+$/,
            checkAvailability: true
        };
        
        this.validationCache = new Map();
        this.debounceTimers = new Map();
    }
    
    async validate(username, forceCheck = false) {
        const input = document.getElementById('username');
        const feedback = document.getElementById('username-feedback');
        
        // Basic validation
        if (!username) {
            this.setFieldState('username', 'neutral', '');
            return false;
        }
        
        if (username.length < this.validationRules.minLength) {
            this.setFieldState('username', 'invalid', `Username must be at least ${this.validationRules.minLength} characters`);
            return false;
        }
        
        if (username.length > this.validationRules.maxLength) {
            this.setFieldState('username', 'invalid', `Username must be no more than ${this.validationRules.maxLength} characters`);
            return false;
        }
        
        if (!this.validationRules.pattern.test(username)) {
            this.setFieldState('username', 'invalid', 'Username can only contain letters, numbers, and underscores');
            return false;
        }
        
        // Check availability
        if (forceCheck || !this.validationCache.has(`username:${username}`)) {
            this.setFieldState('username', 'checking', 'Checking availability...');
            
            try {
                const result = await window.registerAPI.checkAvailability('/api/check-username', { username });
                
                if (result.error) {
                    this.setFieldState('username', 'invalid', result.message || 'Unable to check username availability');
                    return false;
                }
                
                if (result.available) {
                    this.validationCache.set(`username:${username}`, true);
                    this.setFieldState('username', 'valid', `✓ Username "${username}" is available`);
                    return true;
                } else {
                    this.validationCache.set(`username:${username}`, false);
                    this.setFieldState('username', 'invalid', `Username "${username}" is already taken`);
                    return false;
                }
            } catch (error) {
                this.setFieldState('username', 'invalid', 'Unable to check username availability');
                return false;
            }
        } else {
            const isAvailable = this.validationCache.get(`username:${username}`);
            if (isAvailable) {
                this.setFieldState('username', 'valid', `✓ Username "${username}" is available`);
                return true;
            } else {
                this.setFieldState('username', 'invalid', `Username "${username}" is already taken`);
                return false;
            }
        }
    }
    
    setFieldState(fieldName, state, message) {
        const input = document.getElementById(fieldName.replace('-', '_'));
        const feedback = document.getElementById(`${fieldName}-feedback`);
        const loadingIcon = document.getElementById(`${fieldName}-loading`);
        const successIcon = document.getElementById(`${fieldName}-success`);
        const errorIcon = document.getElementById(`${fieldName}-error`);
        
        if (!input || !feedback) return;
        
        // Reset states
        input.classList.remove('valid', 'invalid', 'checking');
        feedback.classList.remove('success', 'error', 'checking');
        
        // Hide all icons
        if (loadingIcon) loadingIcon.classList.add('hidden');
        if (successIcon) successIcon.classList.add('hidden');
        if (errorIcon) errorIcon.classList.add('hidden');
        
        // Apply new state
        switch (state) {
            case 'valid':
                input.classList.add('valid');
                feedback.classList.add('success');
                if (successIcon) successIcon.classList.remove('hidden');
                break;
            case 'invalid':
                input.classList.add('invalid');
                feedback.classList.add('error');
                if (errorIcon) errorIcon.classList.remove('hidden');
                break;
            case 'checking':
                input.classList.add('checking');
                feedback.classList.add('checking');
                if (loadingIcon) loadingIcon.classList.remove('hidden');
                break;
            case 'neutral':
            default:
                // Keep neutral state
                break;
        }
        
        feedback.textContent = message;
    }
}

class EmailValidationService {
    constructor() {
        this.validationRules = {
            pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
            checkAvailability: true
        };
        
        this.validationCache = new Map();
        this.debounceTimers = new Map();
    }
    
    async validate(email, forceCheck = false) {
        const input = document.getElementById('email');
        const feedback = document.getElementById('email-feedback');
        
        if (!email) {
            this.setFieldState('email', 'neutral', '');
            return false;
        }
        
        if (!this.validationRules.pattern.test(email)) {
            this.setFieldState('email', 'invalid', 'Please enter a valid email address');
            return false;
        }
        
        // Check availability
        if (forceCheck || !this.validationCache.has(`email:${email}`)) {
            this.setFieldState('email', 'checking', 'Checking email availability...');
            
            try {
                const result = await window.registerAPI.checkAvailability('/api/check-email', { email });
                
                if (result.error) {
                    this.setFieldState('email', 'invalid', result.message || 'Unable to check email availability');
                    return false;
                }
                
                if (result.available) {
                    this.validationCache.set(`email:${email}`, true);
                    this.setFieldState('email', 'valid', '✓ Email is available');
                    return true;
                } else {
                    this.validationCache.set(`email:${email}`, false);
                    this.setFieldState('email', 'invalid', 'This email is already registered');
                    return false;
                }
            } catch (error) {
                this.setFieldState('email', 'invalid', 'Unable to check email availability');
                return false;
            }
        } else {
            const isAvailable = this.validationCache.get(`email:${email}`);
            if (isAvailable) {
                this.setFieldState('email', 'valid', '✓ Email is available');
                return true;
            } else {
                this.setFieldState('email', 'invalid', 'This email is already registered');
                return false;
            }
        }
    }
    
    setFieldState(fieldName, state, message) {
        const input = document.getElementById(fieldName.replace('-', '_'));
        const feedback = document.getElementById(`${fieldName}-feedback`);
        const loadingIcon = document.getElementById(`${fieldName}-loading`);
        const successIcon = document.getElementById(`${fieldName}-success`);
        const errorIcon = document.getElementById(`${fieldName}-error`);
        
        if (!input || !feedback) return;
        
        // Reset states
        input.classList.remove('valid', 'invalid', 'checking');
        feedback.classList.remove('success', 'error', 'checking');
        
        // Hide all icons
        if (loadingIcon) loadingIcon.classList.add('hidden');
        if (successIcon) successIcon.classList.add('hidden');
        if (errorIcon) errorIcon.classList.add('hidden');
        
        // Apply new state
        switch (state) {
            case 'valid':
                input.classList.add('valid');
                feedback.classList.add('success');
                if (successIcon) successIcon.classList.remove('hidden');
                break;
            case 'invalid':
                input.classList.add('invalid');
                feedback.classList.add('error');
                if (errorIcon) errorIcon.classList.remove('hidden');
                break;
            case 'checking':
                input.classList.add('checking');
                feedback.classList.add('checking');
                if (loadingIcon) loadingIcon.classList.remove('hidden');
                break;
            case 'neutral':
            default:
                // Keep neutral state
                break;
        }
        
        feedback.textContent = message;
    }
}

class PasswordValidationService {
    constructor() {
        this.validationRules = {
            minLength: 8,
            requireUppercase: true,
            requireLowercase: true,
            requireNumber: true,
            requireSpecial: false
        };
    }
    
    validate(password) {
        if (!password) {
            this.setFieldState('password', 'neutral', '');
            this.hidePasswordStrength();
            return false;
        }
        
        const rules = this.validationRules;
        const errors = [];
        let strength = 0;
        
        // Length check
        if (password.length < rules.minLength) {
            errors.push(`At least ${rules.minLength} characters`);
        } else {
            strength += 1;
        }
        
        // Uppercase check
        if (rules.requireUppercase && !/[A-Z]/.test(password)) {
            errors.push('One uppercase letter');
        } else if (rules.requireUppercase) {
            strength += 1;
        }
        
        // Lowercase check
        if (rules.requireLowercase && !/[a-z]/.test(password)) {
            errors.push('One lowercase letter');
        } else if (rules.requireLowercase) {
            strength += 1;
        }
        
        // Number check
        if (rules.requireNumber && !/\d/.test(password)) {
            errors.push('One number');
        } else if (rules.requireNumber) {
            strength += 1;
        }
        
        // Special character check
        if (rules.requireSpecial && !/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
            errors.push('One special character');
        } else if (rules.requireSpecial) {
            strength += 1;
        }
        
        // Additional strength factors
        if (password.length >= 12) strength += 1;
        if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) strength += 1;
        
        this.updatePasswordStrength(strength, password.length);
        
        if (errors.length > 0) {
            this.setFieldState('password', 'invalid', `Password needs: ${errors.join(', ')}`);
            return false;
        } else {
            this.setFieldState('password', 'valid', '✓ Strong password');
            return true;
        }
    }
    
    updatePasswordStrength(strength, length) {
        const container = document.getElementById('password-strength-container');
        const fill = document.getElementById('password-strength-fill');
        const text = document.getElementById('password-strength-text');
        
        if (!container || !fill || !text) return;
        
        container.style.display = 'block';
        
        // Remove existing classes
        fill.className = 'password-strength-fill';
        
        let strengthText = '';
        if (strength <= 2) {
            fill.classList.add('weak');
            strengthText = 'Weak password';
        } else if (strength <= 3) {
            fill.classList.add('fair');
            strengthText = 'Fair password';
        } else if (strength <= 4) {
            fill.classList.add('good');
            strengthText = 'Good password';
        } else {
            fill.classList.add('strong');
            strengthText = 'Strong password';
        }
        
        text.textContent = strengthText;
    }
    
    hidePasswordStrength() {
        const container = document.getElementById('password-strength-container');
        if (container) {
            container.style.display = 'none';
        }
    }
    
    setFieldState(fieldName, state, message) {
        const input = document.getElementById(fieldName.replace('-', '_'));
        const feedback = document.getElementById(`${fieldName}-feedback`);
        const loadingIcon = document.getElementById(`${fieldName}-loading`);
        const successIcon = document.getElementById(`${fieldName}-success`);
        const errorIcon = document.getElementById(`${fieldName}-error`);
        
        if (!input || !feedback) return;
        
        // Reset states
        input.classList.remove('valid', 'invalid', 'checking');
        feedback.classList.remove('success', 'error', 'checking');
        
        // Hide all icons
        if (loadingIcon) loadingIcon.classList.add('hidden');
        if (successIcon) successIcon.classList.add('hidden');
        if (errorIcon) errorIcon.classList.add('hidden');
        
        // Apply new state
        switch (state) {
            case 'valid':
                input.classList.add('valid');
                feedback.classList.add('success');
                if (successIcon) successIcon.classList.remove('hidden');
                break;
            case 'invalid':
                input.classList.add('invalid');
                feedback.classList.add('error');
                if (errorIcon) errorIcon.classList.remove('hidden');
                break;
            case 'checking':
                input.classList.add('checking');
                feedback.classList.add('checking');
                if (loadingIcon) loadingIcon.classList.remove('hidden');
                break;
            case 'neutral':
            default:
                // Keep neutral state
                break;
        }
        
        feedback.textContent = message;
    }
}

class DisplayNameValidationService {
    constructor() {
        this.validationRules = {
            minLength: 2,
            maxLength: 30,
            pattern: /^[a-zA-Z0-9\s_-]+$/
        };
    }
    
    validate(displayName) {
        if (!displayName) {
            this.setFieldState('display-name', 'neutral', '');
            return false;
        }
        
        if (displayName.length < this.validationRules.minLength) {
            this.setFieldState('display-name', 'invalid', `Display name must be at least ${this.validationRules.minLength} characters`);
            return false;
        }
        
        if (displayName.length > this.validationRules.maxLength) {
            this.setFieldState('display-name', 'invalid', `Display name must be no more than ${this.validationRules.maxLength} characters`);
            return false;
        }
        
        if (!this.validationRules.pattern.test(displayName)) {
            this.setFieldState('display-name', 'invalid', 'Display name contains invalid characters');
            return false;
        }
        
        this.setFieldState('display-name', 'valid', '✓ Display name looks good');
        return true;
    }
    
    setFieldState(fieldName, state, message) {
        const input = document.getElementById(fieldName.replace('-', '_'));
        const feedback = document.getElementById(`${fieldName}-feedback`);
        const loadingIcon = document.getElementById(`${fieldName}-loading`);
        const successIcon = document.getElementById(`${fieldName}-success`);
        const errorIcon = document.getElementById(`${fieldName}-error`);
        
        if (!input || !feedback) return;
        
        // Reset states
        input.classList.remove('valid', 'invalid', 'checking');
        feedback.classList.remove('success', 'error', 'checking');
        
        // Hide all icons
        if (loadingIcon) loadingIcon.classList.add('hidden');
        if (successIcon) successIcon.classList.add('hidden');
        if (errorIcon) errorIcon.classList.add('hidden');
        
        // Apply new state
        switch (state) {
            case 'valid':
                input.classList.add('valid');
                feedback.classList.add('success');
                if (successIcon) successIcon.classList.remove('hidden');
                break;
            case 'invalid':
                input.classList.add('invalid');
                feedback.classList.add('error');
                if (errorIcon) errorIcon.classList.remove('hidden');
                break;
            case 'checking':
                input.classList.add('checking');
                feedback.classList.add('checking');
                if (loadingIcon) loadingIcon.classList.remove('hidden');
                break;
            case 'neutral':
            default:
                // Keep neutral state
                break;
        }
        
        feedback.textContent = message;
    }
}

class AgeValidationService {
    constructor() {
        this.minimumAge = 13;
    }
    
    validate(birthDate) {
        if (!birthDate) {
            this.setFieldState('birthdate', 'neutral', '');
            this.hideAgeWarnings();
            return false;
        }
        
        const today = new Date();
        const birth = new Date(birthDate);
        const age = today.getFullYear() - birth.getFullYear();
        const monthDiff = today.getMonth() - birth.getMonth();
        
        // Adjust age if birthday hasn't occurred this year
        const actualAge = (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) 
            ? age - 1 : age;
        
        this.hideAgeWarnings();
        
        if (actualAge < this.minimumAge) {
            this.setFieldState('birthdate', 'invalid', `Age: ${actualAge} years old - Too young to register`);
            this.showAgeWarning();
            return false;
        } else if (actualAge < 18) {
            this.setFieldState('birthdate', 'valid', `Age: ${actualAge} years old - Parental consent required`);
            this.showMinorNotice();
            return true;
        } else {
            this.setFieldState('birthdate', 'valid', `Age: ${actualAge} years old - Valid`);
            return true;
        }
    }
    
    showAgeWarning() {
        const warning = document.getElementById('age_warning');
        if (warning) warning.classList.remove('hidden');
    }
    
    showMinorNotice() {
        const notice = document.getElementById('minor_notice');
        if (notice) notice.classList.remove('hidden');
    }
    
    hideAgeWarnings() {
        const warning = document.getElementById('age_warning');
        const notice = document.getElementById('minor_notice');
        if (warning) warning.classList.add('hidden');
        if (notice) notice.classList.add('hidden');
    }
    
    setFieldState(fieldName, state, message) {
        const input = document.getElementById(fieldName.replace('-', '_'));
        const feedback = document.getElementById(`${fieldName}-feedback`);
        const loadingIcon = document.getElementById(`${fieldName}-loading`);
        const successIcon = document.getElementById(`${fieldName}-success`);
        const errorIcon = document.getElementById(`${fieldName}-error`);
        
        if (!input || !feedback) return;
        
        // Reset states
        input.classList.remove('valid', 'invalid', 'checking');
        feedback.classList.remove('success', 'error', 'checking');
        
        // Hide all icons
        if (loadingIcon) loadingIcon.classList.add('hidden');
        if (successIcon) successIcon.classList.add('hidden');
        if (errorIcon) errorIcon.classList.add('hidden');
        
        // Apply new state
        switch (state) {
            case 'valid':
                input.classList.add('valid');
                feedback.classList.add('success');
                if (successIcon) successIcon.classList.remove('hidden');
                break;
            case 'invalid':
                input.classList.add('invalid');
                feedback.classList.add('error');
                if (errorIcon) errorIcon.classList.remove('hidden');
                break;
            case 'checking':
                input.classList.add('checking');
                feedback.classList.add('checking');
                if (loadingIcon) loadingIcon.classList.remove('hidden');
                break;
            case 'neutral':
            default:
                // Keep neutral state
                break;
        }
        
        feedback.textContent = message;
    }
}

class IDUploadValidationService {
    constructor() {
        this.maxFileSize = 10 * 1024 * 1024; // 10MB
    }
    
    validateIDFile(file) {
        const feedback = document.getElementById('id-upload-feedback');
        if (!file.type.startsWith('image/') && file.type !== 'application/pdf') {
            feedback.textContent = 'Please upload an image file (JPG, PNG) or PDF';
            feedback.className = 'feedback error';
            return false;
        }
        
        if (file.size > this.maxFileSize) {
            feedback.textContent = 'File too large. Maximum size is 10MB';
            feedback.className = 'feedback error';
            return false;
        }
        
        return true;
    }
    
    async validate(file) {
        if (!this.validateIDFile(file)) {
            return false;
        }
        
        // Show preview
        this.showIDPreview(file);
        
        // TODO: Process ID verification
        // This would typically send to backend for AI processing
        setTimeout(() => {
            const feedback = document.getElementById('id-upload-feedback');
            feedback.textContent = '✓ ID uploaded successfully - Verification pending';
            feedback.className = 'feedback success';
        }, 1000);
        
        return true;
    }
    
    showIDPreview(file) {
        const placeholder = document.getElementById('upload-placeholder');
        const preview = document.getElementById('upload-preview');
        const previewImage = document.getElementById('preview-image');
        const previewPDF = document.getElementById('preview-pdf');
        const pdfName = document.getElementById('pdf-name');
        
        placeholder.style.display = 'none';
        preview.classList.remove('hidden');
        
        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                previewImage.src = e.target.result;
                previewImage.style.display = 'block';
                previewPDF.style.display = 'none';
            };
            reader.readAsDataURL(file);
        } else if (file.type === 'application/pdf') {
            pdfName.textContent = file.name;
            previewPDF.style.display = 'flex';
            previewImage.style.display = 'none';
        }
    }
}

class RegisterValidationOrchestrator {
    constructor() {
        this.services = new Map();
        this.initialize();
    }
    
    initialize() {
        // Register validation microservices
        this.registerService('username', new UsernameValidationService());
        this.registerService('email', new EmailValidationService());
        this.registerService('password', new PasswordValidationService());
        this.registerService('displayName', new DisplayNameValidationService());
        this.registerService('age', new AgeValidationService());
        this.registerService('idUpload', new IDUploadValidationService());
        
        console.log('✅ Register Validation Orchestrator initialized');
    }
    
    registerService(name, service) {
        this.services.set(name, service);
        console.log(`✅ ${name} validation service registered`);
    }
    
    getService(name) {
        return this.services.get(name);
    }
    
    async validateAll() {
        const username = document.getElementById('username')?.value || '';
        const email = document.getElementById('email')?.value || '';
        const password = document.getElementById('password')?.value || '';
        const displayName = document.getElementById('display_name')?.value || '';
        const birthDate = document.getElementById('birth_date')?.value || '';
        
        const results = await Promise.all([
            this.services.get('username').validate(username, true),
            this.services.get('email').validate(email, true),
            this.services.get('password').validate(password),
            this.services.get('displayName').validate(displayName),
            this.services.get('age').validate(birthDate)
        ]);
        
        return results.every(result => result === true);
    }
}

// Load individual validation services
// Note: These would be loaded from separate files in a real implementation
console.log('🎯 Loading validation microservices...');

// Initialize the orchestrator
window.registerValidation = new RegisterValidationOrchestrator();

// Global utility functions
window.switchVerificationTab = function(tab) {
    const birthdateTab = document.getElementById('birthdate-tab');
    const idTab = document.getElementById('id-upload-tab');
    const birthdateMethod = document.getElementById('birthdate-verification');
    const idMethod = document.getElementById('id-upload-verification');
    
    if (tab === 'birthdate') {
        birthdateTab.classList.add('active');
        idTab.classList.remove('active');
        birthdateMethod.classList.add('active');
        idMethod.classList.remove('active');
    } else {
        birthdateTab.classList.remove('active');
        idTab.classList.add('active');
        birthdateMethod.classList.remove('active');
        idMethod.classList.add('active');
    }
};

window.removeIDUpload = function() {
    const placeholder = document.getElementById('upload-placeholder');
    const preview = document.getElementById('upload-preview');
    const fileInput = document.getElementById('id_document');
    const feedback = document.getElementById('id-upload-feedback');
    
    placeholder.style.display = 'block';
    preview.classList.add('hidden');
    if (fileInput) fileInput.value = '';
    if (feedback) {
        feedback.textContent = '';
        feedback.className = 'feedback';
    }
};

console.log('🎯 Register Validation Orchestrator loaded');