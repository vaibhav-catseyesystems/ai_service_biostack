from flask import Blueprint,jsonify, request
from services.gemini_service import process_document
from utils.response import make_response
from utils.config import Config
import json

gemini_bp = Blueprint("api", __name__)
  
@gemini_bp.route("/extract-details-ai", methods=["POST"])
def extract_medical_data_controller():
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
        file_bytes = file.read()
        mime_type = file.mimetype
        response_text = process_document(file_bytes, mime_type, relatives_string)
        response_data = json.loads(response_text)
        return jsonify(response_data), 200 #make_response(200, "success", response_data, None)
    except RuntimeError as e:
        return make_response(500, "failure", None, str(e))
    except json.JSONDecodeError:
        return make_response(500, "failure", response_text, "Failed to decode JSON from Gemini response.")
    except Exception as e:
        return make_response(500, "failure", None, f"An unexpected error occurred: {e}")
