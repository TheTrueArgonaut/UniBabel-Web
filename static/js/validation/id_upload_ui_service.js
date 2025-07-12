/**
 * 🎯 ID UPLOAD UI SERVICE - Single Responsibility: UI management for ID upload interface
 */
class IDUploadUIService {
    constructor() {
        this.elements = {
            feedback: null,
            placeholder: null,
            preview: null,
            previewImage: null,
            previewPDF: null,
            pdfName: null,
            processing: null,
            birthdateNotice: null,
            birthdateTab: null,
            birthdateInput: null
        };
        
        this.initializeElements();
    }
    
    initializeElements() {
        this.elements.feedback = document.getElementById('id-upload-feedback');
        this.elements.placeholder = document.getElementById('upload-placeholder');
        this.elements.preview = document.getElementById('upload-preview');
        this.elements.previewImage = document.getElementById('preview-image');
        this.elements.previewPDF = document.getElementById('preview-pdf');
        this.elements.pdfName = document.getElementById('pdf-name');
        this.elements.processing = document.getElementById('upload-processing');
        this.elements.birthdateNotice = document.getElementById('birthdate-auto-notice');
        this.elements.birthdateTab = document.getElementById('birthdate-tab');
        this.elements.birthdateInput = document.getElementById('birth_date');
    }
    
    showPreview(file) {
        if (!this.elements.placeholder || !this.elements.preview) return;
        
        this.elements.placeholder.style.display = 'none';
        this.elements.preview.classList.remove('hidden');
        
        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                if (this.elements.previewImage) {
                    this.elements.previewImage.src = e.target.result;
                    this.elements.previewImage.style.display = 'block';
                }
                if (this.elements.previewPDF) {
                    this.elements.previewPDF.style.display = 'none';
                }
            };
            reader.readAsDataURL(file);
        } else if (file.type === 'application/pdf') {
            if (this.elements.pdfName) {
                this.elements.pdfName.textContent = file.name;
            }
            if (this.elements.previewPDF) {
                this.elements.previewPDF.style.display = 'flex';
            }
            if (this.elements.previewImage) {
                this.elements.previewImage.style.display = 'none';
            }
        }
    }
    
    startProcessing() {
        if (this.elements.processing) {
            this.elements.processing.classList.remove('hidden');
        }
        if (this.elements.preview) {
            this.elements.preview.style.opacity = '0.7';
        }
        if (this.elements.feedback) {
            this.elements.feedback.textContent = '🤖 Starting analysis...';
            this.elements.feedback.className = 'feedback checking';
        }
    }
    
    stopProcessing() {
        if (this.elements.processing) {
            this.elements.processing.classList.add('hidden');
        }
        if (this.elements.preview) {
            this.elements.preview.style.opacity = '1';
        }
    }
    
    showError(documentType) {
        if (!this.elements.feedback) return;
        
        let errorMessage;
        switch (documentType.type) {
            case 'credit_card':
                errorMessage = '💳 ❌ Credit/debit cards are not accepted for age verification. Please upload a government-issued ID.';
                break;
            case 'unreadable':
                errorMessage = '❓ ❌ Could not read text from image. Please ensure the image is clear and well-lit.';
                break;
            case 'unclear':
                errorMessage = '📄 ❌ Unable to identify document type. Please upload a Driver\'s License, Passport, State ID, or National ID Card.';
                break;
            default:
                errorMessage = '❌ Invalid document type. Please upload a government-issued photo ID.';
        }
        
        this.elements.feedback.textContent = errorMessage;
        this.elements.feedback.className = 'feedback error';
        
        this.showGuidance();
        this.restoreBirthdateTab();
        this.clearSuccessStates();
        
        console.log('🚫 Document rejected:', documentType);
    }
    
    showSuccess(ageData, documentType) {
        if (!this.elements.feedback) return;
        
        // Update feedback with success message
        const docTypeName = documentType.type.replace('_', ' ').toUpperCase();
        this.elements.feedback.textContent = `🎉 ${docTypeName} Verified! Age: ${ageData.age} years old (Born: ${ageData.birthdate})`;
        this.elements.feedback.className = 'feedback success';
        
        // Show smart detection notice
        this.showSuccessNotice(ageData, documentType);
        
        // Auto-fill birthdate
        this.fillBirthdate(ageData.birthdate);
        
        // Update birthdate tab
        this.updateBirthdateTabToVerified();
        
        // Success animation
        this.showSuccessAnimation();
    }
    
    showFallback() {
        if (!this.elements.feedback) return;
        
        this.elements.feedback.textContent = '⚠️ ID uploaded successfully, but couldn\'t extract birthdate automatically. Please use the Birth Date tab to enter it manually.';
        this.elements.feedback.className = 'feedback warning';
        
        this.restoreBirthdateTab();
    }
    
    showProcessingError() {
        if (!this.elements.feedback) return;
        
        this.elements.feedback.textContent = '❌ Error processing document. Please try again with a clear photo of your government ID.';
        this.elements.feedback.className = 'feedback error';
        
        this.clearSuccessStates();
        this.restoreBirthdateTab();
    }
    
    showSuccessNotice(ageData, documentType) {
        if (!this.elements.birthdateNotice) return;
        
        this.elements.birthdateNotice.classList.remove('hidden');
        this.elements.birthdateNotice.style.background = '#1e3a8a';
        this.elements.birthdateNotice.style.borderColor = '#3b82f6';
        
        const noticeText = this.elements.birthdateNotice.querySelector('p');
        if (noticeText) {
            noticeText.textContent = `Successfully extracted birthdate: ${ageData.birthdate} from your ${documentType.type.replace('_', ' ')}! No need to enter it manually.`;
        }
        
        const title = this.elements.birthdateNotice.querySelector('h6');
        if (title) {
            title.textContent = 'Smart Age Detection';
        }
    }
    
    showGuidance() {
        if (!this.elements.birthdateNotice) return;
        
        this.elements.birthdateNotice.classList.remove('hidden');
        this.elements.birthdateNotice.style.background = '#991b1b';
        this.elements.birthdateNotice.style.borderColor = '#dc2626';
        
        const noticeText = this.elements.birthdateNotice.querySelector('p');
        if (noticeText) {
            noticeText.innerHTML = `
                <strong>Accepted IDs:</strong><br>
                • Driver's License<br>
                • Passport<br>
                • State ID Card<br>
                • National ID Card<br><br>
                <strong>Not Accepted:</strong> Credit cards, bank cards, receipts, or other documents.
            `;
        }
        
        const title = this.elements.birthdateNotice.querySelector('h6');
        if (title) {
            title.textContent = 'ID Requirements';
        }
    }
    
    fillBirthdate(birthdate) {
        if (!this.elements.birthdateInput) return;
        
        this.elements.birthdateInput.value = birthdate;
        
        // Trigger age validation
        if (window.registerValidation) {
            const ageService = window.registerValidation.getService('age');
            if (ageService) {
                ageService.validate(birthdate);
            }
        }
    }
    
    updateBirthdateTabToVerified() {
        if (!this.elements.birthdateTab) return;
        
        this.elements.birthdateTab.style.opacity = '0.8';
        this.elements.birthdateTab.style.pointerEvents = 'none';
        this.elements.birthdateTab.style.background = 'linear-gradient(45deg, #10b981, #059669)';
        this.elements.birthdateTab.innerHTML = `
            <i class="ri-check-line"></i>
            <span>Age Verified via ID ✓</span>
        `;
    }
    
    restoreBirthdateTab() {
        if (!this.elements.birthdateTab) return;
        
        this.elements.birthdateTab.style.opacity = '1';
        this.elements.birthdateTab.style.pointerEvents = 'auto';
        this.elements.birthdateTab.style.background = '';
        this.elements.birthdateTab.innerHTML = `
            <i class="ri-calendar-line"></i>
            <span>Birth Date</span>
        `;
    }
    
    clearSuccessStates() {
        if (this.elements.birthdateNotice) {
            this.elements.birthdateNotice.classList.add('hidden');
            this.elements.birthdateNotice.style.background = '';
            this.elements.birthdateNotice.style.borderColor = '';
        }
        
        // Clear verification data
        const hiddenInput = document.getElementById('id_verification_data');
        if (hiddenInput) {
            hiddenInput.remove();
        }
    }
    
    showSuccessAnimation() {
        if (!this.elements.preview) return;
        
        this.elements.preview.style.animation = 'pulse 0.6s ease-in-out';
        setTimeout(() => {
            this.elements.preview.style.animation = '';
        }, 600);
    }
}

// Export to global scope
window.IDUploadUIService = IDUploadUIService;

console.log('🎯 ID Upload UI Service loaded');