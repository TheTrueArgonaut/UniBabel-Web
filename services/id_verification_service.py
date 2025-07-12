"""
DIY ID Verification Service
Handles automatic ID verification using OCR - NO external API costs!
Windows compatible version without face recognition.
"""

import pytesseract
import cv2
import re
import os
import logging
from datetime import datetime, date
from PIL import Image
from typing import Dict, Any, Optional, Tuple
import numpy as np


class DIYIDVerificationService:
    """
    DIY ID Verification using OCR
    
    Features:
    - Extract birth date from IDs automatically
    - Calculate age and determine user type
    - Zero external API costs
    - Windows compatible (no CMake required)
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Note: Tesseract OCR binary needs to be installed separately
        # For Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
        # If tesseract not in PATH, uncomment and set path:
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        self.logger.info("🤖 DIY ID Verification Service initialized (OCR only)")
    
    def verify_user_id(self, id_image_path: str, selfie_path: str, user_id: int) -> Dict[str, Any]:
        """
        ID verification pipeline using OCR only
        
        Args:
            id_image_path: Path to uploaded ID document
            selfie_path: Path to uploaded selfie (not used in this version)
            user_id: User ID for logging
            
        Returns:
            Verification result with age, user type, and confidence
        """
        try:
            self.logger.info(f"🔍 Starting ID verification for user {user_id}")
            
            # Step 1: Extract data from ID document
            id_data = self._extract_id_data(id_image_path)
            
            # Check if we got any meaningful text
            raw_text = id_data.get('raw_text', '')
            if not raw_text or len(raw_text.strip()) < 10:
                return {
                    'verified': False,
                    'error': 'Could not read text from image. Please ensure the image is clear and well-lit.',
                    'suggestion': 'Try taking a new photo with better lighting, or use the "Birth Date" option to enter your date of birth manually.',
                    'verification_method': 'DIY_OCR_ONLY',
                    'timestamp': datetime.utcnow().isoformat(),
                    'debug_info': f'Raw OCR text length: {len(raw_text)}'
                }
            
            # Step 2: Calculate age from birth date
            age = self._calculate_age(id_data['birth_date'])
            
            # If we can't determine age, provide helpful feedback
            if age == 0:
                return {
                    'verified': False,
                    'error': 'Could not find birth date in the ID. Please try a clearer photo or use manual entry.',
                    'suggestion': 'Make sure your birth date is clearly visible in the photo, or use the "Birth Date" option instead.',
                    'verification_method': 'DIY_OCR_ONLY',
                    'timestamp': datetime.utcnow().isoformat(),
                    'extracted_text': raw_text[:200] + '...' if len(raw_text) > 200 else raw_text,
                    'debug_info': f'Text extracted but no valid birth date found'
                }
            
            # Step 3: Determine user type
            user_type = self._determine_user_type(age)
            
            # Step 4: Overall verification decision (OCR only)
            verification_success = (
                age > 0 and 
                age < 120 and  # Sanity check
                id_data['birth_date'] is not None
            )
            
            result = {
                'verified': verification_success,
                'age': age,
                'user_type': user_type,
                'name': id_data.get('name', ''),
                'birth_date': id_data['birth_date'],
                'face_match_confidence': 0.8,  # Mock value for compatibility
                'face_match': True,  # Always true since we can't verify
                'extracted_text': raw_text[:200] + '...' if len(raw_text) > 200 else raw_text,
                'verification_method': 'DIY_OCR_ONLY',
                'timestamp': datetime.utcnow().isoformat(),
                'note': 'Face verification skipped - OCR only mode'
            }
            
            self.logger.info(
                f"✅ Verification complete for user {user_id}: "
                f"Success={verification_success}, Age={age}, Type={user_type}"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ ID verification failed for user {user_id}: {str(e)}")
            return {
                'verified': False,
                'error': f'Verification failed: {str(e)}',
                'suggestion': 'Please try uploading a clearer photo or use the "Birth Date" option for manual entry.',
                'verification_method': 'DIY_OCR_ONLY',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _extract_id_data(self, image_path: str) -> Dict[str, Any]:
        """Extract text and data from ID document using OCR with professional improvements"""
        
        try:
            # Load and preprocess image for better OCR
            image = cv2.imread(image_path)
            if image is None:
                raise Exception(f"Could not load image: {image_path}")
            
            # Get image dimensions
            height, width = image.shape[:2]
            self.logger.debug(f"📐 Original image size: {width}x{height}")
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # GROK IMPROVEMENT 1: Resize to 300 DPI equivalent for optimal OCR
            target_width = 1200  # Good resolution for OCR
            if width < target_width:
                scale_factor = target_width / width
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                gray = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
                self.logger.debug(f"📐 Resized to: {new_width}x{new_height}")
            
            # GROK IMPROVEMENT 2: Advanced image preprocessing
            processed_images = []
            
            # Method 1: Basic grayscale (already done)
            processed_images.append(("basic_gray", gray))
            
            # Method 2: Binarization with OTSU threshold
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            processed_images.append(("otsu_binary", binary))
            
            # Method 3: Adaptive threshold
            adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            processed_images.append(("adaptive_thresh", adaptive))
            
            # Method 4: Noise reduction with morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            denoised = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            processed_images.append(("denoised", denoised))
            
            # Method 5: Contrast enhancement
            enhanced = cv2.convertScaleAbs(gray, alpha=1.3, beta=0)
            processed_images.append(("enhanced_contrast", enhanced))
            
            # Method 6: Gaussian blur for noise reduction
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)
            processed_images.append(("gaussian_blur", blurred))
            
            # GROK IMPROVEMENT 3: Use proper PSM and OEM modes with character whitelisting
            ocr_configs = [
                '--oem 1 --psm 6',  # LSTM engine, single block
                '--oem 1 --psm 7',  # LSTM engine, single line
                '--oem 1 --psm 8',  # LSTM engine, single word
                '--oem 1 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz/-: .',
                '--oem 3 --psm 6',  # Default engine, single block
                '--oem 3 --psm 7',  # Default engine, single line
            ]
            
            text_results = []
            confidence_scores = []
            
            # Extract text using multiple methods and configs
            for img_name, img in processed_images:
                for config in ocr_configs:
                    try:
                        # Get both text and confidence data
                        data = pytesseract.image_to_data(img, config=config, output_type=pytesseract.Output.DICT)
                        
                        # Filter by confidence score (>70% as recommended by Grok)
                        high_conf_text = []
                        for i, conf in enumerate(data['conf']):
                            if int(conf) > 70:
                                text = data['text'][i]
                                if text.strip():
                                    high_conf_text.append(text)
                        
                        combined_text = ' '.join(high_conf_text)
                        if combined_text.strip():
                            text_results.append(combined_text)
                            avg_confidence = sum(int(c) for c in data['conf'] if int(c) > 0) / len([c for c in data['conf'] if int(c) > 0])
                            confidence_scores.append(avg_confidence)
                            
                            self.logger.debug(f"📊 {img_name} + {config}: {len(combined_text)} chars, avg conf: {avg_confidence:.1f}%")
                        
                    except Exception as e:
                        self.logger.debug(f"OCR attempt failed for {img_name} + {config}: {e}")
                        continue
            
            # GROK IMPROVEMENT 4: Combine all high-confidence text
            if not text_results:
                # Fallback to basic OCR if confidence filtering fails
                self.logger.warning("⚠️ No high-confidence text found, using fallback OCR")
                text_results = [pytesseract.image_to_string(gray, config='--oem 1 --psm 6')]
            
            combined_text = '\n'.join(text_results)
            
            # Extract specific data from combined text
            birth_date = self._find_birth_date(combined_text)
            name = self._find_name(combined_text)
            
            # Calculate overall confidence score
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
            
            self.logger.debug(f"📄 OCR extracted {len(combined_text)} chars with avg confidence: {avg_confidence:.1f}%")
            self.logger.debug(f"📄 Sample text: {combined_text[:500]}...")
            
            # If we still can't find a birth date, log for debugging
            if not birth_date:
                self.logger.warning(f"⚠️ No birth date found. Confidence: {avg_confidence:.1f}%, Text: {combined_text[:300]}")
            
            return {
                'birth_date': birth_date,
                'name': name,
                'raw_text': combined_text,
                'confidence': avg_confidence
            }
            
        except Exception as e:
            self.logger.error(f"❌ OCR extraction failed: {str(e)}")
            return {
                'birth_date': None,
                'name': None,
                'raw_text': f'OCR Error: {str(e)}',
                'confidence': 0
            }
    
    def _find_birth_date(self, text: str) -> Optional[str]:
        """Find birth date patterns in OCR text"""
        
        # Log the text we're searching through
        self.logger.debug(f"🔍 Searching for birth date in text: {text[:300]}...")
        
        # Expanded birth date patterns for better detection
        patterns = [
            # Standard formats with labels
            r'DOB[:\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})',
            r'Date of Birth[:\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})',
            r'Born[:\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})',
            r'Birth[:\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})',
            r'D\.O\.B[:\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})',
            
            # Florida Driver's License specific patterns (general format)
            r'DOB[:\s]*(\d{2}\/\d{2}\/\d{4})',  # Florida format
            r'(\d{2}\/\d{2}\/\d{4})\s*\d{2}SEX',  # Florida DOB before SEX field
            r'(\d{2}\/\d{2}\/\d{4})\s*[MF]',  # DOB before gender
            r'(\d{2}\/\d{2}\/\d{4})\s*\d{2}HGT',  # DOB before height
            r'(\d{2}\/\d{2}\/\d{4})\s*[MF]\s*VETERAN',  # DOB before gender and veteran status
            
            # Various date formats
            r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})',  # MM/DD/YYYY or DD/MM/YYYY
            r'(\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2})',  # YYYY/MM/DD format
            r'(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4})',      # DD/MM/YYYY or MM/DD/YYYY
            
            # Month name formats
            r'(\d{1,2}[\s\-\.](Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s\-\.]\d{4})',
            r'((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s\-\.]\d{1,2}[\s\-\.]\d{4})',
            
            # Full month name formats
            r'(\d{1,2}[\s\-\.](January|February|March|April|May|June|July|August|September|October|November|December)[\s\-\.]\d{4})',
            r'((January|February|March|April|May|June|July|August|September|October|November|December)[\s\-\.]\d{1,2}[\s\-\.]\d{4})',
            
            # Space-separated formats
            r'(\d{1,2}\s+\d{1,2}\s+\d{4})',
            r'(\d{4}\s+\d{1,2}\s+\d{1,2})',
            
            # No separator formats
            r'(\d{8})',  # MMDDYYYY or DDMMYYYY
        ]
        
        for i, pattern in enumerate(patterns):
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                for match in matches:
                    date_str = match if isinstance(match, str) else match[0]
                    self.logger.debug(f"📅 Pattern {i+1} found birth date: {date_str}")
                    
                    # Validate the date makes sense
                    if self._validate_date_string(date_str):
                        self.logger.info(f"✅ Valid birth date found: {date_str}")
                        return date_str
        
        # If no patterns matched, try a more aggressive search
        self.logger.warning(f"⚠️ No birth date pattern found. Trying aggressive search...")
        
        # Look for any 4-digit year that looks like a birth year
        year_matches = re.findall(r'\b(19\d{2}|20\d{2})\b', text)
        if year_matches:
            self.logger.debug(f"🔍 Found potential birth years: {year_matches}")
            
            # Look for dates near these years
            for year in year_matches:
                # Look for MM/DD/YYYY patterns with this year
                nearby_pattern = fr'\b(\d{{1,2}}[\/\-\.]\d{{1,2}}[\/\-\.]{year})\b'
                nearby_matches = re.findall(nearby_pattern, text)
                if nearby_matches:
                    for date_str in nearby_matches:
                        if self._validate_date_string(date_str):
                            self.logger.info(f"✅ Aggressive search found: {date_str}")
                            return date_str
        
        self.logger.warning("⚠️ No birth date pattern found in OCR text")
        return None
    
    def _validate_date_string(self, date_str: str) -> bool:
        """Validate if a date string makes sense"""
        try:
            # Try to parse the date
            parsed_age = self._calculate_age(date_str)
            # Check if age is reasonable (between 13 and 120)
            return 13 <= parsed_age <= 120
        except:
            return False
    
    def _find_name(self, text: str) -> Optional[str]:
        """Extract name from OCR text"""
        
        # Look for name patterns
        name_patterns = [
            r'Name[:\s]*([A-Z][a-z]+ [A-Z][a-z]+)',
            r'([A-Z][A-Z\s]+)',  # All caps names
            r'([A-Z][a-z]+ [A-Z][a-z]+)',  # Title case names
        ]
        
        for pattern in name_patterns:
            matches = re.findall(pattern, text)
            if matches:
                # Return the longest match (likely full name)
                name = max(matches, key=len).strip()
                if len(name) > 3:  # Must be reasonable length
                    self.logger.debug(f"👤 Found name: {name}")
                    return name
        
        return None
    
    def _calculate_age(self, birth_date_str: Optional[str]) -> int:
        """Calculate age from birth date string"""
        
        if not birth_date_str:
            return 0
            
        try:
            # Clean the date string
            birth_date_str = birth_date_str.strip()
            
            # Try different date formats
            date_formats = [
                '%m/%d/%Y',  # MM/DD/YYYY
                '%d/%m/%Y',  # DD/MM/YYYY
                '%m-%d-%Y',  # MM-DD-YYYY
                '%d-%m-%Y',  # DD-MM-YYYY
                '%Y/%m/%d',  # YYYY/MM/DD
                '%Y-%m-%d',  # YYYY-MM-DD
                '%m.%d.%Y',  # MM.DD.YYYY
                '%d.%m.%Y',  # DD.MM.YYYY
                '%Y.%m.%d',  # YYYY.MM.DD
                '%m %d %Y',  # MM DD YYYY
                '%d %m %Y',  # DD MM YYYY
                '%Y %m %d',  # YYYY MM DD
                '%b %d %Y',  # Jan 15 1990
                '%d %b %Y',  # 15 Jan 1990
                '%B %d %Y',  # January 15 1990
                '%d %B %Y',  # 15 January 1990
                '%b %d, %Y', # Jan 15, 1990
                '%B %d, %Y', # January 15, 1990
                '%m/%d/%y',  # MM/DD/YY
                '%d/%m/%y',  # DD/MM/YY
                '%m-%d-%y',  # MM-DD-YY
                '%d-%m-%y',  # DD-MM-YY
                '%y/%m/%d',  # YY/MM/DD
                '%y-%m-%d',  # YY-MM-DD
            ]
            
            # Handle 8-digit format (MMDDYYYY or DDMMYYYY)
            if len(birth_date_str) == 8 and birth_date_str.isdigit():
                # Try both interpretations
                for fmt in ['%m%d%Y', '%d%m%Y']:
                    try:
                        birth_date = datetime.strptime(birth_date_str, fmt).date()
                        age = self._calculate_age_from_date(birth_date)
                        if 13 <= age <= 120:  # Valid age range
                            self.logger.debug(f"🎂 Parsed 8-digit date {birth_date_str} as {birth_date} (age {age})")
                            return age
                    except ValueError:
                        continue
            
            birth_date = None
            for fmt in date_formats:
                try:
                    birth_date = datetime.strptime(birth_date_str, fmt).date()
                    
                    # Handle 2-digit years
                    if birth_date.year < 100:
                        # If year is less than 30, assume 20xx, otherwise 19xx
                        if birth_date.year < 30:
                            birth_date = birth_date.replace(year=birth_date.year + 2000)
                        else:
                            birth_date = birth_date.replace(year=birth_date.year + 1900)
                    
                    break
                except ValueError:
                    continue
            
            if not birth_date:
                self.logger.warning(f"⚠️ Could not parse birth date: {birth_date_str}")
                return 0
            
            # Calculate age
            age = self._calculate_age_from_date(birth_date)
            
            self.logger.debug(f"🎂 Calculated age: {age} from birth date: {birth_date}")
            return age
            
        except Exception as e:
            self.logger.error(f"❌ Age calculation failed: {str(e)}")
            return 0
    
    def _calculate_age_from_date(self, birth_date: date) -> int:
        """Calculate age from a date object"""
        today = date.today()
        age = today.year - birth_date.year
        
        # Adjust if birthday hasn't occurred this year
        if today < birth_date.replace(year=today.year):
            age -= 1
        
        return age
    
    def _determine_user_type(self, age: int) -> str:
        """Determine user type based on age"""
        
        if age < 13:
            return 'CHILD'
        elif age < 18:
            return 'TEEN'
        else:
            return 'ADULT'
    
    def debug_ocr_text(self, image_path: str) -> Dict[str, Any]:
        """Debug method to see raw OCR output"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return {'error': f"Could not load image: {image_path}"}
            
            # Multiple OCR attempts with different settings
            results = {}
            
            # Basic grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            results['basic_gray'] = pytesseract.image_to_string(gray, config='--oem 3 --psm 6')
            
            # Enhanced contrast
            gray_enhanced = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)
            results['enhanced_contrast'] = pytesseract.image_to_string(gray_enhanced, config='--oem 3 --psm 6')
            
            # Bilateral filter + threshold
            gray_filtered = cv2.bilateralFilter(gray, 9, 75, 75)
            _, thresh = cv2.threshold(gray_filtered, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            results['filtered_threshold'] = pytesseract.image_to_string(thresh, config='--oem 3 --psm 6')
            
            # Different PSM modes
            results['psm_8'] = pytesseract.image_to_string(gray, config='--oem 3 --psm 8')
            results['psm_11'] = pytesseract.image_to_string(gray, config='--oem 3 --psm 11')
            results['psm_12'] = pytesseract.image_to_string(gray, config='--oem 3 --psm 12')
            
            # No restrictions
            results['no_restrictions'] = pytesseract.image_to_string(gray, config='--oem 3 --psm 6')
            
            return results
            
        except Exception as e:
            return {'error': f"Debug OCR failed: {str(e)}"}
    
    def get_supported_date_formats(self) -> list:
        """Get all supported date formats for reference"""
        return [
            'MM/DD/YYYY', 'DD/MM/YYYY', 'YYYY/MM/DD',
            'MM-DD-YYYY', 'DD-MM-YYYY', 'YYYY-MM-DD',
            'MM.DD.YYYY', 'DD.MM.YYYY', 'YYYY.MM.DD',
            'MM DD YYYY', 'DD MM YYYY', 'YYYY MM DD',
            'Jan 15 1990', '15 Jan 1990', 'January 15 1990',
            'DOB: MM/DD/YYYY', 'Date of Birth: MM/DD/YYYY',
            'D.O.B: MM/DD/YYYY', 'MMDDYYYY'
        ]
    
    def save_verification_images(self, id_file, selfie_file, user_id: int) -> Tuple[str, str]:
        """Save uploaded verification images securely"""
        
        # Create verification directory
        verification_dir = os.path.join('instance', 'verifications', str(user_id))
        os.makedirs(verification_dir, exist_ok=True)
        
        # Generate secure filenames
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        id_filename = f"id_{timestamp}.jpg"
        selfie_filename = f"selfie_{timestamp}.jpg"
        
        id_path = os.path.join(verification_dir, id_filename)
        selfie_path = os.path.join(verification_dir, selfie_filename)
        
        # Save files
        id_file.save(id_path)
        selfie_file.save(selfie_path)
        
        self.logger.info(f"💾 Saved verification images for user {user_id}")
        
        return id_path, selfie_path
    
    def cleanup_verification_files(self, id_path: str, selfie_path: str):
        """Clean up verification files after processing"""
        
        try:
            if os.path.exists(id_path):
                os.remove(id_path)
            if os.path.exists(selfie_path):
                os.remove(selfie_path)
            
            self.logger.info("🗑️ Cleaned up verification files")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to cleanup files: {str(e)}")
    
    def get_verification_requirements(self) -> Dict[str, Any]:
        """Get requirements for ID verification"""
        
        return {
            'supported_documents': [
                'Driver\'s License',
                'Passport',
                'State ID',
                'National ID Card'
            ],
            'image_requirements': {
                'format': ['JPG', 'PNG', 'JPEG'],
                'max_size_mb': 10,
                'min_resolution': '640x480',
                'quality': 'Clear, well-lit, no glare'
            },
            'selfie_requirements': {
                'format': ['JPG', 'PNG', 'JPEG'],
                'max_size_mb': 5,
                'requirements': 'Face clearly visible, good lighting (not verified in this version)'
            },
            'processing_time': '5-30 seconds',
            'cost': '$0.00 (Free DIY verification)',
            'limitations': 'Face verification disabled due to missing dependencies'
        }


# Global instance
_id_verification_service = DIYIDVerificationService()


def get_id_verification_service() -> DIYIDVerificationService:
    """Get the global ID verification service instance"""
    return _id_verification_service