/**
 * 🎯 PASSWORD VALIDATION MICROSERVICE - Single Responsibility: Password strength & matching
 */
class PasswordValidationService {
    constructor() {
        this.validationRules = {
            minLength: 8,
            requireUppercase: true,
            requireLowercase: true,
            requireNumber: true,
            requireSpecial: false
        };
        
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        const passwordInput = document.getElementById('password');
        const confirmPasswordInput = document.getElementById('confirm_password');
        
        if (passwordInput) {
            passwordInput.addEventListener('input', (e) => {
                this.validate(e.target.value);
                this.validatePasswordMatch();
            });
        }
        
        if (confirmPasswordInput) {
            confirmPasswordInput.addEventListener('input', (e) => {
                this.validatePasswordMatch();
            });
        }
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
    
    validatePasswordMatch() {
        const password = document.getElementById('password')?.value || '';
        const confirmPassword = document.getElementById('confirm_password')?.value || '';
        
        if (!confirmPassword) {
            this.setFieldState('confirm-password', 'neutral', '');
            return false;
        }
        
        if (password !== confirmPassword) {
            this.setFieldState('confirm-password', 'invalid', 'Passwords do not match');
            return false;
        } else {
            this.setFieldState('confirm-password', 'valid', '✓ Passwords match');
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
                break;
        }
        
        feedback.textContent = message;
    }
}

console.log('🎯 Password Validation Microservice loaded');