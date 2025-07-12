/**
 * 🎯 DISPLAY NAME VALIDATION MICROSERVICE - Single Responsibility: Display name validation
 */
class DisplayNameValidationService {
    constructor() {
        this.validationRules = {
            minLength: 2,
            maxLength: 30,
            pattern: /^[a-zA-Z0-9\s_-]+$/
        };
        
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        const displayNameInput = document.getElementById('display_name');
        if (displayNameInput) {
            displayNameInput.addEventListener('input', (e) => {
                this.validate(e.target.value);
            });
        }
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
                break;
        }
        
        feedback.textContent = message;
    }
}

console.log('🎯 Display Name Validation Microservice loaded');