/**
 * 🎯 ID UPLOAD VALIDATION MICROSERVICE - Single Responsibility: File upload orchestration
 */
class IDUploadValidationService {
    constructor() {
        this.maxFileSize = 10 * 1024 * 1024; // 10MB
        this.uploadedFile = null;
        this.verificationData = null;
        
        // Initialize microservices
        this.fileValidator = new FileValidationService();
        this.imageAnalyzer = new ImageAnalysisService();
        this.documentDetector = new DocumentDetectionService();
        this.ageExtractor = new AgeExtractionService();
        this.uiManager = new IDUploadUIService();
        
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        const uploadArea = document.getElementById('id-upload-area');
        const fileInput = document.getElementById('id_document');
        
        if (!uploadArea || !fileInput) return;
        
        uploadArea.addEventListener('click', () => fileInput.click());
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('drag-over');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            const files = e.dataTransfer.files;
            if (files.length > 0) this.validate(files[0]);
        });
        
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) this.validate(e.target.files[0]);
        });
    }
    
    async validate(file) {
        try {
            // Step 1: Basic file validation
            if (!this.fileValidator.validate(file)) return false;
            
            this.uploadedFile = file;
            this.uiManager.showPreview(file);
            this.uiManager.startProcessing();
            
            // Step 2: Analyze actual image data
            const imageData = await this.imageAnalyzer.analyze(file);
            
            // Step 3: Detect document type from real image features
            const documentType = await this.documentDetector.detect(imageData);
            
            if (!documentType.isValid) {
                this.uiManager.showError(documentType);
                return false;
            }
            
            // Step 4: Extract age from valid government ID
            const ageData = await this.ageExtractor.extract(imageData, documentType);
            
            if (ageData.success) {
                this.uiManager.showSuccess(ageData, documentType);
                this.markAsVerified(ageData, documentType);
            } else {
                this.uiManager.showFallback();
            }
            
            return true;
            
        } catch (error) {
            console.error('ID validation error:', error);
            this.uiManager.showProcessingError();
            return false;
        } finally {
            this.uiManager.stopProcessing();
        }
    }
    
    markAsVerified(ageData, documentType) {
        this.verificationData = {
            method: 'id_upload',
            birthdate: ageData.birthdate,
            age: ageData.age,
            verified: true,
            documentType: documentType.type,
            confidence: documentType.confidence,
            timestamp: new Date().toISOString()
        };
        
        // Store for form submission
        let hiddenInput = document.getElementById('id_verification_data');
        if (!hiddenInput) {
            hiddenInput = document.createElement('input');
            hiddenInput.type = 'hidden';
            hiddenInput.id = 'id_verification_data';
            hiddenInput.name = 'id_verification_data';
            document.getElementById('registerForm').appendChild(hiddenInput);
        }
        hiddenInput.value = JSON.stringify(this.verificationData);
    }
    
    isIDVerified() {
        return this.verificationData && this.verificationData.verified;
    }
    
    getVerificationData() {
        return this.verificationData;
    }
}

console.log('🎯 ID Upload Validation Orchestrator loaded');