from flask import Blueprint, request
from services.document_service import check_document_type_programatic,check_document_owner_name_programatic
from utils.response import make_response

document_bp = Blueprint("document", __name__)

@document_bp.route("/document-type-programatic", methods=["POST"])
def document_type_programatic():
    try:
        data = request.get_json()
        if not data or "document_content" not in data:
            return make_response(400, "failure", None, "please provide file contents")
        file_content = data["document_content"]
        result = check_document_type_programatic(file_content=file_content)
        return make_response(200, "success", result, None)
    except ValueError as ve:
        return make_response(400, "failure", None, str(ve))
    except Exception as e:
        return make_response(500, "failure", None, str(e))

@document_bp.route("/document-owner-programatic", methods=["POST"])
def document_owner_programatic():
    try:
        data = request.get_json()
        if not data or "document_content" not in data:
            return make_response(400, "failure", None, "please provide file contents")
        if not data or "document_type" not in data:
            return make_response(400, "failure", None, "please provide document type")
        file_content = data["document_content"]
        document_type = data["document_type"]
        result = check_document_owner_name_programatic(file_content=file_content,document_type=document_type)
        result = {"document_owner": result}
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
        result = check_document_type_programatic(file)
        return make_response(200, "success", result, None)
    except ValueError as ve:
        return make_response(400, "failure", None, str(ve))
    except Exception as e:
        return make_response(500, "failure", None, str(e))
  