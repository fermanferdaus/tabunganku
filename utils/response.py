from flask import jsonify


def api_response(success, message, data=None, errors=None, status=200):
    """Format standar JSON response: success, message, data, errors."""
    return jsonify({
        'success': success,
        'message': message,
        'data': data,
        'errors': errors
    }), status
