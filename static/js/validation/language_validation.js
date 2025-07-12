/**
 * 🎯 LANGUAGE VALIDATION MICROSERVICE - Single Responsibility: Language selection validation
 */
class LanguageValidationService {
    constructor() {
        this.supportedLanguages = [
            'EN-US', 'EN-GB', 'BG', 'CS', 'DA', 'DE', 'EL', 'ES', 'ES-419', 'ET', 'FI', 'FR', 'HE', 
            'HU', 'ID', 'IT', 'JA', 'KO', 'LT', 'LV', 'NB', 'NL', 'PL', 'PT-PT', 'PT-BR', 'RO', 
            'RU', 'SK', 'SL', 'SV', 'TH', 'TR', 'UK', 'VI', 'ZH-HANS', 'ZH-HANT', 'AR'
        ];
        
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        const languageSelect = document.getElementById('preferred_language');
        if (languageSelect) {
            languageSelect.addEventListener('change', (e) => {
                this.validate(e.target.value);
            });
        }
    }
    
    validate(language) {
        if (!language) {
            this.setFieldState('language', 'invalid', 'Please select your primary language');
            return false;
        }
        
        if (!this.supportedLanguages.includes(language)) {
            this.setFieldState('language', 'invalid', 'Invalid language selection');
            return false;
        }
        
        this.setFieldState('language', 'valid', '✓ Language selected');
        return true;
    }
    
    setFieldState(fieldName, state, message) {
        const select = document.getElementById('preferred_language');
        const feedback = document.getElementById(`${fieldName}-feedback`);
        const successIcon = document.getElementById(`${fieldName}-success`);
        const errorIcon = document.getElementById(`${fieldName}-error`);
        
        if (!select || !feedback) return;
        
        // Reset states
        select.classList.remove('valid', 'invalid');
        feedback.classList.remove('success', 'error');
        
        // Hide all icons
        if (successIcon) successIcon.classList.add('hidden');
        if (errorIcon) errorIcon.classList.add('hidden');
        
        // Apply new state
        switch (state) {
            case 'valid':
                select.classList.add('valid');
                feedback.classList.add('success');
                if (successIcon) successIcon.classList.remove('hidden');
                break;
            case 'invalid':
                select.classList.add('invalid');
                feedback.classList.add('error');
                if (errorIcon) errorIcon.classList.remove('hidden');
                break;
            case 'neutral':
            default:
                break;
        }
        
        feedback.textContent = message;
    }
}

// Export to global scope
window.LanguageValidationService = LanguageValidationService;

console.log('🎯 Language Validation Microservice loaded');