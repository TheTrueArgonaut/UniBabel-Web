/**
 * 🎯 DOCUMENT DETECTION SERVICE - Single Responsibility: Analyze OCR text to detect document type
 */
class DocumentDetectionService {
    constructor() {
        this.patterns = {
            creditCard: {
                keywords: ['visa', 'mastercard', 'american express', 'amex', 'discover', 'credit', 'debit'],
                patterns: [
                    /\b\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\b/, // Credit card number pattern
                    /\b\d{4}\s*\d{6}\s*\d{5}\b/, // Amex pattern
                    /valid\s*thru|expires|exp/i,
                    /cvv|cvc/i
                ]
            },
            driversLicense: {
                keywords: ['driver', 'license', 'licence', 'motor vehicle', 'dmv', 'class', 'endorsements'],
                patterns: [
                    /license\s*#|lic\s*#|dl\s*#/i,
                    /class\s*[a-z]/i,
                    /endorsements/i,
                    /\b(dob|date of birth)\b/i
                ]
            },
            passport: {
                keywords: ['passport', 'united states', 'nationality', 'passport no'],
                patterns: [
                    /passport\s*no/i,
                    /nationality/i,
                    /place of birth/i,
                    /\b[A-Z]{3}\d{6}\b/ // US passport number pattern
                ]
            },
            stateID: {
                keywords: ['identification', 'state id', 'id card', 'state of'],
                patterns: [
                    /identification\s*card/i,
                    /state\s*id/i,
                    /id\s*#/i,
                    /\b(dob|date of birth)\b/i
                ]
            }
        };
    }
    
    async detect(imageData) {
        try {
            const feedback = document.getElementById('id-upload-feedback');
            feedback.textContent = '🔍 Analyzing document type...';
            
            if (!imageData.success || !imageData.text) {
                return {
                    isValid: false,
                    type: 'unreadable',
                    reason: 'Could not extract text from document. Please ensure image is clear.',
                    confidence: 0
                };
            }
            
            const text = imageData.text.toLowerCase();
            const scores = {};
            
            // Analyze text for each document type
            for (const [docType, criteria] of Object.entries(this.patterns)) {
                scores[docType] = this.calculateScore(text, criteria);
            }
            
            console.log('📊 Document type scores:', scores);
            
            // Determine document type based on highest score
            const highestScore = Math.max(...Object.values(scores));
            const detectedType = Object.keys(scores).find(key => scores[key] === highestScore);
            
            // Credit card detection (REJECT)
            if (detectedType === 'creditCard' && scores.creditCard > 0.3) {
                return {
                    isValid: false,
                    type: 'credit_card',
                    reason: 'Credit/debit cards are not accepted for age verification',
                    confidence: scores.creditCard,
                    detectedText: this.extractRelevantText(text, this.patterns.creditCard)
                };
            }
            
            // Valid government ID detection (ACCEPT)
            const validIDTypes = ['driversLicense', 'passport', 'stateID'];
            if (validIDTypes.includes(detectedType) && highestScore > 0.2) {
                const typeMap = {
                    driversLicense: 'drivers_license',
                    passport: 'passport',
                    stateID: 'state_id'
                };
                
                return {
                    isValid: true,
                    type: typeMap[detectedType],
                    reason: 'Valid government-issued identification detected',
                    confidence: highestScore,
                    detectedText: this.extractRelevantText(text, this.patterns[detectedType])
                };
            }
            
            // Insufficient evidence for any document type
            return {
                isValid: false,
                type: 'unclear',
                reason: 'Unable to identify document type. Please ensure you upload a clear government-issued ID.',
                confidence: highestScore,
                scores: scores
            };
            
        } catch (error) {
            console.error('❌ Document detection failed:', error);
            return {
                isValid: false,
                type: 'error',
                reason: 'Error analyzing document type',
                confidence: 0
            };
        }
    }
    
    calculateScore(text, criteria) {
        let score = 0;
        let matches = 0;
        
        // Check keywords
        for (const keyword of criteria.keywords) {
            if (text.includes(keyword.toLowerCase())) {
                score += 0.3;
                matches++;
            }
        }
        
        // Check patterns
        for (const pattern of criteria.patterns) {
            if (pattern.test(text)) {
                score += 0.4;
                matches++;
            }
        }
        
        // Normalize score based on number of criteria
        const totalCriteria = criteria.keywords.length + criteria.patterns.length;
        return matches > 0 ? score / totalCriteria : 0;
    }
    
    extractRelevantText(text, criteria) {
        const relevantLines = [];
        const lines = text.split('\n');
        
        for (const line of lines) {
            for (const keyword of criteria.keywords) {
                if (line.toLowerCase().includes(keyword.toLowerCase())) {
                    relevantLines.push(line.trim());
                    break;
                }
            }
        }
        
        return relevantLines.slice(0, 3); // Return first 3 relevant lines
    }
}

// Export to global scope
window.DocumentDetectionService = DocumentDetectionService;

console.log('🎯 Document Detection Service loaded');