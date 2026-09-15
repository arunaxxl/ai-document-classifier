"""
MIMO Classifier — Classify documents using MIMO LLM API.
"""

import httpx
import json
import os
import re
import time
from dotenv import load_dotenv

load_dotenv()

MIMO_API_KEY = os.getenv("MIMO_API_KEY", "")
MIMO_BASE_URL = os.getenv("MIMO_BASE_URL", "https://api.xiaomimimo.com/v1")
MIMO_MODEL = os.getenv("MIMO_MODEL", "mimo-v2.5")

CLASSIFICATION_PROMPT = """Classify this document into exactly ONE category. Respond with ONLY valid JSON, nothing else.

Categories: payslip, bank_statement, tax_return, drivers_license, passport, invoice, utility_bill, trust_deed, company_registration, financial_statement, letter_of_offer, contract, unknown

Response format (copy exactly): {"type":"category_name","confidence":95,"sub_type":"optional","reasoning":"brief explanation"}

DOCUMENT TEXT:
"""


def clean_ocr_text(text: str) -> str:
    """Clean OCR text for better LLM classification."""
    # Remove non-ASCII characters (garbled OCR artifacts)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    # Remove sequences of special characters (OCR noise)
    text = re.sub(r'[^\w\s\.\,\$\:\-\(\)\#\@\/]{3,}', ' ', text)
    # Collapse multiple spaces
    text = re.sub(r'\s+', ' ', text)
    # Remove very short "words" that are likely OCR noise
    words = text.split()
    cleaned_words = [w for w in words if len(w) > 1 or w.isdigit() or w in '$.,:()-#@/']
    return ' '.join(cleaned_words)


def parse_llm_response(raw: str) -> dict:
    """Parse JSON from LLM response, handling various formats."""
    raw = raw.strip()
    
    # Remove markdown code blocks
    if raw.startswith("```"):
        parts = raw.split("```")
        if len(parts) >= 2:
            raw = parts[1].strip()
            if raw.startswith("json"):
                raw = raw[4:].strip()
    
    # Try direct parse
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    
    # Try to find JSON object in the text
    match = re.search(r'\{[^}]+\}', raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    
    # Try to extract just the type from the text
    valid_types = [
        "payslip", "bank_statement", "tax_return", "drivers_license",
        "passport", "invoice", "utility_bill", "trust_deed",
        "company_registration", "financial_statement", "letter_of_offer",
        "contract"
    ]
    raw_lower = raw.lower()
    for doc_type in valid_types:
        if doc_type in raw_lower:
            return {
                "type": doc_type,
                "confidence": 60,
                "sub_type": "",
                "reasoning": f"Extracted type '{doc_type}' from non-JSON response",
            }
    
    return None


async def classify_document(text: str) -> dict:
    """
    Classify a document using the MIMO API.
    """
    if not text or len(text.strip()) < 10:
        return {
            "type": "unknown",
            "confidence": 5,
            "sub_type": "empty_or_unreadable",
            "reasoning": "Document text is empty or too short to classify",
            "latency_ms": 0,
        }
    
    # Clean OCR artifacts
    cleaned_text = clean_ocr_text(text)
    
    start_time = time.time()
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{MIMO_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {MIMO_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": MIMO_MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a document classifier. Always respond with valid JSON only. No markdown. No explanation.",
                        },
                        {
                            "role": "user",
                            "content": CLASSIFICATION_PROMPT + cleaned_text[:2000],
                        },
                    ],
                    "temperature": 0.1,
                    "max_tokens": 2000,
                },
            )
        
        latency_ms = round((time.time() - start_time) * 1000)
        
        if response.status_code != 200:
            return {
                "type": "unknown",
                "confidence": 0,
                "sub_type": "api_error",
                "reasoning": f"MIMO API error: {response.status_code}",
                "latency_ms": latency_ms,
                "error": response.text,
            }
        
        result = response.json()
        content = result["choices"][0]["message"]["content"].strip()
        
        parsed = parse_llm_response(content)
        
        if parsed is None:
            return {
                "type": "unknown",
                "confidence": 0,
                "sub_type": "parse_error",
                "reasoning": "Could not parse LLM response as JSON",
                "latency_ms": latency_ms,
                "raw_response": content[:200],
            }
        
        return {
            "type": parsed.get("type", "unknown"),
            "confidence": min(100, max(0, int(parsed.get("confidence", 0)))),
            "sub_type": parsed.get("sub_type", ""),
            "reasoning": parsed.get("reasoning", ""),
            "latency_ms": latency_ms,
        }
    
    except Exception as e:
        return {
            "type": "unknown",
            "confidence": 0,
            "sub_type": "error",
            "reasoning": str(e),
            "latency_ms": round((time.time() - start_time) * 1000),
        }
