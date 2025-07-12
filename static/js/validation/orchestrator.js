/**
 * 🎯 REGISTER VALIDATION ORCHESTRATOR - Single Responsibility: Coordinate validation microservices
 * 
 * SRIMI Principles:
 * - Single Responsibility: ONLY coordinates validation services
 * - Reactive: Event-driven validation coordination
 * - Injectable: Uses injected validation services
 * - Micro: Lightweight orchestration logic
 * - Interfaces: Clear validation service contracts
 */

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
        this.registerService('language', new LanguageValidationService());
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
        const confirmPassword = document.getElementById('confirm_password')?.value || '';
        const displayName = document.getElementById('display_name')?.value || '';
        const preferredLanguage = document.getElementById('preferred_language')?.value || '';
        const birthDate = document.getElementById('birth_date')?.value || '';
        
        // Check passwords match
        if (password !== confirmPassword) {
            const feedback = document.getElementById('confirm-password-feedback');
            if (feedback) {
                feedback.textContent = 'Passwords do not match';
                feedback.className = 'feedback error';
            }
            return false;
        }
        
        const results = await Promise.all([
            this.services.get('username').validate(username, true),
            this.services.get('email').validate(email, true),
            this.services.get('password').validate(password),
            this.services.get('displayName').validate(displayName),
            this.services.get('language').validate(preferredLanguage),
            this.services.get('age').validate(birthDate)
        ]);
        
        return results.every(result => result === true);
    }
}

// Global utility functions for the form
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
        idMethod.classList.add('hidden');
        birthdateMethod.classList.remove('hidden');
    } else {
        birthdateTab.classList.remove('active');
        idTab.classList.add('active');
        birthdateMethod.classList.remove('active');
        idMethod.classList.add('active');
        birthdateMethod.classList.add('hidden');
        idMethod.classList.remove('hidden');
    }
};

window.removeIDUpload = function() {
    const placeholder = document.getElementById('upload-placeholder');
    const preview = document.getElementById('upload-preview');
    const fileInput = document.getElementById('id_document');
    const feedback = document.getElementById('id-upload-feedback');
    const birthdateNotice = document.getElementById('birthdate-auto-notice');
    
    placeholder.style.display = 'block';
    preview.classList.add('hidden');
    if (fileInput) fileInput.value = '';
    if (feedback) {
        feedback.textContent = '';
        feedback.className = 'feedback';
    }
    
    // Hide auto-notice and restore birthdate tab
    if (birthdateNotice) {
        birthdateNotice.classList.add('hidden');
    }
    
    // Restore birthdate tab functionality
    const birthdateTab = document.getElementById('birthdate-tab');
    if (birthdateTab) {
        birthdateTab.style.opacity = '1';
        birthdateTab.style.pointerEvents = 'auto';
        birthdateTab.innerHTML = `
            <i class="ri-calendar-line"></i>
            <span>Birth Date</span>
        `;
    }
    
    // Clear any ID verification data
    const hiddenInput = document.getElementById('id_verification_data');
    if (hiddenInput) {
        hiddenInput.remove();
    }
};

window.togglePassword = function(inputId, button) {
    const input = document.getElementById(inputId);
    const icon = button.querySelector("i");

    if (!input || !icon) return;

    if (input.type === "password") {
        input.type = "text";
        icon.className = "ri-eye-off-line text-gray-400";
    } else {
        input.type = "password";
        icon.className = "ri-eye-line text-gray-400";
    }
};

window.toggleCheckbox = function(inputId, container) {
    const input = document.getElementById(inputId);
    const icon = container.querySelector("i");

    if (!input || !icon) return;

    input.checked = !input.checked;

    if (input.checked) {
        container.classList.add("checked");
    } else {
        container.classList.remove("checked");
    }
};

// Initialize the orchestrator when page loads
document.addEventListener('DOMContentLoaded', () => {
    // Wait for all microservices to load
    const checkServices = setInterval(() => {
        const requiredServices = [
            'FileValidationService',
            'ImageAnalysisService', 
            'DocumentDetectionService',
            'AgeExtractionService',
            'IDUploadUIService',
            'LanguageValidationService'
        ];
        
        const servicesLoaded = requiredServices.every(serviceName => 
            typeof window[serviceName] !== 'undefined'
        );
        
        if (servicesLoaded) {
            clearInterval(checkServices);
            window.registerValidation = new RegisterValidationOrchestrator();
            console.log('🎯 All microservices loaded and orchestrator initialized');
        }
    }, 100);
});

console.log('🎯 Register Validation Orchestrator loaded');