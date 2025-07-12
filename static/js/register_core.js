// 🎯 REGISTER CORE MICROSERVICE
// SRIMI Compliant: Single Responsibility - Core state management

class RegisterCore {
    constructor() {
        this.state = {
            currentStep: 1,
            formData: {},
            validationErrors: {},
            isSubmitting: false,
            ageVerified: false,
            parentConsentRequired: false
        };
        
        this.init();
    }
    
    init() {
        console.log('🎯 Register Core initialized');
        this.attachEventListeners();
    }
    
    attachEventListeners() {
        // Birth date change - age verification
        const birthDate = document.getElementById('birth_date');
        if (birthDate) {
            birthDate.addEventListener('change', (e) => {
                this.handleAgeVerification(e.target.value);
            });
        }
        
        // Form submission
        const form = document.getElementById('registerForm');
        if (form) {
            form.addEventListener('submit', (e) => {
                this.handleFormSubmit(e);
            });
        }
    }
    
    handleAgeVerification(birthDateValue) {
        if (!birthDateValue) return;
        
        const birthDate = new Date(birthDateValue);
        const today = new Date();
        const age = today.getFullYear() - birthDate.getFullYear() - 
                   ((today.getMonth() < birthDate.getMonth() || 
                     (today.getMonth() === birthDate.getMonth() && today.getDate() < birthDate.getDate())) ? 1 : 0);
        
        const ageInfo = document.getElementById('age-info');
        
        // Show age info
        if (age >= 0 && age <= 120) {
            ageInfo.textContent = `Age: ${age} years old`;
            ageInfo.className = 'feedback success';
        }
        
        // Handle age restrictions
        if (age < 13) {
            this.setState({ ageVerified: false, parentConsentRequired: false });
            this.showAgeRestriction(true);
            this.disableSubmission('Cannot Register (Under 13)');
        } else if (age < 18) {
            this.setState({ ageVerified: true, parentConsentRequired: true });
            this.showAgeRestriction(false);
            this.enableSubmission('Create Account (Requires Parent Verification)');
        } else {
            this.setState({ ageVerified: true, parentConsentRequired: false });
            this.showAgeRestriction(false);
            this.enableSubmission('Create Account');
        }
    }
    
    setState(newState) {
        this.state = { ...this.state, ...newState };
        this.updateUI();
    }
    
    showAgeRestriction(show) {
        const ageWarning = document.getElementById('age_warning');
        if (ageWarning) {
            ageWarning.classList.toggle('hidden', !show);
        }
    }
    
    disableSubmission(text) {
        const submitButton = document.getElementById('submitButton');
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.textContent = text;
            submitButton.className = 'btn-primary disabled';
        }
    }
    
    enableSubmission(text) {
        const submitButton = document.getElementById('submitButton');
        if (submitButton) {
            submitButton.disabled = false;
            submitButton.textContent = text;
            submitButton.className = 'btn-primary';
        }
    }
    
    async handleFormSubmit(e) {
        e.preventDefault();
        
        if (this.state.isSubmitting) return;
        
        this.setState({ isSubmitting: true });
        
        try {
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            
            // Validate passwords match
            if (data.password !== data.confirm_password) {
                this.showError('Passwords do not match');
                return;
            }
            
            data.terms = document.getElementById('terms').checked;
            
            const result = await window.registerAPI?.submitRegistration(data);
            
            if (result.success) {
                console.log('Registration successful, redirecting to:', result.redirect);
                window.location.href = result.redirect;
            } else {
                const errorMsg = result.errors ? result.errors.join(', ') : 'Registration failed';
                this.showError(errorMsg);
            }
        } catch (error) {
            console.error('Registration error:', error);
            this.showError('Registration failed. Please try again.');
        } finally {
            this.setState({ isSubmitting: false });
        }
    }
    
    updateUI() {
        const submitButton = document.getElementById('submitButton');
        if (submitButton && this.state.isSubmitting) {
            submitButton.disabled = true;
            submitButton.textContent = 'Creating Account...';
        }
    }
    
    showError(message) {
        const errorDiv = document.getElementById('error-message');
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.classList.add('show');
            setTimeout(() => errorDiv.classList.remove('show'), 5000);
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.registerCore = new RegisterCore();
});

window.registerCore = window.registerCore || null;