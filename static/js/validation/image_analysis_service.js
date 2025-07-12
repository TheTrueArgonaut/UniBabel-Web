/**
 * 🎯 IMAGE ANALYSIS SERVICE - Single Responsibility: Real OCR text extraction using Tesseract
 */
class ImageAnalysisService {
    constructor() {
        this.tesseractWorker = null;
        this.initializeTesseract();
    }
    
    async initializeTesseract() {
        try {
            // Load Tesseract.js from CDN if not already loaded
            if (typeof Tesseract === 'undefined') {
                await this.loadTesseractScript();
            }
            
            // Create worker
            this.tesseractWorker = await Tesseract.createWorker('eng');
            console.log('✅ Tesseract OCR initialized');
        } catch (error) {
            console.error('❌ Failed to initialize Tesseract:', error);
        }
    }
    
    async loadTesseractScript() {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://unpkg.com/tesseract.js@v4.1.1/dist/tesseract.min.js';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }
    
    async analyze(file) {
        try {
            // Show progress
            const feedback = document.getElementById('id-upload-feedback');
            feedback.textContent = '🔍 Reading text from document...';
            
            // Ensure Tesseract is ready
            if (!this.tesseractWorker) {
                await this.initializeTesseract();
            }
            
            // Convert file to image data
            const imageData = await this.fileToImageData(file);
            
            // Run OCR on the image
            feedback.textContent = '📝 Extracting text with OCR...';
            const result = await this.tesseractWorker.recognize(imageData);
            
            const extractedText = result.data.text;
            const confidence = result.data.confidence;
            
            console.log('📄 Extracted text:', extractedText);
            console.log('🎯 OCR confidence:', confidence);
            
            return {
                text: extractedText,
                confidence: confidence,
                words: result.data.words,
                lines: result.data.lines,
                file: file,
                success: true
            };
            
        } catch (error) {
            console.error('❌ OCR analysis failed:', error);
            return {
                text: '',
                confidence: 0,
                words: [],
                lines: [],
                file: file,
                success: false,
                error: error.message
            };
        }
    }
    
    async fileToImageData(file) {
        return new Promise((resolve, reject) => {
            if (file.type === 'application/pdf') {
                // For PDFs, we'd need PDF.js, but for now reject PDFs for OCR
                reject(new Error('PDF OCR not implemented yet. Please upload an image.'));
                return;
            }
            
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }
    
    async destroy() {
        if (this.tesseractWorker) {
            await this.tesseractWorker.terminate();
            this.tesseractWorker = null;
        }
    }
}

// Export to global scope
window.ImageAnalysisService = ImageAnalysisService;

console.log('🎯 Image Analysis Service (Tesseract OCR) loaded');