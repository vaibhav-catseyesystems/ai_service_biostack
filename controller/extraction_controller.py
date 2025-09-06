from flask import Blueprint, request
from utils.response import make_response
from services.extraction_service import extract_content

extraction_bp = Blueprint("extraction", __name__)
  
@extraction_bp.route("/extract", methods=["POST"])
def extract_content_route():
    # try:
    if "file" not in request.files:
        return make_response(401, "failure", None, "No file was uploaded")
    file = request.files["file"]
    result = extract_content(file)
    return make_response(200, "success", result, None)
    # except ValueError as ve:
    #     return make_response(400, "failure", None, str(ve))
    # except Exception as e:
    #     return make_response(500, "failure", None, str(e))
