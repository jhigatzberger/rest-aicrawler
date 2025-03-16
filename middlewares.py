from flask import request, jsonify
import os

# Load API key from environment variables
API_KEY = os.getenv("API_KEY")

def validate_api_key():
    """Middleware to validate the API key in headers"""
    client_key = request.headers.get("x-api-key")
    if client_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    return None  # Return None if valid (no error)

def validate_json_request(required_fields):
    """
    Middleware to validate JSON request body.

    Args:
        required_fields (list): List of required fields in the JSON body.

    Returns:
        None or JSON Response (if validation fails)
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON payload"}), 400
    
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"'{field}' field is required."}), 400
    
    return None  # Return None if valid (no error)
