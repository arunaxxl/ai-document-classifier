"""
LangGraph Pipeline — Document classification pipeline with routing logic.
"""

from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from app.ocr import extract_text_from_image, extract_text_from_pdf
from app.classifier import classify_document


# ─── State ────────────────────────────────────────────────────────────────

class PipelineState(TypedDict):
    # Input
    file_bytes: bytes
    file_name: str
    file_type: str  # "image" or "pdf"
    
    # OCR results
    ocr_text: str
    ocr_confidence: float
    ocr_word_count: int
    ocr_method: str
    
    # Classification results
    doc_type: str
    doc_confidence: int
    doc_sub_type: str
    doc_reasoning: str
    classification_latency_ms: int
    
    # Routing
    route: str  # "auto_accept", "review", "reject"
    route_reason: str
    
    # Meta
    total_latency_ms: int
    errors: list


# ─── Nodes ────────────────────────────────────────────────────────────────

async def node_ocr(state: PipelineState) -> dict:
    """Extract text from document using Tesseract OCR."""
    import time
    start = time.time()
    
    try:
        if state["file_type"] == "pdf":
            result = extract_text_from_pdf(state["file_bytes"])
        else:
            result = extract_text_from_image(state["file_bytes"])
        
        latency = round((time.time() - start) * 1000)
        
        return {
            "ocr_text": result.get("text", ""),
            "ocr_confidence": result.get("confidence", 0.0),
            "ocr_word_count": result.get("word_count", 0),
            "ocr_method": result.get("method", "tesseract_ocr"),
            "total_latency_ms": latency,
            "errors": [result["error"]] if "error" in result else [],
        }
    except Exception as e:
        return {
            "ocr_text": "",
            "ocr_confidence": 0.0,
            "ocr_word_count": 0,
            "ocr_method": "error",
            "total_latency_ms": round((time.time() - start) * 1000),
            "errors": [str(e)],
        }


async def node_classify(state: PipelineState) -> dict:
    """Classify document using MIMO LLM."""
    result = await classify_document(state["ocr_text"])
    
    return {
        "doc_type": result.get("type", "unknown"),
        "doc_confidence": result.get("confidence", 0),
        "doc_sub_type": result.get("sub_type", ""),
        "doc_reasoning": result.get("reasoning", ""),
        "classification_latency_ms": result.get("latency_ms", 0),
        "total_latency_ms": state.get("total_latency_ms", 0) + result.get("latency_ms", 0),
    }


async def node_route(state: PipelineState) -> dict:
    """Decide routing based on classification confidence."""
    confidence = state.get("doc_confidence", 0)
    doc_type = state.get("doc_type", "unknown")
    ocr_confidence = state.get("ocr_confidence", 0)
    
    # Routing logic
    if doc_type == "unknown" or confidence < 40:
        return {
            "route": "reject",
            "route_reason": f"Low classification confidence ({confidence}%) or unknown document type",
        }
    elif confidence >= 85 and ocr_confidence >= 80:
        return {
            "route": "auto_accept",
            "route_reason": f"High confidence classification ({confidence}%) with clean OCR ({ocr_confidence}%)",
        }
    elif confidence >= 60:
        return {
            "route": "review",
            "route_reason": f"Medium confidence ({confidence}%) — human review recommended",
        }
    else:
        return {
            "route": "review",
            "route_reason": f"Low confidence ({confidence}%) — requires human verification",
        }


# ─── Conditional Edges ────────────────────────────────────────────────────

def should_classify(state: PipelineState) -> str:
    """Check if OCR produced enough text to classify."""
    if state.get("ocr_word_count", 0) < 3:
        return "skip_classify"
    return "classify"


async def node_skip_classify(state: PipelineState) -> dict:
    """Handle case where OCR failed or produced no meaningful text."""
    return {
        "doc_type": "unknown",
        "doc_confidence": 0,
        "doc_sub_type": "ocr_failed",
        "doc_reasoning": "OCR produced insufficient text for classification",
        "classification_latency_ms": 0,
        "route": "reject",
        "route_reason": "Could not extract readable text from document",
    }


# ─── Build Graph ──────────────────────────────────────────────────────────

def build_pipeline():
    """Build the LangGraph document classification pipeline."""
    
    graph = StateGraph(PipelineState)
    
    # Add nodes
    graph.add_node("ocr", node_ocr)
    graph.add_node("classify", node_classify)
    graph.add_node("skip_classify", node_skip_classify)
    graph.add_node("route", node_route)
    
    # Set entry point
    graph.set_entry_point("ocr")
    
    # Conditional edge from OCR
    graph.add_conditional_edges(
        "ocr",
        should_classify,
        {
            "classify": "classify",
            "skip_classify": "skip_classify",
        },
    )
    
    # Edges
    graph.add_edge("classify", "route")
    graph.add_edge("skip_classify", "route")
    graph.add_edge("route", END)
    
    return graph.compile()


# ─── Pipeline Runner ──────────────────────────────────────────────────────

pipeline = build_pipeline()


async def run_pipeline(file_bytes: bytes, file_name: str, file_type: str) -> dict:
    """
    Run the full classification pipeline on a document.
    
    Args:
        file_bytes: Raw file bytes
        file_name: Original filename
        file_type: "image" or "pdf"
        
    Returns:
        dict with full pipeline results
    """
    import time
    start = time.time()
    
    initial_state: PipelineState = {
        "file_bytes": file_bytes,
        "file_name": file_name,
        "file_type": file_type,
        "ocr_text": "",
        "ocr_confidence": 0.0,
        "ocr_word_count": 0,
        "ocr_method": "",
        "doc_type": "unknown",
        "doc_confidence": 0,
        "doc_sub_type": "",
        "doc_reasoning": "",
        "classification_latency_ms": 0,
        "route": "",
        "route_reason": "",
        "total_latency_ms": 0,
        "errors": [],
    }
    
    result = await pipeline.ainvoke(initial_state)
    
    total_latency = round((time.time() - start) * 1000)
    
    return {
        "file_name": file_name,
        "ocr": {
            "text_preview": result.get("ocr_text", "")[:200],
            "confidence": result.get("ocr_confidence", 0.0),
            "word_count": result.get("ocr_word_count", 0),
            "method": result.get("ocr_method", ""),
        },
        "classification": {
            "type": result.get("doc_type", "unknown"),
            "confidence": result.get("doc_confidence", 0),
            "sub_type": result.get("doc_sub_type", ""),
            "reasoning": result.get("doc_reasoning", ""),
            "latency_ms": result.get("classification_latency_ms", 0),
        },
        "routing": {
            "decision": result.get("route", "unknown"),
            "reason": result.get("route_reason", ""),
        },
        "total_latency_ms": total_latency,
        "errors": result.get("errors", []),
    }
