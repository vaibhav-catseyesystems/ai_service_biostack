from flask import Blueprint, request, jsonify
from utils.response import make_response
from services.extraction_service import extract_content, check_pdf_protection
from services.gemini_service import extract_password_from_text
import logging
logger = logging.getLogger(__name__)

extraction_bp = Blueprint("extraction", __name__)
  
@extraction_bp.route("/extract", methods=["POST"])
def extract_content_route():
    try:
        if "file" not in request.files:
            return make_response(401, "failure", None, "No file was uploaded")
        file = request.files["file"]
        result = extract_content(file)
        return make_response(200, "success", result, None)
    except ValueError as ve:
        return make_response(400, "failure", None, str(ve))
    except Exception as e:
        return make_response(500, "failure", None, str(e))

@extraction_bp.route("/check-pdf-protection", methods=["POST"])
def check_pdf_protection_controller():
    try:
        if "file" not in request.files:
            return make_response(401, "failure", None, "No file was uploaded")
        file = request.files["file"]
        file_bytes = file.read()
        result = check_pdf_protection(file_bytes=file_bytes)
        return jsonify(result)
    except ValueError as ve:
        return make_response(400, "failure", None, str(ve))
    except Exception as e:
        return make_response(500, "failure", None, str(e))

@extraction_bp.route("/pdf-password", methods=["POST"])
def get_pdf_password_controller():
    try:
        data = request.get_json()
        if not data or "body" not in data:
            logger.error(f"extract_password_from_text: 400: please provide file contents, invalid request ")
            return make_response(400, "failure", None, "please provide file contents")
        raw_text = data["body"]
        result = extract_password_from_text(raw_text=raw_text)
        logger.info(f"extract_password_from_text: raw_text {raw_text} password: {result}")
        return jsonify(result)
    except ValueError as ve:
        logger.error(f"extract_password_from_text: 400: {str(ve)} ")
        return make_response(400, "failure", None, str(ve))
    except Exception as e:
        logger.error(f"extract_password_from_text: 500: {str(e)} ")
        return make_response(500, "failure", None, str(e))
