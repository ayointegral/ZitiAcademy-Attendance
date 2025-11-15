from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, User
from ..utils.helpers import success_response, error_response, paginate
from ..utils.decorators import admin_required

bp = Blueprint("users", __name__)


@bp.route("", methods=["GET"])
@jwt_required()
@admin_required
def get_users():
    """Get all users (admin only)"""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    role = request.args.get("role")
    search = request.args.get("search")

    query = User.query

    if role:
        query = query.filter_by(role=role)

    if search:
        query = query.filter(
            (User.username.ilike(f"%{search}%")) | (User.email.ilike(f"%{search}%"))
        )

    result = paginate(query.order_by(User.created_at.desc()), page, per_page)
    return success_response(result)


@bp.route("/<int:user_id>", methods=["GET"])
@jwt_required()
@admin_required
def get_user(user_id):
    """Get user by ID (admin only)"""
    user = User.query.get_or_404(user_id)
    return success_response(user.to_dict())


@bp.route("/<int:user_id>", methods=["PUT"])
@jwt_required()
@admin_required
def update_user(user_id):
    """Update user (admin only)"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    # Update fields
    if "username" in data:
        # Check username uniqueness
        existing = User.query.filter(
            User.username == data["username"], User.id != user_id
        ).first()
        if existing:
            return error_response("Username already taken", 409)
        user.username = data["username"]

    if "email" in data:
        # Check email uniqueness
        existing = User.query.filter(
            User.email == data["email"], User.id != user_id
        ).first()
        if existing:
            return error_response("Email already registered", 409)
        user.email = data["email"]
    if "role" in data:
        user.role = data["role"]

    if "password" in data:
        user.set_password(data["password"])

    try:
        db.session.commit()
        return success_response(user.to_dict(), "User updated successfully")
    except Exception as e:
        db.session.rollback()
        return error_response("Update failed", 500)


@bp.route("/<int:user_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_user(user_id):
    """Delete user (admin only)"""
    current_user_id = get_jwt_identity()

    if user_id == current_user_id:
        return error_response("Cannot delete yourself", 400)

    user = User.query.get_or_404(user_id)

    try:
        db.session.delete(user)
        db.session.commit()
        return success_response(message="User deleted successfully")
    except Exception as e:
        db.session.rollback()
        return error_response("Delete failed", 500)
