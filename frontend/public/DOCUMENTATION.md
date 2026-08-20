# Social Media Content Analyzer — Documentation

A full-stack tool that takes a PDF or scanned image of a social media post, extracts the text, scores it against engagement best-practices, and (optionally) rewrites it using a local LLM.

Built for the Unthinkable Solutions Software Engineering Assessment by **Swakatha Bandyopadhyay** (Reg. No. 23BCE0087).

---

## 1. Overview

Marketers and content creators often have a caption sitting in a screenshot, an exported PDF, or a scanned flyer, and want to know whether it will perform well before posting. This app automates that check:

1. Upload a file (PDF or image).
2. Backend extracts the raw text.
3. A rule-based engine scores the text out of 100 across six engagement factors.
4. The user sees strengths, suggestions, and a full points breakdown.
5. Optionally, a local LLM rewrites the caption to be more engaging — without inventing new facts.

---

## 2. System Architecture

```
┌─────────────────┐        multipart/form-data        ┌──────────────────┐
│   React (Vite)   │ ─────────────────────────────────▶│   FastAPI backend │
│   Frontend       │                                    │                  │
│                  │◀───────────── JSON ─────────────── │  /analyze        │
│                  │                                    │  /improve-caption│
└─────────────────┘                                    └──────┬───────────┘
                                                                │
                                        ┌───────────────────────┼───────────────────────┐
                                        ▼                       ▼                       ▼
                                  extract.py              analysis.py              llm.py
                                  (pdfplumber /            (rule-based             (Ollama /
                                   pytesseract OCR)         scoring engine)         llama3.2:3b)
```

- **Frontend** handles file selection, validation, UI states, and rendering results.
- **Backend** does all heavy lifting: extraction, validation, scoring, and the optional AI rewrite.
- **No database** — the app is stateless; each request is processed and returned independently.

---

## 3. Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React (Vite), Axios, plain CSS |
| Backend | FastAPI, Uvicorn |
| PDF text extraction | pdfplumber |
| OCR (image text extraction) | pytesseract (Tesseract OCR engine) + Pillow |
| AI caption rewrite | Ollama, running `llama3.2:3b` locally |
| Communication | REST API over JSON / multipart form-data |

---

## 4. Features

### 4.1 Document Upload
- Drag-and-drop area or click-to-browse file picker.
- Accepted formats: PDF, PNG, JPG, JPEG, WEBP.
- Max file size: 10 MB.
- Validation happens on **both** frontend (immediate feedback) and backend (authoritative check, since the frontend can be bypassed).

### 4.2 Text Extraction
- **PDFs:** parsed page-by-page with `pdfplumber`; each page's text is kept under a `--- Page N ---` marker so structure isn't lost.
- **Images:** run through Tesseract OCR via `pytesseract`. Works on scanned documents, screenshots, and photographed text.
- Extraction failures (corrupt file, no pages, unreadable scan, no text detected) raise clear, specific error messages rather than generic 500s.

### 4.3 Engagement Analysis (Rule-Based Scoring)
A deterministic scoring engine — no external API calls, so it's free and instant. It checks the extracted text against six weighted signals:

| Check | Points | Logic |
|---|---|---|
| Concise content length | 20 | Ideal range: 10–80 words |
| Call-to-action | 20 | Regex match against CTA phrases (buy, shop, subscribe, follow, click, learn more, visit, download, try, join, share, comment, sign up, order, get yours) |
| Audience interaction | 20 | Presence of a question mark or interaction phrases (tell us, let us know, what do you think, comment below, etc.) |
| Relevant hashtags | 15 | Presence of `#hashtag` patterns |
| Opening hook | 15 | First sentence starts with an attention-grabbing word/phrase (new, discover, breaking, why, how, did you know, etc.) |
| Emoji usage | 10 | Presence of emoji Unicode ranges |

**Score = (passed checks / 6) × 100**, rounded.

Output includes:
- Overall score (0–100)
- Word count
- Boolean flags for each check
- A **strengths** list (what the post does well)
- A **suggestions** list (what to improve, in plain language)

### 4.4 AI Caption Rewrite (Optional, Local LLM)
- Triggered by the "✦ Improve Caption" button after analysis.
- Sends the extracted text to a locally running Ollama instance (`llama3.2:3b`).
- The prompt enforces strict rules: preserve every fact, never invent details (products, prices, dates, discounts, locations), never add new hashtags, only improve hook/wording/structure/CTA, keep it concise.
- This is a trust boundary — the rewrite improves *how* something is said, never *what* is claimed.
- Does **not** affect the engagement score (score is purely rule-based and shown separately).

### 4.5 Score Methodology Panel
- Collapsible "HOW IS THIS SCORE CALCULATED?" section.
- Shows the exact points breakdown so results aren't a black box.

### 4.6 UX & Error Handling
- Loading spinner during extraction ("extracting_text( ) — please wait").
- Inline error boxes for upload failures, extraction failures, and LLM failures — each with a specific, human-readable message.
- "Analyze Another File" button resets all state cleanly.
- Same file can be re-selected consecutively (input value is cleared after each pick).

---

## 5. Use Cases

### Use Case 1 — Analyzing a scanned/screenshotted social post
**Actor:** Content creator with a screenshot of a draft caption.
**Flow:**
1. User drags a PNG screenshot onto the dropzone.
2. Backend OCR-extracts the text.
3. Engagement analysis returns a score with strengths/suggestions.
4. User reads suggestions (e.g., "add a call-to-action") and manually edits their caption before posting.

### Use Case 2 — Analyzing a PDF export of a campaign post
**Actor:** Marketing team member reviewing a client's post exported as a PDF.
**Flow:**
1. User uploads the PDF.
2. `pdfplumber` extracts text per page.
3. Score and breakdown are generated instantly.
4. Team uses the breakdown to justify edits to stakeholders (transparent scoring, not a black-box AI opinion).

### Use Case 3 — Getting an AI-improved rewrite
**Actor:** User who wants a stronger version of their caption, not just a critique.
**Flow:**
1. After analysis, user clicks "Improve Caption."
2. Local LLM rewrites the caption — improving hook, structure, and CTA while preserving every fact.
3. User copies the improved caption for direct use.

### Use Case 4 — Invalid or unsupported file
**Actor:** User accidentally uploads a `.docx` or a 15 MB image.
**Flow:**
1. Frontend validation catches the type/size and shows an immediate error, avoiding a wasted network call.
2. If bypassed (e.g., API called directly), backend re-validates and returns a `400`/`413` with a specific message.

### Use Case 5 — Scanned document with no readable text
**Actor:** User uploads a blank page, a heavily corrupted scan, or a non-text image.
**Flow:**
1. Extraction runs but returns empty/whitespace-only text.
2. Backend returns a `422` with "No readable text was found in the uploaded file."
3. Frontend surfaces this as an inline error instead of crashing or showing an empty score.

### Use Case 6 — Ollama not running
**Actor:** User clicks "Improve Caption" but hasn't started Ollama locally.
**Flow:**
1. Backend's `requests.post` to Ollama raises a `ConnectionError`.
2. Backend returns a `503` with "Ollama is not running. Please start Ollama."
3. Frontend shows this in the caption section without affecting the already-displayed engagement score.

---

## 6. API Reference

### `GET /`
Health check.
```json
{ "status": "ok", "message": "Social Media Content Analyzer API running" }
```

### `POST /analyze`
**Body:** `multipart/form-data` with a `file` field (PDF or image).

**Validation order:** filename present → content-type allowed → file non-empty → size ≤ 10 MB → text successfully extracted → extracted text non-empty.

**Success (200):**
```json
{
  "filename": "post.png",
  "source_type": "image",
  "file_size_bytes": 98112,
  "word_count": 8,
  "extracted_text": "SC Hydro Flask: A new free gift every day",
  "engagement_analysis": {
    "score": 0,
    "word_count": 8,
    "has_cta": false,
    "has_question": false,
    "has_hashtags": false,
    "has_hook": false,
    "has_emoji": false,
    "strengths": [],
    "suggestions": [ "..." ]
  }
}
```

**Error responses:**
| Status | Cause |
|---|---|
| 400 | Missing filename, unsupported file type, or empty file |
| 413 | File exceeds 10 MB |
| 422 | Extraction failed, or no readable text found |

### `POST /improve-caption`
**Body:** `{ "text": "<caption text>" }` (max 5000 characters).

**Success (200):**
```json
{ "original_text": "...", "improved_caption": "..." }
```

**Error responses:**
| Status | Cause |
|---|---|
| 400 | Empty text, or text over 5000 characters |
| 503 | Ollama not running, request timed out, or LLM returned empty response |

---

## 7. Known Limitations

- **Local LLM dependency:** the rewrite feature only works when Ollama is running on the same machine as the backend. In a hosted deployment without Ollama, this feature will return a 503 — the core analysis still works fine.
- **OCR accuracy:** depends on Tesseract's out-of-the-box accuracy; low-quality scans, unusual fonts, or handwriting may extract poorly.
- **Rule-based scoring, not sentiment/virality prediction:** the score reflects adherence to structural best practices (CTA, hook, hashtags, etc.), not a guarantee of real-world engagement.
- **No persistence:** results aren't saved; refreshing the page loses the analysis.
- **CORS is open (`*`)** in the current config — fine for an assessment/demo, but should be restricted to the frontend's actual origin in production.

---

## 8. Future Improvements

- Persist analysis history per user (would need auth + a database).
- Support multi-page PDF post decks (carousel-style content) with per-slide scoring.
- Add platform-specific scoring presets (Instagram vs. LinkedIn vs. X have different best practices).
- Swap/add a hosted LLM fallback when Ollama isn't available, so the rewrite feature works in deployed environments too.
