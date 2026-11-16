"""Standardized JSON response utilities."""
from flask import jsonify


def success_response(message="Success", data=None, status_code=200, headers=None):
    """Format and return a standardized success JSON response."""
    payload = {
        "success": True,
        "status": "success",
        "message": message,
        "data": data if data is not None else {}
    }
    resp = jsonify(payload)
    if headers:
        for k, v in headers.items():
            resp.headers[k] = v
    return resp, status_code


def error_response(message="An error occurred", errors=None, status_code=400, headers=None):
    """Format and return a standardized error JSON response."""
    payload = {
        "success": False,
        "status": "error",
        "message": message,
        "errors": errors if errors is not None else {}
    }
    resp = jsonify(payload)
    if headers:
        for k, v in headers.items():
            resp.headers[k] = v
    return resp, status_code

