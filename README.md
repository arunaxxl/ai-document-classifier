1|# AI Document Classifier — POC
2|
3|## Stack
4|- **Backend:** Python FastAPI + LangGraph
5|- **AI Model:** Claude Sonnet 5 (text classification after OCR)
6|- **OCR:** Tesseract (local)
7|- **Frontend:** React + Vite + Tailwind CSS
8|- **Tracking:** MLflow
9|
10|## Quick Start
11|
12|### Backend
13|```bash
14|cd backend
15|python -m venv venv
16|source venv/bin/activate
17|pip install -r requirements.txt
18|cp .env.example .env  # Add your MIMO API key
19|uvicorn app.main:app --reload --port 8000
20|```
21|
22|### Frontend
23|```bash
24|cd frontend
25|npm install
26|npm run dev
27|```
28|
29|### Generate Sample Documents
30|```bash
31|cd backend
32|python app/generate_samples.py
33|```
34|