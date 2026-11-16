"""Standardized JSON response utilities."""
from flask import jsonify


def success_response(message="Success", data=None, status_code=200):
    """Format and return a standardized success JSON response."""
    payload = {
        "success": True,
        "message": message,
        "data": data if data is not None else {}
    }
    return jsonify(payload), status_code


def error_response(message="An error occurred", errors=None, status_code=400):
    """Format and return a standardized error JSON response."""
    payload = {
        "success": False,
        "message": message,
        "errors": errors if errors is not None else {}
    }
    return jsonify(payload), status_code

