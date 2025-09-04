from utils.text_extractor import extract_text_from_pdf, extract_text_from_image
from utils.classifier import classify_document

def extract_document_content(file_storage):
    try:
        if not file_storage:
            raise ValueError("No file provided")
        
        filename = file_storage.filename.lower()
        file_bytes = file_storage.read()

        # Extract text
        if filename.endswith(".pdf"):
            text = extract_text_from_pdf(file_bytes)
        elif filename.endswith((".png", ".jpg", ".jpeg")):
            text = extract_text_from_image(file_bytes)
        else:
            raise ValueError("Unsupported file type")
        if text==None:
            raise ValueError("No Text could be extracted") 
        return {
            "document_content": text,
        }

    except Exception as e:
        print(f"[ERROR] content extraction failed: {str(e)}")
        raise


def check_document_type(file_storage):
    try:
        if not file_storage:
            raise ValueError("No file provided")

        filename = file_storage.filename.lower()
        file_bytes = file_storage.read()

        # Extract text
        if filename.endswith(".pdf"):
            text = extract_text_from_pdf(file_bytes)
        elif filename.endswith((".png", ".jpg", ".jpeg")):
            text = extract_text_from_image(file_bytes)
        else:
            raise ValueError("Unsupported file type")

        classification, reason = classify_document(text)

        return {
            "extracted_text": text if text else "No text could be extracted",
            "classification": classification,
            "reason": reason
        }

    except Exception as e:
        print(f"[ERROR] check_document_type failed: {str(e)}")
        raise
