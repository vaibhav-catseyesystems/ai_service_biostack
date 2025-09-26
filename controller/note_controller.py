from flask import Blueprint, request
from utils.response import make_response
from services.note_service import convert_audio_to_text

note_bp = Blueprint("note", __name__)

@note_bp.route("/speech-to-text", methods=["POST"])
def speech_to_text_controller():
    try:
        if "file" not in request.files:
            return make_response(401, "failure", None, "No audio file was uploaded")
        file = request.files["file"]
        text = convert_audio_to_text(file)
        return make_response(200, "success", {"transcription": text}, None)
    except ValueError as ve:
        return make_response(400, "failure", None, str(ve))
    except Exception as e:
        return make_response(500, "failure", None, str(e))
