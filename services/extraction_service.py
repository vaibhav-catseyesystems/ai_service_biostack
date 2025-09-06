from utils.text_extractor import extract_text_from_pdf, extract_text_from_image

def extract_content(file_storage):
    try:
        if not file_storage:
            raise ValueError("No file provided")
        filename = file_storage.filename.lower()
        file_bytes = file_storage.read()
        if filename.endswith(".pdf"):
            text = extract_text_from_pdf(file_bytes)
        elif filename.endswith((".png", ".jpg", ".jpeg")):
            text = extract_text_from_image(file_bytes)
        else:
            raise ValueError("Unsupported file type")
        return {
            "extracted_text": text if text else "No text could be extracted",
        }
    except Exception as e:
        print(f"[ERROR] check_document_type failed: {str(e)}")
        raise
