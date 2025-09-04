from flask import jsonify


def make_response(status_code=200, status="success", content=None, error=None):
    """
    Create a standard API response
    """
    # if content is None:
    #     content = {}
    # if error is None:
    #     error = {}
    response = {
        "status_code": status_code,
        "status": status,
        "content": content,
        "error": error,
    }
    return jsonify(response), status_code
