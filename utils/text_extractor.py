import tempfile
import pytesseract
from PIL import Image
import fitz
from io import BytesIO
from paddleocr import PaddleOCR
import os

OCR_ENGINE = os.getenv("OCR_ENGINE", "paddleocr").lower()

# configure tesseract path for Windows (if needed)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
_paddle_ocr = None

def get_paddle_ocr():
    global _paddle_ocr
    if _paddle_ocr is None:
        _paddle_ocr = PaddleOCR(
            use_doc_orientation_classify=False, 
            use_doc_unwarping=False, 
            use_textline_orientation=False) 
    return _paddle_ocr


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
        raise RuntimeError(f"Textual PDF extraction failed: {e}")

def extract_text_from_image(file_bytes: bytes) -> str:
    """
    Extract text from an image using OCR (Tesseract or PaddleOCR).
    """
    try:
        image = Image.open(BytesIO(file_bytes))
        if OCR_ENGINE == "tesseract":
            text = pytesseract.image_to_string(image, lang="eng")
        elif OCR_ENGINE == "paddleocr":
            ocr = get_paddle_ocr()
            tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) 
            tmp_path = tmp.name
            tmp.close()
            try:
                image.save(tmp_path, format="JPEG")
                result = ocr.predict(tmp_path)
            finally:
                os.unlink(tmp_path)            
            
            if not result:
                return ""
            for res in result:
                text=" ".join(res['rec_texts'])
        else:
            raise ValueError(f"OCR engine '{OCR_ENGINE}' not supported")
        return text.strip()
    except Exception as e:
        raise RuntimeError(f"OCR extraction failed: {e}")


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
            buf = BytesIO()
            page.save(buf, format="PNG")
            ocr_text = extract_text_from_image(buf.getvalue())
            full_text.append(f"\n--- OCR Page {i} ---\n{ocr_text.strip()}")
        return "\n".join(full_text).strip()
    except Exception as e:
        raise RuntimeError(f"OCR Error (Fallback Image OCR): {e}")
