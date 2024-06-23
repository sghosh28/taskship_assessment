from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, Item, get_user_collection, get_item_collection
from bson import ObjectId
from .decorators import verified_required, superuser_required

main = Blueprint('main', __name__)

@main.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"msg": "Username and password required"}), 400

    users = get_user_collection()
    if users.find_one({"username": username}):
        return jsonify({"msg": "User already exists"}), 400

    password_hash = generate_password_hash(password)
    user = User(username, password_hash)
    users.insert_one(user.to_dict())
    return jsonify({"msg": "User registered successfully"}), 201

@main.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"msg": "Username and password required"}), 400

    users = get_user_collection()
    user_data = users.find_one({"username": username})
    if not user_data or not check_password_hash(user_data['password_hash'], password):
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200

@main.route('/users', methods=['GET'])
@jwt_required()
@superuser_required
def get_users():
    users = get_user_collection().find()
    result = [{"_id": user["_id"], "username": user["username"], "role": user["role"]} for user in users]
    return jsonify(result), 200

@main.route('/userRole/<user_id>', methods=['POST'])
@jwt_required()
@superuser_required
def change_user_role(user_id):
    data = request.get_json()
    role = data.get('role')
    if not role:
        return jsonify({"msg": "Role required"}), 400

    if role not in ['unverified', 'verified', 'superUser']:
        return jsonify({"msg": "Invalid role"}), 400
    
    users = get_user_collection()
    result = users.update_one({"_id": user_id},{ "$set": { "role": role}})
    if result.matched_count == 0:
        return jsonify({"msg": "User not found"}), 404
    return jsonify({"msg": "User updated successfully"}), 200

@main.route('/items', methods=['POST'])
@jwt_required()
@verified_required
def create_item():
    data = request.get_json()
    user = get_jwt_identity()
    if 'name' not in data or 'description' not in data:
        return jsonify({"msg": "Invalid data"}), 400

    item = Item.from_dict(data, user)
    items = get_item_collection()
    item_insert = items.insert_one(item.to_dict())
    return jsonify({"id": item._id}), 201

@main.route('/items', methods=['GET'])
@jwt_required()
@verified_required
def get_items():
    user = get_jwt_identity()
    items = get_item_collection().find({"created_by": user})
    result = [{"id": str(item["_id"]), "name": item["name"], "description": item["description"], "created_by": item["created_by"], "created_at": item["created_at"]} for item in items]
    return jsonify(result), 200

@main.route('/items/<item_id>', methods=['GET'])
@jwt_required()
@verified_required
def get_item_by_id(item_id):
    user = get_jwt_identity()
    item = get_item_collection().find_one({"_id": item_id})
    if not item:
        return jsonify({"msg": "Item not found"}), 404
    if item["created_by"] != user:
        return jsonify({"msg": "Not Authoried for this item"}), 404
    return jsonify({"id": str(item["_id"]), "name": item["name"], "description": item["description"], "created_by": item["created_by"], "created_at": item["created_at"]}), 200

@main.route('/items/<item_id>', methods=['PUT'])
@jwt_required()
@verified_required
def update_item_by_id(item_id):
    data = request.get_json()
    if 'name' not in data or 'description' not in data:
        return jsonify({"msg": "Invalid data"}), 400
    user = get_jwt_identity()
    items = get_item_collection()
    result = items.update_one({"_id": item_id, "created_by": user}, {"$set": data})
    if result.matched_count == 0:
        return jsonify({"msg": "Item not found"}), 404
    return jsonify({"msg": "Item updated successfully"}), 200

@main.route('/items/<item_id>', methods=['DELETE'])
@jwt_required()
@verified_required
def delete_item_by_id(item_id):
    items = get_item_collection()
    user = get_jwt_identity()
    result = items.delete_one({"_id": item_id, "created_by": user})
    if result.deleted_count == 0:
        return jsonify({"msg": "Item not found"}), 404
    return jsonify({"msg": "Item deleted successfully"}), 200
