from datetime import datetime
from bson import ObjectId
from flask import current_app
from flask_pymongo import PyMongo
import uuid
from . import mongo

    

def get_user_collection():
    return mongo.db.users

def get_item_collection():
    return mongo.db.item

class User:
    def __init__(self, username, password_hash, role='unverified'):
        self._id = str(uuid.uuid4())
        self.username = username
        self.password_hash = password_hash
        self.role = role

    def to_dict(self):
        return {
            "_id": self._id,
            "username": self.username,
            "password_hash": self.password_hash,
            "role": self.role
        }

    @staticmethod
    def from_dict(data):
        return User(
            username=data.get("username"),
            password_hash=data.get("password_hash"),
            role=data.get("role", 'unverified')
        )

class Item:
    def __init__(self, name, description, created_by, created_at=None):
        # put self.id = uuid        
        self._id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.created_by = created_by
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self):
        return {
            "_id": self._id,
            "name": self.name,
            "description": self.description,
            "created_by": self.created_by,
            "created_at": self.created_at
        }

    @staticmethod
    def from_dict(data, user_id):
        return Item(
            name=data.get("name"),
            description=data.get("description"),
            created_by=user_id,
            created_at=data.get("created_at", datetime.utcnow())
        )
