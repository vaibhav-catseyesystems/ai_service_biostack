from flask import Blueprint, request
from services.document_service import check_document_type
from utils.response import make_response

document_bp = Blueprint("document", __name__)

@document_bp.route("/document-type-programatic", methods=["POST"])
def document_type_programatic():
    try:
        if "file" not in request.files:
            return make_response(400, "failure", None, "No file uploaded")
        file = request.files["file"]
        result = check_document_type(file)
        return make_response(200, "success", result, None)
    except ValueError as ve:
        return make_response(400, "failure", None, str(ve))
    except Exception as e:
        return make_response(500, "failure", None, str(e))


@document_bp.route("/document-type-lllm", methods=["POST"])
def document_type_lllm():
    try:
        if "file" not in request.files:
            return make_response(400, "failure", None, "No file uploaded")
        file = request.files["file"]
        result = check_document_type(file)
        return make_response(200, "success", result, None)
    except ValueError as ve:
        return make_response(400, "failure", None, str(ve))
    except Exception as e:
        return make_response(500, "failure", None, str(e))
  