
import os

class Config:
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))  # 16 MB
    ALLOWED_EXTENSIONS = set(["pdf", "png", "jpg", "jpeg"])
    ALLOWED_MIMETYPES = [ 'application/pdf', 'image/jpeg', 'image/png' ]
    MIN_CHARS = int(os.getenv("MIN_CHARS", 20))
    OCR_LANG_DEFAULT = os.getenv("OCR_LANG_DEFAULT", "eng")
    TESSERACT_CMD = r"D:\\Files\\tesseract\\tesseract.exe"
