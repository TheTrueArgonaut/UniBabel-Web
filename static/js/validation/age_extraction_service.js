/**
 * 🎯 AGE EXTRACTION SERVICE - Single Responsibility: Extract birthdate from OCR text
 */
class AgeExtractionService {
    constructor() {
        this.datePatterns = [
            // MM/DD/YYYY
            /\b(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})\b/g,
            // MM-DD-YYYY
            /\b(\d{1,2})\-(\d{1,2})\-(\d{4})\b/g,
            // YYYY-MM-DD
            /\b(\d{4})[\/\-](\d{1,2})[\/\-](\d{1,2})\b/g,
            // Month DD, YYYY
            /\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2}),?\s+(\d{4})\b/gi,
            // DD Month YYYY
            /\b(\d{1,2})\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})\b/gi
        ];
        
        this.dobKeywords = [
            'dob', 'date of birth', 'birth date', 'born', 'birthday'
        ];
        
        this.monthNames = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12,
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        };
    }
    
    async extract(imageData, documentType) {
        try {
            const feedback = document.getElementById('id-upload-feedback');
            feedback.textContent = '📅 Extracting birthdate...';
            
            if (!imageData.success || !imageData.text) {
                return {
                    success: false,
                    reason: 'No text available for date extraction'
                };
            }
            
            const text = imageData.text;
            console.log('🔍 Searching for birthdate in text:', text);
            
            // Find potential dates near DOB keywords
            const candidateDates = this.findCandidateDates(text);
            console.log('📅 Found candidate dates:', candidateDates);
            
            if (candidateDates.length === 0) {
                return {
                    success: false,
                    reason: 'No birthdate found in document'
                };
            }
            
            // Select most likely birthdate
            const birthdate = this.selectBestCandidate(candidateDates);
            
            if (!birthdate) {
                return {
                    success: false,
                    reason: 'Could not parse valid birthdate'
                };
            }
            
            // Calculate age
            const age = this.calculateAge(birthdate);
            
            // Validate age is reasonable (18-120 years old)
            if (age < 13 || age > 120) {
                return {
                    success: false,
                    reason: `Extracted age (${age}) seems invalid`
                };
            }
            
            return {
                success: true,
                birthdate: this.formatDate(birthdate),
                age: age,
                confidence: 0.85
            };
            
        } catch (error) {
            console.error('❌ Age extraction failed:', error);
            return {
                success: false,
                reason: 'Error extracting age from document'
            };
        }
    }
    
    findCandidateDates(text) {
        const candidates = [];
        const lines = text.split('\n');
        
        // Look for dates near DOB keywords
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].toLowerCase();
            
            // Check if line contains DOB keyword
            const hasDOBKeyword = this.dobKeywords.some(keyword => 
                line.includes(keyword)
            );
            
            if (hasDOBKeyword) {
                // Search this line and adjacent lines for dates
                const searchLines = [
                    lines[i-1] || '',
                    lines[i] || '',
                    lines[i+1] || ''
                ].join(' ');
                
                const datesInContext = this.extractDatesFromText(searchLines);
                candidates.push(...datesInContext.map(date => ({
                    ...date,
                    context: 'near_dob_keyword',
                    priority: 10
                })));
            }
        }
        
        // If no dates near DOB keywords, look for any valid dates
        if (candidates.length === 0) {
            const allDates = this.extractDatesFromText(text);
            candidates.push(...allDates.map(date => ({
                ...date,
                context: 'general',
                priority: 1
            })));
        }
        
        return candidates;
    }
    
    extractDatesFromText(text) {
        const dates = [];
        
        for (const pattern of this.datePatterns) {
            let match;
            while ((match = pattern.exec(text)) !== null) {
                const parsedDate = this.parseMatch(match, pattern);
                if (parsedDate) {
                    dates.push({
                        date: parsedDate,
                        text: match[0],
                        confidence: 0.8
                    });
                }
            }
        }
        
        return dates;
    }
    
    parseMatch(match, pattern) {
        try {
            const patternStr = pattern.toString();
            
            if (patternStr.includes('january|february')) {
                // Month name patterns
                const monthStr = match[1] || match[2];
                const dayStr = match[2] || match[1];
                const yearStr = match[3];
                
                const month = this.monthNames[monthStr.toLowerCase()];
                if (!month) return null;
                
                return new Date(parseInt(yearStr), month - 1, parseInt(dayStr));
            } else {
                // Numeric patterns
                let month, day, year;
                
                if (match[1].length === 4) {
                    // YYYY-MM-DD format
                    year = parseInt(match[1]);
                    month = parseInt(match[2]);
                    day = parseInt(match[3]);
                } else {
                    // MM/DD/YYYY format
                    month = parseInt(match[1]);
                    day = parseInt(match[2]);
                    year = parseInt(match[3]);
                }
                
                // Validate ranges
                if (month < 1 || month > 12) return null;
                if (day < 1 || day > 31) return null;
                if (year < 1900 || year > new Date().getFullYear()) return null;
                
                return new Date(year, month - 1, day);
            }
        } catch (error) {
            console.error('Date parsing error:', error);
            return null;
        }
    }
    
    selectBestCandidate(candidates) {
        if (candidates.length === 0) return null;
        
        // Sort by priority and confidence
        candidates.sort((a, b) => {
            const priorityDiff = b.priority - a.priority;
            if (priorityDiff !== 0) return priorityDiff;
            return b.confidence - a.confidence;
        });
        
        // Return the best candidate that represents a reasonable birthdate
        for (const candidate of candidates) {
            const age = this.calculateAge(candidate.date);
            if (age >= 13 && age <= 120) {
                return candidate.date;
            }
        }
        
        return null;
    }
    
    calculateAge(birthDate) {
        const today = new Date();
        const birth = new Date(birthDate);
        
        let age = today.getFullYear() - birth.getFullYear();
        const monthDiff = today.getMonth() - birth.getMonth();
        
        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
            age--;
        }
        
        return age;
    }
    
    formatDate(date) {
        const year = date.getFullYear();
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const day = date.getDate().toString().padStart(2, '0');
        return `${year}-${month}-${day}`;
    }
}

// Export to global scope
window.AgeExtractionService = AgeExtractionService;

console.log('🎯 Age Extraction Service loaded');