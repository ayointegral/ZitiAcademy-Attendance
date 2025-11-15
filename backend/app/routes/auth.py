from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..models import db, User
from ..utils.helpers import success_response, error_response

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["POST"])
def register():
    """Register a new user"""
    data = request.get_json()

    # Validate required fields
    required_fields = ["username", "email", "password"]
    for field in required_fields:
        if not data.get(field):
            return error_response(f"{field} is required", 400)

    # Check if user already exists
    if User.query.filter_by(email=data["email"]).first():
        return error_response("Email already registered", 409)

    if User.query.filter_by(username=data["username"]).first():
        return error_response("Username already taken", 409)

    # Create new user
    user = User(
        username=data["username"],
        email=data["email"],
        role=data.get("role", "student"),  # Default to student
    )
    user.set_password(data["password"])

    try:
        db.session.add(user)
        db.session.commit()
        return success_response(user.to_dict(), "User registered successfully", 201)
    except Exception as e:
        db.session.rollback()
        return error_response("Registration failed", 500)


@bp.route("/login", methods=["POST"])
def login():
    """Login user and return JWT token"""
    data = request.get_json()

    if not data.get("email") or not data.get("password"):
        return error_response("Email and password are required", 400)

    # Find user by email or username
    user = User.query.filter(
        (User.email == data["email"]) | (User.username == data["email"])
    ).first()

    if not user or not user.check_password(data["password"]):
        return error_response("Invalid credentials", 401)

    # Create access token
    access_token = create_access_token(identity=str(user.id))

    return success_response(
        {"access_token": access_token, "user": user.to_dict()}, "Login successful"
    )


@bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """Get current authenticated user"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return error_response("User not found", 404)

    return success_response(user.to_dict())


@bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """Logout user (client should delete token)"""
    # In a production app, you might want to implement token blacklisting
    return success_response(message="Logged out successfully")
