/**
 * 🎯 USERNAME VALIDATION MICROSERVICE - Single Responsibility: Username validation & availability
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
        
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        const usernameInput = document.getElementById('username');
        if (usernameInput) {
            usernameInput.addEventListener('input', (e) => {
                this.debounceValidation(e.target.value, () => {
                    this.validate(e.target.value);
                });
            });
            
            usernameInput.addEventListener('blur', (e) => {
                this.validate(e.target.value, true);
            });
        }
    }
    
    debounceValidation(value, callback) {
        if (this.debounceTimers.has('username')) {
            clearTimeout(this.debounceTimers.get('username'));
        }
        
        this.debounceTimers.set('username', setTimeout(() => {
            callback();
        }, 500));
    }
    
    async validate(username, forceCheck = false) {
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
                const response = await fetch('/check-username', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username: username })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const result = await response.json();
                
                if (result.available) {
                    this.validationCache.set(`username:${username}`, true);
                    this.setFieldState('username', 'valid', `✓ Username "${username}" is available`);
                    return true;
                } else {
                    this.validationCache.set(`username:${username}`, false);
                    this.setFieldState('username', 'invalid', result.message || `Username "${username}" is already taken`);
                    return false;
                }
            } catch (error) {
                console.error('Username validation error:', error);
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
                break;
        }
        
        feedback.textContent = message;
    }
}

console.log('🎯 Username Validation Microservice loaded');