from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from .models import get_user_collection

def role_required(required_role):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            current_user = get_jwt_identity()
            user_collection = get_user_collection()
            user = user_collection.find_one({"username": current_user})
            if user and user['role'] in required_role:
                return fn(*args, **kwargs)
            else:
                return jsonify({"msg": "Access forbidden: insufficient rights"}), 403
        return wrapper
    return decorator

def verified_required(fn):
    return role_required(['verified', 'superUser'])(fn)

def superuser_required(fn):
    return role_required(['superUser'])(fn)
 