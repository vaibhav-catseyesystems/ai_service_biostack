import pytesseract
from PIL import Image
import fitz
from io import BytesIO

# configure tesseract path for Windows (if needed)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_image(file_bytes: bytes) -> str:
    """
    Extract text from an image using Tesseract OCR.
    Supports file bytes instead of file path.
    """
    try:
        image = Image.open(BytesIO(file_bytes))
        text = pytesseract.image_to_string(image, lang="eng")
        return text.strip()
    except Exception as e:
        raise RuntimeError(f"OCR Error (Image): {e}")


def extract_text_from_pdf_textual(file_bytes: bytes) -> str:
    """
    Try to extract text directly from a textual PDF.
    """
    try:
        doc = fitz.open("pdf", file_bytes)
        full_text = []
        for i, page in enumerate(doc, start=1):
            text = page.get_text("text")
            if text.strip():
                full_text.append(f"\n--- Page {i} ---\n{text.strip()}")
        doc.close()
        return "\n".join(full_text).strip()
    except Exception as e:
        raise RuntimeError(f"OCR Error (Textual PDF): {e}")


def pdf_to_images(file_bytes: bytes):
    """
    Convert PDF bytes to images for OCR fallback.
    """
    try:
        images = []
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            for page_num in range(len(doc)):
                pix = doc[page_num].get_pixmap(dpi=300)
                img = Image.open(BytesIO(pix.tobytes("png")))
                images.append(img)
        return images
    except Exception as e:
        raise RuntimeError(f"PDF to image conversion failed: {e}")

def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = extract_text_from_pdf_textual(file_bytes)

    if text and len(text.strip()) > 50:
        return text
    # fallback OCR
    try:
        pages = pdf_to_images(file_bytes)
        full_text = []
        for i, page in enumerate(pages, start=1):
            text = pytesseract.image_to_string(page, lang="eng")
            full_text.append(f"\n--- OCR Page {i} ---\n{text.strip()}")
        return "\n".join(full_text).strip()
    except Exception as e:
        raise RuntimeError(f"OCR Error (Fallback Image OCR): {e}")
