from flask import Flask
from controller.document_controller import document_bp
from controller.gemini_controller import gemini_bp
from utils.response import make_response
from utils.logger_config import setup_logging

setup_logging()
def create_app():
    app = Flask(__name__)
    
    # Register Blueprints
    # app.register_blueprint(document_bp, url_prefix="/api")
    app.register_blueprint(gemini_bp, url_prefix="/api")

    @app.route("/health", methods=["GET"])
    def health_check():
        return make_response(200, "success", {"message": "running"}, None)

    # Global Error Handlers
    @app.errorhandler(404)
    def not_found(e):
        return make_response(404, "failure", None, "Resource not found")

    @app.errorhandler(400)
    def bad_request(e):
        return make_response(400, "failure",None, "Bad request")

    @app.errorhandler(500)
    def internal_error(e):
        return make_response(500, "failure", None, "Internal server error")

    return app


if __name__ == "__main__":
    try:
        app = create_app()
        app.run(host="0.0.0.0", port=5105, debug=True)
    except Exception as e:
        print("Error starting app:",e)
