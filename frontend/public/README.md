# Social Media Content Analyzer

A full-stack web app that extracts text from uploaded PDFs or scanned images and analyzes it for social media engagement quality — then optionally rewrites the caption using a local LLM.

Built for the Unthinkable Solutions Software Engineering Assessment.

**Live app:** [ADD_YOUR_DEPLOYED_URL_HERE]
**Repo:** [ADD_YOUR_GITHUB_URL_HERE]

---

## Features

- **Document upload** — drag-and-drop or click-to-browse, supports PDF, PNG, JPG, JPEG, WEBP (max 10 MB)
- **Text extraction**
  - PDFs parsed page-by-page with `pdfplumber`, preserving page structure
  - Images processed with Tesseract OCR (`pytesseract`)
- **Engagement analysis** — deterministic, rule-based scoring (no external API needed) across 6 weighted checks:
  - Concise content length — 20 pts
  - Call-to-action — 20 pts
  - Audience interaction — 20 pts
  - Relevant hashtags — 15 pts
  - Opening hook — 15 pts
  - Emoji usage — 10 pts
  - Total: 100 pts, with a strengths/suggestions breakdown
- **AI caption rewrite (optional)** — sends the extracted text to a locally running Ollama model (`llama3.2:3b`) to produce a more engaging rewrite, with strict prompting to prevent fabricated facts, prices, or hashtags
- **UX details** — loading states, inline error handling, expandable "how is this score calculated" panel, file validation on both client and server

---

## Tech Stack

**Frontend:** React (Vite), Axios
**Backend:** FastAPI (Python), Uvicorn
**Text extraction:** pdfplumber, pytesseract + Pillow
**AI rewrite:** Ollama running `llama3.2:3b` locally

---

## Project Structure

```
├── frontend/
│   ├── src/
│   │   ├── App.jsx        # main UI + state management
│   │   ├── main.jsx
│   │   └── index.css
│   └── index.html
└── backend/
    ├── main.py             # FastAPI routes: /analyze, /improve-caption
    ├── extract.py          # PDF + OCR text extraction
    ├── analysis.py         # rule-based engagement scoring
    └── llm.py              # Ollama integration for caption rewrite
```

---

## Running Locally

### Prerequisites
- Python 3.10+
- Node.js 18+
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) installed and on PATH
- [Ollama](https://ollama.com) installed, with the model pulled:
  ```bash
  ollama pull llama3.2:3b
  ollama serve
  ```

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install fastapi uvicorn python-multipart pdfplumber pytesseract pillow requests
uvicorn main:app --reload
```
Backend runs at `http://127.0.0.1:8000`.

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Frontend runs at `http://localhost:5173`.

> Note: the caption-improvement feature requires Ollama running locally. Everything else (upload, extraction, scoring) works without it.

---

## API Endpoints

### `POST /analyze`
Accepts a `multipart/form-data` file upload (PDF or image).

Response:
```json
{
  "filename": "post.png",
  "source_type": "image",
  "file_size_bytes": 98304,
  "word_count": 8,
  "extracted_text": "...",
  "engagement_analysis": {
    "score": 45,
    "word_count": 8,
    "has_cta": false,
    "has_question": false,
    "has_hashtags": false,
    "has_hook": false,
    "has_emoji": false,
    "strengths": [...],
    "suggestions": [...]
  }
}
```

### `POST /improve-caption`
Accepts `{ "text": "..." }`, returns `{ "original_text": "...", "improved_caption": "..." }` using the local LLM.

---

## Approach

See [`APPROACH.md`](./APPROACH.md) for the 200-word write-up.

---

## Author

**Swakatha Bandyopadhyay**
Reg. No. 23BCE0087
