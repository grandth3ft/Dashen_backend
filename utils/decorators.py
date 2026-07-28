"""
Small helpers layered on top of flask-jwt-extended.

Role is stored as a JWT custom claim at token-creation time, so
@admin_required doesn't need a DB lookup on every request.
"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get("role") != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs)

    return wrapper
