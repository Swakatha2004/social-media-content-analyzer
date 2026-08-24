import pdfplumber
import easyocr
from PIL import Image
import io

# Load OCR reader once when the backend starts.
# English is enough for the social-media assignment.
reader = easyocr.Reader(["en"], gpu=False)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """PDF se text extract karta hai, page-wise."""

    text_parts = []

    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            if len(pdf.pages) == 0:
                raise ValueError("PDF has no pages")

            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()

                if page_text:
                    text_parts.append(
                        f"--- Page {i + 1} ---\n{page_text}"
                    )

        if not text_parts:
            raise ValueError(
                "No extractable text found in PDF "
                "(might be scanned/image-based)"
            )

        return "\n\n".join(text_parts)

    except Exception as e:
        raise RuntimeError(f"PDF extraction failed: {str(e)}")


def extract_text_from_image(file_bytes: bytes) -> str:
    """Image se OCR ke through text extract karta hai."""

    try:
        image = Image.open(io.BytesIO(file_bytes)).convert("RGB")

        # EasyOCR expects an image array
        import numpy as np

        image_array = np.array(image)

        results = reader.readtext(image_array, detail=0)

        text = "\n".join(results)

        if not text.strip():
            raise ValueError("No text detected in image")

        return text.strip()

    except Exception as e:
        raise RuntimeError(f"OCR extraction failed: {str(e)}")