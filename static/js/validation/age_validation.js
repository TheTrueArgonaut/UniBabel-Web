/**
 * 🎯 AGE VALIDATION MICROSERVICE - Single Responsibility: Age verification & warnings
 */
class AgeValidationService {
    constructor() {
        this.minimumAge = 13;
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        const birthDateInput = document.getElementById('birth_date');
        if (birthDateInput) {
            birthDateInput.addEventListener('change', (e) => {
                this.validate(e.target.value);
            });
        }
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
                break;
        }
        
        feedback.textContent = message;
    }
}

console.log('🎯 Age Validation Microservice loaded');