1|"""
2|FastAPI Main — Document Classification API endpoints.
3|"""
4|
5|import os
6|import json
7|from datetime import datetime
8|from pathlib import Path
9|from fastapi import FastAPI, UploadFile, File, HTTPException
10|from fastapi.middleware.cors import CORSMiddleware
11|from fastapi.staticfiles import StaticFiles
12|from dotenv import load_dotenv
13|
14|load_dotenv()
15|
16|app = FastAPI(
17|    title="AI Document Classifier",
18|    description="AI-powered document classification pipeline",
19|    version="1.0.0",
20|)
21|
22|# CORS — allow React frontend
23|app.add_middleware(
24|    CORSMiddleware,
25|    allow_origins=["http://localhost:5173", "http://localhost:3000"],
26|    allow_credentials=True,
27|    allow_methods=["*"],
28|    allow_headers=["*"],
29|)
30|
31|# ─── Results Storage (in-memory for POC) ──────────────────────────────────
32|
33|classification_history: list[dict] = []
34|
35|# ─── Sample Documents Directory ───────────────────────────────────────────
36|
37|SAMPLE_DIR = Path(__file__).parent / "sample_docs"
38|
39|
40|# ─── Endpoints ────────────────────────────────────────────────────────────
41|
42|@app.get("/")
43|async def root():
44|    return {
45|        "service": "AI Document Classifier",
46|        "status": "running",
47|        "model": os.getenv("MIMO_MODEL", "mimo-v2.5"),
48|    }
49|
50|
51|@app.post("/api/classify")
52|async def classify_document(file: UploadFile = File(...)):
53|    """
54|    Classify an uploaded document.
55|    
56|    Accepts: PDF, PNG, JPG, JPEG, TIFF, BMP
57|    Returns: Classification result with type, confidence, routing decision
58|    """
59|    from app.pipeline import run_pipeline
60|    
61|    # Validate file type
62|    allowed_types = {
63|        "application/pdf": "pdf",
64|        "image/png": "image",
65|        "image/jpeg": "image",
66|        "image/jpg": "image",
67|        "image/tiff": "image",
68|        "image/bmp": "image",
69|    }
70|    
71|    file_type = allowed_types.get(file.content_type)
72|    if not file_type:
73|        raise HTTPException(
74|            status_code=400,
75|            detail=f"Unsupported file type: {file.content_type}. Allowed: {', '.join(allowed_types.keys())}",
76|        )
77|    
78|    # Read file
79|    file_bytes = await file.read()
80|    if len(file_bytes) == 0:
81|        raise HTTPException(status_code=400, detail="Empty file")
82|    
83|    if len(file_bytes) > 10 * 1024 * 1024:  # 10MB limit
84|        raise HTTPException(status_code=400, detail="File too large (max 10MB)")
85|    
86|    # Run pipeline
87|    try:
88|        result = await run_pipeline(file_bytes, file.filename, file_type)
89|    except Exception as e:
90|        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")
91|    
92|    # Store result
93|    result["timestamp"] = datetime.now().isoformat()
94|    classification_history.insert(0, result)
95|    
96|    # Keep only last 100 results
97|    if len(classification_history) > 100:
98|        classification_history.pop()
99|    
100|    return result
101|
102|
103|@app.get("/api/history")
104|async def get_history():
105|    """Get classification history."""
106|    return {
107|        "total": len(classification_history),
108|        "results": classification_history,
109|    }
110|
111|
112|@app.get("/api/stats")
113|async def get_stats():
114|    """Get classification statistics."""
115|    if not classification_history:
116|        return {
117|            "total_classifications": 0,
118|            "type_distribution": {},
119|            "route_distribution": {},
120|            "avg_confidence": 0,
121|            "avg_latency_ms": 0,
122|        }
123|    
124|    type_dist = {}
125|    route_dist = {}
126|    total_confidence = 0
127|    total_latency = 0
128|    
129|    for r in classification_history:
130|        doc_type = r.get("classification", {}).get("type", "unknown")
131|        route = r.get("routing", {}).get("decision", "unknown")
132|        
133|        type_dist[doc_type] = type_dist.get(doc_type, 0) + 1
134|        route_dist[route] = route_dist.get(route, 0) + 1
135|        total_confidence += r.get("classification", {}).get("confidence", 0)
136|        total_latency += r.get("total_latency_ms", 0)
137|    
138|    n = len(classification_history)
139|    
140|    return {
141|        "total_classifications": n,
142|        "type_distribution": type_dist,
143|        "route_distribution": route_dist,
144|        "avg_confidence": round(total_confidence / n, 1),
145|        "avg_latency_ms": round(total_latency / n),
146|    }
147|
148|
149|@app.get("/api/samples")
150|async def list_samples():
151|    """List available sample documents."""
152|    if not SAMPLE_DIR.exists():
153|        return {"samples": [], "message": "Run generate_samples.py first"}
154|    
155|    samples = []
156|    for f in sorted(SAMPLE_DIR.iterdir()):
157|        if f.suffix.lower() in [".png", ".jpg", ".jpeg", ".pdf", ".tiff", ".bmp"]:
158|            samples.append({
159|                "name": f.name,
160|                "path": str(f),
161|                "size_kb": round(f.stat().st_size / 1024, 1),
162|            })
163|    
164|    return {"samples": samples}
165|
166|
167|@app.post("/api/classify-sample/{filename}")
168|async def classify_sample(filename: str):
169|    """Classify a pre-loaded sample document."""
170|    file_path = SAMPLE_DIR / filename
171|    
172|    if not file_path.exists():
173|        raise HTTPException(status_code=404, detail=f"Sample not found: {filename}")
174|    
175|    from app.pipeline import run_pipeline
176|    
177|    file_bytes = file_path.read_bytes()
178|    
179|    # Determine file type
180|    suffix = file_path.suffix.lower()
181|    file_type = "pdf" if suffix == ".pdf" else "image"
182|    
183|    try:
184|        result = await run_pipeline(file_bytes, filename, file_type)
185|    except Exception as e:
186|        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")
187|    
188|    result["timestamp"] = datetime.now().isoformat()
189|    classification_history.insert(0, result)
190|    
191|    return result
192|