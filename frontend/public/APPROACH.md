# Approach

I split the project into a FastAPI backend and a React (Vite) frontend, connected over a REST API.

**Extraction:** PDFs are parsed with `pdfplumber` page-by-page, preserving order rather than collapsing everything into one blob. Images go through Tesseract OCR via `pytesseract`. Both paths are wrapped in error handling, so unreadable, empty, or unsupported files return clear messages instead of silent failures.

**Analysis:** Rather than relying on a paid API for the core scoring, I built a deterministic, rule-based engine that checks six weighted engagement signals — length, CTA, audience interaction, hashtags, hook strength, and emoji usage — and returns a 0–100 score with itemized strengths and suggestions. This keeps the core feature free, fast, and fully explainable (the UI exposes the exact point breakdown).

**AI layer:** As an optional enhancement, I integrated a local Ollama model (`llama3.2:3b`) to rewrite captions for better engagement. The prompt strictly forbids inventing facts, prices, or hashtags, so the rewrite improves tone and structure without fabricating content — an important trust boundary for real marketing use.

**Validation:** File type, size, and emptiness are checked on both client and server, with loading states and inline errors throughout for a smooth UX.
