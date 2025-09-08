from flask import Blueprint,jsonify, request
from services.gemini_service import process_document, extract_document_details
from utils.response import make_response
from utils.config import Config
import json
import logging

logger = logging.getLogger(__name__)

gemini_bp = Blueprint("gemini", __name__)
  
@gemini_bp.route("/extract-details-ai", methods=["POST"])
def extract_details_ai_controller():
    if 'file' not in request.files:
        return make_response(400, "failure", None, "No file part in the request")
    
    if 'relatives_string' not in request.form:
        return make_response(400, "failure", None, "No 'relatives_string' provided")

    file = request.files['file']
    relatives_string = request.form['relatives_string']

    if file.filename == '':
        return make_response(400, "failure", None, "No selected file")
    mime_type = file.mimetype
    if mime_type not in Config.ALLOWED_MIMETYPES:
        return make_response(415, "failure", None, "Invalid file type. Only PDF and image files are allowed.")
    try:
        logger.info(f"Getting response for file: {file.filename} relatives: {relatives_string}")
        file_bytes = file.read()
        response_text = process_document(file_bytes, mime_type, relatives_string)
        response_data = json.loads(response_text)
        return jsonify(response_data), 200 #make_response(200, "success", response_data, None)
    except RuntimeError as e:
        return make_response(500, "failure", None, str(e))
    except json.JSONDecodeError:
        return make_response(500, "failure", response_text, "Failed to decode JSON from Gemini response.")
    except Exception as e:
        return make_response(500, "failure", None, f"An unexpected error occurred: {e}")

@gemini_bp.route("/medical_report_extract", methods=["POST"])
def medical_report_extract_controller():
    if 'file' not in request.files:
        return make_response(400, "failure", None, "No file part in the request")
    if 'document_type' not in request.form:
        return make_response(400, "failure", None, "No 'document_type' provided")
    if 'relatives_string' not in request.form:
        return make_response(400, "failure", None, "No 'relatives_string' provided")

    file = request.files['file']
    if file.filename == '':
        return make_response(400, "failure", None, "No selected file")
    mime_type = file.mimetype
    if mime_type not in Config.ALLOWED_MIMETYPES:
        return make_response(415, "failure", None, "Invalid file type. Only PDF and image files are allowed.")
    
    document_type = request.form['document_type']
    relatives_string = request.form['relatives_string']
    response_text = None
    try:
        file_bytes = file.read()
        response_text = extract_document_details( file_bytes=file_bytes, mime_type=mime_type, relatives_string=relatives_string, document_type=document_type)
        response_data = json.loads(response_text)
        return jsonify(response_data), 200 
    except RuntimeError as e:
        return make_response(500, "failure", None, str(e))
    except json.JSONDecodeError:
        return make_response(500, "failure", None, f"Failed to decode JSON from Gemini response. {response_text}")
    except Exception as e:
        return make_response(500, "failure", None, f"An unexpected error occurred: {e}")
