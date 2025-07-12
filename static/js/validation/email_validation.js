/**
 * 🎯 EMAIL VALIDATION MICROSERVICE - Single Responsibility: Email validation & availability
 */
class EmailValidationService {
    constructor() {
        this.validationRules = {
            pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
            checkAvailability: true
        };
        
        this.validationCache = new Map();
        this.debounceTimers = new Map();
        
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        const emailInput = document.getElementById('email');
        if (emailInput) {
            emailInput.addEventListener('input', (e) => {
                this.debounceValidation(e.target.value, () => {
                    this.validate(e.target.value);
                });
            });
            
            emailInput.addEventListener('blur', (e) => {
                this.validate(e.target.value, true);
            });
        }
    }
    
    debounceValidation(value, callback) {
        if (this.debounceTimers.has('email')) {
            clearTimeout(this.debounceTimers.get('email'));
        }
        
        this.debounceTimers.set('email', setTimeout(() => {
            callback();
        }, 500));
    }
    
    async validate(email, forceCheck = false) {
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
                const response = await fetch('/check-email', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: email })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const result = await response.json();
                
                if (result.available) {
                    this.validationCache.set(`email:${email}`, true);
                    this.setFieldState('email', 'valid', '✓ Email is available');
                    return true;
                } else {
                    this.validationCache.set(`email:${email}`, false);
                    this.setFieldState('email', 'invalid', result.message || 'This email is already registered');
                    return false;
                }
            } catch (error) {
                console.error('Email validation error:', error);
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
                break;
        }
        
        feedback.textContent = message;
    }
}

console.log('🎯 Email Validation Microservice loaded');