"""
Authentication routes: register, login, profile.

Passwords are hashed with Bcrypt before ever touching the database.
JWTs carry the user's role as a custom claim so downstream routes
(e.g. @admin_required) don't need an extra DB query per request.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from extensions import db, bcrypt
from models import User
from utils.validators import is_valid_email, is_valid_password

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    full_name = (data.get("full_name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    phone = (data.get("phone") or "").strip()
    password = data.get("password") or ""

    if not full_name or not email or not password:
        return jsonify({"error": "full_name, email and password are required"}), 400

    if not is_valid_email(email):
        return jsonify({"error": "Please provide a valid email address"}), 400

    if not is_valid_password(password):
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "An account with this email already exists"}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    user = User(
        full_name=full_name,
        email=email,
        phone=phone,
        password=hashed_password,
        role="user",
    )
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})

    return jsonify({"message": "Account created successfully", "token": token, "user": user.to_dict()}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})

    return jsonify({"message": "Logged in successfully", "token": token, "user": user.to_dict()}), 200


@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"user": user.to_dict(include_stats=True)}), 200


@auth_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json(silent=True) or {}

    full_name = data.get("full_name")
    email = data.get("email")
    phone = data.get("phone")
    password = data.get("password")

    if full_name:
        user.full_name = full_name.strip()

    if phone is not None:
        user.phone = phone.strip()

    if email:
        email = email.strip().lower()
        if not is_valid_email(email):
            return jsonify({"error": "Please provide a valid email address"}), 400
        existing = User.query.filter_by(email=email).first()
        if existing and existing.id != user.id:
            return jsonify({"error": "This email is already in use"}), 409
        user.email = email

    if password:
        if not is_valid_password(password):
            return jsonify({"error": "Password must be at least 6 characters"}), 400
        user.password = bcrypt.generate_password_hash(password).decode("utf-8")

    db.session.commit()

    return jsonify({"message": "Profile updated successfully", "user": user.to_dict(include_stats=True)}), 200
