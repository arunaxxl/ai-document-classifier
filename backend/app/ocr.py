"""
OCR Module — Extract text from document images using Tesseract.
"""

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import io
import os


def preprocess_image(image: Image.Image) -> Image.Image:
    """Enhance image quality for better OCR accuracy."""
    # Convert to RGB first if needed
    if image.mode != "RGB":
        image = image.convert("RGB")
    
    # Convert to grayscale
    img = image.convert("L")
    
    # Scale up small images for better OCR
    width, height = img.size
    if width < 1500:
        scale = 1500 / width
        img = img.resize((int(width * scale), int(height * scale)), Image.LANCZOS)
    
    # Increase contrast significantly
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.5)
    
    # Increase sharpness
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(2.0)
    
    # Binarize (threshold) for cleaner text
    img = img.point(lambda x: 0 if x < 140 else 255)
    
    return img


def extract_text_from_image(image_bytes: bytes) -> dict:
    """
    Extract text from an image using Tesseract OCR.
    
    Returns:
        dict with 'text', 'confidence', 'word_count'
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        processed_image = preprocess_image(image)
        
        # Use Tesseract with optimized config
        custom_config = r'--oem 3 --psm 6 -l eng'
        
        # Get detailed OCR data
        data = pytesseract.image_to_data(
            processed_image, 
            output_type=pytesseract.Output.DICT,
            config=custom_config
        )
        
        # Calculate average confidence (excluding -1 entries)
        confidences = [int(c) for c in data["conf"] if int(c) > 0]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Extract full text
        text = pytesseract.image_to_string(processed_image, config=custom_config)
        
        # Clean text
        text = text.strip()
        
        return {
            "text": text,
            "confidence": round(avg_confidence, 1),
            "word_count": len(text.split()),
            "char_count": len(text),
        }
    except Exception as e:
        return {
            "text": "",
            "confidence": 0.0,
            "word_count": 0,
            "char_count": 0,
            "error": str(e),
        }


def extract_text_from_pdf(pdf_bytes: bytes) -> dict:
    """
    Extract text from a PDF file.
    For images in PDFs, converts to image first then OCR.
    """
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        text = "\n".join(text_parts).strip()
        
        if len(text) > 50:
            return {
                "text": text,
                "confidence": 95.0,
                "word_count": len(text.split()),
                "char_count": len(text),
                "method": "direct_text",
            }
        else:
            page = doc[0]
            pix = page.get_pixmap()
            img_bytes = pix.tobytes("png")
            result = extract_text_from_image(img_bytes)
            result["method"] = "ocr"
            return result
    except ImportError:
        return {
            "text": "",
            "confidence": 0.0,
            "word_count": 0,
            "char_count": 0,
            "error": "PyMuPDF not installed. Install with: pip install PyMuPDF",
        }
