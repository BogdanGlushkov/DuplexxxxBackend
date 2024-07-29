from flask import Blueprint, request, jsonify

from app.models.Auth import Role, UserAcc

from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.extensions import db, bcrypt
from datetime import datetime, timedelta
from config import Config
    
    
auth = Blueprint('auth', __name__, template_folder='templates')
    
    
@auth.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = UserAcc.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        # Создайте токен, включая имя пользователя
        token = create_access_token(identity=user.id, additional_claims={"username": user.username, "role": user.role.name})
        return jsonify({'token': token}), 200

    return jsonify({'error': 'Invalid credentials'}), 401

@auth.route('/api/add_user', methods=['POST'])
@jwt_required()
def add_user():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'message': 'Access forbidden: Admins only'}), 403

    data = request.get_json()
    username = data['username']
    password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    role_name = data.get('role', 'user')
    role = Role.query.filter_by(name=role_name).first()
    
    if UserAcc.query.filter_by(username=username).first():
        return jsonify({'message': 'User already exists'}), 400

    new_user = UserAcc(username=username, password=password, role=role)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User added successfully'}), 201

@auth.route('/api/users', methods=['GET'])
@jwt_required()
def get_users():
    users = UserAcc.query.all()
    user_list = [{'id': user.id, 'username': user.username, 'role': user.role.name} for user in users]
    return jsonify(user_list), 200

@auth.route('/api/update_user/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    data = request.json
    user = UserAcc.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    user.username = data.get('username', user.username)
    if 'password' in data:
        user.password = bcrypt.generate_password_hash(data['password'])  # Ensure to hash passwords
    user.role_id = Role.query.filter_by(name=data.get('role')).first().id
    
    db.session.commit()
    return jsonify({'message': 'User updated successfully'}), 200

@auth.route('/api/delete_user/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    user = UserAcc.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200