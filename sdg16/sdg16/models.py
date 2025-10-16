from django.db import models
import pytesseract
from PIL import Image
import os
import json
from datetime import datetime

class Evidence(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    submitted_by = models.CharField(max_length=100)
    date_submitted = models.DateTimeField(auto_now_add=True)
    ai_judgment = models.TextField(blank=True)
    
    # 🔥 CRAZY MULTIPLE IMAGE EVIDENCE FIELDS! 🔥
    image_evidence = models.ImageField(upload_to='evidence_images/', blank=True, null=True)
    extracted_text = models.TextField(blank=True, help_text="OCR extracted text from image evidence")
    image_analysis = models.TextField(blank=True, help_text="AI analysis of image content")
    confidence_score = models.FloatField(default=0.0, help_text="OCR confidence score")
    
    # 🚀 NEW MULTI-FILE SUPPORT! 🚀
    multiple_images_data = models.TextField(blank=True, help_text="JSON data for multiple images")
    total_files_count = models.IntegerField(default=0)
    combined_extracted_text = models.TextField(blank=True, help_text="Combined text from all images")
    processing_status = models.CharField(max_length=50, default='pending', choices=[
        ('pending', '⏳ Pending'),
        ('processing', '🔄 Processing'),
        ('completed', '✅ Completed'),
        ('failed', '❌ Failed'),
        ('partial', '⚠️ Partial Success')
    ])
    crazy_effects_enabled = models.BooleanField(default=True, help_text="Enable crazy visual effects")

    def __str__(self):
        return self.title
    
    def extract_text_from_image(self):
        """🔥 CRAZY OCR MAGIC USING PYTESSERACT! 🔥"""
        if self.image_evidence and os.path.exists(self.image_evidence.path):
            try:
                # Open the image using PIL
                image = Image.open(self.image_evidence.path)
                
                # 🚀 PYTESSERACT MAGIC - Extract all text from image!
                extracted_text = pytesseract.image_to_string(image)
                
                # Get detailed OCR data with confidence scores
                ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
                
                # Calculate average confidence score
                confidences = [int(conf) for conf in ocr_data['conf'] if int(conf) > 0]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                
                # Save extracted text and confidence
                self.extracted_text = extracted_text.strip()
                self.confidence_score = avg_confidence
                
                # 🔥 CRAZY ENHANCEMENT - Analyze the extracted text for evidence patterns!
                self.analyze_extracted_content()
                
                return True, extracted_text, avg_confidence
                
            except Exception as e:
                self.extracted_text = f"❌ OCR Error: {str(e)}"
                self.confidence_score = 0.0
                return False, str(e), 0.0
        
        return False, "No image provided", 0.0
    
    def analyze_extracted_content(self):
        """🧠 CRAZY AI ANALYSIS OF EXTRACTED TEXT! 🧠"""
        if not self.extracted_text:
            return
        
        # Look for key evidence patterns
        evidence_keywords = [
            'document', 'certificate', 'license', 'permit', 'contract',
            'agreement', 'receipt', 'invoice', 'letter', 'report',
            'statement', 'declaration', 'testimony', 'witness',
            'signature', 'date', 'official', 'stamp', 'seal'
        ]
        
        corruption_keywords = [
            'bribe', 'corruption', 'illegal', 'fraud', 'embezzlement',
            'kickback', 'money laundering', 'nepotism', 'abuse of power'
        ]
        
        justice_keywords = [
            'court', 'judge', 'lawyer', 'legal', 'law', 'justice',
            'rights', 'violation', 'complaint', 'case', 'trial'
        ]
        
        found_patterns = []
        text_lower = self.extracted_text.lower()
        
        # Check for evidence patterns
        for keyword in evidence_keywords:
            if keyword in text_lower:
                found_patterns.append(f"📋 Evidence Type: {keyword.title()}")
        
        # Check for corruption indicators
        for keyword in corruption_keywords:
            if keyword in text_lower:
                found_patterns.append(f"🚨 Corruption Alert: {keyword.title()}")
        
        # Check for justice-related content
        for keyword in justice_keywords:
            if keyword in text_lower:
                found_patterns.append(f"⚖️ Justice Matter: {keyword.title()}")
        
        # Generate analysis report
        if found_patterns:
            self.image_analysis = f"""
🔍 **AUTOMATED IMAGE ANALYSIS**

**Detected Patterns:**
{chr(10).join(['• ' + pattern for pattern in found_patterns])}

**Text Quality Score:** {self.confidence_score:.1f}%

**SDG 16 Relevance:** {'🟢 HIGH' if any('corruption' in p.lower() or 'justice' in p.lower() for p in found_patterns) else '🟡 MEDIUM'}

**Recommendation:** {'🚨 URGENT REVIEW REQUIRED' if any('corruption' in p.lower() for p in found_patterns) else '📋 Standard Processing'}
            """
        else:
            self.image_analysis = f"""
🔍 **AUTOMATED IMAGE ANALYSIS**

**Status:** Text extracted successfully
**Quality Score:** {self.confidence_score:.1f}%
**Content Type:** General document/image
**SDG 16 Relevance:** 🟡 TO BE DETERMINED

**Next Steps:** Manual review recommended for context analysis
            """

    def save(self, *args, **kwargs):
        """Override save to automatically extract text when image is uploaded"""
        super().save(*args, **kwargs)
        
        # 🔥 AUTOMATIC OCR PROCESSING ON SAVE! 🔥
        if self.image_evidence and not self.extracted_text:
            success, text, confidence = self.extract_text_from_image()
            if success:
                # Save again with the extracted text
                super().save(update_fields=['extracted_text', 'confidence_score', 'image_analysis'])