import pdfplumber
from PIL import Image
import io
import numpy as np
from rapidocr_onnxruntime import RapidOCR


ocr = RapidOCR()


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
        image_array = np.array(image)

        result, _ = ocr(image_array)

        if not result:
            raise ValueError("No text detected in image")

        text = "\n".join(
            item[1] for item in result
        )

        if not text.strip():
            raise ValueError("No text detected in image")

        return text.strip()

    except Exception as e:
        raise RuntimeError(f"OCR extraction failed: {str(e)}")