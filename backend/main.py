from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from analysis import analyze_content
from extract import extract_text_from_pdf, extract_text_from_image
from llm import improve_caption


app = FastAPI(title="Social Media Content Analyzer")


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# File Validation
# --------------------------------------------------

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

ALLOWED_PDF_TYPES = {
    "application/pdf"
}

ALLOWED_IMAGE_TYPES = {
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/webp"
}


# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "Social Media Content Analyzer API running"
    }


# --------------------------------------------------
# Analyze Uploaded File
# --------------------------------------------------

@app.post("/analyze")
async def analyze_file(file: UploadFile = File(...)):

    # 1. Filename validation
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided. Please upload a PDF or image."
        )

    # 2. File type validation
    content_type = file.content_type

    if (
        content_type not in ALLOWED_PDF_TYPES
        and content_type not in ALLOWED_IMAGE_TYPES
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Please upload a PDF, PNG, JPG, JPEG, or WEBP image."
            )
        )

    # 3. Read file
    file_bytes = await file.read()

    # 4. Empty file validation
    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty. Please select a valid file."
        )

    # 5. File size validation
    file_size = len(file_bytes)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File is too large. Maximum allowed size is 10 MB."
        )

    # 6. Extract text
    try:

        if content_type in ALLOWED_PDF_TYPES:

            extracted_text = extract_text_from_pdf(file_bytes)
            source_type = "pdf"

        else:

            extracted_text = extract_text_from_image(file_bytes)
            source_type = "image"

    except RuntimeError as e:

        raise HTTPException(
            status_code=422,
            detail=str(e)
        )

    # 7. Validate extracted text
    if not extracted_text or not extracted_text.strip():

        raise HTTPException(
            status_code=422,
            detail="No readable text was found in the uploaded file."
        )

    # 8. Word count
    word_count = len(extracted_text.split())

    # 9. Engagement analysis
    engagement_analysis = analyze_content(extracted_text)

    # 10. Return response
    return {
        "filename": file.filename,
        "source_type": source_type,
        "file_size_bytes": file_size,
        "word_count": word_count,
        "extracted_text": extracted_text,
        "engagement_analysis": engagement_analysis,
    }


# --------------------------------------------------
# Caption Improvement Request
# --------------------------------------------------

class CaptionRequest(BaseModel):
    text: str


# --------------------------------------------------
# Improve Caption using Local LLM
# --------------------------------------------------

@app.post("/improve-caption")
async def improve_caption_endpoint(request: CaptionRequest):

    # 1. Validate caption
    if not request.text or not request.text.strip():

        raise HTTPException(
            status_code=400,
            detail="No caption text provided."
        )

    # 2. Optional safety limit
    if len(request.text) > 5000:

        raise HTTPException(
            status_code=400,
            detail="Caption is too long. Maximum supported length is 5000 characters."
        )

    # 3. Call local LLM
    try:

        improved = improve_caption(request.text)

        if not improved or not improved.strip():

            raise RuntimeError(
                "The AI model returned an empty response."
            )

        return {
            "original_text": request.text,
            "improved_caption": improved.strip()
        }

    except RuntimeError as e:

        raise HTTPException(
            status_code=503,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=503,
            detail=f"Local AI service unavailable: {str(e)}"
        )