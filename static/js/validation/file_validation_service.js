/**
 * 🎯 FILE VALIDATION SERVICE - Single Responsibility: File format & size validation
 */
class FileValidationService {
    constructor() {
        this.maxFileSize = 10 * 1024 * 1024; // 10MB
        this.allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf'];
    }
    
    validate(file) {
        const feedback = document.getElementById('id-upload-feedback');
        
        if (!this.isValidType(file)) {
            feedback.textContent = 'Please upload an image file (JPG, PNG) or PDF';
            feedback.className = 'feedback error';
            return false;
        }
        
        if (!this.isValidSize(file)) {
            feedback.textContent = 'File too large. Maximum size is 10MB';
            feedback.className = 'feedback error';
            return false;
        }
        
        return true;
    }
    
    isValidType(file) {
        return this.allowedTypes.includes(file.type) || 
               file.type.startsWith('image/');
    }
    
    isValidSize(file) {
        return file.size <= this.maxFileSize;
    }
}

// Export to global scope
window.FileValidationService = FileValidationService;

console.log('🎯 File Validation Service loaded');